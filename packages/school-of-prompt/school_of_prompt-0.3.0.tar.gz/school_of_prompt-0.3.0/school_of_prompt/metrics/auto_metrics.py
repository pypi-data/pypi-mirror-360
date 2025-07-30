"""
Auto metric selection with smart defaults.
Enhanced with tolerance-based, domain-specific, and statistical metrics.
"""

from typing import Union, List, Optional, Any, Dict
from ..core.simple_interfaces import SimpleMetric, SimpleTask
import math
import statistics


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

    # Original metrics
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
    
    # Tolerance-based metrics
    elif name_lower == "within_1":
        return SimpleMetric("within_1", lambda p, a: _within_tolerance(p, a, 1))
    elif name_lower == "within_2":
        return SimpleMetric("within_2", lambda p, a: _within_tolerance(p, a, 2))
    elif name_lower == "within_3":
        return SimpleMetric("within_3", lambda p, a: _within_tolerance(p, a, 3))
    elif name_lower == "within_5":
        return SimpleMetric("within_5", lambda p, a: _within_tolerance(p, a, 5))
    
    # Domain-specific metrics
    elif name_lower == "valid_rate":
        return SimpleMetric("valid_rate", _valid_rate)
    elif name_lower == "token_efficiency":
        return SimpleMetric("token_efficiency", _token_efficiency)
    elif name_lower == "response_quality":
        return SimpleMetric("response_quality", _response_quality)
    
    # Statistical metrics
    elif name_lower == "r2_score":
        return SimpleMetric("r2_score", _r2_score)
    elif name_lower == "prediction_confidence":
        return SimpleMetric("prediction_confidence", _prediction_confidence)
    elif name_lower == "error_std":
        return SimpleMetric("error_std", _error_std)
    elif name_lower == "median_error":
        return SimpleMetric("median_error", _median_error)
    
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


# Enhanced metrics implementations

def _within_tolerance(predictions: List[Any], actuals: List[Any], tolerance: float) -> float:
    """Calculate percentage of predictions within tolerance of actual values."""
    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have same length")
    
    if not predictions:
        return 0.0
    
    try:
        pred_nums = [float(p) for p in predictions]
        actual_nums = [float(a) for a in actuals]
        
        within_tolerance = sum(1 for p, a in zip(pred_nums, actual_nums) 
                              if abs(p - a) <= tolerance)
        return within_tolerance / len(predictions)
    except (ValueError, TypeError):
        raise ValueError("Tolerance metrics require numeric predictions and actuals")


def _valid_rate(predictions: List[Any], actuals: List[Any]) -> float:
    """Calculate rate of valid/parseable predictions."""
    if not predictions:
        return 0.0
    
    valid_count = 0
    for pred in predictions:
        # Check if prediction is valid based on different criteria
        if pred is not None and str(pred).strip():
            # Basic validity: not None and not empty
            valid_count += 1
    
    return valid_count / len(predictions)


def _token_efficiency(predictions: List[Any], actuals: List[Any]) -> float:
    """Calculate token efficiency (shorter responses get bonus for equal accuracy)."""
    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have same length")
    
    if not predictions:
        return 0.0
    
    # Calculate base accuracy
    base_accuracy = _accuracy(predictions, actuals)
    
    # Calculate average token length (approximate)
    avg_length = sum(len(str(p).split()) for p in predictions) / len(predictions)
    
    # Efficiency bonus for shorter responses (normalized)
    efficiency_bonus = max(0, (50 - avg_length) / 50)  # 50 tokens as baseline
    
    return base_accuracy * (1 + efficiency_bonus * 0.1)  # 10% max bonus


def _response_quality(predictions: List[Any], actuals: List[Any]) -> float:
    """Calculate response quality based on completeness and format."""
    if not predictions:
        return 0.0
    
    quality_scores = []
    for pred in predictions:
        pred_str = str(pred).strip()
        
        # Quality criteria
        score = 0.0
        
        # Completeness (not empty)
        if pred_str:
            score += 0.5
        
        # Reasonable length (not too short, not too long)
        if 1 <= len(pred_str.split()) <= 20:
            score += 0.3
        
        # Contains expected format (basic check)
        if pred_str and not pred_str.startswith("Error"):
            score += 0.2
        
        quality_scores.append(score)
    
    return sum(quality_scores) / len(quality_scores)


def _r2_score(predictions: List[Any], actuals: List[Any]) -> float:
    """Calculate R-squared score."""
    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have same length")
    
    if not predictions:
        return 0.0
    
    try:
        pred_nums = [float(p) for p in predictions]
        actual_nums = [float(a) for a in actuals]
        
        # Calculate means
        actual_mean = sum(actual_nums) / len(actual_nums)
        
        # Calculate sum of squares
        ss_res = sum((a - p) ** 2 for a, p in zip(actual_nums, pred_nums))
        ss_tot = sum((a - actual_mean) ** 2 for a in actual_nums)
        
        if ss_tot == 0:
            return 1.0 if ss_res == 0 else 0.0
        
        return 1 - (ss_res / ss_tot)
    except (ValueError, TypeError):
        raise ValueError("R2 score requires numeric predictions and actuals")


def _prediction_confidence(predictions: List[Any], actuals: List[Any]) -> float:
    """Calculate prediction confidence based on consistency."""
    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have same length")
    
    if not predictions:
        return 0.0
    
    # Simple confidence measure: inverse of prediction variance
    try:
        pred_nums = [float(p) for p in predictions]
        if len(set(pred_nums)) == 1:
            return 1.0  # All predictions the same = high confidence
        
        pred_std = statistics.stdev(pred_nums)
        # Normalize confidence (lower std = higher confidence)
        return max(0, 1 - (pred_std / (max(pred_nums) - min(pred_nums))))
    except (ValueError, TypeError):
        # For non-numeric predictions, use string consistency
        pred_strs = [str(p).lower() for p in predictions]
        unique_preds = len(set(pred_strs))
        return 1 - (unique_preds - 1) / len(predictions)


def _error_std(predictions: List[Any], actuals: List[Any]) -> float:
    """Calculate standard deviation of errors."""
    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have same length")
    
    if not predictions:
        return 0.0
    
    try:
        pred_nums = [float(p) for p in predictions]
        actual_nums = [float(a) for a in actuals]
        
        errors = [abs(p - a) for p, a in zip(pred_nums, actual_nums)]
        return statistics.stdev(errors) if len(errors) > 1 else 0.0
    except (ValueError, TypeError):
        raise ValueError("Error std requires numeric predictions and actuals")


def _median_error(predictions: List[Any], actuals: List[Any]) -> float:
    """Calculate median absolute error."""
    if len(predictions) != len(actuals):
        raise ValueError("Predictions and actuals must have same length")
    
    if not predictions:
        return 0.0
    
    try:
        pred_nums = [float(p) for p in predictions]
        actual_nums = [float(a) for a in actuals]
        
        errors = [abs(p - a) for p, a in zip(pred_nums, actual_nums)]
        return statistics.median(errors)
    except (ValueError, TypeError):
        raise ValueError("Median error requires numeric predictions and actuals")


# Enhanced metric selection with task-specific recommendations
def get_recommended_metrics(task_type: str, target_range: Optional[tuple] = None) -> List[str]:
    """Get recommended metrics based on task type and target range."""
    
    if task_type.lower() in ["classification", "sentiment", "categorization"]:
        return ["accuracy", "f1_score", "precision", "recall", "valid_rate"]
    
    elif task_type.lower() in ["regression", "rating", "scoring"]:
        base_metrics = ["mae", "rmse", "r2_score", "median_error"]
        
        # Add tolerance metrics based on target range
        if target_range:
            range_size = target_range[1] - target_range[0]
            if range_size <= 10:  # Small range (e.g., 1-10 rating)
                base_metrics.extend(["within_1", "within_2"])
            elif range_size <= 20:  # Medium range (e.g., 0-18 age)
                base_metrics.extend(["within_2", "within_3"])
            else:  # Large range
                base_metrics.extend(["within_5"])
        
        return base_metrics
    
    elif task_type.lower() in ["generation", "summarization", "text_gen"]:
        return ["response_quality", "token_efficiency", "valid_rate"]
    
    else:
        # Default comprehensive set
        return ["accuracy", "mae", "valid_rate", "response_quality"]
