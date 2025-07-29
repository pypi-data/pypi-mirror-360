"""
Core type definitions for EvalX evaluation framework.
"""

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Union,
    Tuple,
    Protocol,
    TypeVar,
    Generic,
    Callable,
    Awaitable,
    Literal,
)
from typing_extensions import TypedDict, NotRequired
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from datetime import datetime
from pathlib import Path

# Type aliases
ScoreType = Union[float, int, bool]
MetricValue = Union[ScoreType, Dict[str, ScoreType], List[ScoreType]]
ModelIdentifier = str  # e.g., "openai:gpt-4", "anthropic:claude-3"
TaskType = Literal[
    "question_answering",
    "summarization", 
    "dialogue",
    "translation",
    "classification",
    "generation",
    "retrieval",
    "reasoning",
    "coding",
    "unknown"
]

ValidationLevel = Literal["quick", "production", "research_grade"]
StatisticalTest = Literal["t_test", "wilcoxon", "mann_whitney", "bootstrap", "permutation"]
EnsembleStrategy = Literal["voting", "weighted_voting", "stacking", "averaging"]

# Core data structures
@dataclass
class EvaluationInput:
    """Input data for evaluation."""
    input_text: Optional[str] = None
    output_text: Optional[str] = None
    reference_text: Optional[str] = None
    context: Optional[Union[str, List[str]]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "input_text": self.input_text,
            "output_text": self.output_text,
            "reference_text": self.reference_text,
            "context": self.context,
            "metadata": self.metadata,
        }

@dataclass
class MetricResult:
    """Result from a single metric evaluation."""
    metric_name: str
    value: MetricValue
    confidence: Optional[float] = None
    explanation: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def numeric_value(self) -> Optional[float]:
        """Get numeric representation of the value."""
        if isinstance(self.value, (int, float)):
            return float(self.value)
        elif isinstance(self.value, bool):
            return 1.0 if self.value else 0.0
        elif isinstance(self.value, dict) and "score" in self.value:
            return float(self.value["score"])
        return None

@dataclass
class StatisticalResult:
    """Statistical analysis results."""
    mean: float
    std: float
    median: float
    confidence_interval: Tuple[float, float]
    sample_size: int
    effect_size: Optional[float] = None
    p_value: Optional[float] = None
    is_significant: Optional[bool] = None
    test_statistic: Optional[float] = None
    test_name: Optional[str] = None
    power: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "mean": self.mean,
            "std": self.std,
            "median": self.median,
            "confidence_interval": self.confidence_interval,
            "sample_size": self.sample_size,
            "effect_size": self.effect_size,
            "p_value": self.p_value,
            "is_significant": self.is_significant,
            "test_statistic": self.test_statistic,
            "test_name": self.test_name,
            "power": self.power,
        }

@dataclass
class EvaluationResult:
    """Complete evaluation results."""
    metric_results: List[MetricResult]
    statistical_results: Dict[str, StatisticalResult] = field(default_factory=dict)
    overall_score: Optional[float] = None
    interpretation: Optional[str] = None
    recommendations: Optional[List[str]] = None
    execution_time: Optional[float] = None
    cost: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    def get_metric_result(self, metric_name: str) -> Optional[MetricResult]:
        """Get result for a specific metric."""
        for result in self.metric_results:
            if result.metric_name == metric_name:
                return result
        return None
    
    def get_numeric_scores(self) -> Dict[str, float]:
        """Get all numeric scores as a dictionary."""
        scores = {}
        for result in self.metric_results:
            if result.numeric_value is not None:
                scores[result.metric_name] = result.numeric_value
        return scores
    
    def summary(self) -> str:
        """Generate a human-readable summary."""
        lines = [f"Evaluation Results ({len(self.metric_results)} metrics)"]
        
        if self.overall_score is not None:
            lines.append(f"Overall Score: {self.overall_score:.3f}")
        
        for result in self.metric_results:
            if result.numeric_value is not None:
                lines.append(f"  {result.metric_name}: {result.numeric_value:.3f}")
        
        if self.interpretation:
            lines.append(f"\nInterpretation: {self.interpretation}")
        
        if self.recommendations:
            lines.append("\nRecommendations:")
            for rec in self.recommendations:
                lines.append(f"  - {rec}")
        
        return "\n".join(lines)

@dataclass
class ValidationReport:
    """Validation report for metrics."""
    metric_name: str
    human_correlation: Optional[float] = None
    inter_annotator_agreement: Optional[float] = None
    benchmark_scores: Dict[str, float] = field(default_factory=dict)
    robustness_score: Optional[float] = None
    bias_analysis: Dict[str, Any] = field(default_factory=dict)
    validation_level: ValidationLevel = "production"
    timestamp: datetime = field(default_factory=datetime.now)
    
    def is_valid(self, threshold: float = 0.7) -> bool:
        """Check if metric meets validation threshold."""
        if self.human_correlation is not None:
            return self.human_correlation >= threshold
        return False

@dataclass
class EvaluationConfig:
    """Configuration for evaluation."""
    validation_level: ValidationLevel = "production"
    confidence_level: float = 0.95
    bootstrap_samples: int = 1000
    statistical_tests: List[StatisticalTest] = field(default_factory=lambda: ["t_test"])
    multiple_comparisons_correction: Optional[str] = None
    cache_enabled: bool = True
    parallel_execution: bool = True
    max_workers: int = 4
    timeout: Optional[float] = None
    cost_budget: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "validation_level": self.validation_level,
            "confidence_level": self.confidence_level,
            "bootstrap_samples": self.bootstrap_samples,
            "statistical_tests": self.statistical_tests,
            "multiple_comparisons_correction": self.multiple_comparisons_correction,
            "cache_enabled": self.cache_enabled,
            "parallel_execution": self.parallel_execution,
            "max_workers": self.max_workers,
            "timeout": self.timeout,
            "cost_budget": self.cost_budget,
        }

# Protocol definitions
class MetricProtocol(Protocol):
    """Protocol for metric implementations."""
    
    name: str
    description: str
    required_inputs: List[str]
    
    def evaluate(self, input_data: EvaluationInput) -> MetricResult:
        """Evaluate a single input."""
        ...
    
    async def evaluate_async(self, input_data: EvaluationInput) -> MetricResult:
        """Evaluate a single input asynchronously."""
        ...
    
    def evaluate_batch(self, inputs: List[EvaluationInput]) -> List[MetricResult]:
        """Evaluate multiple inputs."""
        ...
    
    async def evaluate_batch_async(self, inputs: List[EvaluationInput]) -> List[MetricResult]:
        """Evaluate multiple inputs asynchronously."""
        ...

class EvaluatorProtocol(Protocol):
    """Protocol for evaluator implementations."""
    
    def evaluate(self, inputs: List[EvaluationInput], config: EvaluationConfig) -> EvaluationResult:
        """Evaluate inputs with configuration."""
        ...
    
    async def evaluate_async(self, inputs: List[EvaluationInput], config: EvaluationConfig) -> EvaluationResult:
        """Evaluate inputs asynchronously."""
        ...

class OrchestratorProtocol(Protocol):
    """Protocol for orchestrator implementations."""
    
    def plan_evaluation(self, instruction: str, data: List[EvaluationInput]) -> "EvaluationPlan":
        """Plan evaluation based on instruction."""
        ...
    
    async def execute_plan(self, plan: "EvaluationPlan") -> EvaluationResult:
        """Execute evaluation plan."""
        ...

# Additional types for advanced features
@dataclass
class ModelConfig:
    """Configuration for LLM models."""
    model_id: ModelIdentifier
    temperature: float = 0.0
    max_tokens: Optional[int] = None
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: Optional[float] = None
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "model_id": self.model_id,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
        }

@dataclass
class PromptTemplate:
    """Template for LLM prompts."""
    template: str
    variables: List[str]
    few_shot_examples: Optional[List[Dict[str, Any]]] = None
    system_message: Optional[str] = None
    
    def format(self, **kwargs) -> str:
        """Format template with variables."""
        return self.template.format(**kwargs)

@dataclass
class EvaluationPlan:
    """Plan for evaluation execution."""
    task_type: TaskType
    metrics: List[str]
    workflow_steps: List[str]
    estimated_cost: Optional[float] = None
    estimated_time: Optional[float] = None
    confidence_level: float = 0.95
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "task_type": self.task_type,
            "metrics": self.metrics,
            "workflow_steps": self.workflow_steps,
            "estimated_cost": self.estimated_cost,
            "estimated_time": self.estimated_time,
            "confidence_level": self.confidence_level,
        }

# Exceptions
class EvalXError(Exception):
    """Base exception for EvalX."""
    pass

class MetricError(EvalXError):
    """Error in metric evaluation."""
    pass

class ValidationError(EvalXError):
    """Error in validation."""
    pass

class ConfigurationError(EvalXError):
    """Error in configuration."""
    pass

class ModelError(EvalXError):
    """Error in model interaction."""
    pass

# Type variables for generics
T = TypeVar('T')
MetricT = TypeVar('MetricT', bound=MetricProtocol)
EvaluatorT = TypeVar('EvaluatorT', bound=EvaluatorProtocol) 