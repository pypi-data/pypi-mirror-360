"""
Semantic similarity metric implementation using sentence transformers.
"""

from typing import Dict, Any, Union, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from ...core.base import BaseMetric
from ...core.types import EvaluationInput, MetricResult


class SemanticSimilarityMetric(BaseMetric):
    """
    Semantic similarity metric using sentence transformers.
    
    Measures semantic similarity between generated and reference text
    using pre-trained sentence embedding models.
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        threshold: Optional[float] = None,
        cache_embeddings: bool = True,
        **kwargs
    ):
        super().__init__(
            name="semantic_similarity",
            description="Semantic similarity using sentence transformers",
            required_inputs=["output_text", "reference_text"],
            **kwargs
        )
        self.model_name = model_name
        self.threshold = threshold
        self.cache_embeddings = cache_embeddings
        self._model = None
        self._embedding_cache = {} if cache_embeddings else None
    
    @property
    def model(self) -> SentenceTransformer:
        """Lazy load the sentence transformer model."""
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text, using cache if enabled."""
        if self.cache_embeddings and text in self._embedding_cache:
            return self._embedding_cache[text]
        
        embedding = self.model.encode([text])[0]
        
        if self.cache_embeddings:
            self._embedding_cache[text] = embedding
        
        return embedding
    
    def _compute_score(self, input_data: EvaluationInput) -> Union[float, Dict[str, Any]]:
        """Compute semantic similarity score."""
        try:
            # Get embeddings
            ref_embedding = self._get_embedding(input_data.reference_text)
            out_embedding = self._get_embedding(input_data.output_text)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(
                ref_embedding.reshape(1, -1),
                out_embedding.reshape(1, -1)
            )[0][0]
            
            # Convert to 0-1 range (cosine similarity can be -1 to 1)
            normalized_similarity = (similarity + 1) / 2
            
            # Calculate additional metrics
            embedding_distance = np.linalg.norm(ref_embedding - out_embedding)
            dot_product = np.dot(ref_embedding, out_embedding)
            
            result = {
                "score": round(float(normalized_similarity), 4),
                "cosine_similarity": round(float(similarity), 4),
                "embedding_distance": round(float(embedding_distance), 4),
                "dot_product": round(float(dot_product), 4),
                "model_name": self.model_name
            }
            
            # Add threshold-based classification if threshold is set
            if self.threshold is not None:
                result["passes_threshold"] = normalized_similarity >= self.threshold
                result["threshold"] = self.threshold
            
            return result
            
        except Exception as e:
            return {
                "score": 0.0,
                "error": str(e),
                "model_name": self.model_name
            }
    
    def evaluate(self, input_data: EvaluationInput) -> MetricResult:
        """Evaluate semantic similarity and return structured result."""
        result = super().evaluate(input_data)
        
        # Add confidence and explanation
        if isinstance(result.value, dict) and "score" in result.value:
            result.confidence = self._calculate_confidence(result.value)
            result.explanation = self._generate_explanation(result.value)
        
        return result
    
    def _calculate_confidence(self, score_dict: Dict[str, Any]) -> float:
        """Calculate confidence based on embedding quality and text characteristics."""
        if "error" in score_dict:
            return 0.0
        
        # Base confidence on the model quality and text length
        confidence = 0.8  # Base confidence for sentence transformers
        
        # Adjust based on cosine similarity magnitude
        cosine_sim = abs(score_dict.get("cosine_similarity", 0.0))
        if cosine_sim > 0.8:
            confidence += 0.1
        elif cosine_sim < 0.2:
            confidence -= 0.2
        
        return max(0.1, min(1.0, confidence))
    
    def _generate_explanation(self, score_dict: Dict[str, Any]) -> str:
        """Generate human-readable explanation of the semantic similarity."""
        if "error" in score_dict:
            return f"Semantic similarity calculation failed: {score_dict['error']}"
        
        score = score_dict.get("score", 0.0)
        cosine_sim = score_dict.get("cosine_similarity", 0.0)
        model_name = score_dict.get("model_name", "unknown")
        
        explanation = f"Semantic similarity: {score:.3f} (cosine: {cosine_sim:.3f}) using {model_name}. "
        
        if score >= 0.9:
            explanation += "Very high semantic similarity - texts are nearly identical in meaning."
        elif score >= 0.8:
            explanation += "High semantic similarity - texts convey very similar meanings."
        elif score >= 0.7:
            explanation += "Good semantic similarity - texts share similar concepts."
        elif score >= 0.6:
            explanation += "Moderate semantic similarity - texts have some shared meaning."
        elif score >= 0.4:
            explanation += "Low semantic similarity - texts have limited shared meaning."
        else:
            explanation += "Very low semantic similarity - texts have different meanings."
        
        # Add threshold information if available
        if "threshold" in score_dict:
            threshold = score_dict["threshold"]
            passes = score_dict.get("passes_threshold", False)
            status = "passes" if passes else "fails"
            explanation += f" {status.capitalize()} threshold of {threshold:.2f}."
        
        return explanation
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        if self._embedding_cache is not None:
            self._embedding_cache.clear()
    
    def get_cache_size(self) -> int:
        """Get the current size of the embedding cache."""
        return len(self._embedding_cache) if self._embedding_cache else 0 