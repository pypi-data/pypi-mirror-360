"""
Meta-evaluation system for EvalX.

This module provides tools for evaluating the quality of evaluation metrics themselves,
including reliability, validity, bias assessment, and interpretability analysis.
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from scipy import stats
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod

from ..core.base import BaseMetric
from ..core.types import EvaluationInput, MetricResult, EvaluationResult


@dataclass
class MetricQualityReport:
    """Comprehensive report on metric quality."""
    metric_name: str
    reliability: float  # 0-1, consistency across evaluations
    validity: float     # 0-1, correlation with ground truth
    bias: float        # 0-1, fairness across groups (lower is better)
    interpretability: float  # 0-1, how well humans understand the metric
    computational_efficiency: float  # 0-1, speed and resource usage
    
    # Detailed breakdowns
    reliability_details: Dict[str, float]
    validity_details: Dict[str, float]
    bias_details: Dict[str, Any]
    interpretability_details: Dict[str, Any]
    efficiency_details: Dict[str, float]
    
    overall_quality: float  # Weighted combination of all factors
    
    def __post_init__(self):
        """Calculate overall quality score."""
        if self.overall_quality == 0:  # Not set manually
            self.overall_quality = (
                self.reliability * 0.25 +
                self.validity * 0.30 +
                (1 - self.bias) * 0.20 +  # Lower bias is better
                self.interpretability * 0.15 +
                self.computational_efficiency * 0.10
            )


class MetaEvaluator:
    """Evaluates the quality of evaluation metrics themselves."""
    
    def __init__(self, confidence_level: float = 0.95):
        self.confidence_level = confidence_level
    
    def evaluate_metric_quality(
        self,
        metric: BaseMetric,
        evaluation_data: List[EvaluationInput],
        ground_truth: Optional[List[float]] = None,
        human_judgments: Optional[List[float]] = None,
        demographic_groups: Optional[List[str]] = None
    ) -> MetricQualityReport:
        """
        Comprehensive evaluation of metric quality.
        
        Args:
            metric: The metric to evaluate
            evaluation_data: Data to evaluate the metric on
            ground_truth: True scores if available
            human_judgments: Human expert judgments if available
            demographic_groups: Group labels for bias assessment
            
        Returns:
            Comprehensive quality report
        """
        # Get metric scores
        metric_scores = self._get_metric_scores(metric, evaluation_data)
        
        # Assess reliability
        reliability, reliability_details = self._assess_reliability(
            metric, evaluation_data, metric_scores
        )
        
        # Assess validity
        validity, validity_details = self._assess_validity(
            metric_scores, ground_truth, human_judgments
        )
        
        # Assess bias
        bias, bias_details = self._assess_bias(
            metric_scores, demographic_groups
        )
        
        # Assess interpretability
        interpretability, interpretability_details = self._assess_interpretability(
            metric, metric_scores
        )
        
        # Assess computational efficiency
        efficiency, efficiency_details = self._assess_efficiency(
            metric, evaluation_data
        )
        
        return MetricQualityReport(
            metric_name=metric.name,
            reliability=reliability,
            validity=validity,
            bias=bias,
            interpretability=interpretability,
            computational_efficiency=efficiency,
            reliability_details=reliability_details,
            validity_details=validity_details,
            bias_details=bias_details,
            interpretability_details=interpretability_details,
            efficiency_details=efficiency_details,
            overall_quality=0  # Will be calculated in __post_init__
        )
    
    def _get_metric_scores(
        self, 
        metric: BaseMetric, 
        evaluation_data: List[EvaluationInput]
    ) -> List[float]:
        """Get metric scores for all evaluation data."""
        scores = []
        for data in evaluation_data:
            try:
                result = metric.evaluate(data)
                score = result.numeric_value if result.numeric_value is not None else 0.0
                scores.append(score)
            except Exception:
                scores.append(0.0)  # Handle errors gracefully
        return scores
    
    def _assess_reliability(
        self,
        metric: BaseMetric,
        evaluation_data: List[EvaluationInput],
        original_scores: List[float]
    ) -> Tuple[float, Dict[str, float]]:
        """Assess metric reliability through test-retest and internal consistency."""
        
        # Test-retest reliability (run metric multiple times)
        test_retest_scores = []
        for _ in range(3):  # Run 3 times
            scores = self._get_metric_scores(metric, evaluation_data)
            test_retest_scores.append(scores)
        
        # Calculate test-retest correlation
        if len(test_retest_scores) >= 2:
            correlations = []
            for i in range(len(test_retest_scores)):
                for j in range(i + 1, len(test_retest_scores)):
                    corr, _ = stats.pearsonr(test_retest_scores[i], test_retest_scores[j])
                    if not np.isnan(corr):
                        correlations.append(corr)
            
            test_retest_reliability = np.mean(correlations) if correlations else 0.0
        else:
            test_retest_reliability = 0.0
        
        # Internal consistency (variance of scores)
        score_variance = np.var(original_scores)
        score_range = np.max(original_scores) - np.min(original_scores)
        consistency_score = 1.0 - (score_variance / (score_range + 1e-8))
        consistency_score = max(0.0, min(1.0, consistency_score))
        
        # Combine reliability measures
        overall_reliability = (test_retest_reliability * 0.7 + consistency_score * 0.3)
        
        details = {
            "test_retest_reliability": test_retest_reliability,
            "internal_consistency": consistency_score,
            "score_variance": score_variance,
            "score_range": score_range,
            "num_correlations": len(correlations) if 'correlations' in locals() else 0
        }
        
        return overall_reliability, details
    
    def _assess_validity(
        self,
        metric_scores: List[float],
        ground_truth: Optional[List[float]] = None,
        human_judgments: Optional[List[float]] = None
    ) -> Tuple[float, Dict[str, float]]:
        """Assess metric validity against ground truth and human judgments."""
        
        validity_scores = []
        details = {}
        
        # Criterion validity (correlation with ground truth)
        if ground_truth is not None and len(ground_truth) == len(metric_scores):
            criterion_validity, p_value = stats.pearsonr(metric_scores, ground_truth)
            if not np.isnan(criterion_validity):
                validity_scores.append(abs(criterion_validity))
                details["criterion_validity"] = criterion_validity
                details["criterion_p_value"] = p_value
        
        # Concurrent validity (correlation with human judgments)
        if human_judgments is not None and len(human_judgments) == len(metric_scores):
            concurrent_validity, p_value = stats.pearsonr(metric_scores, human_judgments)
            if not np.isnan(concurrent_validity):
                validity_scores.append(abs(concurrent_validity))
                details["concurrent_validity"] = concurrent_validity
                details["concurrent_p_value"] = p_value
        
        # Construct validity (factor analysis would go here in full implementation)
        # For now, use score distribution properties
        score_distribution_validity = self._assess_score_distribution(metric_scores)
        validity_scores.append(score_distribution_validity)
        details["distribution_validity"] = score_distribution_validity
        
        # Overall validity
        overall_validity = np.mean(validity_scores) if validity_scores else 0.0
        
        return overall_validity, details
    
    def _assess_bias(
        self,
        metric_scores: List[float],
        demographic_groups: Optional[List[str]] = None
    ) -> Tuple[float, Dict[str, Any]]:
        """Assess metric bias across demographic groups."""
        
        if demographic_groups is None or len(demographic_groups) != len(metric_scores):
            return 0.0, {"message": "No demographic data provided"}
        
        # Group scores by demographics
        group_scores = {}
        for score, group in zip(metric_scores, demographic_groups):
            if group not in group_scores:
                group_scores[group] = []
            group_scores[group].append(score)
        
        if len(group_scores) < 2:
            return 0.0, {"message": "Need at least 2 groups for bias assessment"}
        
        # Calculate bias metrics
        group_means = {group: np.mean(scores) for group, scores in group_scores.items()}
        group_stds = {group: np.std(scores) for group, scores in group_scores.items()}
        
        # Demographic parity (difference in means)
        mean_values = list(group_means.values())
        mean_difference = max(mean_values) - min(mean_values)
        max_possible_difference = 1.0  # Assuming scores are 0-1
        demographic_parity_bias = mean_difference / max_possible_difference
        
        # Equalized odds (difference in standard deviations)
        std_values = list(group_stds.values())
        std_difference = max(std_values) - min(std_values)
        equalized_odds_bias = std_difference / (np.mean(std_values) + 1e-8)
        
        # Statistical significance test
        group_names = list(group_scores.keys())
        if len(group_names) == 2:
            # Two-sample t-test
            t_stat, p_value = stats.ttest_ind(
                group_scores[group_names[0]], 
                group_scores[group_names[1]]
            )
            statistical_significance = p_value < 0.05
        else:
            # One-way ANOVA
            f_stat, p_value = stats.f_oneway(*group_scores.values())
            statistical_significance = p_value < 0.05
        
        # Overall bias (higher means more biased)
        overall_bias = (demographic_parity_bias + equalized_odds_bias) / 2
        
        details = {
            "group_means": group_means,
            "group_stds": group_stds,
            "demographic_parity_bias": demographic_parity_bias,
            "equalized_odds_bias": equalized_odds_bias,
            "statistical_significance": statistical_significance,
            "p_value": p_value,
            "num_groups": len(group_scores)
        }
        
        return overall_bias, details
    
    def _assess_interpretability(
        self,
        metric: BaseMetric,
        metric_scores: List[float]
    ) -> Tuple[float, Dict[str, Any]]:
        """Assess how interpretable the metric is."""
        
        interpretability_factors = []
        details = {}
        
        # Description clarity (length and complexity of description)
        description = metric.description
        desc_length = len(description.split())
        desc_complexity = len([word for word in description.split() if len(word) > 7])
        
        # Shorter, simpler descriptions are more interpretable
        length_score = max(0.0, 1.0 - (desc_length - 10) / 50)  # Optimal around 10 words
        complexity_score = max(0.0, 1.0 - desc_complexity / 10)
        
        interpretability_factors.append(length_score)
        interpretability_factors.append(complexity_score)
        
        details["description_length"] = desc_length
        details["description_complexity"] = desc_complexity
        details["length_score"] = length_score
        details["complexity_score"] = complexity_score
        
        # Score range and distribution
        score_range = max(metric_scores) - min(metric_scores)
        score_std = np.std(metric_scores)
        
        # Good interpretability means reasonable range and distribution
        range_score = min(1.0, score_range / 1.0)  # Assume 0-1 is ideal range
        distribution_score = min(1.0, score_std / 0.3)  # Some variance is good
        
        interpretability_factors.append(range_score)
        interpretability_factors.append(distribution_score)
        
        details["score_range"] = score_range
        details["score_std"] = score_std
        details["range_score"] = range_score
        details["distribution_score"] = distribution_score
        
        # Metric name clarity
        name_clarity = 1.0 - (len(metric.name.split('_')) - 1) * 0.1  # Prefer simple names
        name_clarity = max(0.0, name_clarity)
        
        interpretability_factors.append(name_clarity)
        details["name_clarity"] = name_clarity
        
        # Overall interpretability
        overall_interpretability = np.mean(interpretability_factors)
        
        return overall_interpretability, details
    
    def _assess_efficiency(
        self,
        metric: BaseMetric,
        evaluation_data: List[EvaluationInput]
    ) -> Tuple[float, Dict[str, float]]:
        """Assess computational efficiency of the metric."""
        
        import time
        
        # Time a small batch
        sample_size = min(10, len(evaluation_data))
        sample_data = evaluation_data[:sample_size]
        
        # Single evaluation timing
        start_time = time.time()
        for data in sample_data:
            try:
                metric.evaluate(data)
            except Exception:
                pass  # Handle errors gracefully
        single_eval_time = (time.time() - start_time) / sample_size
        
        # Batch evaluation timing
        start_time = time.time()
        try:
            metric.evaluate_batch(sample_data)
        except Exception:
            pass
        batch_eval_time = (time.time() - start_time) / sample_size
        
        # Efficiency scores (lower time is better)
        single_efficiency = max(0.0, 1.0 - single_eval_time / 1.0)  # 1 second is poor
        batch_efficiency = max(0.0, 1.0 - batch_eval_time / 1.0)
        
        # Memory usage (simplified)
        memory_efficiency = 0.8  # Placeholder - would need actual memory profiling
        
        overall_efficiency = (single_efficiency + batch_efficiency + memory_efficiency) / 3
        
        details = {
            "single_eval_time": single_eval_time,
            "batch_eval_time": batch_eval_time,
            "single_efficiency": single_efficiency,
            "batch_efficiency": batch_efficiency,
            "memory_efficiency": memory_efficiency,
            "sample_size": sample_size
        }
        
        return overall_efficiency, details
    
    def _assess_score_distribution(self, scores: List[float]) -> float:
        """Assess whether score distribution is reasonable."""
        
        if len(scores) < 2:
            return 0.0
        
        # Check for reasonable variance
        score_std = np.std(scores)
        if score_std < 0.01:  # Too little variance
            return 0.3
        elif score_std > 0.5:  # Too much variance
            return 0.7
        else:
            return 1.0  # Good variance
    
    def compare_metrics(
        self,
        metrics: List[BaseMetric],
        evaluation_data: List[EvaluationInput],
        ground_truth: Optional[List[float]] = None,
        human_judgments: Optional[List[float]] = None
    ) -> Dict[str, MetricQualityReport]:
        """Compare multiple metrics and return quality reports."""
        
        reports = {}
        for metric in metrics:
            report = self.evaluate_metric_quality(
                metric, evaluation_data, ground_truth, human_judgments
            )
            reports[metric.name] = report
        
        return reports
    
    def generate_quality_ranking(
        self,
        quality_reports: Dict[str, MetricQualityReport]
    ) -> List[Tuple[str, float]]:
        """Generate ranking of metrics by overall quality."""
        
        rankings = [
            (name, report.overall_quality)
            for name, report in quality_reports.items()
        ]
        
        # Sort by quality (descending)
        rankings.sort(key=lambda x: x[1], reverse=True)
        
        return rankings


class AdaptiveMetricSelector:
    """Selects optimal metrics based on meta-evaluation results."""
    
    def __init__(self, meta_evaluator: MetaEvaluator):
        self.meta_evaluator = meta_evaluator
    
    def select_optimal_metrics(
        self,
        candidate_metrics: List[BaseMetric],
        evaluation_data: List[EvaluationInput],
        selection_criteria: Dict[str, float] = None,
        max_metrics: int = 5
    ) -> List[BaseMetric]:
        """
        Select optimal metrics based on quality assessment.
        
        Args:
            candidate_metrics: List of metrics to choose from
            evaluation_data: Data to evaluate metrics on
            selection_criteria: Weights for different quality aspects
            max_metrics: Maximum number of metrics to select
            
        Returns:
            Selected metrics ordered by quality
        """
        
        if selection_criteria is None:
            selection_criteria = {
                "reliability": 0.25,
                "validity": 0.30,
                "bias": 0.20,  # Lower bias is better
                "interpretability": 0.15,
                "efficiency": 0.10
            }
        
        # Evaluate all metrics
        quality_reports = self.meta_evaluator.compare_metrics(
            candidate_metrics, evaluation_data
        )
        
        # Calculate custom scores based on criteria
        metric_scores = []
        for metric in candidate_metrics:
            report = quality_reports[metric.name]
            
            custom_score = (
                report.reliability * selection_criteria["reliability"] +
                report.validity * selection_criteria["validity"] +
                (1 - report.bias) * selection_criteria["bias"] +  # Lower bias is better
                report.interpretability * selection_criteria["interpretability"] +
                report.computational_efficiency * selection_criteria["efficiency"]
            )
            
            metric_scores.append((metric, custom_score))
        
        # Sort by custom score
        metric_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top metrics
        selected_metrics = [metric for metric, _ in metric_scores[:max_metrics]]
        
        return selected_metrics


# Export meta-evaluation components
__all__ = [
    "MetricQualityReport",
    "MetaEvaluator",
    "AdaptiveMetricSelector",
] 