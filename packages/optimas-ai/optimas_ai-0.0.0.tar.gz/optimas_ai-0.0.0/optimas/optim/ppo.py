import os
import sys
import json
import wandb
import time
import math
import random
import argparse
import datetime
from functools import partial
from typing import List, Dict, Optional
from tqdm import tqdm
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from datasets import Dataset
from dotenv import load_dotenv

from transformers import (AutoTokenizer, AutoModelForCausalLM,
                          BitsAndBytesConfig, GenerationConfig)
from trl import (PPOTrainer, PPOConfig,
                 AutoModelForCausalLMWithValueHead)
from trl.models import PreTrainedModelWrapper
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

from optimas.reward.model import RewardModel


def train_ppo(
    component_name: str,
    base_model: str,
    reward_model: RewardModel,
    output_dir: str,
    reward_fn_factory: callable,
    make_dataset: callable,
    lora_cfg: LoraConfig,
    *,
    batch_size: int = 16,
    ppo_epochs: int = 4,
    max_new_tokens: int = 96,
    learning_rate: float = 5e-5,
    train_steps: int = 800,
    resume_adapter: Optional[str] = None,
    save_every: int = 0,
    save_epoch_ratio: float = 0.25,
    mini_batch_size: int = 4,
    gradient_accumulation_steps: int = 2,
    project_name: str = "ppo-training",
    reward_trainset: List = None,
    val_dataset: Dataset | None = None,
    val_metrics_path: str | None = None,
    val_every_ratio: float = 0.25,
    args=None,
) -> str:
    """
    Finetune a *single* component with PPO and return the directory
    that now contains the up-to-date LoRA adapter.
    """
    # Initialize wandb for logging
    try:
        run_name = f"{component_name}_{time.strftime('%Y%m%d_%H%M%S')}"
        wandb.init(project=project_name, name=run_name, config={
            "component_name": component_name,
            "base_model": base_model,
            "batch_size": batch_size,
            "ppo_epochs": ppo_epochs,
            "max_new_tokens": max_new_tokens,
            "learning_rate": learning_rate,
            "train_steps": train_steps,
            "mini_batch_size": mini_batch_size,
            "gradient_accumulation_steps": gradient_accumulation_steps,
        })
        wandb_enabled = True
        print(f"Wandb initialized successfully with run name: {run_name}")
    except Exception as e:
        print(f"Warning: Could not initialize wandb: {e}")
        print("Training will continue but metrics won't be logged to wandb.")
        wandb_enabled = False

    import os

    os.makedirs(output_dir, exist_ok=True)

    tok = AutoTokenizer.from_pretrained(base_model)
    tok.pad_token = tok.eos_token
    tok.padding_side = "left"

    quant_cfg = BitsAndBytesConfig(load_in_4bit=True,
                                  bnb_4bit_use_double_quant=True)
    base_policy = AutoModelForCausalLM.from_pretrained(
        base_model, quantization_config=quant_cfg
    )
    base_policy = prepare_model_for_kbit_training(base_policy)

    # Now apply LoRA to the base model
    peft_model = get_peft_model(base_policy, lora_cfg)

    # Now wrap with ValueHead
    policy = AutoModelForCausalLMWithValueHead.from_pretrained(
        peft_model,
    )

    policy.config.use_cache = False
    if not hasattr(policy, "generation_config"):
        policy.generation_config = GenerationConfig.from_pretrained(base_model)

    device_idx = int(args.policy_device.split(":")[-1])
    policy.to(f"cuda:{device_idx}")

    device = next(policy.parameters()).device
    print(f"Using device: {device}")
    # Resume from adapter if specified
    if resume_adapter:
        policy.pretrained_model.load_adapter(
            resume_adapter,
            adapter_name="default",
            is_trainable=True
        )

    print(f"Preparing dataset for component: {component_name}")
   
    train_ds = make_dataset(component_name, output_dir, "train", args.per_component_train_size)

    if len(train_ds) == 0:
        raise ValueError(f"No training examples were generated for component {component_name}")

    print(f"Created dataset with {len(train_ds)} examples for {component_name}")

    dl = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        collate_fn=lambda x: x,
        drop_last=False
    )

    eval_every_steps = max(1, int(train_steps * val_every_ratio))

    reward_fn = reward_fn_factory(reward_model, component_name)

    # ──────────────────────────────────────────────────────────────────── trainer
    ppo_cfg = PPOConfig(
        batch_size=batch_size,
        mini_batch_size=mini_batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        ppo_epochs=ppo_epochs,
        learning_rate=learning_rate,
        log_with='wandb' if wandb_enabled else None,
        whiten_rewards=True,
        score_clip=1.0,
        target_kl=0.04
    )

    trainer = PPOTrainer(
        config=ppo_cfg,
        model=policy,
        tokenizer=tok,
        ref_model=None,
    )

    step = 0
    for epoch in range(ppo_epochs):
        print(f"\n=== Starting Epoch {epoch+1}/{ppo_epochs} ===")

        epoch_dir = os.path.join(output_dir, f"epoch_{epoch+1}")
        os.makedirs(epoch_dir, exist_ok=True)

        epoch_pbar = tqdm(dl, desc=f"Epoch {epoch+1}", dynamic_ncols=True)
        total_steps_per_epoch = len(epoch_pbar)

        epoch_rewards = []
        epoch_losses = []

        for batch_idx, batch in enumerate(epoch_pbar):
            if not batch:
                continue

            prompts = [ex["prompt"] for ex in batch]

            query_tensors = tok(
                prompts,
                return_tensors="pt",
                padding=True,
                truncation=True,
            ).input_ids.to(device)

            gen_tensors = policy.generate(
                query_tensors,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=0.7,
                pad_token_id=tok.eos_token_id,
            )

            resp_tensors = [
                gen[len(q):] for gen, q in zip(gen_tensors, query_tensors)
            ]

            completions = tok.batch_decode(resp_tensors, skip_special_tokens=True)

            samples_for_reward = [
                {
                    "prompt": p,
                    "completion": c.strip(),
                    "orig": ex,
                }
                for p, c, ex in zip(prompts, completions, batch)
            ]
            rewards = reward_fn(samples_for_reward)
            rewards = [(r - 0.5) * 2.0 for r in rewards]

            epoch_rewards.extend(rewards)

            mean_reward = sum(rewards) / len(rewards)

            # Handle dynamic batch sizes
            current_bs = len(prompts)
            orig_bs = trainer.config.batch_size
            orig_mbs = trainer.config.mini_batch_size
            gradient_accumulation_steps = trainer.config.gradient_accumulation_steps
            backward_batch_size = trainer.config.backward_batch_size

            # Temporarily adjust config for this batch
            if current_bs != orig_bs:
                print(f"Adjusting batch size from {orig_bs} to {current_bs}")
                trainer.config.batch_size = current_bs
                trainer.config.mini_batch_size = min(current_bs, orig_mbs)
                trainer.config.gradient_accumulation_steps = max(
                    1, math.ceil(current_bs / trainer.config.mini_batch_size)
                )
                trainer.config.backward_batch_size = (
                    trainer.config.mini_batch_size * trainer.config.gradient_accumulation_steps
                )
                trainer.backward_batch_size = trainer.config.backward_batch_size

            scores = []
            for r in rewards:
                r_float = float(r)
                scores.append(torch.tensor(r_float, dtype=torch.float, device=device))

            # try:
            stats = trainer.step(
                queries=[t.detach() for t in query_tensors],
                responses=[t.detach() for t in resp_tensors],
                scores=scores,
            )

            trainer.config.batch_size = orig_bs
            trainer.config.mini_batch_size = orig_mbs
            trainer.config.gradient_accumulation_steps = gradient_accumulation_steps
            trainer.config.backward_batch_size = backward_batch_size

            if stats:
                if 'ppo/loss/total' in stats:
                    loss_value = stats['ppo/loss/total']
                    loss_value = float(loss_value.item() if hasattr(loss_value, 'item') else loss_value)
                    epoch_losses.append(loss_value)
                else:
                    loss_value = 0.0

                epoch_pbar.set_postfix({
                    'reward': f"{mean_reward:.4f}",
                    'loss': f"{loss_value:.4f}"
                })

                # Log metrics to wandb
                if wandb_enabled:
                    key_metrics = {"epoch": epoch + 1, "batch": batch_idx, "step": step, "mean_reward": mean_reward, "loss": loss_value, }

                    for stat_key in ['ppo/loss/total', 'ppo/policy/entropy', 'ppo/mean_scores',
                                    'ppo/policy/advantages_mean', 'ppo/returns/mean', 'time/ppo/total']:
                        if stat_key in stats:
                            stat_value = stats[stat_key]
                            # Convert to Python scalar if needed
                            if hasattr(stat_value, 'item'):
                                key_metrics[stat_key.split('/')[-1]] = stat_value.item()
                            elif hasattr(stat_value, 'shape') and stat_value.shape == (1,):
                                key_metrics[stat_key.split('/')[-1]] = float(stat_value[0])
                            else:
                                key_metrics[stat_key.split('/')[-1]] = float(stat_value)

                    wandb.log(key_metrics)

            step += 1

            # Save checkpoint if requested
            if save_every and step % save_every == 0:
                checkpoint_dir = os.path.join(output_dir, f"step_{step}")
                os.makedirs(checkpoint_dir, exist_ok=True)
                policy.save_pretrained(checkpoint_dir, safe_serialization=True)
                tok.save_pretrained(checkpoint_dir)
                print(f"Saved checkpoint at step {step} to {checkpoint_dir}")

            if (
                0 < save_epoch_ratio < 1
                and step % int(save_epoch_ratio * total_steps_per_epoch) == 0
            ):
                current_ratio = float(step / total_steps_per_epoch)
                epoch_checkpoint_dir = os.path.join(
                    output_dir, f"epoch_{epoch+1}_ratio_{current_ratio:.2f}")
                os.makedirs(epoch_checkpoint_dir, exist_ok=True)
                policy.save_pretrained(epoch_checkpoint_dir, safe_serialization=True)
                tok.save_pretrained(epoch_checkpoint_dir)
                print(f"Saved epoch checkpoint at step {step} to {epoch_checkpoint_dir}")

            if step >= train_steps:
                break

        if step >= train_steps:
            # Save the model at current steps
            checkpoint_dir = os.path.join(output_dir, f"step_{step}")
            os.makedirs(checkpoint_dir, exist_ok=True)
            policy.save_pretrained(checkpoint_dir, safe_serialization=True)
            tok.save_pretrained(checkpoint_dir)
            print(f"!!!!!!! Saved checkpoint at step {step} to {checkpoint_dir}")
            break

        # Calculate and log epoch statistics
        if epoch_rewards:
            epoch_mean_reward = sum(epoch_rewards) / len(epoch_rewards)
            print(f"Epoch {epoch+1} mean reward: {epoch_mean_reward:.4f}")

            if epoch_losses:
                epoch_mean_loss = sum(epoch_losses) / len(epoch_losses)
                print(f"Epoch {epoch+1} mean loss: {epoch_mean_loss:.4f}")

            if wandb_enabled:
                wandb.log({
                    "epoch": epoch + 1,
                    "epoch_mean_reward": epoch_mean_reward,
                    "epoch_mean_loss": epoch_mean_loss if epoch_losses else 0
                })

        policy.save_pretrained(epoch_dir, safe_serialization=True)
        tok.save_pretrained(epoch_dir)
        print(f"Saved model for epoch {epoch+1} to {epoch_dir}")

    final_dir = os.path.join(output_dir, "final")
    os.makedirs(final_dir, exist_ok=True)
    policy.save_pretrained(final_dir, safe_serialization=True)
    tok.save_pretrained(final_dir)
    print(f"Saved final model to {final_dir}")

    if wandb_enabled:
        wandb.finish()

    return output_dir


if __name__ == "__main__":
    import argparse, pathlib, dotenv, os, sys
    dotenv.load_dotenv()
    ap = argparse.ArgumentParser()
    ap.add_argument("--component_name", required=True,
                    choices=["session_analyzer", "candidate_profiler"])
    ap.add_argument("--base_model", required=True)
    ap.add_argument("--reward_model_path", required=True)
    ap.add_argument("--output_dir", required=True)
    ap.add_argument("--train_steps", type=int, default=1000)
    ap.add_argument("--save_every", type=int, default=0,
                   help="Save checkpoint every N steps (0 to disable)")
    ap.add_argument("--wandb_project", type=str, default="ppo-training",
                   help="Project name for W&B logging")
    args = ap.parse_args()

    rm = RewardModel.from_pretrained(args.reward_model_path)