import warnings
import numpy as np
from typing import Any, Dict, List, Optional, Tuple, Union
from transformers.trainer_utils import EvalPrediction
import torch
import torch.nn as nn


def compute_accuracy_and_margin(eval_pred: EvalPrediction) -> dict[str, float]:
    predictions, labels = eval_pred
    assert predictions.ndim == 2

    # Here, predictions is rewards_chosen and rewards_rejected. Shapes are (batch_size, 2) and (batch_size,)
    # We want to see the gap between rewards_chosen and rewards_rejected.
    labels = np.array(labels, dtype=int)
    margins = np.array(predictions[:, labels] - predictions[:, 1 - labels], dtype=float)
    accuracy = np.array(margins > 0).mean().item() + 0.5 * np.array(margins == 0).mean().item()
    margin = margins.mean().item()

    equal_mask = predictions[:, 0] == predictions[:, 1]
    equal_predictions_count = int(equal_mask.sum())

    if equal_predictions_count > 0:
        warnings.warn(
            f"There are {equal_predictions_count} out of {len(predictions[:, 0])} instances where the predictions "
            "for both options are equal. These instances are ignored in the accuracy_disgard_equal computation.",
            UserWarning,
        )

    # Filter out equal predictions
    predictions = predictions[~equal_mask]
    labels = labels[~equal_mask]

    # Use the remaining predictions for accuracy calculation
    predictions = np.argmax(predictions, axis=1)
    return {
        "margin": margin, 
        "accuracy": accuracy
    }

