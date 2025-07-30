
import os
import wandb
import warnings
import yaml
import torch
from transformers import (
    AutoModelForSequenceClassification, AutoTokenizer, HfArgumentParser, BitsAndBytesConfig, EarlyStoppingCallback
)
import copy
from dataclasses import dataclass, field
from datasets import load_dataset
from peft import LoraConfig
from typing import List, Optional
import os.path as osp
import json
from dotenv import load_dotenv
import sys

from optimas.reward.callback import PerComponentSaveCallback
from optimas.utils.logger import setup_logger
from optimas.external import RewardConfig, RewardTrainer
from optimas.utils.load import load_model_and_tokenizer
from optimas.reward.dataset import RewardDataset
from optimas.reward.finetune import run_finetune

from examples.systems import registered_systems
from examples.datasets import registered_datasets

# Define script arguments
@dataclass
class ScriptArgs:
    base_model_name: str = "meta-llama/Llama-3.1-8B-Instruct"
    hf_repo_or_local_dir: str = ""
    system_name: str = ""
    dataset: str = ""
    train_multi_head: bool = True
    output_dir: str = ""
    wandb_run_name: str = ""
    per_device_train_batch_size: int = 8
    per_device_eval_batch_size: int = 4
    gradient_accumulation_steps: int = 1
    torch_empty_cache_steps: int = 1
    max_steps: int = -1
    learning_rate: float = 5e-5
    early_stopping_patience: int = 512
    num_train_epochs: int = 20
    max_length: int = 2048
    logging_steps: int = 10
    eval_steps: int = 10
    save_steps: int = 10
    eval_strategy: str = "steps"
    metric_for_best_model: str = "eval_loss"
    lora_r: int = 16
    lora_alpha: int = 8
    lora_dropout: float = 0.05
    eval_ratio: float = 0.1
    report_to: str = "wandb"
    save_total_limit: int = 3
    warmup_steps: int = 0
    weight_decay: float = 0.0
    state_dict_path: str = None
    add_margin: bool = False
    push_to_hub: bool = True
    component_name_lst: List[str] = None
    load_best_model_at_end: bool = True
    use_score_scaling: bool = False
    use_score_norm: bool = False
    use_lora: bool = False
    save_model_per_component: bool = True
    test_best_model_only: bool = True

    def __post_init__(self):
        # Convert all attributes with value "None" (string) to actual None
        for field_name, field_value in self.__dict__.items():
            if field_value == "None":
                setattr(self, field_name, None)


def main():
    load_dotenv('.env')
    parser = HfArgumentParser(ScriptArgs)
    if len(sys.argv) == 2 and sys.argv[1].endswith(".yaml"):
        with open(sys.argv[1], "r") as f:
            yaml_config = yaml.safe_load(f)
        args = parser.parse_dict(yaml_config)[0]
    else:
        args = parser.parse_args_into_dataclasses()[0]
    
    output_dir = osp.join(args.output_dir, args.system_name)
    logger = setup_logger(__name__, log_file=osp.join(output_dir, "output.log"))

    if os.environ.get('LOCAL_RANK', '0') == '0':
        wandb.init(
            entity=os.environ.get('WANDB_ENTITY'),
            project=os.environ.get('WANDB_PROJECT'),
            name=args.wandb_run_name,
            config=args,
            save_code=True
        )

    if args.use_lora:
        peft_config = LoraConfig(
            r=args.lora_r,
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout,
            bias="none",
            task_type="CAUSAL_LM",
            init_lora_weights="gaussian",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                            "gate_proj", "up_proj", "down_proj"]
        )
    else:
        peft_config = None

    # Configure training
    training_args = RewardConfig(
        do_train=True,
        output_dir=output_dir,
        logging_dir=output_dir,
        per_device_train_batch_size=args.per_device_train_batch_size,
        per_device_eval_batch_size=args.per_device_eval_batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        num_train_epochs=args.num_train_epochs,
        max_length=args.max_length,
        logging_steps=args.logging_steps,
        eval_steps=args.eval_steps,
        save_steps=args.save_steps,
        eval_strategy=args.eval_strategy,
        push_to_hub=args.push_to_hub,
        report_to=args.report_to,
        torch_empty_cache_steps=args.torch_empty_cache_steps,
        max_steps=args.max_steps,
        save_total_limit=args.save_total_limit,
        warmup_steps=args.warmup_steps,
        weight_decay=args.weight_decay,
        metric_for_best_model=args.metric_for_best_model,
        load_best_model_at_end=args.load_best_model_at_end,
        use_score_scaling=args.use_score_scaling,
        use_score_norm=args.use_score_norm,
        ddp_find_unused_parameters=False,
    )

    system = registered_systems[args.system_name]()
    trainset, valset, testset = registered_datasets[args.dataset]()

    reward_dataset = RewardDataset(
        args.hf_repo_or_local_dir, system,
        original_trainset=trainset + valset
        )
    ds = reward_dataset.to_preference_dataset(
        eval_ratio=args.eval_ratio,
        add_margin=args.add_margin
    )

    num_labels = len(system.optimizable_components) if args.train_multi_head else 1
    logger.info(f"[reward_model_train] Setting the number of output dims to {num_labels}")

    model, tokenizer = load_model_and_tokenizer(
        args.base_model_name,
        peft_config=peft_config,
        model_class=AutoModelForSequenceClassification,
        state_dict_path=args.state_dict_path,
        num_labels=num_labels
    )

    ############ Callback ############
    eval_callback = PerComponentSaveCallback(
        system=system,
        tokenizer=tokenizer,
        repo_name=args.hf_repo_or_local_dir,
        push_to_hub=args.push_to_hub,
        metric_for_best_model=args.metric_for_best_model,
        save_model_per_component=args.save_model_per_component
    )
    early_stopping_callback = EarlyStoppingCallback(early_stopping_patience=args.early_stopping_patience)
    
    ############ Train model ############
    logger.info(f"[reward_model_train] {system.optimizable_components=}")

    trainer = run_finetune(
        ds, model, tokenizer, training_args,
        train_last_layer=True, 
        callbacks=[eval_callback, early_stopping_callback], 
        component_to_idx=system.optimizable_component_to_idx
    )

    ############ SAVING ############
    if training_args.eval_strategy != "no":
        metrics = trainer.evaluate()
        trainer.log_metrics("eval", metrics)
        trainer.save_metrics("eval", metrics)

    wandb.finish()

if __name__ == "__main__":
    main()
