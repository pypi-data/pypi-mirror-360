"""
BLEU score metric implementation.
"""

from typing import Dict, Any, Union
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.tokenize import word_tokenize

from ...core.base import BaseMetric
from ...core.types import EvaluationInput, MetricResult


class BleuMetric(BaseMetric):
    """
    BLEU (Bilingual Evaluation Understudy) score metric.
    
    Measures n-gram overlap between generated and reference text.
    Higher scores indicate better quality.
    """
    
    def __init__(
        self,
        n_gram: int = 4,
        smoothing: bool = True,
        weights: tuple = None,
        **kwargs
    ):
        super().__init__(
            name="bleu_score",
            description="BLEU score measuring n-gram overlap with reference",
            required_inputs=["output_text", "reference_text"],
            **kwargs
        )
        self.n_gram = n_gram
        self.smoothing = smoothing
        self.weights = weights or tuple(1.0/n_gram for _ in range(n_gram))
        self.smoothing_function = SmoothingFunction().method1 if smoothing else None
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
    
    def _compute_score(self, input_data: EvaluationInput) -> Union[float, Dict[str, Any]]:
        """Compute BLEU score for the input."""
        try:
            # Tokenize texts
            reference_tokens = word_tokenize(input_data.reference_text.lower())
            candidate_tokens = word_tokenize(input_data.output_text.lower())
            
            # Calculate BLEU score
            score = sentence_bleu(
                [reference_tokens],  # BLEU expects list of reference token lists
                candidate_tokens,
                weights=self.weights,
                smoothing_function=self.smoothing_function
            )
            
            # Calculate individual n-gram scores for detailed analysis
            individual_scores = {}
            for n in range(1, min(self.n_gram + 1, len(candidate_tokens) + 1)):
                n_weights = tuple(1.0 if i == n-1 else 0.0 for i in range(self.n_gram))
                individual_scores[f"bleu_{n}"] = sentence_bleu(
                    [reference_tokens],
                    candidate_tokens,
                    weights=n_weights,
                    smoothing_function=self.smoothing_function
                )
            
            return {
                "score": round(score, 4),
                "individual_scores": individual_scores,
                "reference_length": len(reference_tokens),
                "candidate_length": len(candidate_tokens)
            }
            
        except Exception as e:
            return {
                "score": 0.0,
                "error": str(e),
                "reference_length": 0,
                "candidate_length": 0
            }
    
    def evaluate(self, input_data: EvaluationInput) -> MetricResult:
        """Evaluate BLEU score and return structured result."""
        result = super().evaluate(input_data)
        
        # Extract main score for easier access
        if isinstance(result.value, dict) and "score" in result.value:
            result.confidence = self._calculate_confidence(result.value)
            result.explanation = self._generate_explanation(result.value)
        
        return result
    
    def _calculate_confidence(self, score_dict: Dict[str, Any]) -> float:
        """Calculate confidence based on text lengths and n-gram coverage."""
        if "error" in score_dict:
            return 0.0
        
        ref_len = score_dict.get("reference_length", 0)
        cand_len = score_dict.get("candidate_length", 0)
        
        # Confidence decreases with very short texts
        min_len = min(ref_len, cand_len)
        if min_len < 3:
            return 0.3
        elif min_len < 6:
            return 0.6
        elif min_len < 10:
            return 0.8
        else:
            return 0.9
    
    def _generate_explanation(self, score_dict: Dict[str, Any]) -> str:
        """Generate human-readable explanation of the score."""
        if "error" in score_dict:
            return f"BLEU calculation failed: {score_dict['error']}"
        
        score = score_dict.get("score", 0.0)
        ref_len = score_dict.get("reference_length", 0)
        cand_len = score_dict.get("candidate_length", 0)
        
        explanation = f"BLEU score: {score:.3f}. "
        
        if score >= 0.7:
            explanation += "Excellent n-gram overlap with reference."
        elif score >= 0.5:
            explanation += "Good n-gram overlap with reference."
        elif score >= 0.3:
            explanation += "Moderate n-gram overlap with reference."
        elif score >= 0.1:
            explanation += "Low n-gram overlap with reference."
        else:
            explanation += "Very low n-gram overlap with reference."
        
        explanation += f" Reference length: {ref_len}, Generated length: {cand_len}."
        
        # Add length ratio analysis
        if cand_len > 0 and ref_len > 0:
            ratio = cand_len / ref_len
            if ratio < 0.5:
                explanation += " Generated text is significantly shorter."
            elif ratio > 2.0:
                explanation += " Generated text is significantly longer."
            else:
                explanation += " Generated text length is reasonable."
        
        return explanation 