"""
Evaluation suite classes providing high-level interfaces for EvalX.
"""

import asyncio
from typing import List, Dict, Any, Optional, Union
from dataclasses import asdict

from .types import (
    EvaluationInput,
    EvaluationResult,
    EvaluationConfig,
    EvaluationPlan,
    MetricResult,
    ValidationLevel,
    TaskType,
)
from .base import BaseMetric, BaseEvaluator, WeightedEvaluator
from ..agents.orchestrator import IntelligentOrchestrator
from ..agents.planner import EvaluationPlanner
from ..agents.interpreter import ResultInterpreter
from ..validation.statistical import StatisticalAnalyzer
from ..utils.config import Config


class EvaluationSuite:
    """
    Main evaluation suite with intelligent agentic orchestration.
    
    This is the recommended interface for most users, providing natural language
    instruction-based evaluation with automatic metric selection and workflow planning.
    """
    
    def __init__(
        self,
        config: Optional[EvaluationConfig] = None,
        orchestrator: Optional[IntelligentOrchestrator] = None,
        **kwargs
    ):
        self.config = config or EvaluationConfig()
        self.orchestrator = orchestrator or IntelligentOrchestrator()
        self.metadata = kwargs
        self._plan: Optional[EvaluationPlan] = None
    
    @classmethod
    def from_instruction(
        cls,
        instruction: str,
        validation_level: ValidationLevel = "production",
        **kwargs
    ) -> "EvaluationSuite":
        """
        Create evaluation suite from natural language instruction.
        
        Args:
            instruction: Natural language description of what to evaluate
            validation_level: Level of validation rigor
            **kwargs: Additional configuration options
        
        Returns:
            Configured EvaluationSuite instance
        """
        config = EvaluationConfig(validation_level=validation_level, **kwargs)
        suite = cls(config=config)
        suite._instruction = instruction
        return suite
    
    def plan(self, data: List[Union[Dict[str, Any], EvaluationInput]]) -> EvaluationPlan:
        """
        Plan evaluation based on instruction and data.
        
        Args:
            data: Input data for evaluation
            
        Returns:
            Evaluation plan with selected metrics and workflow
        """
        # Convert data to EvaluationInput format
        eval_inputs = []
        for item in data:
            if isinstance(item, EvaluationInput):
                eval_inputs.append(item)
            elif isinstance(item, dict):
                eval_inputs.append(EvaluationInput(
                    input_text=item.get("input", item.get("input_text")),
                    output_text=item.get("output", item.get("output_text")),
                    reference_text=item.get("reference", item.get("reference_text")),
                    context=item.get("context"),
                    metadata=item.get("metadata", {})
                ))
            else:
                raise ValueError(f"Unsupported data format: {type(item)}")
        
        # Use orchestrator to plan evaluation
        if hasattr(self, '_instruction'):
            self._plan = self.orchestrator.plan_evaluation(self._instruction, eval_inputs)
        else:
            # Default plan for direct usage
            task_type = self.orchestrator.identify_task_type("", eval_inputs)
            self._plan = EvaluationPlan(
                task_type=task_type,
                metrics=["semantic_similarity", "coherence"],
                workflow_steps=["evaluate", "analyze"],
                confidence_level=self.config.confidence_level
            )
        
        return self._plan
    
    async def evaluate_async(
        self,
        data: List[Union[Dict[str, Any], EvaluationInput]],
        plan: Optional[EvaluationPlan] = None
    ) -> EvaluationResult:
        """
        Evaluate data asynchronously using planned or provided evaluation plan.
        
        Args:
            data: Input data for evaluation
            plan: Optional evaluation plan (will create one if not provided)
            
        Returns:
            Comprehensive evaluation results
        """
        if plan is None:
            plan = self.plan(data)
        
        # Execute plan using orchestrator
        result = await self.orchestrator.execute_plan(plan)
        
        # Add interpretation and recommendations if configured
        if self.config.validation_level in ["production", "research_grade"]:
            interpreter = ResultInterpreter()
            result.interpretation = await interpreter.interpret_results(result)
            result.recommendations = await interpreter.generate_recommendations(result)
        
        return result
    
    def evaluate(
        self,
        data: List[Union[Dict[str, Any], EvaluationInput]],
        plan: Optional[EvaluationPlan] = None
    ) -> EvaluationResult:
        """
        Evaluate data synchronously.
        
        Args:
            data: Input data for evaluation
            plan: Optional evaluation plan
            
        Returns:
            Comprehensive evaluation results
        """
        return asyncio.run(self.evaluate_async(data, plan))


class MetricSuite(BaseEvaluator):
    """
    Fine-grained evaluation suite for custom metric combinations.
    
    Provides direct control over metric selection and configuration,
    suitable for users who want explicit control over the evaluation process.
    """
    
    def __init__(
        self,
        metrics: Optional[List[BaseMetric]] = None,
        config: Optional[EvaluationConfig] = None,
        combination_strategy: str = "weighted_average",
        **kwargs
    ):
        super().__init__(metrics or [], config, **kwargs)
        self.combination_strategy = combination_strategy
        self.statistical_analyzer = StatisticalAnalyzer()
    
    def add_traditional_metric(self, metric_name: str, **kwargs) -> "MetricSuite":
        """Add a traditional metric (BLEU, ROUGE, etc.)."""
        from ..metrics.traditional import TraditionalMetrics
        metric = getattr(TraditionalMetrics, metric_name)(**kwargs)
        self.add_metric(metric)
        return self
    
    def add_llm_judge(self, name: str, prompt: str, model: str = "gpt-4", **kwargs) -> "MetricSuite":
        """Add an LLM-as-judge metric."""
        from ..metrics.llm_judge import LLMJudge
        metric = LLMJudge.create(name=name, prompt=prompt, model=model, **kwargs)
        self.add_metric(metric)
        return self
    
    def add_hybrid_metric(self, name: str, components: List[str], **kwargs) -> "MetricSuite":
        """Add a hybrid metric combining multiple approaches."""
        from ..metrics.hybrid import HybridMetric
        metric = HybridMetric.create(name=name, components=components, **kwargs)
        self.add_metric(metric)
        return self
    
    def _combine_results(self, metric_results: List[MetricResult]) -> float:
        """Combine metric results based on strategy."""
        if self.combination_strategy == "weighted_average":
            return self._weighted_average(metric_results)
        elif self.combination_strategy == "harmonic_mean":
            return self._harmonic_mean(metric_results)
        elif self.combination_strategy == "geometric_mean":
            return self._geometric_mean(metric_results)
        else:
            return self._weighted_average(metric_results)  # Default
    
    def _weighted_average(self, metric_results: List[MetricResult]) -> float:
        """Weighted average combination."""
        total_score = 0.0
        total_weight = 0.0
        
        for result in metric_results:
            if result.numeric_value is not None:
                weight = result.metadata.get("weight", 1.0)
                total_score += result.numeric_value * weight
                total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _harmonic_mean(self, metric_results: List[MetricResult]) -> float:
        """Harmonic mean combination (emphasizes lower scores)."""
        values = [r.numeric_value for r in metric_results if r.numeric_value is not None and r.numeric_value > 0]
        if not values:
            return 0.0
        return len(values) / sum(1/v for v in values)
    
    def _geometric_mean(self, metric_results: List[MetricResult]) -> float:
        """Geometric mean combination."""
        import math
        values = [r.numeric_value for r in metric_results if r.numeric_value is not None and r.numeric_value > 0]
        if not values:
            return 0.0
        product = 1.0
        for v in values:
            product *= v
        return product ** (1.0 / len(values))
    
    async def evaluate_with_stats(
        self,
        data: List[Union[Dict[str, Any], EvaluationInput]],
        confidence_level: float = 0.95,
        bootstrap_samples: int = 1000
    ) -> EvaluationResult:
        """
        Evaluate with comprehensive statistical analysis.
        
        Args:
            data: Input data for evaluation
            confidence_level: Confidence level for statistical tests
            bootstrap_samples: Number of bootstrap samples
            
        Returns:
            Evaluation results with statistical analysis
        """
        # Convert data format
        eval_inputs = self._convert_data_format(data)
        
        # Run evaluation
        result = await self.evaluate_async(eval_inputs)
        
        # Add statistical analysis
        if len(eval_inputs) > 1:  # Need multiple samples for stats
            result.statistical_results = await self.statistical_analyzer.analyze_results(
                result,
                confidence_level=confidence_level,
                bootstrap_samples=bootstrap_samples
            )
        
        return result
    
    def _convert_data_format(self, data: List[Union[Dict[str, Any], EvaluationInput]]) -> List[EvaluationInput]:
        """Convert various data formats to EvaluationInput."""
        eval_inputs = []
        for item in data:
            if isinstance(item, EvaluationInput):
                eval_inputs.append(item)
            elif isinstance(item, dict):
                eval_inputs.append(EvaluationInput(
                    input_text=item.get("input", item.get("input_text")),
                    output_text=item.get("output", item.get("output_text")),
                    reference_text=item.get("reference", item.get("reference_text")),
                    context=item.get("context"),
                    metadata=item.get("metadata", {})
                ))
            else:
                raise ValueError(f"Unsupported data format: {type(item)}")
        return eval_inputs


class ResearchSuite(MetricSuite):
    """
    Research-grade evaluation suite with comprehensive validation and statistical analysis.
    
    Designed for academic research and rigorous evaluation scenarios,
    includes human validation, benchmark testing, and publication-ready analysis.
    """
    
    def __init__(
        self,
        metrics: Optional[List[str]] = None,
        validation_datasets: Optional[List[str]] = None,
        statistical_tests: Optional[List[str]] = None,
        human_validation: bool = False,
        **kwargs
    ):
        config = EvaluationConfig(
            validation_level="research_grade",
            statistical_tests=statistical_tests or ["t_test", "wilcoxon", "bootstrap"],
            **kwargs
        )
        super().__init__(config=config, **kwargs)
        
        # Initialize research-specific components
        self.validation_datasets = validation_datasets or []
        self.human_validation_enabled = human_validation
        self.benchmark_suite = None
        self.human_validator = None
        
        # Auto-add metrics if specified
        if metrics:
            self._add_research_metrics(metrics)
    
    def _add_research_metrics(self, metric_names: List[str]) -> None:
        """Add research-validated metrics."""
        for metric_name in metric_names:
            if metric_name in ["accuracy", "helpfulness", "groundedness"]:
                self.add_llm_judge(
                    name=metric_name,
                    prompt=self._get_research_prompt(metric_name),
                    model="gpt-4",
                    validation_required=True
                )
            elif metric_name in ["bleu", "rouge", "meteor", "semantic_similarity"]:
                self.add_traditional_metric(metric_name)
    
    def _get_research_prompt(self, metric_name: str) -> str:
        """Get research-validated prompts for LLM judges."""
        prompts = {
            "accuracy": """
            You are an expert evaluator assessing the factual accuracy of responses.
            Rate the accuracy on a scale of 0.0 to 1.0 where:
            - 1.0 = Completely accurate, all facts are correct
            - 0.5 = Partially accurate, some facts are correct
            - 0.0 = Completely inaccurate, facts are wrong
            
            Input: {input_text}
            Output: {output_text}
            Reference: {reference_text}
            
            Provide only a numeric score between 0.0 and 1.0.
            """,
            "helpfulness": """
            You are an expert evaluator assessing how helpful a response is to the user.
            Rate the helpfulness on a scale of 0.0 to 1.0 where:
            - 1.0 = Extremely helpful, fully addresses the user's need
            - 0.5 = Moderately helpful, partially addresses the need
            - 0.0 = Not helpful, does not address the user's need
            
            Input: {input_text}
            Output: {output_text}
            
            Provide only a numeric score between 0.0 and 1.0.
            """,
            "groundedness": """
            You are an expert evaluator assessing how well a response is grounded in the provided context.
            Rate the groundedness on a scale of 0.0 to 1.0 where:
            - 1.0 = Fully grounded, all information comes from context
            - 0.5 = Partially grounded, some information from context
            - 0.0 = Not grounded, information not supported by context
            
            Context: {context}
            Output: {output_text}
            
            Provide only a numeric score between 0.0 and 1.0.
            """
        }
        return prompts.get(metric_name, "Rate this response on a scale of 0.0 to 1.0.")
    
    async def evaluate_research_grade(
        self,
        system_outputs: List[Union[Dict[str, Any], EvaluationInput]],
        reference_outputs: Optional[List[str]] = None,
        human_annotations: Optional[List[Dict[str, Any]]] = None
    ) -> EvaluationResult:
        """
        Perform research-grade evaluation with full validation pipeline.
        
        Args:
            system_outputs: Outputs from the system being evaluated
            reference_outputs: Gold standard reference outputs
            human_annotations: Human annotations for validation
            
        Returns:
            Comprehensive research-grade evaluation results
        """
        # Convert to evaluation inputs
        eval_inputs = self._convert_data_format(system_outputs)
        
        # Add reference outputs if provided
        if reference_outputs:
            for i, ref in enumerate(reference_outputs):
                if i < len(eval_inputs):
                    eval_inputs[i].reference_text = ref
        
        # Run core evaluation
        result = await self.evaluate_with_stats(
            eval_inputs,
            confidence_level=0.95,
            bootstrap_samples=1000
        )
        
        # Add research-specific analysis
        if self.human_validation_enabled and human_annotations:
            result = await self._add_human_validation(result, human_annotations)
        
        if self.validation_datasets:
            result = await self._add_benchmark_validation(result)
        
        # Generate research report
        result.metadata["research_report"] = self._generate_research_report(result)
        
        return result
    
    async def _add_human_validation(
        self,
        result: EvaluationResult,
        human_annotations: List[Dict[str, Any]]
    ) -> EvaluationResult:
        """Add human validation analysis."""
        if self.human_validator is None:
            from ..validation.human import HumanValidation
            self.human_validator = HumanValidation()
        
        validation_report = await self.human_validator.validate_against_human(
            result, human_annotations
        )
        result.metadata["human_validation"] = validation_report
        return result
    
    async def _add_benchmark_validation(self, result: EvaluationResult) -> EvaluationResult:
        """Add benchmark validation analysis."""
        if self.benchmark_suite is None:
            from ..validation.benchmarks import BenchmarkSuite
            self.benchmark_suite = BenchmarkSuite()
        
        benchmark_results = await self.benchmark_suite.validate_metrics(
            self.metrics, self.validation_datasets
        )
        result.metadata["benchmark_validation"] = benchmark_results
        return result
    
    def _generate_research_report(self, result: EvaluationResult) -> str:
        """Generate a research-ready report."""
        report_sections = [
            "# Research Evaluation Report",
            f"Generated at: {result.timestamp}",
            "",
            "## Methodology",
            f"- Metrics: {[m.name for m in self.metrics]}",
            f"- Sample size: {len(result.metric_results) // len(self.metrics)}",
            f"- Confidence level: {self.config.confidence_level}",
            "",
            "## Results",
        ]
        
        # Add statistical results
        for metric_name, stats in result.statistical_results.items():
            report_sections.extend([
                f"### {metric_name}",
                f"- Mean: {stats.mean:.3f} ± {stats.std:.3f}",
                f"- 95% CI: [{stats.confidence_interval[0]:.3f}, {stats.confidence_interval[1]:.3f}]",
                f"- Effect size: {stats.effect_size:.3f}" if stats.effect_size else "",
                ""
            ])
        
        # Add validation results
        if "human_validation" in result.metadata:
            report_sections.extend([
                "## Human Validation",
                f"- Correlation with human judgments: {result.metadata['human_validation']}",
                ""
            ])
        
        return "\n".join(report_sections)
    
    def generate_research_report(self, result: EvaluationResult) -> str:
        """Generate a comprehensive research report."""
        return result.metadata.get("research_report", "No research report available") 