import copy
import torch
from typing import Any, Dict, List
from datasets import DatasetDict
from optimas.optim.args import OptimasArguments
from optimas.arch.system import CompoundAISystem
from optimas.reward.model import RewardModel
from optimas.utils.logger import setup_logger
from optimas.utils.parallel import run_parallel_tasks
from optimas.wrappers.prediction import Prediction
from optimas.optim.opro import OPRO
from optimas.optim.ppo import train_ppo
from optimas.wrappers.example import Example
from optimas.utils.lora import *
from optimas.optim.cp_optimizer import ComponentOptimizer
import json
import itertools
import os
import random   
from pathlib import Path


import numpy as np
import random
from tqdm import tqdm
from collections import defaultdict, deque
from datasets import Dataset
from optimas.collect.reward_dataset import generate_reward_dataset
from optimas.reward.eval import eval_system
from optimas.reward.dataset import RewardDataset
from optimas.external import RewardConfig
from optimas.reward.finetune import run_finetune
import wandb

logger = setup_logger(__name__)


class OptimasOptimizer:
    def __init__(
        self,
        system,
        train_dataset,
        val_dataset,
        test_dataset,
        preference_dataset=None,  # Added parameter for existing preference dataset
        reward_model=None,
        per_iteration_rm_train_size=-1,
        tokenizer=None,
        iterations=5,
        per_iteration_input_size=20,
        base_model_name="meta-llama/Llama-3.1-8B-Instruct",
        output_dir="./outputs",
        cooldown_period=1,  # Number of iterations before a component can be optimized again
        optimas_args=None,  # Add OptimasArguments
        replay_buffer_size=200,
        use_replay_buffer=False
    ):
        self.system = system
        self.train_dataset = train_dataset
        self.val_dataset = val_dataset
        self.test_dataset = test_dataset
        self.preference_dataset = preference_dataset
        self.reward_model = reward_model
        self.per_iteration_rm_train_size = per_iteration_rm_train_size
        self.iterations = iterations
        self.per_iteration_input_size = per_iteration_input_size
        self.component_performance_history = defaultdict(list)
        self.logger = setup_logger("optimizer")
        self.base_model_name = base_model_name
        self.output_dir = output_dir
        self.tokenizer = tokenizer
        self.cooldown_period = cooldown_period
        self.optimas_args = optimas_args  # Store the optimas arguments
        self.use_replay_buffer = use_replay_buffer
        self.replay_buffer = deque(maxlen=replay_buffer_size) if use_replay_buffer else None

        # Track recently optimized components
        self.recently_optimized = {}  # Module name -> iteration when last optimized

        # Track current adapter paths for local_lm components
        self.current_adapters = {}  # component_name -> adapter_path

        # Make sure output directory exists
        os.makedirs(output_dir, exist_ok=True)

    def select_component_to_optimize(self, preference_dataset, current_iteration):
        """
        Select a component to optimize based on the score gaps in preference data.
        Uses softmax to probabilistically select components with higher average gaps.
        Args:
            preference_dataset: DatasetDict containing preference pairs for each component
            current_iteration: The current optimization iteration
        Returns:
            String: The selected component name, or None if no eligible components
        """
        if not preference_dataset:
            component_names = list(component_gaps.keys())
            return random.choice(component_names) if component_names else None

        # Calculate average score gap for each component
        component_gaps = {}
        for component_name, dataset in preference_dataset.items():
            # Skip components that were recently optimized (still in cooldown)
            if (
                component_name in self.recently_optimized
                and current_iteration - self.recently_optimized[component_name]
                < self.cooldown_period
            ):
                self.logger.info(
                    f"Module {component_name} is in cooldown period, skipping"
                )
                continue

            # Calculate average gap between chosen and rejected scores
            score_chosen = dataset["score_chosen"]
            score_rejected = dataset["score_rejected"]
            if len(score_chosen) == 0:
                continue

            avg_gap = sum(c - r for c, r in zip(score_chosen, score_rejected)) / len(
                score_chosen
            )
            component_gaps[component_name] = avg_gap
            self.logger.info(f"Module {component_name} average score gap: {avg_gap:.4f}")

        if not component_gaps:
            self.logger.warning(
                "No eligible components found (all in cooldown or no data)"
            )
            return None

        # Apply softmax to create probability distribution
        component_names = list(component_gaps.keys())
        gap_values = [component_gaps[name] for name in component_names]

        # Convert to torch tensor and apply softmax
        gaps_tensor = torch.tensor(gap_values)
        probs = torch.nn.functional.softmax(gaps_tensor, dim=0).numpy()

        # Sample a component based on probabilities
        selected_idx = np.random.choice(len(component_names), p=probs)

        # log each component's probability
        wandb.log(
            {"iteration": current_iteration,
             **{f"prob_{component_name}": prob for component_name, prob in zip(component_names, probs)}}
        )

        selected_component = component_names[selected_idx]
        self.logger.info(
            f"Selected component {selected_component} for optimization with probability {probs[selected_idx]:.4f}"
        )

        # Log all component probabilities for transparency
        for i, name in enumerate(component_names):
            self.logger.info(
                f"Module {name}: gap={gap_values[i]:.4f}, probability={probs[i]:.4f}"
            )
        return selected_component

    def _is_local_lm_component(self, component_name):
        component = self.system.components[component_name]
        return isinstance(component.variable, Path)

    def _update_system_with_adapter(self, component_name, adapter_path):
        """Update system to use the new adapter for a local LLM component"""
        # Store the adapter path
        self.current_adapters[component_name] = adapter_path

        # Update the component's adapter_path to use the new adapter
        component = self.system.components[component_name]
        component.update(adapter_path)
        
    def _get_current_adapter_state(self):
        """Get the current state of all adapters for saving/loading"""
        return copy.deepcopy(self.current_adapters)

    def _restore_adapter_state(self, adapter_state):
        """Restore adapter state and update system accordingly"""
        for component_name, adapter_path in adapter_state.items():
            if adapter_path and self._is_local_lm_component(component_name):
                self._update_system_with_adapter(component_name, adapter_path)
        self.current_adapters = copy.deepcopy(adapter_state)

    def optimize_component(self, component_name, hf_repo_or_local_dir):
        """
        Optimize a specific component using techniques from the existing framework.
        For local LLM components, this includes PPO training.
        """
        self.logger.info(f"Optimizing component: {component_name}")

        self.reward_model.eval()
        reward_model = RewardModel(self.reward_model, self.tokenizer, self.system)

        # Prepare dataset specific to this component
        train_dataset = RewardDataset(
            system=self.system,
            hf_repo_or_local_dir=hf_repo_or_local_dir,
            original_trainset=self.train_dataset + self.test_dataset,
        ).to_inputs_only_dataset()

        self.logger.info(f'Training dataset size: {len(train_dataset[component_name]["input"])}')

        # Clone and modify optimas_args for this specific component
        component_optimas_args = copy.deepcopy(self.optimas_args)

        # Override with component-specific settings
        component_optimas_args.components_to_apply = [
            component_name
        ]  # Focus only on this component
        component_optimas_args.per_component_train_size = min(
            len(train_dataset[component_name]["input"]), component_optimas_args.per_component_train_size
        )

        # Create component-specific output dir
        component_output_dir = os.path.join(self.output_dir, f"optim_{component_name}")
        os.makedirs(component_output_dir, exist_ok=True)
        component_optimas_args.output_dir = component_output_dir

        self.logger.info(
            f"Configured OptimasArguments for {component_name}: {vars(component_optimas_args)}"
        )

        # Initialize and run optimizer with the args from command line
        optimizer = ComponentOptimizer(
            args=component_optimas_args,
            system=self.system,
            reward_model=reward_model,
            train_dataset=train_dataset,
            original_trainset=self.train_dataset,
            val_dataset=self.val_dataset,
            val_metrics_path=os.path.join(component_output_dir, "val_metrics.json"),
        )

        # Optimize just this component
        optimized_system = optimizer.optimize()

        # For local LLM components, check if PPO training produced new adapters
        if self._is_local_lm_component(component_name):
            # Look for PPO output directory
            ppo_output_dir = os.path.join(component_output_dir, "ppo", component_name)
            if os.path.exists(ppo_output_dir):
                # Find the best adapter using the enhanced function
                new_adapter_path = get_adapter_from_ppo_output(component_output_dir, component_name)

                if new_adapter_path:
                    self.logger.info(f"Found new adapter for {component_name}: {new_adapter_path}")

                    # Update the system to use the new adapter
                    self._update_system_with_adapter(component_name, new_adapter_path)
                else:
                    self.logger.warning(f"No valid adapter found in PPO output directory: {ppo_output_dir}")
            else:
                self.logger.info(f"No PPO output directory found: {ppo_output_dir}")

        return optimized_system

    def train_reward_model(self, component_name, hf_repo_or_local_dir, per_iteration_rm_train_size=-1):
        """
        Train a reward model on the collected preference data for the specified component.
        Args:
            component_name: Name of the component to train the reward model for
            hf_repo_or_local_dir: Path to the preference dataset
        Returns:
            Trained reward model
        """
        self.logger.info(f"Training reward model for component: {component_name}")
        # Create component-specific output directory
        component_output_dir = os.path.join(self.output_dir, f"reward_model_{component_name}")
        os.makedirs(component_output_dir, exist_ok=True)

        # Training configuration
        training_args = RewardConfig(
            do_train=True,
            output_dir=component_output_dir,
            logging_dir=component_output_dir,
            per_device_train_batch_size=2,
            per_device_eval_batch_size=2,
            gradient_accumulation_steps=8,
            learning_rate=5e-5,
            num_train_epochs=1,
            max_length=2048,
            logging_steps=10,
            eval_steps=50,
            save_steps=50,
            eval_strategy="no",
            metric_for_best_model="eval_loss",
            load_best_model_at_end=False,
            use_score_scaling=False,
            use_score_norm=False,
            ddp_find_unused_parameters=False,
        )

        # Load dataset
        reward_dataset = RewardDataset(hf_repo_or_local_dir, self.system)

        # Format the dataset
        ds = reward_dataset.to_preference_dataset(eval_ratio=0, add_margin=False)

        if per_iteration_rm_train_size != -1:
            # shuffle and take the first per_iteration_rm_train_size samples
            random.seed(42)
            train_list = ds["train"].to_list()
            random.shuffle(train_list)
            train_list = train_list[:per_iteration_rm_train_size]
            ds["train"] = Dataset.from_list(train_list)
        # Otherwise use the full reward dataset

        # Train the reward model
        trainer = run_finetune(
            ds,
            self.reward_model,
            self.tokenizer,
            training_args,
            train_last_layer=True,
            component_to_idx={component_name: self.system.optimizable_component_to_idx[component_name]}
        )

        return trainer.model

    def optimize(self):
        """
        Main optimization loop using the existing preference dataset to select components.
        """
        # Store initial system state dict for comparison
        original_state_dict = self.system.state_dict()
        original_adapter_state = self._get_current_adapter_state()

        # Optimization history
        history = {"iterations": [], "overall_performance": []}

        # Set reward_model at the beginning
        local_hyper_param_search = any([component.variable_search_space for component in self.system.components.values()])
        if not self.optimas_args.global_hyper_param_search and local_hyper_param_search:
            self.system.register_rm(
                RewardModel(self.reward_model, self.tokenizer, self.system), sample_size=1
            ) # => sample_size=1 causes no effect to components without variable_search_space

        # Evaluate initial performance
        try:
            metrics, _ = eval_system(system=self.system, testset=self.val_dataset, num_repeat=1)
            initial_score = metrics['mean']
            self.logger.info(f"Initial score: {initial_score:.4f}")
        except Exception as e:
            self.logger.warning(
                f"Error evaluating initial system: {e}. Setting initial score to 0."
            )
            initial_score = 0

        history["overall_performance"].append(initial_score)

        # Best score and system state so far
        best_score = initial_score
        best_state_dict = original_state_dict
        best_adapter_state = original_adapter_state
        current_best_iteration = 0

        wandb.log(
            {
                "iteration": 0,
                "eval/score": best_score,
                "eval/best_score": best_score
            }
        )

        skip_data_gen = self.optimas_args.skip_data_gen
        flag_data_gen = self.preference_dataset is None

        if skip_data_gen and not self.preference_dataset:
            self.logger.error(
                "Skipping online data generation but no preference dataset provided. "
                "Will not be able to optimize components."
            )
            return self.system, history

        # Log preference dataset stats
        if self.preference_dataset:
            self.logger.info("Using provided preference dataset:")
            for component_name, dataset in self.preference_dataset.items():
                self.logger.info(f"  {component_name}: {len(dataset)} preference pairs")

        # Main optimization loop
        self.logger.info("Starting optimization iterations...")
        for iteration in range(self.iterations):
            self.logger.info(f"Starting iteration {iteration+1}/{self.iterations}")

            # Select a component to optimize based on preference data
            component_to_optimize = self.select_component_to_optimize(
                self.preference_dataset, iteration
            )

            if not component_to_optimize:
                self.logger.warning(
                    "No suitable component to optimize, ending optimization"
                )
                break

            self.logger.info(f"Selected component to optimize: {component_to_optimize}")
            
            if skip_data_gen or not flag_data_gen:
                self.logger.info(
                    "Skipping fresh training dataset generation: either skip_data_gen is enabled "
                    "or reusing existing preference_dataset until performance improves"
                )
                fresh_preference_dataset = [component_to_optimize]
            else:
                subset_size = min(len(self.train_dataset), self.per_iteration_input_size)
                dataset_subset = random.sample(self.train_dataset, subset_size)
                fresh_preference_dataset = generate_reward_dataset(
                    system=self.system,
                    dataset=dataset_subset,
                    component_names=[component_to_optimize],
                    num_forward_estimate=3,
                    num_repeat_samples=5,
                    max_workers=4,
                    num_per_instance=1
                )

            # ------------------------------------------------------------------
            # Build training dataset for reward-model update
            # ------------------------------------------------------------------
            if component_to_optimize in fresh_preference_dataset:

                if not enable_data_gen or skip_online_datagen:
                    dataset_path = os.path.join(
                        self.output_dir,
                        f"preference_dataset_{iteration}_{component_to_optimize}",
                    )
                    selected_data = {
                        component_to_optimize: self.preference_dataset[component_to_optimize]
                    }
                    DatasetDict(selected_data).save_to_disk(dataset_path)

                elif self.use_replay_buffer:
                    dataset = fresh_preference_dataset[component_to_optimize]

                    # 1) push new pairs into buffer
                    for i in range(len(dataset)):
                        sample = {
                            "context": dataset["context"][i],
                            "response_chosen": dataset["response_chosen"][i],
                            "response_rejected": dataset["response_rejected"][i],
                            "score_chosen": dataset["score_chosen"][i],
                            "score_rejected": dataset["score_rejected"][i],
                        }
                        if "margin" in dataset.column_names:
                            sample["margin"] = dataset["margin"][i]
                        self.replay_buffer.append(sample)

                    self.logger.info(
                        f"Added {len(dataset)} samples to buffer. "
                        f"Buffer size = {len(self.replay_buffer)}/{self.replay_buffer.maxlen}"
                    )

                    # 2) convert entire buffer back to Dataset
                    buffer_data = {
                        "context": [s["context"] for s in self.replay_buffer],
                        "response_chosen": [s["response_chosen"] for s in self.replay_buffer],
                        "response_rejected": [s["response_rejected"] for s in self.replay_buffer],
                        "score_chosen": [s["score_chosen"] for s in self.replay_buffer],
                        "score_rejected": [s["score_rejected"] for s in self.replay_buffer],
                    }
                    if any("margin" in s for s in self.replay_buffer):
                        buffer_data["margin"] = [s.get("margin", 0.0) for s in self.replay_buffer]

                    training_dataset = DatasetDict(
                        {component_to_optimize: Dataset.from_dict(buffer_data)}
                    )

                    dataset_path = os.path.join(
                        self.output_dir,
                        f"buffer_preference_dataset_{iteration}_{component_to_optimize}",
                    )
                    training_dataset.save_to_disk(dataset_path)

                else:
                    dataset_path = os.path.join(
                        self.output_dir,
                        f"fresh_preference_dataset_{iteration}_{component_to_optimize}",
                    )
                    fresh_preference_dataset.save_to_disk(dataset_path)

                # -------- reward-model fine-tune on dataset_path --------
                trained_model = self.train_reward_model(
                    component_to_optimize, dataset_path, self.per_iteration_rm_train_size
                )
                self.reward_model = trained_model

                # Save the current system state before optimization
                current_state_dict = self.system.state_dict()
                current_adapter_state = self._get_current_adapter_state()

                # Optimize the component
                optimized_system = self.optimize_component(
                    component_to_optimize, dataset_path
                )

                if not self.optimas_args.global_hyper_param_search and local_hyper_param_search:
                    self.system.register_rm(
                        RewardModel(self.reward_model, self.tokenizer, self.system), sample_size=1
                    )

                # Evaluate optimized system
                try:
                    metrics, _ = eval_system(system=optimized_system, testset=self.val_dataset, num_repeat=1)
                    new_score = metrics['mean']
                    self.logger.info(
                        f"After optimizing {component_to_optimize}, score: {new_score:.4f} (previous: {best_score:.4f})"
                    )

                    # Record this successful optimization
                    history["iterations"].append(
                        {
                            "iteration": iteration + 1,
                            "current_best_iteration": current_best_iteration,
                            "component_optimized": component_to_optimize,
                            "score_before": best_score,
                            "score_after": new_score,
                            "improvement": new_score - best_score,
                        }
                    )

                    if self.preference_dataset:
                        history["iterations"][-1]["gap_data"] = {
                            "num_pairs": len(
                                self.preference_dataset[component_to_optimize]
                            ),
                            "avg_gap": sum(
                                self.preference_dataset[component_to_optimize][
                                    "score_chosen"
                                ]
                            )
                            / len(self.preference_dataset[component_to_optimize])
                            - sum(
                                self.preference_dataset[component_to_optimize][
                                    "score_rejected"
                                ]
                            )
                            / len(self.preference_dataset[component_to_optimize]),
                        }


                    wandb.log(
                        {
                            "iteration": iteration + 1,
                            "component_idx": self.system.optimizable_component_to_idx[component_to_optimize],
                            "eval/score": new_score,
                            "eval/best_score": best_score
                        }
                    )

                    # Check if there's improvement
                    if new_score > best_score:
                        flag_data_gen = True
                        self.logger.info(
                            f"Performance improved from {best_score:.4f} to {new_score:.4f}"
                        )
                        best_score = new_score
                        best_state_dict = optimized_system.state_dict()
                        best_adapter_state = self._get_current_adapter_state()
                        current_best_iteration = iteration + 1

                        # Save the improved system state
                        torch.save(
                            best_state_dict,
                            os.path.join(
                                self.output_dir,
                                f"system_state_iteration_{iteration+1}_{component_to_optimize}.pth",
                            ),
                        )

                        # Save adapter state
                        with open(
                            os.path.join(
                                self.output_dir,
                                f"adapter_state_iteration_{iteration+1}_{component_to_optimize}.json",
                            ), "w"
                        ) as f:
                            json.dump(best_adapter_state, f, indent=2)

                        # Mark this component as recently optimized
                        self.recently_optimized[component_to_optimize] = iteration
                    else:
                        self.logger.info(
                            f"No improvement from optimizing {component_to_optimize}, reverting"
                        )
                        # Revert the system state
                        self.system.load_state_dict(current_state_dict)
                        self._restore_adapter_state(current_adapter_state)
                        
                except Exception as e:
                    self.logger.error(
                        f"Error evaluating optimized system: {e}. Reverting."
                    )
                    # Revert the system state
                    self.system.load_state_dict(current_state_dict)
                    self._restore_adapter_state(current_adapter_state)
            else:
                self.logger.warning(
                    f"No preference data available for component {component_to_optimize}"
                )

            # Update to best state so far for next iteration
            self.system.load_state_dict(best_state_dict)
            self._restore_adapter_state(best_adapter_state)

            # Update performance history
            history["overall_performance"].append(best_score)

        # Final improvement calculation
        improvement = best_score - initial_score
        self.logger.info(
            f"Overall improvement: {improvement:.4f} ({initial_score:.4f} to {best_score:.4f})"
        )
        history["overall_improvement"] = improvement

        # Ensure we return the system with the best state
        self.system.load_state_dict(best_state_dict)
        self._restore_adapter_state(best_adapter_state)

        return self.system, history
