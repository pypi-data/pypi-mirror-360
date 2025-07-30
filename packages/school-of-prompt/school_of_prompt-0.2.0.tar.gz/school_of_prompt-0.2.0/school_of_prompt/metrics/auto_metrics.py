"""
Auto metric selection with smart defaults.
"""

from typing import Union, List, Optional, Any
from ..core.simple_interfaces import SimpleMetric, SimpleTask


def auto_select_metrics(
    metrics: Optional[Union[str, List[str], List[SimpleMetric]]],
    task: SimpleTask
) -> List[SimpleMetric]:
    """
    Auto-select appropriate metrics based on task type.

    Args:
        metrics: Metric names, instances, or None for auto-selection
        task: Task instance to help determine appropriate metrics

    Returns:
        List of SimpleMetric instances
    """

    if metrics is None:
        # Auto-select based on task type
        return _auto_select_for_task(task)

    if isinstance(metrics, str):
        metrics = [metrics]

    result = []
    for metric in metrics:
        if isinstance(metric, SimpleMetric):
            result.append(metric)
        elif isinstance(metric, str):
            result.append(_create_metric_by_name(metric))
        else:
            raise ValueError(f"Unsupported metric type: {type(metric)}")

    return result


def _auto_select_for_task(task: SimpleTask) -> List[SimpleMetric]:
    """Select appropriate metrics based on task characteristics."""

    # Try to infer task type from the task's extract function
    # This is a heuristic - in practice you might want to make this more robust

    # Default to accuracy for classification-like tasks
    return [
        _create_metric_by_name("accuracy"),
        _create_metric_by_name("f1")
    ]


def _create_metric_by_name(name: str) -> SimpleMetric:
    """Create metric instance by name."""

    name_lower = name.lower()

    if name_lower == "accuracy":
        return SimpleMetric("accuracy", _accuracy)
    elif name_lower in ["f1", "f1_score"]:
        return SimpleMetric("f1_score", _f1_score)
    elif name_lower == "precision":
        return SimpleMetric("precision", _precision)
    elif name_lower == "recall":
        return SimpleMetric("recall", _recall)
    elif name_lower in ["mae", "mean_absolute_error"]:
        return SimpleMetric("mae", _mae)
    elif name_lower in ["mse", "mean_squared_error"]:
        return SimpleMetric("mse", _mse)
    elif name_lower in ["rmse", "root_mean_squared_error"]:
        return SimpleMetric("rmse", _rmse)
    else:
        raise ValueError(f"Unknown metric: {name}")


# Metric implementations
def _accuracy(predictions: List[Any], actuals: List[Any]) -> float:
    """Calculate accuracy."""
    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have same length")

    if not predictions:
        return 0.0

    correct = sum(1 for p, a in zip(predictions, actuals)
                  if str(p).lower() == str(a).lower())
    return correct / len(predictions)


def _f1_score(predictions: List[Any], actuals: List[Any]) -> float:
    """Calculate F1 score (macro-averaged for multi-class)."""
    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have same length")

    if not predictions:
        return 0.0

    # Convert to strings for comparison
    preds = [str(p).lower() for p in predictions]
    acts = [str(a).lower() for a in actuals]

    # Get unique classes
    classes = set(preds + acts)

    if len(classes) <= 2:
        # Binary F1
        return _binary_f1(preds, acts, list(classes))
    else:
        # Macro F1
        f1_scores = []
        for cls in classes:
            f1 = _binary_f1(preds, acts, [cls])
            if f1 > 0:  # Only include non-zero F1 scores
                f1_scores.append(f1)

        return sum(f1_scores) / len(f1_scores) if f1_scores else 0.0


def _binary_f1(
        predictions: List[str],
        actuals: List[str],
        positive_classes: List[str]) -> float:
    """Calculate binary F1 score."""

    # Convert to binary (positive class vs rest)
    pred_binary = [1 if p in positive_classes else 0 for p in predictions]
    actual_binary = [1 if a in positive_classes else 0 for a in actuals]

    tp = sum(
        1 for p,
        a in zip(
            pred_binary,
            actual_binary) if p == 1 and a == 1)
    fp = sum(
        1 for p,
        a in zip(
            pred_binary,
            actual_binary) if p == 1 and a == 0)
    fn = sum(
        1 for p,
        a in zip(
            pred_binary,
            actual_binary) if p == 0 and a == 1)

    if tp == 0:
        return 0.0

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    if precision + recall == 0:
        return 0.0

    return 2 * (precision * recall) / (precision + recall)


def _precision(predictions: List[Any], actuals: List[Any]) -> float:
    """Calculate precision (macro-averaged)."""
    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have same length")

    if not predictions:
        return 0.0

    preds = [str(p).lower() for p in predictions]
    acts = [str(a).lower() for a in actuals]

    classes = set(preds + acts)
    precisions = []

    for cls in classes:
        tp = sum(1 for p, a in zip(preds, acts) if p == cls and a == cls)
        fp = sum(1 for p, a in zip(preds, acts) if p == cls and a != cls)

        if tp + fp > 0:
            precisions.append(tp / (tp + fp))

    return sum(precisions) / len(precisions) if precisions else 0.0


def _recall(predictions: List[Any], actuals: List[Any]) -> float:
    """Calculate recall (macro-averaged)."""
    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have same length")

    if not predictions:
        return 0.0

    preds = [str(p).lower() for p in predictions]
    acts = [str(a).lower() for a in actuals]

    classes = set(preds + acts)
    recalls = []

    for cls in classes:
        tp = sum(1 for p, a in zip(preds, acts) if p == cls and a == cls)
        fn = sum(1 for p, a in zip(preds, acts) if p != cls and a == cls)

        if tp + fn > 0:
            recalls.append(tp / (tp + fn))

    return sum(recalls) / len(recalls) if recalls else 0.0


def _mae(predictions: List[Any], actuals: List[Any]) -> float:
    """Calculate Mean Absolute Error."""
    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have same length")

    if not predictions:
        return 0.0

    try:
        pred_nums = [float(p) for p in predictions]
        actual_nums = [float(a) for a in actuals]

        errors = [abs(p - a) for p, a in zip(pred_nums, actual_nums)]
        return sum(errors) / len(errors)
    except (ValueError, TypeError):
        raise ValueError("MAE requires numeric predictions and actuals")


def _mse(predictions: List[Any], actuals: List[Any]) -> float:
    """Calculate Mean Squared Error."""
    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have same length")

    if not predictions:
        return 0.0

    try:
        pred_nums = [float(p) for p in predictions]
        actual_nums = [float(a) for a in actuals]

        errors = [(p - a) ** 2 for p, a in zip(pred_nums, actual_nums)]
        return sum(errors) / len(errors)
    except (ValueError, TypeError):
        raise ValueError("MSE requires numeric predictions and actuals")


def _rmse(predictions: List[Any], actuals: List[Any]) -> float:
    """Calculate Root Mean Squared Error."""
    import math
    return math.sqrt(_mse(predictions, actuals))
