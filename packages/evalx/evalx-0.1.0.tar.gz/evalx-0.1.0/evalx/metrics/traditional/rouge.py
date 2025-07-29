"""
ROUGE score metric implementation.
"""

from typing import Dict, Any, Union, List
from rouge_score import rouge_scorer

from ...core.base import BaseMetric
from ...core.types import EvaluationInput


class RougeMetric(BaseMetric):
    """
    ROUGE (Recall-Oriented Understudy for Gisting Evaluation) score metric.
    
    Measures recall-oriented n-gram overlap between generated and reference text.
    """
    
    def __init__(
        self,
        rouge_types: List[str] = None,
        use_stemmer: bool = True,
        **kwargs
    ):
        super().__init__(
            name="rouge_score",
            description="ROUGE score measuring recall-oriented n-gram overlap",
            required_inputs=["output_text", "reference_text"],
            **kwargs
        )
        self.rouge_types = rouge_types or ["rouge1", "rouge2", "rougeL"]
        self.use_stemmer = use_stemmer
        self.scorer = rouge_scorer.RougeScorer(self.rouge_types, use_stemmer=use_stemmer)
    
    def _compute_score(self, input_data: EvaluationInput) -> Union[float, Dict[str, Any]]:
        """Compute ROUGE scores for the input."""
        try:
            scores = self.scorer.score(input_data.reference_text, input_data.output_text)
            
            # Extract F1 scores for each ROUGE type
            rouge_scores = {}
            for rouge_type in self.rouge_types:
                if rouge_type in scores:
                    rouge_scores[rouge_type] = {
                        "precision": round(scores[rouge_type].precision, 4),
                        "recall": round(scores[rouge_type].recall, 4),
                        "fmeasure": round(scores[rouge_type].fmeasure, 4)
                    }
            
            # Calculate average F1 score
            avg_f1 = sum(
                rouge_scores[rt]["fmeasure"] for rt in self.rouge_types if rt in rouge_scores
            ) / len(self.rouge_types)
            
            return {
                "score": round(avg_f1, 4),
                "individual_scores": rouge_scores,
                "rouge_types": self.rouge_types
            }
            
        except Exception as e:
            return {
                "score": 0.0,
                "error": str(e),
                "rouge_types": self.rouge_types
            } 