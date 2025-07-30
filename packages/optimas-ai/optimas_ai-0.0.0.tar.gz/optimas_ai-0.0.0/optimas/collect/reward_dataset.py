import json
from typing import Any, Dict, List, Tuple, Union

import numpy as np
from tqdm import tqdm
from datasets import Dataset, DatasetDict
from collections import defaultdict
from contextlib import nullcontext

from optimas.arch.system import CompoundAISystem
from optimas.collect.process import process_dataset_parallel
from optimas.collect.sample import generate_samples, evaluate_samples
from optimas.collect.utils import get_context_from_traj
from optimas.utils.logger import setup_logger
from optimas.wrappers.example import Example
from optimas.wrappers.prediction import Prediction

logger = setup_logger(__name__)


def generate_reward_dataset(
    system: CompoundAISystem,
    dataset: Union[List[Example], Tuple[List[Example], List[Prediction]]],
    component_names: List[str] = None,
    num_forward_estimate: int = 3,
    num_repeat_samples: int = 3,
    max_workers: int = 16,
    process_reward_func: Any = None,
    forward_to_component: str = None,
    sample_temperature: float = None,
    num_per_instance: int = 1,
    **kwargs
) -> DatasetDict:
    """
    Generate a DatasetDict containing preference pairs

    Procedure:
      1) Process the original dataset in parallel to get the base (examples, preds, scores).
      2) For each component in component_names:
         a) Generate trajectory samples (perturbations) for each example.
         b) Collect all (example_index, example, trajectory) into one flat list.
         c) Evaluate these perturbed trajectories in parallel (no separate nums needed).
         d) Group the results by example_index to find the best and worst trajectories.
         e) Build a preference pair for each example (context + chosen vs. rejected outputs).
      3) Store the results in a Hugging Face DatasetDict keyed by component.

    Args:
        system: The system to process and evaluate examples.
        component_names: A list of components to be perturbed.
        dataset: The input dataset (list of Example objects).
        num_forward_estimate: How many components to move forward for evaluation.
        max_workers: Maximum parallel workers used (for both process and evaluation).
        num_repeat_samples: Number of perturbed samples to generate per example per component.
        **kwargs: Additional keyword arguments (unused here).

    Returns:
        A DatasetDict keyed by component, where each Dataset contains:
          - context
          - response_chosen
          - response_rejected
          - score_chosen
          - score_rejected
          - info_chosen
          - info_rejected
    """

    system_context = {}
    for component_name in system.components:
        if hasattr(system.components[component_name], "temperature") and sample_temperature is not None:
            system_context[component_name] = {"temperature": sample_temperature}
        if getattr(system.components[component_name], "variable_search_space", None):
            system_context[component_name] = {"randomize_variable": True}

    # 1) Process the base dataset in parallel
    if isinstance(dataset, tuple):
        logger.info("Using pre-processed dataset.")
        examples, preds = dataset
    else:
        with system.context(system_context):
            examples, preds, _ = process_dataset_parallel(
                dataset=dataset,
                system=system,
                max_workers=max_workers,
            )

    if component_names is None:
        component_names = [key for key in system.components.keys() if system.components[key].optimizable]

    dataset_dict = {}

    # 2) For each component, generate preference pairs
    for component_name in component_names:  # component_names[::-1]:
        # A. Generate all traj samples for each example, flattening into one list
        flat_eval_list = []  # will hold tuples of (example_index, example, trajectory)

        for i in tqdm(range(len(examples)), desc=f"Generate Samples for {component_name}"):
            for _ in range(num_per_instance):
                example, pred = examples[i], preds[i]
                component = system.components[component_name]

                with system.context(system_context):
                    # Use the appropriate context manager
                    traj_samples = generate_samples(
                        system=system,
                        example=example,
                        traj=pred.traj,
                        components_to_perturb=[component_name],
                        num_samples=num_repeat_samples,
                        max_workers=max_workers
                    )
                # If we have more than 1 unique variant, collect them for evaluation
                if traj_samples and len(traj_samples) > 1:
                    for traj in traj_samples:
                        flat_eval_list.append((i, example, traj))
                else:
                    logger.info(f"Skipping example {i} for component {component_name} due to insufficient variants.")

        # B. Evaluate all trajectories in one go
        scores_and_infos = evaluate_samples(
            system=system,
            examples=[x[1] for x in flat_eval_list],  # extract the Example
            trajs=[x[2] for x in flat_eval_list],     # extract the trajectory
            max_workers=max_workers,
            num_forward_estimate=num_forward_estimate,
            forward_to_component=forward_to_component,
            process_reward_func=process_reward_func
        )
        # scores_and_infos is a list of (score, info), same length as flat_eval_list

        # C. Group the results by example_index
        # We'll create a dict: example_index -> list of (score, info, trajectory)
        results_by_example = defaultdict(list)

        for (ex_idx, ex, traj), (score, info) in zip(flat_eval_list, scores_and_infos):
            results_by_example[ex_idx].append((score, info, traj))

        # D. For each example, pick chosen (max) and rejected (min) based on scores
        preference_data = []
        for idx, example in enumerate(examples):
            # If this example had no additional samples, skip
            if idx not in results_by_example:
                continue

            # results for one example: a list of (score, info, trajectory)
            sample_results = results_by_example[idx]

            # If there's only 1 variant, we can't form a pair
            if len(sample_results) < 2:
                continue

            # scores
            score_list = [r[0] for r in sample_results]
            info_list = [r[1] for r in sample_results]
            traj_list = [r[2] for r in sample_results]

            chosen_idx = int(np.argmax(score_list))
            rejected_idx = int(np.argmin(score_list))

            # Construct the context from the first trajectory's context
            # (or any reference trajectory, since they should share the same context)
            reference_traj = traj_list[0]
            context = {
                k: v
                for k, v in reference_traj.items()
                if k != component_name
            }
            # Keep the current component's input from reference
            context.update({
                component_name: {"input": reference_traj[component_name]["input"]}
            })

            # If it's the last component, we can use the reference output
            if component_name == list(system.components.keys())[-1]:
                try:
                    # TODO: HARD CODED FOR NOW
                    if "gd_answer" in system.ground_fields or "groundtruth" in system.ground_fields:
                        ground_field = system.ground_fields[0]
                        key = system.final_output_fields[0]
                        traj_list.append({component_name: {"output": {key: example[ground_field]}, "variable": "none"}})
                    else:
                        keys = system.final_output_fields
                        traj_list.append({component_name: {"output": {key: example[key] for key in keys}, "variable": "none"}})
                    # TODO: HERE ASSUMES THE BEST METRIC TO BE 1.0
                    info_list.append([None])
                    score_list.append(1.0)
                except Exception as e:
                    logger.error(f"Cannot get ground truth for example {idx} in component {component_name}: {e}")
                    pass

            # get all the (i, j) index pairs where score_list[i] > score_list[j] and i>j
            index_pairs = [
                (i, j) for i in range(len(score_list)) for j in range(len(score_list))
                if score_list[i] > score_list[j] and i > j
            ]

            for i, j in index_pairs:
                preference_data.append({
                    "context": context,
                    "response_chosen": traj_list[i][component_name]["output"],
                    "response_rejected": traj_list[j][component_name]["output"],
                    "score_chosen": score_list[i],
                    "score_rejected": score_list[j],
                    "info_chosen": info_list[i],
                    "info_rejected": info_list[j],
                    "variable_chosen": traj_list[i][component_name]["variable"],
                    "variable_rejected": traj_list[j][component_name]["variable"],
                })

        if len(preference_data) > 0:
            dataset_dict[component_name] = Dataset.from_dict({
                "context": [
                    json.dumps(d["context"]) for d in preference_data
                ],
                "response_chosen": [
                    json.dumps(d["response_chosen"]) for d in preference_data
                ],
                "response_rejected": [
                    json.dumps(d["response_rejected"]) for d in preference_data
                ],
                "score_chosen": [
                    d["score_chosen"] for d in preference_data
                ],
                "score_rejected": [
                    d["score_rejected"] for d in preference_data
                ],
                "info_chosen": [
                    json.dumps(d["info_chosen"]) for d in preference_data
                ],
                "info_rejected": [
                    json.dumps(d["info_rejected"]) for d in preference_data
                ],
                "variable_chosen": [
                    json.dumps(d["variable_chosen"]) for d in preference_data
                ],
                "variable_rejected": [
                    json.dumps(d["variable_rejected"]) for d in preference_data
                ],
            })

    return DatasetDict(dataset_dict)
