import sys
import os
import json
import yaml
import datetime
from peft import LoraConfig
from typing import List, Optional

import torch
import numpy as np
import wandb
from tqdm import tqdm
from dotenv import load_dotenv
from datasets import load_dataset
from transformers import AutoModelForSequenceClassification, HfArgumentParser
from dataclasses import dataclass, field

from optimas.reward.eval import eval_system
from optimas.utils.logger import setup_logger
from optimas.optim.optimizer import OptimasOptimizer
from optimas.optim.args import OptimasArguments
from optimas.reward.dataset import RewardDataset
from optimas.utils.load import load_model_and_tokenizer
from examples.systems import registered_systems
from examples.datasets import registered_datasets


@dataclass
class OptimizationArgs:
    # Dataset and pipeline
    dataset: str
    system: str
    run_name: str
    val_size: int = 10
    num_repeat: int = 1
    max_sample_workers: int = 4
    dotenv_path: str = ".env"

    # Optimization 
    cooldown: int = 1
    iterations: int = 5
    replay_buffer_size: int = 200
    per_iteration_input_size: int = 10
    global_hyper_param_search: bool = False
    components_to_apply: List[str] = field(default_factory=lambda: ["all"])
    use_replay_buffer: bool = False

    # Reward model
    per_iteration_rm_train_size: int = -1
    train_multi_head: bool = True

    # Optimas arguments
    auto: bool = False
    verbose: bool = True
    validate: bool = True
    optimize_prompts: bool = True
    prompt_optimizer: str = "opro"
    per_component_train_size: int = 20
    per_component_search_size: int = 20
    num_prompt_candidates: int = 3
    requires_permission_to_run: bool = False
    val_every_prompt_iter: int = 3
    val_every_ppo_ratio: float = 0.25
    val_every_grid_ratio: float = 0.25

    # Model and data paths
    output_dir: str = "./on_policy_optim"
    base_model: str = "meta-llama/Llama-3.1-8B-Instruct"
    state_dict_path: Optional[str] = None
    system_state_dict_path: Optional[str] = None
    preference_dataset: str = ""
    load_in_4bit: bool = False
    load_in_8bit: bool = False

    # PPO
    weight_optimizer: str = "none"  # or "ppo"
    ppo_train_steps: int = 800
    ppo_epochs: int = 0
    ppo_batch_size: int = 2
    ppo_learning_rate: float = 1e-4
    ppo_save_every: int = 0
    ppo_save_epoch_ratio: float = 0.25
    ppo_resume_adapter: Optional[str] = None
    ppo_base_model_name: str = "Qwen/Qwen2.5-1.5B-Instruct"

    # Amazon system specific
    session_adapter: Optional[str] = None
    profiler_adapter: Optional[str] = None

    # LoRA
    lora_r: int = 32
    lora_alpha: int = 16
    lora_dropout: float = 0.0


if __name__ == "__main__":

    with open(sys.argv[1], "r") as f:
        config = yaml.safe_load(f)

    parser = HfArgumentParser(OptimizationArgs)
    args = parser.parse_dict(config)[0]
    
    load_dotenv('.env')

    wandb.init(
        entity=os.environ.get('WANDB_ENTITY'),
        project=os.environ.get('WANDB_PROJECT'),
        name=f"{args.run_name}_{args.dataset}",
        config=args,
        save_code=True
    )

    # Customize output dir with timestamp
    args.output_dir = os.path.join(args.output_dir, args.dataset, args.system, args.run_name)
    os.makedirs(args.output_dir, exist_ok=True)

    # Set up logging
    logger = setup_logger(
        __name__, log_file=os.path.join(args.output_dir, "output.log")
    )
    logger.info(f"Arguments: {args}")

    # Load environment variables
    load_dotenv(args.dotenv_path)

    # Initialize system with appropriate parameters based on system type
    system = registered_systems[args.system](
        log_dir=args.output_dir, max_sample_workers=args.max_sample_workers
    )

    # Load dataset
    logger.info(f"Loading dataset: {args.dataset}")
    trainset, valset, testset = registered_datasets[args.dataset]()
    valset = valset[:args.val_size]

    logger.info(
        f"Dataset sizes - Train: {len(trainset)}, Val: {len(valset)}, Test: {len(testset) if testset else 'N/A'}"
    )

    # Load preference dataset
    logger.info(f"Loading preference dataset from {args.preference_dataset}")
    preference_dataset = load_dataset(args.preference_dataset)

    # Load initial system state if provided
    if args.system_state_dict_path:
        logger.info(f"Loading system state from {args.system_state_dict_path}")
        system_state_dict = torch.load(args.system_state_dict_path)
        system.load_state_dict(system_state_dict)

    # Create OptimasArguments from command-line arguments
    optimas_args = OptimasArguments(
        optimize_prompts=args.optimize_prompts,
        prompt_optimizer=args.prompt_optimizer,
        per_component_train_size=args.per_component_train_size,
        per_component_search_size=args.per_component_search_size,
        num_prompt_candidates=args.num_prompt_candidates,
        requires_permission_to_run=args.requires_permission_to_run,
        verbose=args.verbose,
        output_dir=args.output_dir,
        weight_optimizer=args.weight_optimizer,
        global_hyper_param_search=args.global_hyper_param_search,
        components_to_apply=args.components_to_apply,
        ppo_train_steps=args.ppo_train_steps,
        ppo_epochs=args.ppo_epochs, # we take min(epoch, steps) in PPO training
        ppo_batch_size=args.ppo_batch_size,
        ppo_learning_rate=args.ppo_learning_rate,
        ppo_save_every=args.ppo_save_every,
        ppo_save_epoch_ratio=args.ppo_save_epoch_ratio,
        ppo_base_model_name=args.ppo_base_model_name,
        val_every_prompt_iter=args.val_every_prompt_iter,
        val_every_ppo_ratio=args.val_every_ppo_ratio,
        max_sample_workers=args.max_sample_workers,
        policy_device=f"cuda:{torch.cuda.current_device()}"
    )

    # Configure LoRA for the reward model
    logger.info(f"Initializing LoRA-based reward model with {args.base_model}")

    peft_config = LoraConfig(
        r=args.lora_r,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        bias="none",
        task_type="CAUSAL_LM",
        init_lora_weights="gaussian",
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ]
    )

    # Load initial model for reward training
    model, tokenizer = load_model_and_tokenizer(
        args.base_model,
        peft_config=peft_config,
        model_class=AutoModelForSequenceClassification,
        num_labels=(
            len(system.optimizable_components) if args.train_multi_head else 1
        ),
        state_dict_path=args.state_dict_path,
    )

    # Create optimizer
    logger.info("Initializing On-Policy Optimizer")
    optimizer = OptimasOptimizer(
        iterations=args.iterations,
        per_iteration_input_size=args.per_iteration_input_size,
        per_iteration_rm_train_size=args.per_iteration_rm_train_size,
        system=system,
        train_dataset=trainset,
        val_dataset=valset,
        test_dataset=testset,
        preference_dataset=preference_dataset,
        reward_model=model,
        tokenizer=tokenizer,
        base_model_name=args.base_model,
        output_dir=args.output_dir,
        cooldown_period=args.cooldown,
        optimas_args=optimas_args,  
        replay_buffer_size=args.replay_buffer_size,
        use_replay_buffer=args.use_replay_buffer,  
    )

    # Run optimization
    logger.info("Starting optimization process")
    optimized_system, history = optimizer.optimize()

    # Save optimization history
    history_path = os.path.join(args.output_dir, "optimization_history.json")
    logger.info(f"Saving optimization history to {history_path}")
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)

    # Evaluate final system on test set if available
    if testset and len(testset) > 0:
        logger.info("Evaluating optimized system on test set")
        try:
            metrics, preds = eval_system(
                system=optimized_system, testset=testset, num_repeat=args.num_repeat
            )
            metrics_path = os.path.join(args.output_dir, "eval_metrics.json")
            logger.info(f"Saving evaluation metrics to {metrics_path}")
            with open(metrics_path, "w") as f:
                json.dump(metrics, f, sort_keys=True, indent=2)

            wandb.log(
                {   "iteration": args.iterations,
                    "test/score": metrics["mean"],
                    "test/std": metrics["std"],
                }
            )
        except Exception as e:
            logger.error(f"Error evaluating optimized system: {e}")

    # Save final optimized system
    final_system_path = os.path.join(args.output_dir, "final_optimized_system.pth")
    logger.info(f"Saving final optimized system to {final_system_path}")
    torch.save(optimized_system.state_dict(), final_system_path)

    # Save final adapter state
    final_adapter_state = optimizer._get_current_adapter_state()
    with open(os.path.join(args.output_dir, "final_adapter_state.json"), "w") as f:
        json.dump(final_adapter_state, f, indent=2)

    # Log improvement summary
    if "overall_improvement" in history:
        improvement = history["overall_improvement"]
        logger.info(f"Final improvement: {improvement:.4f}")

        # Create a summary file with key metrics
        summary = {
            "timestamp": datetime.datetime.now().isoformat(),
            "system": args.system,
            "dataset": args.dataset,
            "iterations": args.iterations,
            "initial_score": history["overall_performance"][0],
            "final_score": history["overall_performance"][-1],
            "improvement": improvement,
            "components_optimized": (
                [it["component_optimized"] for it in history["iterations"]]
                if "iterations" in history
                else []
            ),
            "final_adapter_state": final_adapter_state,
        }

        with open(os.path.join(args.output_dir, "optimization_summary.json"), "w") as f:
            json.dump(summary, f, indent=2)

    print(f"Optimization complete. Final system saved to {final_system_path}")
    print(f"Overall improvement: {history.get('overall_improvement', 'N/A')}")
    print(f"Final adapter state: {final_adapter_state}")
