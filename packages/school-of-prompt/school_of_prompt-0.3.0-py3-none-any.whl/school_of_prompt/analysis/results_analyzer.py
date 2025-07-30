"""
Comprehensive results analysis with statistical significance testing.
Enhanced analysis capabilities for prompt optimization results.
"""

from typing import Dict, List, Any, Optional, Tuple
import statistics
import math
from dataclasses import dataclass
from ..core.simple_interfaces import SimpleMetric


@dataclass
class StatisticalTest:
    """Results of a statistical significance test."""
    test_name: str
    statistic: float
    p_value: float
    significant: bool
    confidence_level: float
    interpretation: str


@dataclass
class PromptComparison:
    """Comparison between two prompts."""
    prompt1: str
    prompt2: str
    metric: str
    score1: float
    score2: float
    improvement: float
    improvement_percentage: float
    statistical_test: Optional[StatisticalTest] = None


@dataclass
class ErrorAnalysis:
    """Analysis of prediction errors."""
    total_errors: int
    error_rate: float
    error_distribution: Dict[str, int]
    common_errors: List[Tuple[str, str, int]]  # (predicted, actual, count)
    error_patterns: Dict[str, Any]


@dataclass
class PerformanceBreakdown:
    """Detailed performance breakdown by categories."""
    overall_score: float
    by_category: Dict[str, float]
    by_difficulty: Dict[str, float]
    by_length: Dict[str, float]
    confidence_intervals: Dict[str, Tuple[float, float]]


@dataclass
class ComprehensiveResults:
    """Comprehensive analysis results."""
    summary: Dict[str, Any]
    prompt_comparisons: List[PromptComparison]
    error_analysis: ErrorAnalysis
    performance_breakdown: PerformanceBreakdown
    statistical_significance: Dict[str, StatisticalTest]
    recommendations: List[str]
    visualizations: Dict[str, Any]


class ResultsAnalyzer:
    """Advanced results analyzer with statistical testing."""
    
    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
    
    def analyze_results(
        self,
        results: Dict[str, Any],
        detailed_data: List[Dict[str, Any]]
    ) -> ComprehensiveResults:
        """Perform comprehensive analysis of optimization results."""
        
        # Extract basic information
        prompts_data = results.get("details", [])
        metrics_used = list(prompts_data[0]["scores"].keys()) if prompts_data else []
        
        # Perform various analyses
        summary = self._generate_enhanced_summary(results, detailed_data)
        prompt_comparisons = self._compare_prompts(prompts_data, metrics_used)
        error_analysis = self._analyze_errors(detailed_data)
        performance_breakdown = self._analyze_performance_breakdown(detailed_data)
        statistical_tests = self._perform_statistical_tests(prompts_data, metrics_used)
        recommendations = self._generate_recommendations(
            prompt_comparisons, error_analysis, performance_breakdown
        )
        visualizations = self._prepare_visualization_data(
            prompts_data, error_analysis, performance_breakdown
        )
        
        return ComprehensiveResults(
            summary=summary,
            prompt_comparisons=prompt_comparisons,
            error_analysis=error_analysis,
            performance_breakdown=performance_breakdown,
            statistical_significance=statistical_tests,
            recommendations=recommendations,
            visualizations=visualizations
        )
    
    def _generate_enhanced_summary(
        self, 
        results: Dict[str, Any], 
        detailed_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate enhanced summary with additional insights."""
        
        base_summary = results.get("summary", {})
        prompts_data = results.get("details", [])
        
        if not prompts_data:
            return base_summary
        
        # Calculate additional summary statistics
        all_scores = {}
        for prompt_result in prompts_data:
            for metric, score in prompt_result["scores"].items():
                if metric not in all_scores:
                    all_scores[metric] = []
                all_scores[metric].append(score)
        
        enhanced_summary = {
            **base_summary,
            "num_prompts_evaluated": len(prompts_data),
            "num_samples_per_prompt": prompts_data[0]["num_samples"] if prompts_data else 0,
            "total_evaluations": len(prompts_data) * (prompts_data[0]["num_samples"] if prompts_data else 0),
            "metric_statistics": {}
        }
        
        # Add detailed metric statistics
        for metric, scores in all_scores.items():
            enhanced_summary["metric_statistics"][metric] = {
                "mean": statistics.mean(scores),
                "median": statistics.median(scores),
                "std": statistics.stdev(scores) if len(scores) > 1 else 0,
                "min": min(scores),
                "max": max(scores),
                "range": max(scores) - min(scores),
                "coefficient_of_variation": (statistics.stdev(scores) / statistics.mean(scores)) if len(scores) > 1 and statistics.mean(scores) != 0 else 0
            }
        
        # Add confidence intervals for best score
        best_prompt_idx = 0
        best_score = 0
        primary_metric = list(all_scores.keys())[0] if all_scores else None
        
        if primary_metric:
            for i, prompt_result in enumerate(prompts_data):
                if prompt_result["scores"][primary_metric] > best_score:
                    best_score = prompt_result["scores"][primary_metric]
                    best_prompt_idx = i
            
            # Calculate confidence interval for best prompt
            best_predictions = prompts_data[best_prompt_idx]["predictions"]
            best_actuals = prompts_data[best_prompt_idx]["actuals"]
            
            if len(best_predictions) > 1:
                ci = self._calculate_confidence_interval(best_predictions, best_actuals, primary_metric)
                enhanced_summary["best_score_confidence_interval"] = ci
        
        return enhanced_summary
    
    def _compare_prompts(
        self, 
        prompts_data: List[Dict[str, Any]], 
        metrics: List[str]
    ) -> List[PromptComparison]:
        """Compare all pairs of prompts with statistical testing."""
        comparisons = []
        
        for i in range(len(prompts_data)):
            for j in range(i + 1, len(prompts_data)):
                prompt1_data = prompts_data[i]
                prompt2_data = prompts_data[j]
                
                for metric in metrics:
                    score1 = prompt1_data["scores"][metric]
                    score2 = prompt2_data["scores"][metric]
                    
                    improvement = score2 - score1
                    improvement_pct = (improvement / score1 * 100) if score1 != 0 else 0
                    
                    # Perform statistical test
                    stat_test = self._paired_t_test(
                        prompt1_data["predictions"],
                        prompt1_data["actuals"],
                        prompt2_data["predictions"],
                        prompt2_data["actuals"],
                        metric
                    )
                    
                    comparison = PromptComparison(
                        prompt1=prompt1_data["prompt"],
                        prompt2=prompt2_data["prompt"],
                        metric=metric,
                        score1=score1,
                        score2=score2,
                        improvement=improvement,
                        improvement_percentage=improvement_pct,
                        statistical_test=stat_test
                    )
                    
                    comparisons.append(comparison)
        
        return comparisons
    
    def _analyze_errors(self, detailed_data: List[Dict[str, Any]]) -> ErrorAnalysis:
        """Analyze prediction errors in detail."""
        if not detailed_data:
            return ErrorAnalysis(0, 0, {}, [], {})
        
        # Collect all predictions and actuals
        all_predictions = []
        all_actuals = []
        
        for item in detailed_data:
            all_predictions.append(item.get("prediction", ""))
            all_actuals.append(item.get("actual", ""))
        
        # Count errors
        errors = [(pred, actual) for pred, actual in zip(all_predictions, all_actuals) 
                 if str(pred).lower() != str(actual).lower()]
        
        total_errors = len(errors)
        error_rate = total_errors / len(all_predictions) if all_predictions else 0
        
        # Error distribution
        error_types = {}
        error_pairs = {}
        
        for pred, actual in errors:
            # Error by predicted value
            if pred not in error_types:
                error_types[pred] = 0
            error_types[pred] += 1
            
            # Error pairs (predicted -> actual)
            pair_key = f"{pred} -> {actual}"
            if pair_key not in error_pairs:
                error_pairs[pair_key] = 0
            error_pairs[pair_key] += 1
        
        # Most common errors
        common_errors = sorted(
            [(pred, actual, count) for (pred, actual), count in 
             [(pair.split(" -> ")[0], pair.split(" -> ")[1], count) 
              for pair, count in error_pairs.items()]],
            key=lambda x: x[2],
            reverse=True
        )[:10]  # Top 10 most common errors
        
        # Error patterns analysis
        error_patterns = self._analyze_error_patterns(errors, all_predictions, all_actuals)
        
        return ErrorAnalysis(
            total_errors=total_errors,
            error_rate=error_rate,
            error_distribution=error_types,
            common_errors=common_errors,
            error_patterns=error_patterns
        )
    
    def _analyze_error_patterns(
        self, 
        errors: List[Tuple[str, str]], 
        all_predictions: List[str], 
        all_actuals: List[str]
    ) -> Dict[str, Any]:
        """Analyze patterns in prediction errors."""
        patterns = {}
        
        # Length-based error analysis
        length_errors = {}
        for pred, actual in errors:
            pred_len = len(str(pred))
            if pred_len not in length_errors:
                length_errors[pred_len] = 0
            length_errors[pred_len] += 1
        
        patterns["errors_by_prediction_length"] = length_errors
        
        # Numeric prediction analysis (if applicable)
        try:
            numeric_predictions = [float(p) for p in all_predictions if str(p).replace('.', '').replace('-', '').isdigit()]
            numeric_actuals = [float(a) for a in all_actuals if str(a).replace('.', '').replace('-', '').isdigit()]
            
            if numeric_predictions and numeric_actuals:
                # Bias analysis
                prediction_errors = [p - a for p, a in zip(numeric_predictions, numeric_actuals)]
                patterns["mean_prediction_bias"] = statistics.mean(prediction_errors)
                patterns["prediction_bias_std"] = statistics.stdev(prediction_errors) if len(prediction_errors) > 1 else 0
                
                # Overestimation vs underestimation
                overestimations = [e for e in prediction_errors if e > 0]
                underestimations = [e for e in prediction_errors if e < 0]
                
                patterns["overestimation_rate"] = len(overestimations) / len(prediction_errors)
                patterns["underestimation_rate"] = len(underestimations) / len(prediction_errors)
                patterns["perfect_predictions"] = len([e for e in prediction_errors if e == 0])
        
        except (ValueError, TypeError):
            # Non-numeric predictions
            pass
        
        return patterns
    
    def _analyze_performance_breakdown(self, detailed_data: List[Dict[str, Any]]) -> PerformanceBreakdown:
        """Analyze performance by different categories."""
        if not detailed_data:
            return PerformanceBreakdown(0, {}, {}, {}, {})
        
        # Overall performance
        correct_predictions = sum(1 for item in detailed_data 
                                if str(item.get("prediction", "")).lower() == str(item.get("actual", "")).lower())
        overall_score = correct_predictions / len(detailed_data)
        
        # Performance by category (if category information is available)
        by_category = {}
        category_field = None
        for field in ["category", "class", "type", "domain"]:
            if field in detailed_data[0]:
                category_field = field
                break
        
        if category_field:
            category_groups = {}
            for item in detailed_data:
                category = item[category_field]
                if category not in category_groups:
                    category_groups[category] = []
                category_groups[category].append(item)
            
            for category, items in category_groups.items():
                correct = sum(1 for item in items 
                            if str(item.get("prediction", "")).lower() == str(item.get("actual", "")).lower())
                by_category[category] = correct / len(items) if items else 0
        
        # Performance by difficulty (text length as proxy)
        by_difficulty = {}
        for item in detailed_data:
            # Use text length as difficulty proxy
            text_content = ""
            for field in ["text", "content", "description", "title"]:
                if field in item:
                    text_content = str(item[field])
                    break
            
            if text_content:
                length = len(text_content.split())
                if length < 10:
                    difficulty = "easy"
                elif length < 30:
                    difficulty = "medium"
                else:
                    difficulty = "hard"
                
                if difficulty not in by_difficulty:
                    by_difficulty[difficulty] = []
                by_difficulty[difficulty].append(item)
        
        # Calculate difficulty performance
        difficulty_scores = {}
        for difficulty, items in by_difficulty.items():
            correct = sum(1 for item in items 
                        if str(item.get("prediction", "")).lower() == str(item.get("actual", "")).lower())
            difficulty_scores[difficulty] = correct / len(items) if items else 0
        
        # Performance by text length ranges
        by_length = {}
        length_ranges = [(0, 50), (50, 100), (100, 200), (200, float('inf'))]
        
        for start, end in length_ranges:
            range_key = f"{start}-{end if end != float('inf') else '∞'}"
            range_items = []
            
            for item in detailed_data:
                text_content = ""
                for field in ["text", "content", "description", "title"]:
                    if field in item:
                        text_content = str(item[field])
                        break
                
                if text_content:
                    char_length = len(text_content)
                    if start <= char_length < end:
                        range_items.append(item)
            
            if range_items:
                correct = sum(1 for item in range_items 
                            if str(item.get("prediction", "")).lower() == str(item.get("actual", "")).lower())
                by_length[range_key] = correct / len(range_items)
        
        # Calculate confidence intervals
        confidence_intervals = {}
        for category, score in {**by_category, **difficulty_scores, **by_length}.items():
            if score > 0:
                # Simple confidence interval calculation
                n = len([item for sublist in [by_category, difficulty_scores, by_length] 
                        for category_name, items in sublist.items() if category_name == category])
                if n > 1:
                    se = math.sqrt(score * (1 - score) / n)
                    z_score = 1.96  # 95% confidence
                    margin = z_score * se
                    confidence_intervals[category] = (max(0, score - margin), min(1, score + margin))
        
        return PerformanceBreakdown(
            overall_score=overall_score,
            by_category=by_category,
            by_difficulty=difficulty_scores,
            by_length=by_length,
            confidence_intervals=confidence_intervals
        )
    
    def _perform_statistical_tests(
        self, 
        prompts_data: List[Dict[str, Any]], 
        metrics: List[str]
    ) -> Dict[str, StatisticalTest]:
        """Perform statistical significance tests."""
        tests = {}
        
        if len(prompts_data) < 2:
            return tests
        
        # Compare best vs worst for each metric
        for metric in metrics:
            scores = [(i, prompt["scores"][metric]) for i, prompt in enumerate(prompts_data)]
            scores.sort(key=lambda x: x[1])
            
            worst_idx, worst_score = scores[0]
            best_idx, best_score = scores[-1]
            
            if worst_idx != best_idx:
                # Perform t-test between best and worst
                test_result = self._paired_t_test(
                    prompts_data[worst_idx]["predictions"],
                    prompts_data[worst_idx]["actuals"],
                    prompts_data[best_idx]["predictions"],
                    prompts_data[best_idx]["actuals"],
                    metric
                )
                
                tests[f"{metric}_best_vs_worst"] = test_result
        
        return tests
    
    def _paired_t_test(
        self, 
        predictions1: List[Any], 
        actuals1: List[Any],
        predictions2: List[Any], 
        actuals2: List[Any],
        metric_name: str
    ) -> StatisticalTest:
        """Perform paired t-test between two sets of predictions."""
        
        # Calculate individual scores for each prediction
        scores1 = self._calculate_individual_scores(predictions1, actuals1, metric_name)
        scores2 = self._calculate_individual_scores(predictions2, actuals2, metric_name)
        
        if len(scores1) != len(scores2) or len(scores1) < 2:
            return StatisticalTest(
                test_name="Paired t-test",
                statistic=0,
                p_value=1.0,
                significant=False,
                confidence_level=self.confidence_level,
                interpretation="Insufficient data for statistical testing"
            )
        
        # Calculate differences
        differences = [s2 - s1 for s1, s2 in zip(scores1, scores2)]
        
        if len(set(differences)) == 1:  # All differences are the same
            return StatisticalTest(
                test_name="Paired t-test",
                statistic=0,
                p_value=1.0,
                significant=False,
                confidence_level=self.confidence_level,
                interpretation="No variation in differences"
            )
        
        # Calculate t-statistic
        mean_diff = statistics.mean(differences)
        std_diff = statistics.stdev(differences)
        n = len(differences)
        
        t_stat = mean_diff / (std_diff / math.sqrt(n))
        
        # Simple p-value approximation (for a more accurate implementation, use scipy.stats)
        # This is a rough approximation
        degrees_freedom = n - 1
        p_value = self._approximate_t_test_p_value(abs(t_stat), degrees_freedom)
        
        significant = p_value < self.alpha
        
        interpretation = self._interpret_t_test(t_stat, p_value, significant, mean_diff)
        
        return StatisticalTest(
            test_name="Paired t-test",
            statistic=t_stat,
            p_value=p_value,
            significant=significant,
            confidence_level=self.confidence_level,
            interpretation=interpretation
        )
    
    def _calculate_individual_scores(
        self, 
        predictions: List[Any], 
        actuals: List[Any], 
        metric_name: str
    ) -> List[float]:
        """Calculate individual scores for each prediction-actual pair."""
        scores = []
        
        for pred, actual in zip(predictions, actuals):
            if metric_name.lower() == "accuracy":
                score = 1.0 if str(pred).lower() == str(actual).lower() else 0.0
            elif metric_name.lower() in ["mae", "mean_absolute_error"]:
                try:
                    score = abs(float(pred) - float(actual))
                except (ValueError, TypeError):
                    score = 1.0 if str(pred).lower() == str(actual).lower() else 0.0
            elif metric_name.lower().startswith("within_"):
                try:
                    tolerance = float(metric_name.split("_")[1])
                    score = 1.0 if abs(float(pred) - float(actual)) <= tolerance else 0.0
                except (ValueError, TypeError):
                    score = 1.0 if str(pred).lower() == str(actual).lower() else 0.0
            else:
                # Default to accuracy for unknown metrics
                score = 1.0 if str(pred).lower() == str(actual).lower() else 0.0
            
            scores.append(score)
        
        return scores
    
    def _approximate_t_test_p_value(self, t_stat: float, df: int) -> float:
        """Approximate p-value for t-test (rough approximation)."""
        # Very rough approximation - in practice, use proper statistical library
        if df < 1:
            return 1.0
        
        # Simple approximation based on standard normal for large df
        if df > 30:
            # Approximate as normal distribution
            if t_stat > 2.58:
                return 0.01
            elif t_stat > 1.96:
                return 0.05
            elif t_stat > 1.645:
                return 0.10
            else:
                return 0.20
        else:
            # Conservative estimates for small samples
            if t_stat > 3.0:
                return 0.01
            elif t_stat > 2.0:
                return 0.05
            elif t_stat > 1.5:
                return 0.10
            else:
                return 0.20
    
    def _interpret_t_test(
        self, 
        t_stat: float, 
        p_value: float, 
        significant: bool, 
        mean_diff: float
    ) -> str:
        """Interpret t-test results."""
        if not significant:
            return f"No statistically significant difference (p={p_value:.3f})"
        
        direction = "improvement" if mean_diff > 0 else "degradation"
        magnitude = "large" if abs(t_stat) > 3 else "moderate" if abs(t_stat) > 2 else "small"
        
        return f"Statistically significant {direction} (p={p_value:.3f}, {magnitude} effect size)"
    
    def _calculate_confidence_interval(
        self, 
        predictions: List[Any], 
        actuals: List[Any], 
        metric_name: str
    ) -> Tuple[float, float]:
        """Calculate confidence interval for a metric."""
        scores = self._calculate_individual_scores(predictions, actuals, metric_name)
        
        if len(scores) < 2:
            return (0, 0)
        
        mean_score = statistics.mean(scores)
        std_score = statistics.stdev(scores)
        n = len(scores)
        
        # 95% confidence interval
        z_score = 1.96
        margin = z_score * (std_score / math.sqrt(n))
        
        return (max(0, mean_score - margin), min(1, mean_score + margin))
    
    def _generate_recommendations(
        self,
        prompt_comparisons: List[PromptComparison],
        error_analysis: ErrorAnalysis,
        performance_breakdown: PerformanceBreakdown
    ) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Best prompt recommendations
        if prompt_comparisons:
            best_comparison = max(prompt_comparisons, key=lambda x: x.improvement)
            if best_comparison.improvement > 0:
                recommendations.append(
                    f"Use '{best_comparison.prompt2[:50]}...' as it shows "
                    f"{best_comparison.improvement_percentage:.1f}% improvement over baseline"
                )
        
        # Error pattern recommendations
        if error_analysis.error_rate > 0.2:  # High error rate
            recommendations.append(
                f"High error rate ({error_analysis.error_rate:.1%}). "
                "Consider improving prompt clarity or adding examples."
            )
        
        if error_analysis.common_errors:
            most_common = error_analysis.common_errors[0]
            recommendations.append(
                f"Most common error: predicting '{most_common[0]}' instead of '{most_common[1]}' "
                f"({most_common[2]} times). Consider addressing this specific confusion."
            )
        
        # Performance breakdown recommendations
        if performance_breakdown.by_difficulty:
            worst_difficulty = min(performance_breakdown.by_difficulty.items(), key=lambda x: x[1])
            recommendations.append(
                f"Performance is lowest on {worst_difficulty[0]} content ({worst_difficulty[1]:.1%}). "
                "Consider specialized prompts for this difficulty level."
            )
        
        # Statistical significance recommendations
        significant_improvements = [comp for comp in prompt_comparisons 
                                  if comp.statistical_test and comp.statistical_test.significant 
                                  and comp.improvement > 0]
        
        if significant_improvements:
            recommendations.append(
                f"Found {len(significant_improvements)} statistically significant improvements. "
                "Focus on prompts with proven statistical advantage."
            )
        elif len(prompt_comparisons) > 1:
            recommendations.append(
                "No statistically significant differences found between prompts. "
                "Consider testing more diverse prompt variations."
            )
        
        return recommendations
    
    def _prepare_visualization_data(
        self,
        prompts_data: List[Dict[str, Any]],
        error_analysis: ErrorAnalysis,
        performance_breakdown: PerformanceBreakdown
    ) -> Dict[str, Any]:
        """Prepare data for visualization."""
        viz_data = {}
        
        # Performance comparison chart data
        if prompts_data:
            metrics = list(prompts_data[0]["scores"].keys())
            
            viz_data["performance_comparison"] = {
                "prompts": [f"Prompt {i+1}" for i in range(len(prompts_data))],
                "metrics": metrics,
                "scores": [[prompt["scores"][metric] for metric in metrics] 
                          for prompt in prompts_data]
            }
        
        # Error distribution chart data
        viz_data["error_distribution"] = {
            "labels": list(error_analysis.error_distribution.keys()),
            "values": list(error_analysis.error_distribution.values())
        }
        
        # Performance breakdown chart data
        viz_data["performance_breakdown"] = {
            "categories": {
                "by_category": performance_breakdown.by_category,
                "by_difficulty": performance_breakdown.by_difficulty,
                "by_length": performance_breakdown.by_length
            }
        }
        
        # Common errors chart data
        if error_analysis.common_errors:
            viz_data["common_errors"] = {
                "error_pairs": [f"{pred} → {actual}" for pred, actual, _ in error_analysis.common_errors[:5]],
                "counts": [count for _, _, count in error_analysis.common_errors[:5]]
            }
        
        return viz_data