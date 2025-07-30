from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import traceback
from typing import Callable, List, Any, Tuple, Optional
from optimas.utils.logger import setup_logger

logger = setup_logger(__name__)


def run_parallel_tasks(
    task_func: Callable[..., Any],
    task_args: List[Tuple[Any, ...]],
    max_workers: int = 4,
    use_tqdm: bool = False, 
    task_desc: str = "[run_parallel_tasks]"
) -> List[Any]:
    """
    Executes a given function in parallel with multiple sets of arguments.

    Args:
        task_func (Callable[..., Any]): The function to execute in parallel.
        task_args (List[Tuple[Any, ...]]): A list of argument tuples for each function call.
        max_workers (int): Number of worker threads to use for parallel execution.
        task_desc (str): Description for the progress bar.

    Returns:
        List[Any]: A list of results corresponding to each function call.
    """

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(task_func, *args): args for args in task_args}
        
        if use_tqdm:
            for future in tqdm(as_completed(futures), total=len(futures), desc=task_desc):
                try:
                    results.append(future.result())
                except Exception as e:
                    logger.info(f"Error in parallel execution for args {futures[future]}: {traceback.format_exc()}")
                    results.append(None)
        else:
            for future in as_completed(futures):
                try:
                    results.append(future.result())
                except Exception as e:
                    logger.info(f"Error in parallel execution for args {futures[future]}: {traceback.format_exc()}")
                    results.append(None)
    return results
