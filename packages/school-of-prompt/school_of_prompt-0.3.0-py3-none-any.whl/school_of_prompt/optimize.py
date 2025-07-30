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
    data: Union[str, pd.DataFrame, SimpleDataSource, Dict[str, str]],
    task: Union[str, SimpleTask],
    prompts: Union[str, List[str], Path],
    model: Union[str, Dict[str, Any], SimpleModel] = "gpt-3.5-turbo",
    metrics: Optional[Union[str, List[str], List[SimpleMetric]]] = None,
    api_key: Optional[str] = None,
    sample_size: Optional[int] = None,
    random_seed: int = 42,
    output_dir: Optional[str] = None,
    verbose: bool = True,
    # Enhanced parameters
    config: Optional[Union[str, Dict[str, Any]]] = None,
    sampling_strategy: str = "random",
    enrichers: Optional[List[str]] = None,
    preprocessors: Optional[List[str]] = None,
    cross_validation: bool = False,
    k_fold: int = 5,
    cache_enabled: bool = True,
    batch_size: int = 100,
    parallel_evaluation: bool = False,
    comprehensive_analysis: bool = False
) -> Dict[str, Any]:
    """
    Optimize prompts with minimal setup required.

    Args:
        data: Path to CSV/JSONL file, DataFrame, custom data source, or dict of datasets
        task: Task description (e.g., "classify sentiment") or custom task
        prompts: List of prompt variants or path to file containing prompts
        model: Model name, config dict, or custom model instance
        metrics: Metrics to evaluate (auto-selected if None)
        api_key: API key (or set OPENAI_API_KEY env var)
        sample_size: Limit evaluation to N samples
        random_seed: Random seed for reproducibility
        output_dir: Directory to save results (optional)
        verbose: Print progress information
        
        # Enhanced parameters
        config: Path to YAML config file or config dict (overrides other params)
        sampling_strategy: "random", "stratified", or "balanced"
        enrichers: List of data enrichment functions to apply
        preprocessors: List of data preprocessing functions to apply
        cross_validation: Whether to use cross-validation
        k_fold: Number of folds for cross-validation
        cache_enabled: Enable intelligent caching
        batch_size: Batch size for processing
        parallel_evaluation: Use parallel processing
        comprehensive_analysis: Include detailed statistical analysis

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

    # Handle configuration file if provided
    if config:
        from .core.config import FrameworkConfig, load_config_from_file
        
        if isinstance(config, str):
            config_obj = load_config_from_file(config)
        else:
            config_obj = FrameworkConfig(config_dict=config)
        
        # Override parameters with config values
        data = data or config_obj.get_datasets()
        task = task or config_obj.task_type
        metrics = metrics or config_obj.evaluation_metrics
        sample_size = sample_size or config_obj.sample_size
        sampling_strategy = config_obj.sampling_strategy
        cross_validation = config_obj.cross_validation
        k_fold = config_obj.k_fold
        cache_enabled = config_obj.cache_enabled
        batch_size = config_obj.batch_size
        parallel_evaluation = config_obj.parallel_evaluation
        output_dir = output_dir or config_obj.output_dir
        
        if verbose:
            print(f"📋 Loaded configuration: {config_obj.task_name}")

    # Handle API key
    if api_key is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "API key required. Set OPENAI_API_KEY env var or pass api_key parameter.")

    # Configure caching
    if cache_enabled:
        from .production.cache import configure_global_cache
        configure_global_cache(enabled=True)

    # Auto-load data with enhanced features
    if verbose:
        print("📁 Loading data...")
    dataset = auto_load_data(
        data,
        sample_size=sample_size,
        random_seed=random_seed,
        sampling_strategy=sampling_strategy,
        enrichers=enrichers,
        preprocessors=preprocessors
    )

    # Handle multi-dataset case
    if isinstance(dataset, dict):
        if verbose:
            print(f"📊 Multi-dataset mode: {list(dataset.keys())}")
        
        return _run_multi_dataset_optimization(
            datasets=dataset,
            task=task,
            prompts=prompts,
            model=model,
            metrics=metrics,
            api_key=api_key,
            cross_validation=cross_validation,
            k_fold=k_fold,
            batch_size=batch_size,
            parallel_evaluation=parallel_evaluation,
            comprehensive_analysis=comprehensive_analysis,
            output_dir=output_dir,
            verbose=verbose
        )

    # Single dataset case - detect task
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

    # Handle cross-validation
    if cross_validation:
        if verbose:
            print(f"🔄 Running {k_fold}-fold cross-validation...")
        results = _run_cross_validation(
            dataset=dataset,
            task=task_obj,
            prompts=prompt_variants,
            model=model_obj,
            metrics=metrics_list,
            k_fold=k_fold,
            batch_size=batch_size,
            parallel_evaluation=parallel_evaluation,
            verbose=verbose
        )
    else:
        # Standard optimization
        if verbose:
            print("🚀 Running optimization...")
        results = _run_optimization(
            dataset=dataset,
            task=task_obj,
            prompts=prompt_variants,
            model=model_obj,
            metrics=metrics_list,
            batch_size=batch_size,
            parallel_evaluation=parallel_evaluation,
            verbose=verbose
        )

    # Add comprehensive analysis if requested
    if comprehensive_analysis:
        if verbose:
            print("🔍 Running comprehensive analysis...")
        results = _add_comprehensive_analysis(results)

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
    batch_size: int = 100,
    parallel_evaluation: bool = False,
    verbose: bool = True
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


def _run_cross_validation(
    dataset: List[Dict[str, Any]],
    task: SimpleTask,
    prompts: List[str],
    model: SimpleModel,
    metrics: List[SimpleMetric],
    k_fold: int = 5,
    batch_size: int = 100,
    parallel_evaluation: bool = False,
    verbose: bool = True
) -> Dict[str, Any]:
    """Run cross-validation evaluation."""
    
    # Split dataset into k folds
    import random
    shuffled_data = dataset.copy()
    random.shuffle(shuffled_data)
    
    fold_size = len(dataset) // k_fold
    folds = []
    for i in range(k_fold):
        start_idx = i * fold_size
        end_idx = start_idx + fold_size if i < k_fold - 1 else len(dataset)
        folds.append(shuffled_data[start_idx:end_idx])
    
    cv_results = {
        "prompts": {},
        "best_prompt": None,
        "best_score": None,
        "summary": {},
        "details": [],
        "cross_validation": {
            "k_fold": k_fold,
            "fold_results": [],
            "mean_scores": {},
            "std_scores": {}
        }
    }
    
    # Run evaluation on each fold
    all_fold_scores = {prompt: [] for prompt in prompts}
    
    for fold_idx in range(k_fold):
        if verbose:
            print(f"🔄 Cross-validation fold {fold_idx + 1}/{k_fold}")
        
        # Use current fold as test, others as train (though we don't train here)
        test_fold = folds[fold_idx]
        
        fold_results = _run_optimization(
            dataset=test_fold,
            task=task,
            prompts=prompts,
            model=model,
            metrics=metrics,
            batch_size=batch_size,
            parallel_evaluation=parallel_evaluation,
            verbose=False
        )
        
        cv_results["cross_validation"]["fold_results"].append(fold_results)
        
        # Collect scores for each prompt
        for i, prompt in enumerate(prompts):
            prompt_key = f"prompt_{i + 1}"
            if prompt_key in fold_results["prompts"]:
                primary_metric = metrics[0].name
                score = fold_results["prompts"][prompt_key]["scores"][primary_metric]
                all_fold_scores[prompt].append(score)
    
    # Calculate mean and std across folds
    import statistics
    
    best_mean_score = 0
    best_prompt = None
    
    for i, prompt in enumerate(prompts):
        prompt_key = f"prompt_{i + 1}"
        scores = all_fold_scores[prompt]
        
        if scores:
            mean_score = statistics.mean(scores)
            std_score = statistics.stdev(scores) if len(scores) > 1 else 0
            
            cv_results["prompts"][prompt_key] = {
                "prompt": prompt,
                "mean_score": mean_score,
                "std_score": std_score,
                "fold_scores": scores
            }
            
            if mean_score > best_mean_score:
                best_mean_score = mean_score
                best_prompt = prompt
    
    cv_results["best_prompt"] = best_prompt
    cv_results["best_score"] = best_mean_score
    
    # Calculate overall statistics
    for metric in metrics:
        metric_scores = []
        for fold_result in cv_results["cross_validation"]["fold_results"]:
            for prompt_result in fold_result["details"]:
                metric_scores.append(prompt_result["scores"][metric.name])
        
        if metric_scores:
            cv_results["cross_validation"]["mean_scores"][metric.name] = statistics.mean(metric_scores)
            cv_results["cross_validation"]["std_scores"][metric.name] = statistics.stdev(metric_scores) if len(metric_scores) > 1 else 0
    
    return cv_results


def _run_multi_dataset_optimization(
    datasets: Dict[str, List[Dict[str, Any]]],
    task: Union[str, SimpleTask],
    prompts: Union[str, List[str], Path],
    model: Union[str, Dict[str, Any], SimpleModel],
    metrics: Optional[Union[str, List[str], List[SimpleMetric]]],
    api_key: str,
    cross_validation: bool = False,
    k_fold: int = 5,
    batch_size: int = 100,
    parallel_evaluation: bool = False,
    comprehensive_analysis: bool = False,
    output_dir: Optional[str] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """Run optimization across multiple datasets."""
    
    multi_results = {
        "datasets": {},
        "aggregate_results": {},
        "best_overall_prompt": None,
        "best_overall_score": None
    }
    
    # Process each dataset
    for dataset_name, dataset in datasets.items():
        if verbose:
            print(f"\n📊 Processing dataset: {dataset_name}")
        
        # Run optimization on this dataset
        dataset_results = optimize(
            data=dataset,
            task=task,
            prompts=prompts,
            model=model,
            metrics=metrics,
            api_key=api_key,
            cross_validation=cross_validation,
            k_fold=k_fold,
            batch_size=batch_size,
            parallel_evaluation=parallel_evaluation,
            comprehensive_analysis=comprehensive_analysis,
            verbose=verbose
        )
        
        multi_results["datasets"][dataset_name] = dataset_results
    
    # Aggregate results across datasets
    if multi_results["datasets"]:
        multi_results["aggregate_results"] = _aggregate_multi_dataset_results(
            multi_results["datasets"]
        )
        
        # Find best overall prompt
        best_score = 0
        best_prompt = None
        
        for dataset_name, results in multi_results["datasets"].items():
            if results["best_score"] and results["best_score"] > best_score:
                best_score = results["best_score"]
                best_prompt = results["best_prompt"]
        
        multi_results["best_overall_prompt"] = best_prompt
        multi_results["best_overall_score"] = best_score
    
    return multi_results


def _aggregate_multi_dataset_results(dataset_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate results across multiple datasets."""
    
    aggregated = {
        "mean_scores_by_prompt": {},
        "performance_by_dataset": {},
        "consistency_scores": {}
    }
    
    # Get all prompts and metrics
    first_result = list(dataset_results.values())[0]
    all_prompts = list(first_result["prompts"].keys())
    
    if first_result["details"]:
        all_metrics = list(first_result["details"][0]["scores"].keys())
    else:
        all_metrics = []
    
    # Calculate mean scores across datasets for each prompt
    for prompt_key in all_prompts:
        aggregated["mean_scores_by_prompt"][prompt_key] = {}
        
        for metric in all_metrics:
            scores = []
            for dataset_name, results in dataset_results.items():
                if prompt_key in results["prompts"]:
                    score = results["prompts"][prompt_key]["scores"][metric]
                    scores.append(score)
            
            if scores:
                import statistics
                aggregated["mean_scores_by_prompt"][prompt_key][metric] = {
                    "mean": statistics.mean(scores),
                    "std": statistics.stdev(scores) if len(scores) > 1 else 0,
                    "scores": scores
                }
    
    # Performance by dataset
    for dataset_name, results in dataset_results.items():
        aggregated["performance_by_dataset"][dataset_name] = {
            "best_score": results["best_score"],
            "best_prompt": results["best_prompt"]
        }
    
    return aggregated


def _add_comprehensive_analysis(results: Dict[str, Any]) -> Dict[str, Any]:
    """Add comprehensive statistical analysis to results."""
    
    # Create detailed data for analysis
    detailed_data = []
    for prompt_result in results["details"]:
        for i, (pred, actual) in enumerate(zip(prompt_result["predictions"], prompt_result["actuals"])):
            detailed_data.append({
                "prompt": prompt_result["prompt"],
                "prediction": pred,
                "actual": actual,
                "sample_index": i
            })
    
    # Run comprehensive analysis
    from .analysis.results_analyzer import ResultsAnalyzer
    analyzer = ResultsAnalyzer()
    comprehensive_results = analyzer.analyze_results(results, detailed_data)
    
    # Add to results
    results["comprehensive_analysis"] = {
        "statistical_significance": {
            test_name: {
                "statistic": test.statistic,
                "p_value": test.p_value,
                "significant": test.significant,
                "interpretation": test.interpretation
            }
            for test_name, test in comprehensive_results.statistical_significance.items()
        },
        "error_analysis": {
            "total_errors": comprehensive_results.error_analysis.total_errors,
            "error_rate": comprehensive_results.error_analysis.error_rate,
            "common_errors": comprehensive_results.error_analysis.common_errors[:5],
            "error_patterns": comprehensive_results.error_analysis.error_patterns
        },
        "performance_breakdown": {
            "overall_score": comprehensive_results.performance_breakdown.overall_score,
            "by_category": comprehensive_results.performance_breakdown.by_category,
            "by_difficulty": comprehensive_results.performance_breakdown.by_difficulty,
            "confidence_intervals": comprehensive_results.performance_breakdown.confidence_intervals
        },
        "recommendations": comprehensive_results.recommendations,
        "prompt_comparisons": [
            {
                "prompt1": comp.prompt1[:50] + "..." if len(comp.prompt1) > 50 else comp.prompt1,
                "prompt2": comp.prompt2[:50] + "..." if len(comp.prompt2) > 50 else comp.prompt2,
                "improvement_percentage": comp.improvement_percentage,
                "significant": comp.statistical_test.significant if comp.statistical_test else False
            }
            for comp in comprehensive_results.prompt_comparisons[:5]  # Top 5 comparisons
        ]
    }
    
    return results
