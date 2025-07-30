"""
Main optimization function - the simple API entry point.
School of Prompt framework.
"""

import os
import pandas as pd
from typing import Union, List, Dict, Any, Optional
from pathlib import Path

from .core.simple_interfaces import SimpleMetric, SimpleDataSource, SimpleModel, SimpleTask
from .data.auto_loader import auto_load_data
from .models.auto_model import auto_create_model
from .tasks.auto_task import auto_detect_task
from .metrics.auto_metrics import auto_select_metrics


def optimize(
    data: Union[str, pd.DataFrame, SimpleDataSource],
    task: Union[str, SimpleTask],
    prompts: Union[str, List[str], Path],
    model: Union[str, Dict[str, Any], SimpleModel] = "gpt-3.5-turbo",
    metrics: Optional[Union[str, List[str], List[SimpleMetric]]] = None,
    api_key: Optional[str] = None,
    sample_size: Optional[int] = None,
    random_seed: int = 42,
    output_dir: Optional[str] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Optimize prompts with minimal setup required.

    Args:
        data: Path to CSV/JSONL file, DataFrame, or custom data source
        task: Task description (e.g., "classify sentiment") or custom task
        prompts: List of prompt variants or path to file containing prompts
        model: Model name, config dict, or custom model instance
        metrics: Metrics to evaluate (auto-selected if None)
        api_key: API key (or set OPENAI_API_KEY env var)
        sample_size: Limit evaluation to N samples
        random_seed: Random seed for reproducibility
        output_dir: Directory to save results (optional)
        verbose: Print progress information

    Returns:
        Dictionary with results including scores, best prompt, and analysis

    Examples:
        # Level 0 - Dead simple
        results = optimize(
            data="reviews.csv",
            task="classify sentiment",
            prompts=["Is this positive?", "Rate the sentiment"],
            api_key="sk-..."
        )

        # Level 1 - More control
        results = optimize(
            data="reviews.csv",
            task="classify sentiment",
            prompts="prompts/sentiment.txt",
            model={"name": "gpt-4", "temperature": 0.1},
            metrics=["accuracy", "f1"],
            sample_size=1000
        )
    """

    # Handle API key
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "API key required. Set OPENAI_API_KEY env var or pass api_key parameter.")

    # Auto-load data
    if verbose:
        print("📁 Loading data...")
    dataset = auto_load_data(
        data,
        sample_size=sample_size,
        random_seed=random_seed)

    # Auto-detect or create task
    if verbose:
        print("🎯 Setting up task...")
    task_obj = auto_detect_task(task, dataset)

    # Load prompts
    if verbose:
        print("📝 Loading prompts...")
    prompt_variants = _load_prompts(prompts)

    # Auto-create model
    if verbose:
        print("🤖 Setting up model...")
    model_obj = auto_create_model(model, api_key)

    # Auto-select metrics
    if verbose:
        print("📊 Setting up metrics...")
    metrics_list = auto_select_metrics(metrics, task_obj)

    # Run optimization
    if verbose:
        print("🚀 Running optimization...")
    results = _run_optimization(
        dataset=dataset,
        task=task_obj,
        prompts=prompt_variants,
        model=model_obj,
        metrics=metrics_list,
        verbose=verbose
    )

    # Save results if requested
    if output_dir:
        _save_results(results, output_dir, verbose)

    if verbose:
        print("✅ Optimization complete!")
        _print_summary(results)

    return results


def _load_prompts(prompts: Union[str, List[str], Path]) -> List[str]:
    """Load prompt variants from various sources."""
    if isinstance(prompts, (str, Path)):
        path = Path(prompts)
        if path.exists():
            # Read from file (one prompt per line)
            with open(path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        else:
            # Single prompt string
            return [str(prompts)]
    elif isinstance(prompts, list):
        return prompts
    else:
        raise ValueError(
            "prompts must be string, list of strings, or path to file")


def _run_optimization(
    dataset: List[Dict[str, Any]],
    task: SimpleTask,
    prompts: List[str],
    model: SimpleModel,
    metrics: List[SimpleMetric],
    verbose: bool
) -> Dict[str, Any]:
    """Run the actual optimization process."""

    results = {
        "prompts": {},
        "best_prompt": None,
        "best_score": None,
        "summary": {},
        "details": []
    }

    for i, prompt in enumerate(prompts):
        if verbose:
            print(
                f"  Evaluating prompt {i + 1}/{len(prompts)}: {prompt[:50]}...")

        prompt_results = _evaluate_prompt(
            prompt=prompt,
            dataset=dataset,
            task=task,
            model=model,
            metrics=metrics
        )

        results["prompts"][f"prompt_{i + 1}"] = prompt_results
        results["details"].append(prompt_results)

        # Track best prompt (using first metric as primary)
        primary_score = prompt_results["scores"][metrics[0].name]
        if results["best_score"] is None or primary_score > results["best_score"]:
            results["best_prompt"] = prompt
            results["best_score"] = primary_score

    # Generate summary
    results["summary"] = _generate_summary(results["details"], metrics)

    return results


def _evaluate_prompt(
    prompt: str,
    dataset: List[Dict[str, Any]],
    task: SimpleTask,
    model: SimpleModel,
    metrics: List[SimpleMetric]
) -> Dict[str, Any]:
    """Evaluate a single prompt against the dataset."""

    predictions = []
    actuals = []

    for sample in dataset:
        # Format prompt with sample data
        formatted_prompt = task.format_prompt(prompt, sample)

        # Get model prediction
        response = model.generate(formatted_prompt)
        prediction = task.extract_prediction(response)
        actual = task.get_ground_truth(sample)

        predictions.append(prediction)
        actuals.append(actual)

    # Calculate metrics
    scores = {}
    for metric in metrics:
        score = metric.calculate(predictions, actuals)
        scores[metric.name] = score

    return {
        "prompt": prompt,
        "scores": scores,
        "predictions": predictions,
        "actuals": actuals,
        "num_samples": len(dataset)
    }


def _generate_summary(
        details: List[Dict[str, Any]], metrics: List[SimpleMetric]) -> Dict[str, Any]:
    """Generate summary statistics across all prompts."""
    summary = {"metrics": {}}

    for metric in metrics:
        scores = [d["scores"][metric.name] for d in details]
        summary["metrics"][metric.name] = {
            "mean": sum(scores) / len(scores),
            "min": min(scores),
            "max": max(scores),
            "range": max(scores) - min(scores)
        }

    return summary


def _save_results(results: Dict[str, Any],
                  output_dir: str, verbose: bool) -> None:
    """Save results to output directory."""
    import json
    from datetime import datetime

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = output_path / f"optimization_results_{timestamp}.json"

    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    if verbose:
        print(f"💾 Results saved to {results_file}")


def _print_summary(results: Dict[str, Any]) -> None:
    """Print a summary of results."""
    print("\n" + "=" * 50)
    print("🏆 OPTIMIZATION RESULTS")
    print("=" * 50)

    print(f"\nBest Prompt: {results['best_prompt']}")
    print(f"Best Score: {results['best_score']:.4f}")

    print(f"\nEvaluated {len(results['prompts'])} prompt variants")

    # Show metric comparison
    if results['details']:
        print("\nMetric Comparison:")
        for metric_name in results['details'][0]['scores'].keys():
            scores = [d['scores'][metric_name] for d in results['details']]
            print(f"  {metric_name}: {min(scores):.3f} - {max(scores):.3f}")
