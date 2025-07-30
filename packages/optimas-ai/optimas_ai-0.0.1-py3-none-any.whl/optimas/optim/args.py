from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class OptimasArguments:
    """
    Configuration for the optimization process.
    """

    device: str = field(
        default="cuda:0",
        metadata={"help": "Device for training and evaluation (e.g., 'cuda:0', 'cpu')."}
    )
    max_seq_length: int = field(default=512, metadata={"help": "Maximum input sequence length."})

    skip_data_gen: bool = field(
        default=False,
        metadata={"help": "Skip online data generation."}
    )

    # ---------------------------
    #            Prompt
    # ---------------------------
    optimize_prompts: bool = field(default=True, metadata={"help": "Optimize prompts during process."})
    prompt_optimizer: str = field(
        default="mipro",
        metadata={
            "help": "Prompt optimization method.",
            "choices": ["mipro", "copro", "opro"],
            },
    )
    # ----------- Common -----------
    num_threads: int = field(default=1, metadata={"help": "Number of threads for parallel ops."})
    per_component_train_size: int = field(
        default=50, metadata={"help": "Train size for COPRO optimization."}
    )
    per_component_search_size: int = field(
        default=20, metadata={"help": "Hyper parameter search size."}
    )
    num_prompt_candidates: int = field(default=10, metadata={"help": "Number of candidate prompts."})
    output_dir: str = field(
        default="./output",
        metadata={"help": "Directory to save the optimized variables."}
    )

    # ----------- DSPy -----------
    requires_permission_to_run: bool = field(default=False, metadata={"help": "Requires permission to run dspy prompt optimization."})
    verbose: bool = field(default=True, metadata={"help": "Verbose mode."})

    num_candidates: int = field(
        default=10,
        metadata={"help": "Number of candidates for DSPy optimization."}
    )
    num_iterations: int = field(
        default=2,
        metadata={"help": "Number of iterations for DSPy optimization."}
    )

    # ----------- COPRO -----------
    copro_depth: int = field(default=2, metadata={"help": "Number of optimization iterations per prompt."})

    # ----------- MIPRO -----------
    auto: str = field(
        default=None, metadata={"help": "Must be one of {'light', 'medium', 'heavy', None}"}
    )

    # Parameter
    optimize_parameters: bool = field(default=True, metadata={"help": "Optimize model parameters."})

    global_hyper_param_search: bool = field(
        default=False,
        metadata={"help": "Enable hyperparameter search."}
    )

    components_to_apply: List[str] = field(
        default_factory=lambda: ["all"],
        metadata={"help": "Modules to apply optimization."}
    )

    # ----------- PPO -----------
    ppo_train_steps: int = field(
        default=800,
        metadata={"help": "Number of training steps for PPO."}
    )
    ppo_epochs: int = field(
        default=4,
        metadata={"help": "Number of epochs for PPO."}
    )
    ppo_batch_size: int = field(
        default=2,
        metadata={"help": "Batch size for PPO."}
    )
    ppo_learning_rate: float = field(
        default=1e-4,
        metadata={"help": "Learning rate for PPO."}
    )
    ppo_save_every: int = field(
        default=0,
        metadata={"help": "Save adapter every N steps."}
    )
    ppo_save_epoch_ratio: float = field(
        default=0.25,
        metadata={"help": "Save adapter every N epochs."}
    )
    ppo_resume_adapter: Optional[str] = field(
        default=None,
        metadata={"help": "Resume from a specific adapter."}
    )
    weight_optimizer: str = field(
        default="none",
        metadata={
            "help": "Weight optimizer for PPO.",
            "choices": ["ppo"],
        },
    )
    ppo_base_model_name: str = field(
        default="Qwen/Qwen2.5-1.5B-Instruct",
        metadata={"help": "Base model name for PPO."}
    )
    emb_sim_reward: bool = field(
        default=False,
        metadata={"help": "Use embedding similarity reward."}
    )

    # ---------------- validation settings -------------
    validate: bool = field(
        default=True,
        metadata={"help": "Enable validation during optimization."}
    )
    val_every_ppo_ratio: float = field(
        default=0.25,
        metadata={"help": "Validation ratio for PPO."}
    )
    val_every_prompt_iter: int = field(
        default=5,
        metadata={"help": "Validation interval for prompt optimization."}
    )
    val_every_grid_ratio: float = field(
        default=0.25,
        metadata={"help": "Validation ratio for grid search."}
    )

    max_sample_workers: int = field(
        default=8,
        metadata={"help": "Maximum number of sample workers."}
    )

    # ----------------- GPU settings -------------------
    reward_device: str = field(
        default="cuda:0",
        metadata={"help": "Device for reward model."}
    )
    policy_device: str = field(
        default="cuda:0",
        metadata={"help": "Device for policy model."}
    )

    # ----------- OPRO -----------
    opro_llm_model: str = field(
        default="gpt-4o-mini",
        metadata={"help": "LLM model for OPRO optimization"}
    )
    opro_temperature: float = field(
        default=0.7,
        metadata={"help": "Temperature for OPRO LLM"}
    )
    opro_max_new_tokens: int = field(
        default=512,
        metadata={"help": "Maximum new tokens for OPRO LLM"}
    )
    opro_meta_prompt_preamble_template: str = field(
        default="This component is meant to handle the task:\n{component_description}\nWe want to improve its prompt based on prior attempts.\n",
        metadata={"help": "Meta prompt preamble template for OPRO (use {component_description} placeholder)"}
    )
