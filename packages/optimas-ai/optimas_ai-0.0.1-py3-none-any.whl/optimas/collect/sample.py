import copy
from typing import Any, Dict, List, Optional, Tuple
from optimas.arch.system import CompoundAISystem
from concurrent.futures import ThreadPoolExecutor

from optimas.collect.process import process_dataset_parallel
from optimas.wrappers.example import Example
from optimas.wrappers.prediction import Prediction
from optimas.utils.operation import unique_objects
from optimas.collect.utils import get_context_from_traj
from tqdm import tqdm


def generate_samples(
    system: CompoundAISystem,
    example: Example,
    components_to_perturb: List[str],
    traj: Dict,
    num_samples: int = 3,
    max_workers: int = 8
) -> List[Any]:
    """
    Generates candidate states by perturbing outputs from specified components.

    Args:
        system (CompoundAISystem): The system used to run sub-systems.
        components_to_perturb (List[str]): Names of components to perturb.
        traj (Dict): The trajectory dictionary used to reference the original states.
        num_samples (int, optional): Number of samples to generate.
        max_workers (int, optional): Number of workers for parallel sampling.

    Returns:
        List[Any]: A list of unique samples (each sample's structure depends on your system).
                   If no unique samples can be generated, an empty list might be returned.
    """
    component_names = list(system.components.keys())
    components_to_perturb_idx = [component_names.index(m) for m in components_to_perturb]
    earliest_midx, latest_midx = min(components_to_perturb_idx), max(components_to_perturb_idx)
    latest_component_name = component_names[latest_midx]
    
    # Build the original trajectory subset
    original_traj = {m: traj[m] for m in component_names[:latest_midx + 1]}

    # Flatten the context from all components before earliest_midx
    context = {
        **{k: getattr(example, k) for k in system.required_input_fields},
        **{
            k: v 
            for m in component_names[:earliest_midx] 
            for k, v in traj[m]['input'].items()
        },
        **{
            k: v 
            for m in component_names[:earliest_midx] 
            for k, v in traj[m]['output'].items()
        },
    }
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        perturbed_samples = list(
            executor.map(
                lambda _: system.run_subsystem(
                    start_component=earliest_midx,
                    end_component=latest_midx,
                    **context
                ),
                range(num_samples)
            )
        )
    # Append the original traj for uniqueness checking
    perturbed_trajs = [{**original_traj, **s.traj} for s in perturbed_samples]
    perturbed_trajs.append(original_traj)

    # Identify unique outputs from the latest component's 'output'
    _, unique_indices = unique_objects(
        [t[latest_component_name]['output'] for t in perturbed_trajs],
        return_idx=True
    )
    unique_samples = [perturbed_trajs[i] for i in unique_indices]

    return unique_samples


def evaluate_samples(
    system,
    examples: List[Example],
    trajs: List[Dict],
    forward_to_component: str = None,
    process_reward_func: callable = None,
    max_workers: int = 8,
    num_forward_estimate: int = 3,
) -> List[Tuple[Any, Dict]]:
    """
    Evaluate multiple (example, traj) pairs in parallel using ThreadPoolExecutor.
    Args:
        system: The system or CompoundAISystem used for sub-system runs/evaluation.
        examples: A list of Example objects, each representing inputs to evaluate.
        trajs: A corresponding list of partial trajectories (dict), one per example.
        forward_to_component: (Optional) Module name at which to stop if not running to the end.
        process_reward_func: (Optional) Custom function for computing final score if we stop before the last component.
        max_workers: Number of parallel threads to use (default=8).

    Returns:
        A list of (score_list, final_output_list) tuples for each (example, pred) pair.
    """

    # Ensure that examples and trajs align
    if len(examples) != len(trajs):
        raise ValueError("Number of examples must match number of trajs.")

    component_names = list(system.components.keys())

    if forward_to_component is None:
        forward_to_component = component_names[-1]

    def single_eval(example_and_traj: Tuple[Example, Dict]) -> Tuple[Any, dict]:
        example, traj = example_and_traj

        # Copy the trajectory to avoid mutating the original
        local_traj = copy.copy(traj)

        # Identify completed components
        existing_component_names = list(local_traj.keys())
        if not existing_component_names:
            raise ValueError("Trajectory is empty—no components in `traj`.")

        # Convert each existing component name to its index and pick the max
        existing_component_indices = [component_names.index(m) for m in existing_component_names]
        last_completed_idx = max(existing_component_indices)

        # Build the context from current trajectory
        context = get_context_from_traj(local_traj)

        # Always add fields required by the system
        context.update({k: getattr(example, k) for k in system.required_input_fields})
        
        scores, preds = [], []
        for _ in range(num_forward_estimate):
            if last_completed_idx + 1 < len(component_names):
                # Run sub-system from the component AFTER the last completed to the scorer component
                pred = system.run_subsystem(
                    start_component=last_completed_idx + 1,
                    end_component=forward_to_component,
                    **context
                )
            else:
                pred = Prediction(**context, traj=local_traj)

            # If we ended on the last component, evaluate directly
            if forward_to_component == component_names[-1]:
                score = system.evaluate(example, pred)
            else:
                # Use the custom reward function for scoring
                if process_reward_func is None:
                    raise ValueError(
                        "Must provide process_reward_func if not running to the final component."
                    )
                score = process_reward_func(system, example, pred)
            scores.append(score)
            preds.append(pred)

        avg_score = sum(scores) / len(scores)
        additional_info = [{"traj": p.traj, "score": s} for p, s in zip(preds, scores)]
        return avg_score, additional_info

    # Parallelize the evaluation over all (example, traj) pairs
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = executor.map(single_eval, zip(examples, trajs))
        results = list(
            tqdm(futures, total=len(examples), desc="Evaluating Samples")
        )
    return results