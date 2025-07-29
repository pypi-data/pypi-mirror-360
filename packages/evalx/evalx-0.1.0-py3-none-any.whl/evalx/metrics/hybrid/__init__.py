"""
Hybrid evaluation metrics that combine multiple approaches.
"""

from ...core.base import BaseMetric
from ...core.types import EvaluationInput


class HybridMetric(BaseMetric):
    """
    Hybrid metric that combines multiple evaluation approaches.
    
    Can combine traditional metrics, LLM-as-judge, and learned metrics
    using various combination strategies.
    """
    
    def __init__(self, name: str, components: list, strategy: str = "weighted_average", **kwargs):
        super().__init__(
            name=name,
            description=f"Hybrid metric combining {len(components)} components",
            required_inputs=["output_text"],  # Will be updated based on components
            **kwargs
        )
        self.components = components
        self.strategy = strategy
    
    @classmethod
    def create(cls, name: str, components: list, **kwargs):
        """Create a hybrid metric."""
        return cls(name=name, components=components, **kwargs)
    
    def _compute_score(self, input_data: EvaluationInput):
        # TODO: Implement hybrid scoring
        return {"score": 0.7} 