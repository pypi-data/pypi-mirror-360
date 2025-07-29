"""
Exact match metric implementation.
"""

from ...core.base import BaseMetric
from ...core.types import EvaluationInput


class ExactMatchMetric(BaseMetric):
    """Exact match metric."""
    
    def __init__(self, case_sensitive: bool = False, **kwargs):
        super().__init__(
            name="exact_match",
            description="Exact string match",
            required_inputs=["output_text", "reference_text"],
            **kwargs
        )
        self.case_sensitive = case_sensitive
    
    def _compute_score(self, input_data: EvaluationInput):
        output = input_data.output_text
        reference = input_data.reference_text
        
        if not self.case_sensitive:
            output = output.lower()
            reference = reference.lower()
        
        match = output.strip() == reference.strip()
        return {"score": 1.0 if match else 0.0} 