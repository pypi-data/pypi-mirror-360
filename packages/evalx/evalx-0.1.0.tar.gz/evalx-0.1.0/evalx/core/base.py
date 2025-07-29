"""
Base classes for EvalX evaluation framework.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

from .types import (
    EvaluationInput,
    MetricResult,
    EvaluationResult,
    EvaluationConfig,
    EvaluationPlan,
    MetricProtocol,
    EvaluatorProtocol,
    OrchestratorProtocol,
    MetricError,
    ValidationError,
)


class BaseMetric(ABC):
    """Base class for all metrics."""
    
    def __init__(
        self,
        name: str,
        description: str,
        required_inputs: List[str],
        weight: float = 1.0,
        **kwargs
    ):
        self.name = name
        self.description = description
        self.required_inputs = required_inputs
        self.weight = weight
        self.metadata = kwargs
    
    def validate_input(self, input_data: EvaluationInput) -> None:
        """Validate that input data contains required fields."""
        for field in self.required_inputs:
            if not hasattr(input_data, field) or getattr(input_data, field) is None:
                raise ValidationError(
                    f"Metric '{self.name}' requires field '{field}' but it was not provided"
                )
    
    @abstractmethod
    def _compute_score(self, input_data: EvaluationInput) -> Union[float, Dict[str, Any]]:
        """Compute the actual metric score. Must be implemented by subclasses."""
        pass
    
    def evaluate(self, input_data: EvaluationInput) -> MetricResult:
        """Evaluate a single input."""
        try:
            self.validate_input(input_data)
            start_time = time.time()
            score = self._compute_score(input_data)
            execution_time = time.time() - start_time
            
            return MetricResult(
                metric_name=self.name,
                value=score,
                metadata={
                    "execution_time": execution_time,
                    "weight": self.weight,
                    **self.metadata
                }
            )
        except Exception as e:
            raise MetricError(f"Error evaluating metric '{self.name}': {str(e)}") from e
    
    async def evaluate_async(self, input_data: EvaluationInput) -> MetricResult:
        """Evaluate a single input asynchronously."""
        # Default implementation runs synchronously in thread pool
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            return await loop.run_in_executor(executor, self.evaluate, input_data)
    
    def evaluate_batch(self, inputs: List[EvaluationInput]) -> List[MetricResult]:
        """Evaluate multiple inputs."""
        results = []
        for input_data in inputs:
            try:
                result = self.evaluate(input_data)
                results.append(result)
            except Exception as e:
                # Create error result
                error_result = MetricResult(
                    metric_name=self.name,
                    value=0.0,
                    metadata={"error": str(e)}
                )
                results.append(error_result)
        return results
    
    async def evaluate_batch_async(self, inputs: List[EvaluationInput]) -> List[MetricResult]:
        """Evaluate multiple inputs asynchronously."""
        tasks = [self.evaluate_async(input_data) for input_data in inputs]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', weight={self.weight})"


class BaseEvaluator(ABC):
    """Base class for evaluators that combine multiple metrics."""
    
    def __init__(
        self,
        metrics: List[BaseMetric],
        config: Optional[EvaluationConfig] = None,
        **kwargs
    ):
        self.metrics = metrics
        self.config = config or EvaluationConfig()
        self.metadata = kwargs
    
    def add_metric(self, metric: BaseMetric) -> None:
        """Add a metric to the evaluator."""
        self.metrics.append(metric)
    
    def remove_metric(self, metric_name: str) -> None:
        """Remove a metric by name."""
        self.metrics = [m for m in self.metrics if m.name != metric_name]
    
    def get_metric(self, metric_name: str) -> Optional[BaseMetric]:
        """Get a metric by name."""
        for metric in self.metrics:
            if metric.name == metric_name:
                return metric
        return None
    
    @abstractmethod
    def _combine_results(self, metric_results: List[MetricResult]) -> float:
        """Combine metric results into overall score. Must be implemented by subclasses."""
        pass
    
    def evaluate(self, inputs: List[EvaluationInput], config: Optional[EvaluationConfig] = None) -> EvaluationResult:
        """Evaluate inputs with all metrics."""
        eval_config = config or self.config
        start_time = time.time()
        
        all_metric_results = []
        
        if eval_config.parallel_execution and len(self.metrics) > 1:
            # Parallel execution of metrics
            with ThreadPoolExecutor(max_workers=eval_config.max_workers) as executor:
                future_to_metric = {
                    executor.submit(metric.evaluate_batch, inputs): metric
                    for metric in self.metrics
                }
                
                for future in as_completed(future_to_metric):
                    metric = future_to_metric[future]
                    try:
                        results = future.result(timeout=eval_config.timeout)
                        all_metric_results.extend(results)
                    except Exception as e:
                        # Create error results for this metric
                        error_results = [
                            MetricResult(
                                metric_name=metric.name,
                                value=0.0,
                                metadata={"error": str(e)}
                            )
                            for _ in inputs
                        ]
                        all_metric_results.extend(error_results)
        else:
            # Sequential execution
            for metric in self.metrics:
                try:
                    results = metric.evaluate_batch(inputs)
                    all_metric_results.extend(results)
                except Exception as e:
                    # Create error results for this metric
                    error_results = [
                        MetricResult(
                            metric_name=metric.name,
                            value=0.0,
                            metadata={"error": str(e)}
                        )
                        for _ in inputs
                    ]
                    all_metric_results.extend(error_results)
        
        # Group results by sample
        grouped_results = {}
        for i, result in enumerate(all_metric_results):
            sample_idx = i % len(inputs)
            if sample_idx not in grouped_results:
                grouped_results[sample_idx] = []
            grouped_results[sample_idx].append(result)
        
        # Calculate overall score
        sample_scores = []
        for sample_results in grouped_results.values():
            try:
                sample_score = self._combine_results(sample_results)
                sample_scores.append(sample_score)
            except Exception:
                sample_scores.append(0.0)
        
        overall_score = sum(sample_scores) / len(sample_scores) if sample_scores else 0.0
        execution_time = time.time() - start_time
        
        return EvaluationResult(
            metric_results=all_metric_results,
            overall_score=overall_score,
            execution_time=execution_time,
            metadata={
                "num_samples": len(inputs),
                "num_metrics": len(self.metrics),
                "config": eval_config.to_dict(),
                **self.metadata
            }
        )
    
    async def evaluate_async(self, inputs: List[EvaluationInput], config: Optional[EvaluationConfig] = None) -> EvaluationResult:
        """Evaluate inputs asynchronously."""
        eval_config = config or self.config
        start_time = time.time()
        
        # Run all metrics in parallel
        tasks = [metric.evaluate_batch_async(inputs) for metric in self.metrics]
        metric_results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_metric_results = []
        for results_list in metric_results_lists:
            if isinstance(results_list, Exception):
                # Handle exception by creating error results
                error_results = [
                    MetricResult(
                        metric_name="unknown",
                        value=0.0,
                        metadata={"error": str(results_list)}
                    )
                    for _ in inputs
                ]
                all_metric_results.extend(error_results)
            else:
                all_metric_results.extend(results_list)
        
        # Group results by sample (similar to sync version)
        grouped_results = {}
        for i, result in enumerate(all_metric_results):
            sample_idx = i % len(inputs)
            if sample_idx not in grouped_results:
                grouped_results[sample_idx] = []
            grouped_results[sample_idx].append(result)
        
        # Calculate overall score
        sample_scores = []
        for sample_results in grouped_results.values():
            try:
                sample_score = self._combine_results(sample_results)
                sample_scores.append(sample_score)
            except Exception:
                sample_scores.append(0.0)
        
        overall_score = sum(sample_scores) / len(sample_scores) if sample_scores else 0.0
        execution_time = time.time() - start_time
        
        return EvaluationResult(
            metric_results=all_metric_results,
            overall_score=overall_score,
            execution_time=execution_time,
            metadata={
                "num_samples": len(inputs),
                "num_metrics": len(self.metrics),
                "config": eval_config.to_dict(),
                "async": True,
                **self.metadata
            }
        )


class BaseOrchestrator(ABC):
    """Base class for intelligent orchestrators."""
    
    def __init__(self, **kwargs):
        self.metadata = kwargs
    
    @abstractmethod
    def plan_evaluation(self, instruction: str, data: List[EvaluationInput]) -> EvaluationPlan:
        """Plan evaluation based on natural language instruction."""
        pass
    
    @abstractmethod
    async def execute_plan(self, plan: EvaluationPlan) -> EvaluationResult:
        """Execute evaluation plan."""
        pass
    
    def identify_task_type(self, instruction: str, data: List[EvaluationInput]) -> str:
        """Identify the type of task based on instruction and data."""
        instruction_lower = instruction.lower()
        
        # Simple heuristics for task identification
        if any(word in instruction_lower for word in ["summarize", "summary", "summarization"]):
            return "summarization"
        elif any(word in instruction_lower for word in ["question", "answer", "qa", "qna"]):
            return "question_answering"
        elif any(word in instruction_lower for word in ["dialogue", "chat", "conversation"]):
            return "dialogue"
        elif any(word in instruction_lower for word in ["translate", "translation"]):
            return "translation"
        elif any(word in instruction_lower for word in ["classify", "classification", "category"]):
            return "classification"
        elif any(word in instruction_lower for word in ["retrieve", "retrieval", "search"]):
            return "retrieval"
        elif any(word in instruction_lower for word in ["code", "coding", "programming"]):
            return "coding"
        elif any(word in instruction_lower for word in ["reason", "reasoning", "logic"]):
            return "reasoning"
        elif any(word in instruction_lower for word in ["generate", "generation", "create"]):
            return "generation"
        else:
            return "unknown"


class WeightedEvaluator(BaseEvaluator):
    """Simple evaluator that combines metrics using weighted average."""
    
    def _combine_results(self, metric_results: List[MetricResult]) -> float:
        """Combine results using weighted average."""
        total_score = 0.0
        total_weight = 0.0
        
        for result in metric_results:
            if result.numeric_value is not None:
                weight = result.metadata.get("weight", 1.0)
                total_score += result.numeric_value * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0 