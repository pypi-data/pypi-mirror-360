"""
EvalX: Next-Generation LLM Evaluation Framework

A comprehensive evaluation framework that combines traditional metrics,
LLM-as-judge evaluations, and intelligent agentic orchestration.
"""

from .core.types import (
    EvaluationInput,
    EvaluationResult,
    MetricResult,
    StatisticalResult,
    ValidationReport,
    EvaluationConfig,
)

from .core.base import (
    BaseMetric,
    BaseEvaluator,
    BaseOrchestrator,
)

from .core.suite import (
    EvaluationSuite,
    MetricSuite,
    ResearchSuite,
)

from .metrics.traditional import TraditionalMetrics
from .metrics.llm_judge import LLMJudge
from .metrics.hybrid import HybridMetric
from .metrics.multimodal import (
    MultimodalInput,
    ImageTextAlignmentMetric,
    ImageCaptionQualityMetric,
    CodeCorrectnessMetric,
    AudioQualityMetric,
)

from .agents.orchestrator import IntelligentOrchestrator
from .agents.planner import EvaluationPlanner
from .agents.interpreter import ResultInterpreter

from .validation.statistical import StatisticalAnalyzer
from .validation.benchmarks import BenchmarkSuite
from .validation.human import HumanValidation

from .meta_evaluation import (
    MetricQualityReport,
    MetaEvaluator,
    AdaptiveMetricSelector,
)

from .utils.config import Config
from .utils.cache import CacheManager
from .utils.async_utils import AsyncEvaluationEngine

# Version information
__version__ = "0.1.0"
__author__ = "Vishal Seelam"
__email__ = "vishalseelam@gmail.com"

# Main exports
__all__ = [
    # Core types
    "EvaluationInput",
    "EvaluationResult",
    "MetricResult",
    "StatisticalResult",
    "ValidationReport",
    "EvaluationConfig",
    
    # Base classes
    "BaseMetric",
    "BaseEvaluator",
    "BaseOrchestrator",
    
    # Evaluation suites
    "EvaluationSuite",
    "MetricSuite",
    "ResearchSuite",
    
    # Metrics
    "TraditionalMetrics",
    "LLMJudge",
    "HybridMetric",
    
    # Multimodal metrics
    "MultimodalInput",
    "ImageTextAlignmentMetric",
    "ImageCaptionQualityMetric",
    "CodeCorrectnessMetric",
    "AudioQualityMetric",
    
    # Agents
    "IntelligentOrchestrator",
    "EvaluationPlanner",
    "ResultInterpreter",
    
    # Validation
    "StatisticalAnalyzer",
    "BenchmarkSuite",
    "HumanValidation",
    
    # Meta-evaluation
    "MetricQualityReport",
    "MetaEvaluator",
    "AdaptiveMetricSelector",
    
    # Utils
    "Config",
    "CacheManager",
    "AsyncEvaluationEngine",
]

# Convenience imports for common use cases
from .core.suite import EvaluationSuite as Suite
from .metrics.traditional import TraditionalMetrics as Traditional
from .metrics.llm_judge import LLMJudge as Judge
from .agents.orchestrator import IntelligentOrchestrator as Orchestrator

# Create global config instance
config = Config()

# Add convenience exports
__all__.extend(["Suite", "Traditional", "Judge", "Orchestrator", "config"]) 