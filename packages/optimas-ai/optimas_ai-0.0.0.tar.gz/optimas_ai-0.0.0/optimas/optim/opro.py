# opro.py
import copy
import re
import random
import bisect
from tqdm import tqdm
from typing import Callable, List, Optional, Union
from optimas.utils.api import get_llm_output
from optimas.arch.base import BaseComponent
from optimas.utils.logger import setup_logger
from optimas.utils.parallel import run_parallel_tasks
from optimas.wrappers.prediction import Prediction

logger = setup_logger(__name__)


class SortedCandidateList:
    def __init__(self, candidates):
        self.candidates = candidates

    def insert(self, candidate):
        """
        Insert a new candidate while maintaining the sort order.
        candidate: Tuple of (str, int) where int is the score
        """
        bisect.insort_right(self.candidates, candidate, key=lambda x: x[1])

    def get_all_sorted(self):
        """Return all candidates sorted from lowest to highest score"""
        return self.candidates

    def get_lowest_score(self):
        """Return the candidate with the lowest score"""
        if not self.candidates:
            return None
        return self.candidates[0]

    def get_highest_score(self):
        """Return the candidate with the highest score"""
        if not self.candidates:
            return None
        return self.candidates[-1]

TIPS = {
        "creative": "Don't be afraid to be creative when creating the new instruction!",
        "simple": "Keep the instruction clear and concise.",
        "description": "Make sure your instruction is very informative and descriptive.",
        "specific": "The instruction should include specific details such as numbers or conditions.",
        # "high_stakes": "The instruction should include a high stakes scenario in which the LM must solve the task!",
        # "persona": 'Include a persona that is relevant to the task in the instruction (ie. "You are a ...")',
    }

class OPRO:
    """
    OPRO (Large Language Models as Optimizers):
    Iteratively propose improved prompts using an LLM.

    Parameters:
    -----------
    metric: Callable
        A function metric(example, prediction) -> float that
        returns a scalar reward for a given prompt.
    llm_model: str
        Name of the model to call via get_llm_output (e.g. "gpt-4o").
    num_prompt_candidates: int
        How many times to iteratively improve the prompt.
    temperature: float
        Temperature for the optimizer LLM calls.
    max_new_tokens: int
        Maximum tokens for the optimizer LLM calls.
    meta_prompt_preamble: str
        A string describing the overall task to the optimizer LLM.
    """

    def __init__(
        self,
        metric: Callable,
        llm_model: str = "gpt-4o",
        num_prompt_candidates: int = 5,
        temperature: float = 0.7,
        max_new_tokens: int = 512,
        meta_prompt_preamble: Optional[str] = None,
        max_sample_workers=4,
    ):
        self.metric = metric
        self.llm_model = llm_model
        self.num_prompt_candidates = num_prompt_candidates
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.max_sample_workers = max_sample_workers

        # Optionally describe the task in the meta-prompt
        self.meta_prompt_preamble = meta_prompt_preamble or (
            "You are an AI specialized in improving prompts for a certain component.\n"
            "We have a list of (prompt, score) pairs tried so far.\n"
            "Please propose an improved new prompt that may yield a higher score.\n"
        )

    def compile(
        self,
        component: BaseComponent,
        initial_prompt: Union[str, "dspy.Signature"],
        trainset: List,
        include_initial_prompt: bool = False,
        **kwargs
    ) -> Union[str, "dspy.Signature"]:
        """
        Run the OPRO iterations to improve `initial_prompt`.
        `trainset` is the data on which we will evaluate the candidate.

        Return the best prompt found.
        """

        if include_initial_prompt:
            best_prompt = initial_prompt
            best_score = self._evaluate_prompt(component, initial_prompt, trainset)
            logger.info(f"Initial prompt: {initial_prompt}, Score: {best_score}")
            prompt_score_pairs = [(initial_prompt, best_score)]

            prompt_history = [(best_prompt, best_score)]
            prompt_history = SortedCandidateList(prompt_history)
        else:
            best_score = -1e5
            prompt_score_pairs = []
            prompt_history = SortedCandidateList([])

        for iteration in range(self.num_prompt_candidates):
            meta_prompt = self._build_meta_prompt(prompt_history)

            logger.info(f'{meta_prompt=}')
            new_candidate = get_llm_output(
                message=meta_prompt,
                model=self.llm_model,
                temperature=self.temperature,
                max_new_tokens=self.max_new_tokens,
            )
            new_candidate = self._parse_llm_solution(new_candidate)
            logger.info(f'{new_candidate=}')

            logger.info(f"Iteration {iteration + 1}: Proposed new candidate prompt: {new_candidate}")
            candidate_score = self._evaluate_prompt(component, new_candidate, trainset)
            prompt_history.insert((new_candidate, candidate_score))

            if candidate_score >= best_score:
                best_score = candidate_score

            prompt_score_pairs.append((new_candidate, candidate_score))

        # shuffle the prompt_score_pairs
        random.shuffle(prompt_score_pairs)
        prompt_score_pairs.sort(key=lambda x: x[1], reverse=True)

        logger.info(f'{prompt_history.candidates=}')
        return prompt_score_pairs[0][0], prompt_score_pairs

    def _build_meta_prompt(self, prompt_history: List[tuple]) -> str:
        """
        Build the meta-prompt string from the prompt history.
        """
        history_str = ""
        for i, (prompt_i, score_i) in enumerate(prompt_history.candidates):
            history_str += f"Prompt #{i+1}:\n{prompt_i}\nScore: {round(score_i, 3)}\n\n"

        tip = TIPS.get(random.choice(list(TIPS.keys())), "")
        meta_prompt = (
            f"{self.meta_prompt_preamble}\n"
            f"Below are the previous prompt attempts and their scores.\n"
            f"The prompt are arranged in ascending order based on their scores, where higher scores indicate better quality\n\n"
            f"{history_str}"
            f"Observe the patter carefully. Now propose a new improved prompt. {tip}\n"
            f"Format:\nSolution: <your new prompt>\n"
        )
        return meta_prompt

    def _parse_llm_solution(self, llm_response: str) -> Optional[str]:
        """
        Extract the actual new prompt from the LLM response.
        For example, look for a line like: 'Solution: ...'
        """
        match = re.search(r"Solution:\s*(.*)", llm_response, re.IGNORECASE)
        if match:
            # Extract the prompt after "Solution:"
            return match.group(1).strip()
        else:
            return llm_response

    def _evaluate_prompt(self, component, candidate_prompt: str, trainset: List) -> float:
        """
        Evaluate the candidate prompt using the provided metric on the trainset.
        The `metric` expects (example, pred) or something similar.
        """
        total_score = 0.0
        assert isinstance(component.variable, str), "Module variable should be a string."
        def process_single_example(component, example):
            """Process a single example through the component"""
            pred = component(**example.inputs())
            pred = Prediction(**pred)
            return pred

        # Prepare the task arguments
        task_args = [(component, example) for example in trainset]

        # Run in parallel
        with component.context(variable=candidate_prompt):
            predictions = run_parallel_tasks(
                task_func=process_single_example,
                task_args=task_args,
                max_workers=self.max_sample_workers,  # Adjust based on your system capabilities
                use_tqdm=True,
                task_desc="Evaluate prompt"
            )

        # Filter out None results (from errors) if needed
        predictions = [pred for pred in predictions if pred is not None]

        avg_score = self.metric(trainset, predictions)
        return avg_score
