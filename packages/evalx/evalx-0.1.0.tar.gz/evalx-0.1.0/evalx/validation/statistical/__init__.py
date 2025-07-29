"""
Statistical analysis module for evaluation results.
"""

import numpy as np
from typing import Dict, List
from scipy import stats

from ...core.types import EvaluationResult, StatisticalResult


class StatisticalAnalyzer:
    """
    Statistical analyzer for evaluation results.
    
    Provides comprehensive statistical analysis including confidence intervals,
    significance testing, effect sizes, and power analysis.
    """
    
    def __init__(self):
        pass
    
    async def analyze_results(
        self,
        result: EvaluationResult,
        confidence_level: float = 0.95,
        bootstrap_samples: int = 1000
    ) -> Dict[str, StatisticalResult]:
        """
        Analyze evaluation results with comprehensive statistics.
        
        Args:
            result: Evaluation results to analyze
            confidence_level: Confidence level for intervals
            bootstrap_samples: Number of bootstrap samples
            
        Returns:
            Dictionary of statistical results by metric
        """
        statistical_results = {}
        
        # Group results by metric
        metric_scores = {}
        for metric_result in result.metric_results:
            metric_name = metric_result.metric_name
            if metric_name not in metric_scores:
                metric_scores[metric_name] = []
            
            if metric_result.numeric_value is not None:
                metric_scores[metric_name].append(metric_result.numeric_value)
        
        # Analyze each metric
        for metric_name, scores in metric_scores.items():
            if len(scores) > 1:  # Need multiple samples for statistics
                stat_result = self._analyze_metric_scores(
                    scores, confidence_level, bootstrap_samples
                )
                statistical_results[metric_name] = stat_result
        
        return statistical_results
    
    def _analyze_metric_scores(
        self,
        scores: List[float],
        confidence_level: float,
        bootstrap_samples: int
    ) -> StatisticalResult:
        """Analyze scores for a single metric."""
        scores_array = np.array(scores)
        
        # Basic statistics
        mean = np.mean(scores_array)
        std = np.std(scores_array, ddof=1)
        median = np.median(scores_array)
        sample_size = len(scores)
        
        # Confidence interval using bootstrap
        confidence_interval = self._bootstrap_confidence_interval(
            scores_array, confidence_level, bootstrap_samples
        )
        
        # Effect size (Cohen's d against a baseline of 0.5)
        baseline = 0.5
        effect_size = (mean - baseline) / std if std > 0 else 0.0
        
        return StatisticalResult(
            mean=mean,
            std=std,
            median=median,
            confidence_interval=confidence_interval,
            sample_size=sample_size,
            effect_size=effect_size
        )
    
    def _bootstrap_confidence_interval(
        self,
        data: np.ndarray,
        confidence_level: float,
        n_samples: int
    ) -> tuple[float, float]:
        """Calculate bootstrap confidence interval."""
        bootstrap_means = []
        
        for _ in range(n_samples):
            # Resample with replacement
            bootstrap_sample = np.random.choice(data, size=len(data), replace=True)
            bootstrap_means.append(np.mean(bootstrap_sample))
        
        # Calculate percentiles for confidence interval
        alpha = 1 - confidence_level
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        lower_bound = np.percentile(bootstrap_means, lower_percentile)
        upper_bound = np.percentile(bootstrap_means, upper_percentile)
        
        return (lower_bound, upper_bound) 