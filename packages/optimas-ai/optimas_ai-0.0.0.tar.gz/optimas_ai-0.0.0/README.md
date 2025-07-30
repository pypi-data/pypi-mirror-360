
<div align="center">
<figure class="center-figure"> <img src="media/compound-ai-system.jpg" width="85%"></figure>
</div>

<h1 align="left">
    Optimas: Optimizing Compound AI Systems with Globally Aligned Local Rewards
</h1>

<div align="left">

[![](https://img.shields.io/badge/website-Optimas-purple?style=plastic&logo=Google%20chrome)](https://optimas.stanford.edu/)
[![](https://img.shields.io/badge/Arxiv-paper-red?style=plastic&logo=arxiv)](https://arxiv.org/abs/2404.13207)
[![](https://img.shields.io/badge/pip-optimas--ai-brightgreen?style=plastic&logo=Python)](https://pypi.org/project/optimas-ai/) 
[![](https://img.shields.io/badge/doc-online-blue?style=plastic&logo=Read%20the%20Docs)](https://optimas.stanford.edu/docs/getting-started/introduction)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>


## NEWS
- **[Jul 2025]** We release Optimas!

## What is Optimas?
Optimas is a unified framework for end-to-end optimization of compound AI systems. While traditional optimization methods focus on single configuration types—such as prompts or hyperparameters—modern compound AI systems require coordinated optimization across multiple heterogeneous configuration types that work well together.

Optimas addresses this fundamental challenge through its core innovation: **Globally Aligned Local Reward Functions (LRFs)** that align each component's optimization with global system performance. This enables efficient, decentralized optimization while ensuring that local improvements contribute meaningfully to global rewards, backed by formal theoretical guarantees.



🔥 Check out our [website](https://optimas.stanford.edu/) for more overview!

--------------------------------------------------
1. Generate Preference Data (used for reward model and optimization)
--------------------------------------------------

`python -m scripts.generate_reward_dataset scripts/configs/generate/{dataset}.yaml`

This runs reward data generation over a given dataset + system.
Output: HuggingFace-style reward dataset saved locally.

--------------------------------------------------
2. Train Initial Reward Model (Local Reward Functions)
--------------------------------------------------

`torchrun --master_port=56780 --nnodes=1 --nproc_per_node=4 -m scripts.train_reward_model scripts/configs/train/{dataset}.yaml`

Trains a reward model using preference data. You need to include WANDB_ENTITY and WANDB_PROJECT in the `.env` file or export them in your shell:
```
export WANDB_ENTITY=your_wandb_entity
export WANDB_PROJECT=your_wandb_project
```

--------------------------------------------------
3. Run Optimization (Prompts, PPO LoRA, Hyperparameters)
--------------------------------------------------

`python -m scripts.optimize_system scripts/configs/optimize/{dataset}.yaml`

Uses Globally Aligned Local Reward Functions (LRFs) to optimize component variables. 
Supports:
    - prompt tuning (opro, mipro, copro)
    - hyperparameter search
    - PPO for local models via LoRA (works with vLLM + OpenAI API)
Each component can be optimized independently or jointly.

Remember to include WANDB_ENTITY and WANDB_PROJECT in the `.env` file or export them in your shell.

--------------------------------------------------
4. Evaluate Final System
--------------------------------------------------

`python scripts/eval_system.py scripts/configs/eval/{dataset}.yaml`

Evaluates a saved system state dict on val/test sets.
Supports test repeat for randomized components.

--------------------------------------------------
Component Types Supported
--------------------------------------------------

- Prompt templates (as strings)
- Model config (e.g., model name, temperature)
- Hyperparameters (grid search)
- Local LLM weights (LoRA + PPO finetuning)

Each component declares:
    - input_fields
    - output_fields
    - variable (what to optimize)
    - variable_search_space (optional)

--------------------------------------------------
Adding Your Own System
--------------------------------------------------

1. Define your pipeline in examples/systems/<your_system>.py as `system_engine()`
2. Register it in examples/systems/__init__.py
3. Add your dataset to examples/datasets/

Example:
```python
    def system_engine():
        return CompoundAISystem(
            components={...},
            final_output_fields=[...],
            ground_fields=[...],
            eval_func=...
        )
```

## Reference 

Please consider citing our paper if you use our benchmark or code in your work:
```
@inproceedings{optimas,
    title        = {Optimas: Optimizing Compound AI Systems with Globally Aligned Local Rewards},
    author       = {
        Shirley Wu and Parth Sarthi and Shiyu Zhao and 
        Aaron Lee and Herumb Shandilya and 
        Adrian Mladenic Grobelnik and Nurendra Choudhary and 
       Eddie Huang and Karthik Subbian and Linjun Zhang and Diyi Yang and
        James Zou and Jure Leskovec
    },
    year  = {2025}
}
```