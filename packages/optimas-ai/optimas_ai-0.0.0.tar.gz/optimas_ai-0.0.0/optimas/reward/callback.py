import copy
import os
import re
import json
import wandb
import shutil
import numpy as np
import torch
import importlib.util
from pathlib import Path
from typing import List, Optional, Callable
from transformers import TrainerCallback

from optimas.utils.save import save_model_and_tokenizer
from optimas.utils.logger import setup_logger
from optimas.arch.system import CompoundAISystem
from optimas.reward.eval import eval_system
from optimas.reward.model import RewardModel
import time

logger = setup_logger(__name__)

PREFIX_STATE_DICT_DIR = "full"
PREFIX_CHECKPOINT_DIR = "checkpoint"


# Integration functions:
def is_wandb_available():
    # any value of WANDB_DISABLED disables wandb
    ENV_VARS_TRUE_VALUES = {"1", "ON", "YES", "TRUE"}
    if os.getenv("WANDB_DISABLED", "").upper() in ENV_VARS_TRUE_VALUES:
        logger.warning(
            "Using the `WANDB_DISABLED` environment variable is deprecated and will be removed in v5. Use the "
            "--report_to flag to control the integrations used for logging result (for instance --report_to none)."
        )
        return False
    return importlib.util.find_spec("wandb") is not None


class PerComponentSaveCallback(TrainerCallback):
    """
    A TrainerCallback that saves model checkpoints, manages full model backups, and tracks the best model 
    based on evaluation metrics.
    """
    def __init__(
        self,
        system: CompoundAISystem,
        tokenizer,
        metric_for_best_model: str,
        repo_name: str = None,
        push_to_hub: bool = False,
        criteria: Optional[Callable[[str], bool]] = None,
        save_model_per_component: bool = True
    ):
        """
        Initializes the callback.
        Args:
            tokenizer: Tokenizer to save along with the model.
            repo_name (str): Repository name for pushing to the hub.
            push_to_hub (bool, optional): Whether to push model checkpoints to the hub. Default is False.
            criteria (callable, optional): Function to filter which model parameters to save.
                                           Defaults to saving LoRA weights and 'score.weight'.
        """
        self.tokenizer = tokenizer
        self.repo_name = repo_name

        self.component_names = [m for m in system.components if system.components[m].optimizable] if system else []
            
        self.metric_for_best_model = metric_for_best_model
        self.save_model_per_component = save_model_per_component
        self.criteria = criteria or (lambda x: "score.weight" in x.lower() or "lora" in x.lower())
        
        self.push_to_hub = push_to_hub
    
    def on_train_begin(self, args, state, control, model, **kwargs):
        """
        Initializes the callback.
        """
        if not state.is_world_process_zero:
            return

        # Save the initial model and tokenizer
        self.init_model_path = os.path.join(args.output_dir, f"{PREFIX_STATE_DICT_DIR}-init")
        save_model_and_tokenizer(
            model, self.tokenizer, self.init_model_path,
            repo_name=self.repo_name, push_to_hub=self.push_to_hub, criteria=self.criteria
        )

    def on_train_end(self, args, state, control, model, **kwargs):
        """
        Saves the final full model and renames the best checkpoint based on evaluation metrics.
        This method runs only on the primary process (LOCAL_RANK=0).
        """
        if not state.is_world_process_zero:
            return
        
        last_checkpoint = os.path.join(args.output_dir, f"{PREFIX_STATE_DICT_DIR}-last")
        save_model_and_tokenizer(
            model, self.tokenizer, last_checkpoint, 
            repo_name=self.repo_name, push_to_hub=self.push_to_hub, criteria=self.criteria
        )
        if state.best_model_checkpoint:
            # Rename best model checkpoint
            best_checkpoint_name = os.path.basename(state.best_model_checkpoint).replace(PREFIX_CHECKPOINT_DIR, PREFIX_STATE_DICT_DIR)
            best_model_checkpoint = os.path.join(args.output_dir, best_checkpoint_name)
            
            model_info = {}
            if best_model_checkpoint:
                model_info.update({
                    "best_metric": state.best_metric,
                    "best_model_step": int(best_model_checkpoint.split("-")[-1])
                })
                best_model_path = os.path.join(args.output_dir, f"{PREFIX_STATE_DICT_DIR}-best")
                os.rename(best_model_checkpoint, best_model_path)

            if self.save_model_per_component:
                for m in self.component_names:
                    if self.best_step_per_component[m]:
                        per_component_step_checkpoint = os.path.join(args.output_dir, f"{PREFIX_STATE_DICT_DIR}-{m}-{self.best_step_per_component[m]}")
                        per_component_best_checkpoint = os.path.join(args.output_dir, f"{PREFIX_STATE_DICT_DIR}-{m}-best")
                        os.rename(per_component_step_checkpoint, per_component_best_checkpoint)
                        model_info.update({f"best_{m}_step": self.best_step_per_component[m]})
        else:
            os.rename(self.init_model_path, os.path.join(args.output_dir, f"{PREFIX_STATE_DICT_DIR}-best"))
            model_info = {"best_metric": None, "best_model_step": 0}

        if is_wandb_available():
            table = wandb.Table(columns=["Metric", "Value"])
            for key, value in model_info.items():
                table.add_data(key, value)
                
            wandb.log({"model_results": table})

        with open(os.path.join(args.output_dir, "model_info.json"), "w") as f:
            json.dump(model_info, f, indent=4)

    def _get_best_step_from_log_history(self, log_history, metric_key, higher_is_better=True) -> int:
        """
        Retrieves the best model checkpoint step based on the evaluation metrics.

        Args:
            log_history (list): List of evaluation metrics.
            metric_key (str): Key to retrieve the metric from the log history.

        Returns:
            int: Step of the best model checkpoint.
        """
        best_metric = None
        best_step = None
        for log in log_history:
            if metric_key in log:
                metric = log[metric_key]
                if best_metric is None or (higher_is_better and metric > best_metric) or (not higher_is_better and metric < best_metric):
                    best_metric = metric
                    best_step = log["step"]
        return best_step

    def on_save(self, args, state, control, model, **kwargs):
        """
        Saves a model checkpoint at the current training step and manages checkpoint rotation.
        This method runs only on the primary process (LOCAL_RANK=0).
        """
        if not state.is_world_process_zero:
            return

        step_checkpoint = os.path.join(args.output_dir, f"{PREFIX_STATE_DICT_DIR}-{state.global_step}")
        save_model_and_tokenizer(
            model, self.tokenizer, step_checkpoint,
            repo_name=f"{self.repo_name}-{state.global_step}", push_to_hub=self.push_to_hub,
            criteria=self.criteria
        )
        # Identify best model checkpoint
        if state.best_model_checkpoint:
            best_checkpoint_name = os.path.basename(state.best_model_checkpoint).replace(PREFIX_CHECKPOINT_DIR, PREFIX_STATE_DICT_DIR)
            best_model_checkpoint = os.path.join(args.output_dir, best_checkpoint_name)
        else:
            best_model_checkpoint = None
        self._rotate_checkpoints(args, state, best_model_checkpoint=best_model_checkpoint, prefix=PREFIX_STATE_DICT_DIR)
        
        if self.save_model_per_component:
            self.best_step_per_component = {
                m: self._get_best_step_from_log_history(
                    state.log_history, 
                    self.metric_for_best_model.replace("eval_", f"eval_{m}_"),
                    higher_is_better=not "loss" in self.metric_for_best_model
                ) for m in self.component_names
            }

            for m in self.component_names:
                if self.best_step_per_component[m] == state.global_step:
                    per_component_step_checkpoint = os.path.join(args.output_dir, f"{PREFIX_STATE_DICT_DIR}-{m}-{state.global_step}")

                    save_model_and_tokenizer(
                        model, self.tokenizer, per_component_step_checkpoint,
                        repo_name=f"{self.repo_name}-{m}-{state.global_step}", push_to_hub=self.push_to_hub,
                        criteria=self.criteria
                    )
                    self._rotate_checkpoints(args, state, best_model_checkpoint=best_model_checkpoint, prefix=f"{PREFIX_STATE_DICT_DIR}-{m}")

    def _rotate_checkpoints(self, args, state, best_model_checkpoint, prefix=PREFIX_STATE_DICT_DIR) -> None:
        """
        Rotates checkpoints to maintain a maximum number of checkpoints.

        Args:
            args: Trainer arguments.
            state: Trainer state.
            best_model_checkpoint (str): Best model checkpoint path.
            prefix (str): Prefix for the checkpoint directory.            
        """
        if not args.save_total_limit or args.save_total_limit <= 0:
            return

        full_checkpoints_sorted = self._sorted_full_checkpoints(
            args.output_dir, state, 
            best_model_checkpoint=best_model_checkpoint, 
            prefix=prefix
        )
        if len(full_checkpoints_sorted) <= args.save_total_limit:
            return
        # Adjust limit to prevent deleting the best checkpoint
        save_limit = args.save_total_limit
        if best_model_checkpoint and save_limit == 1 and full_checkpoints_sorted[-1] != best_model_checkpoint:
            save_limit = 2
        # Delete excess checkpoints
        to_delete = full_checkpoints_sorted[:max(0, len(full_checkpoints_sorted) - save_limit)]
        for checkpoint in to_delete:
            print(f"Deleting outdated checkpoint: {checkpoint}")
            shutil.rmtree(checkpoint, ignore_errors=True)

    def _sorted_full_checkpoints(self, output_dir, state, best_model_checkpoint: str, prefix: str) -> tuple[Optional[str], List[str]]:
        """
        Returns the sorted full model checkpoints and the best model checkpoint if available.

        Args:
            state: Trainer state containing the best model checkpoint.
            best_model_checkpoint (str): Best model checkpoint path.
            prefix (str): Prefix for the checkpoint directory.

        Returns:
            tuple: Sorted full model checkpoints.
        """

        full_checkpoints = [str(x) for x in Path(output_dir).glob(f"{prefix}-*") if x.is_dir()]
        sorted_checkpoints = sorted(
            (int(re.search(rf"{prefix}-(\d+)", path).group(1)), path)
            for path in full_checkpoints if re.search(rf"{prefix}-(\d+)", path)
        )

        sorted_checkpoints = [path for _, path in sorted_checkpoints]

        # Ensure best checkpoint is not deleted
        if best_model_checkpoint in sorted_checkpoints:
            sorted_checkpoints.append(sorted_checkpoints.pop(sorted_checkpoints.index(best_model_checkpoint)))

        return sorted_checkpoints
    