"""
huggingface-cli download Qwen/Qwen2-1.5B --local-dir local_lm/qwen-1_5b/base

CUDA_VISIBLE_DEVICES=6,7 VLLM_ALLOW_RUNTIME_LORA_UPDATING=True python -m vllm.entrypoints.openai.api_server \
    --port 8877 --host localhost --trust-remote-code \
    --enable-lora \
    --max-lora-rank 32 \
    --max-loras 2 \
    --model local_lm/qwen-1_5b/base \
    --tensor-parallel-size 2
"""
import os
import os.path as osp
import json
import requests
from typing import Dict, Any, List, Optional
from peft import LoraConfig
from pathlib import Path
from dotenv import load_dotenv
import dspy
import copy

from optimas.arch.system import CompoundAISystem
from optimas.arch.base import BaseComponent
from optimas.adapt.dspy import create_component_from_dspy
from optimas.reward.model import RewardModel
from datasets import Dataset
from optimas.utils.lora import load_lora_adapter


# change input path to env variable
BASE_MODEL_PATH = os.getenv(
    "BASE_MODEL_PATH", "local_lm/qwen-1_5b/base",
)


# Helper functions
def accuracy(answer: str, gd_answer: str) -> float:
    """Exact-match accuracy metric."""
    return 1.0 if str(answer) == str(gd_answer) else 0.0


def post_http_request(
    prompt: str,
    api_url: str,
    headers: Dict[str, str],
    base_model: str,
    adapter_id: str = None,
    *,
    n: int = 1,
    temperature: float = 0.6,
    stream: bool = False,
    max_tokens: int = 512,
) -> requests.Response:
    """
    Send a completion request to *local* vLLM in OpenAI-compatible mode.
    """
    payload: Dict[str, Any] = {
        "model": base_model,
        "prompt": prompt,
        "n": n,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream,
        
    }
    if adapter_id is not None:
        payload["model"] = adapter_id

    return requests.post(
        api_url,
        headers=headers,
        json=payload,
        stream=stream,
        timeout=180
    )


def get_response(response: requests.Response) -> str:
    """
    Extract the first completion string from an OpenAI response.
    """
    response.raise_for_status()
    data = response.json()
    # OpenAI schema → choices[0].text
    return data["choices"][0]["text"].strip()

# --------------------------------------------------------------------------- #
#  Modules                                                                    #
# --------------------------------------------------------------------------- #
class SessionAnalyzerModule(BaseComponent):
    """Summarise a user's session into a compact context string (local LLM)."""

    def __init__(
        self,
        base_model_path,
        lora_cfg: LoraConfig,
        host: str = "localhost",
        port: int = 8877,
    ):
        self.host = host
        self.port = port
        self.api_url = f"http://{host}:{port}/v1/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('VLLM_API_KEY', 'dummy')}",
            "User-Agent": "SessionAnalyzerClient",
        }

        super().__init__(
            description="Summarise session into context using local VLLM",
            input_fields=["sequence"],
            output_fields=["context"],
            variable=Path(base_model_path),
            config={
                "base_model_path": base_model_path,
                "lora_cfg": lora_cfg,
                "temperature": 0.6,
            }
        )
        self.adapter_id = self.__class__.__name__

    def on_variable_update_end(self):
        load_lora_adapter(self.__class__.__name__, self.variable, self.host, self.port)

    def forward(self, **inputs):
        sequence = inputs["sequence"]
        prompt = (
            "You are an e-commerce behaviour analyst.\n\n"
            "Session sequence:\n"
            f"{sequence}\n\n"
            "Provide a 2-3 sentence summary of the user's browsing intent."
        )
        response = post_http_request(
            prompt,
            self.api_url,
            headers=self.headers,
            temperature=self.config.temperature,
            base_model=self.config.base_model_path,
            adapter_id=None if str(self.variable) == str(self.config.base_model_path) else self.adapter_id,
        )
        summary = get_response(response)
        return {"context": summary}


class CandidateProfilerModule(BaseComponent):
    """Give line-by-line feedback on each candidate item (local LLM)."""

    def __init__(
        self,
        base_model_path,
        lora_cfg: LoraConfig,
        host: str = "localhost",
        port: int = 8877,
    ):
        self.host = host
        self.port = port
        self.api_url = f"http://{host}:{port}/v1/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('VLLM_API_KEY', 'dummy')}",
            "User-Agent": "CandidateProfilerClient",
        }

        super().__init__(
            description="Generate feedback for each candidate using local VLLM",
            input_fields=["context", "choices"],
            output_fields=["feedback"],
            variable=Path(base_model_path),
            config={
                "base_model_path": base_model_path,
                "lora_cfg": lora_cfg,
                "temperature": 0.6,
            }
        )
        self.adapter_id = self.__class__.__name__

    def on_variable_update_end(self):
        load_lora_adapter(self.adapter_id, self.variable, self.host, self.port)

    def forward(self, **inputs):
        context = inputs["context"]
        choices = inputs["choices"]
        prompt = (
            "You are an e-commerce candidate profiler.\n\n"
            "Session summary:\n"
            f"{context}\n\n"
            "Candidate items:\n"
            f"{json.dumps(choices, indent=2)}\n\n"
            "For each item, on its own line, write a brief (1-2 sentence) "
            "comment on why the user might or might not choose it next."
        )

        # Use the current adapter_id (which might be an adapter) or the base model

        response = post_http_request(
            prompt,
            self.api_url,
            headers=self.headers,
            temperature=self.config.temperature,
            base_model=self.config.base_model_path,
            adapter_id=None if str(self.variable) == str(self.config.base_model_path) else self.adapter_id,
        )
        feedback = get_response(response)
        return {"feedback": feedback}


class NextItemDecider(dspy.Signature):
    """Select the next item by considering both the summary and the provided feedback carefully."""
    context: str = dspy.InputField(prefix="Context: ", desc="Summary of behaviour")
    feedback: str = dspy.InputField(prefix="Feedback: ", desc="Comments per option")
    answer: str = dspy.OutputField(prefix="Answer: ", desc="Index of item chosen")


# --------------------------------------------------------------------------- #
#  Pipeline factory                                                           #
# --------------------------------------------------------------------------- #
def system_engine(*args, **kwargs):
    from dotenv import load_dotenv
    import os.path as osp
    import os

    # Load .env secrets
    dotenv_path = osp.expanduser(".env")
    load_dotenv(dotenv_path)

    # Configure LLM
    lm = dspy.LM(
        model="openai/gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        max_tokens=1024,
        temperature=0.3,
    )
    dspy.settings.configure(lm=lm)

    # Host and port setup for VLLM adapters
    host = os.getenv("VLLM_HOST", "localhost")
    port = int(os.getenv("VLLM_PORT", "8877"))

    lora_cfg = LoraConfig(
        r=32, 
        lora_alpha=32, 
        lora_dropout=0.05,
        target_modules=[
            "q_proj", "k_proj", "v_proj", "o_proj"
        ],
        bias="none",
        task_type="CAUSAL_LM",
    )
    # Initialize system using constructor-based configuration
    system = CompoundAISystem(
        components={
            "session_analyzer": SessionAnalyzerModule(
                lora_cfg=lora_cfg, host=host, port=port, base_model_path=BASE_MODEL_PATH
            ),
            "candidate_profiler": CandidateProfilerModule(
                lora_cfg=lora_cfg, host=host, port=port, base_model_path=BASE_MODEL_PATH
            ),
            "next_item_decider": create_component_from_dspy(NextItemDecider),
        },
        final_output_fields=["answer"],
        ground_fields=["gd_answer"],
        eval_func=accuracy,
        *args,
        **kwargs,
    )

    return system


def build_prompt(
    component_name: str,
    sample: Dict,
    policy_role: str = "assistant",
) -> str:
    """
    Re-create *exactly* the prompt used inside the system
    so the policy sees the same distribution it will face at inference.
    """
    if component_name == "session_analyzer":
        sequence = sample.get("sequence", "")
        if not sequence:
            raise ValueError("Missing required 'sequence' field for session_analyzer")

        prompt = (
            "You are an e-commerce behavior analyst.\n\n"
            "Session sequence:\n"
            f"{sequence}\n\n"
            "Provide a 2-3 sentence summary of the user's browsing intent."
        )
    elif component_name == "candidate_profiler":
        context = sample.get("context", "")
        choices = sample.get("choices", [])

        if not context or not choices:
            raise ValueError("Missing required 'context' or 'choices' fields for candidate_profiler")

        prompt = (
            "You are an e-commerce candidate profiler.\n\n"
            "Session summary:\n"
            f"{context}\n\n"
            "Candidate items:\n"
            f"{json.dumps(choices, indent=2)}\n\n"
            "For each item, on its own line, write a brief (1-2 sentence) "
            "comment on why the user might or might not choose it next."
        )
    else:
        raise ValueError(f"Unknown component: {component_name}")

    # We let the **policy** continue from the prompt.
    return prompt


def make_dataset(component_name: str, output_dir: str, split: str = "train", train_size: int = -1) -> Dataset:
    """
    Convert your optimization dataset into a 🤗 Dataset with only the columns
    we need. This function handles the data transformation necessary for PPO training.
    """
    trainset, valset, testset = dataset_engine()
    if train_size != -1:
        trainset = trainset[:min(len(trainset), train_size)]
        print(f"Using {len(trainset)} training examples for ppo training")
    raw_dataset = trainset if split == "train" else testset
    random.seed(42)
    random.shuffle(raw_dataset)

    # Create an intermediary processing system to generate missing fields
    # hard code for Amazon system for now
    temp_system =  system = system_engine(log_dir=output_dir)

    temp_system.rm = None
    temp_system.sample_size = None
    temp_system.components_to_apply = []

    processed_examples = []
    for example in raw_dataset:
        example_dict = {"sequence": example.sequence, "choices": example.choices, "gd_answer": example.gd_answer}

        # For candidate_profiler, we need to generate 'context' by running through session_analyzer
        if component_name == "candidate_profiler":
            session_result = temp_system.components["session_analyzer"](sequence=example.sequence)
            example_dict["context"] = session_result["context"]

        processed_examples.append(example_dict)

    hf_dataset = Dataset.from_list(processed_examples)

    def add_prompt(example):
        example["prompt"] = build_prompt(component_name, example)
        return example

    hf_dataset = hf_dataset.map(add_prompt)
    return hf_dataset


def reward_fn_factory(
    reward_model: RewardModel, component_name: str
):
    """
    Wrap the optimas RewardModel so PPOTrainer can call it.
    PPOTrainer expects `reward_fn(samples: List[dict]) -> List[float]`.
    Each sample is a dict with keys `prompt` and `completion`.
    """

    def reward_fn(samples: List[Dict]) -> List[float]:
        rewards = []
        for s in samples:
            if isinstance(s, str):
                s = json.loads(s)

            # Ensure we have the original data
            orig_data = s.get("orig", {})

            if component_name == "session_analyzer":
                reward = reward_model.evaluate(
                    component_name,
                    sequence=orig_data.get("sequence", ""),
                    context=s["completion"],
                    sigmoid=True,
                )
            elif component_name == "candidate_profiler":
                reward = reward_model.evaluate(
                    component_name,
                    context=orig_data.get("context", ""),
                    choices=orig_data.get("choices", []),
                    feedback=s["completion"],
                    sigmoid=True,
                )
            else:
                raise ValueError(f"Unknown component: {component_name}")

            rewards.append(float(reward))
        return rewards

    return reward_fn

if __name__ == "__main__":

    from examples.datasets.amazon import dataset_engine
    trainset, valset, testset = dataset_engine()

    system = system_engine()

    pred = system(sequence=trainset[0].sequence, choices=trainset[0].choices)
    print("Sample prediction:", pred.answer)
    print("Sample answer:", trainset[0].gd_answer)

    print("Evaluating on testset...")
    with system.context({"session_analyzer": {"temperature": 1.0}}):
        scores = system.evaluate_multiple(testset)
        print("Average score:", sum(scores) / len(scores))
    
    comp = system.components['session_analyzer']
    result1 = comp(sequence=trainset[0].sequence)
    comp.update(Path('path/to/your/lora_adapter'))
    result2 = comp(sequence=trainset[0].sequence)
    print("Result 1:", result1)
    print("Result 2:", result2)