import os
import os.path as osp
import json
import threading
import hashlib
from typing import Any, Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
from tqdm import tqdm
from datasets import Dataset, DatasetDict

from optimas.arch.system import CompoundAISystem
from optimas.utils.logger import setup_logger

logger = setup_logger(__name__)


def process_example(system: CompoundAISystem, example: Any) -> Tuple[Any, Any, float] | None:
    """
    Process a single example through the system and return predictions and evaluation score.

    Args:
        system (CompoundAISystem): The compound AI system used for processing.
        example (Any): A single input example (should support attribute access for input fields).

    Returns:
        tuple: (example, prediction, score) if successful.
        None: if an exception occurs during processing.
    """
    try:
        inputs = {k: getattr(example, k) for k in system.required_input_fields}
        prediction = system(**inputs)
        score = system.evaluate(example, prediction)
        return example, prediction, score
    except Exception as e:
        logger.error(f"Failed to process example: {e}", exc_info=True)
        return None


def process_dataset_parallel(
    dataset: List[Any],
    system: CompoundAISystem,
    max_workers: int = 4,
) -> Tuple[List[Any], List[Any], List[float]]:
    """
    Process a list of examples in parallel using multiple threads.

    Args:
        dataset (List[Any]): A list of input examples to process.
        system (CompoundAISystem): The compound AI system for inference and evaluation.
        max_workers (int, optional): Number of threads to use for parallel processing. Defaults to 4.

    Returns:
        Tuple[List[Any], List[Any], List[float]]: 
            A tuple of (examples, predictions, evaluation scores).
    """
    examples, predictions, scores = [], [], []

    # Thread-safe counter for progress tracking
    counter_lock = threading.Lock()
    counter = {"processed": 0}

    # Initialize progress bar
    pbar = tqdm(total=len(dataset), desc="Processing examples")

    def update_progress():
        with counter_lock:
            counter["processed"] += 1
            pbar.update(1)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(process_example, system, example): example
            for example in dataset
        }

        for future in as_completed(futures):
            result = future.result()
            if result is not None:
                ex, pred, score = result
                examples.append(ex)
                predictions.append(pred)
                scores.append(score)
            update_progress()

    pbar.close()
    return examples, predictions, scores
