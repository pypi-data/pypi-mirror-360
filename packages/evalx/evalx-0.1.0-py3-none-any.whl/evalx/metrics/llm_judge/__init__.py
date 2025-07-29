"""
LLM-as-judge evaluation metrics.

This module provides advanced LLM-based evaluation metrics with structured outputs,
prompt optimization, and multi-model support.
"""

from .base import LLMJudgeMetric
from .prompts import PromptLibrary
from .models import ModelManager
from .structured_output import StructuredOutputParser

class LLMJudge:
    """Factory class for creating LLM-as-judge evaluation metrics."""
    
    @staticmethod
    def create(
        name: str,
        prompt: str,
        model: str = "gpt-4",
        scale: str = "binary",  # binary, continuous, categorical
        few_shot_examples: list = None,
        structured_output: bool = True,
        **kwargs
    ):
        """
        Create an LLM-as-judge metric.
        
        Args:
            name: Name of the metric
            prompt: Evaluation prompt template
            model: Model identifier (e.g., "gpt-4", "claude-3")
            scale: Type of output scale
            few_shot_examples: Example inputs/outputs for few-shot learning
            structured_output: Whether to use structured JSON output
            **kwargs: Additional configuration
        
        Returns:
            Configured LLMJudgeMetric instance
        """
        return LLMJudgeMetric(
            name=name,
            prompt=prompt,
            model=model,
            scale=scale,
            few_shot_examples=few_shot_examples,
            structured_output=structured_output,
            **kwargs
        )
    
    @staticmethod
    def accuracy(model: str = "gpt-4", **kwargs):
        """Create accuracy evaluation metric."""
        prompt = PromptLibrary.get_prompt("accuracy")
        return LLMJudge.create(
            name="accuracy",
            prompt=prompt,
            model=model,
            scale="continuous",
            **kwargs
        )
    
    @staticmethod
    def helpfulness(model: str = "gpt-4", **kwargs):
        """Create helpfulness evaluation metric."""
        prompt = PromptLibrary.get_prompt("helpfulness")
        return LLMJudge.create(
            name="helpfulness",
            prompt=prompt,
            model=model,
            scale="continuous",
            **kwargs
        )
    
    @staticmethod
    def coherence(model: str = "gpt-4", **kwargs):
        """Create coherence evaluation metric."""
        prompt = PromptLibrary.get_prompt("coherence")
        return LLMJudge.create(
            name="coherence",
            prompt=prompt,
            model=model,
            scale="continuous",
            **kwargs
        )
    
    @staticmethod
    def groundedness(model: str = "gpt-4", **kwargs):
        """Create groundedness evaluation metric."""
        prompt = PromptLibrary.get_prompt("groundedness")
        return LLMJudge.create(
            name="groundedness",
            prompt=prompt,
            model=model,
            scale="continuous",
            **kwargs
        )
    
    @staticmethod
    def relevance(model: str = "gpt-4", **kwargs):
        """Create relevance evaluation metric."""
        prompt = PromptLibrary.get_prompt("relevance")
        return LLMJudge.create(
            name="relevance",
            prompt=prompt,
            model=model,
            scale="continuous",
            **kwargs
        )

__all__ = [
    "LLMJudge",
    "LLMJudgeMetric",
    "PromptLibrary",
    "ModelManager",
    "StructuredOutputParser",
] 