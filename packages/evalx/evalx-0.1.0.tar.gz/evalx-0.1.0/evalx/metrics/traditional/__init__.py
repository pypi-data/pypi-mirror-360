"""
Traditional evaluation metrics implementation.

This module provides implementations of established NLP evaluation metrics
like BLEU, ROUGE, METEOR, semantic similarity, and others.
"""

from .bleu import BleuMetric
from .rouge import RougeMetric
from .meteor import MeteorMetric
from .semantic_similarity import SemanticSimilarityMetric
from .bert_score import BertScoreMetric
from .exact_match import ExactMatchMetric
from .levenshtein import LevenshteinMetric

class TraditionalMetrics:
    """Factory class for creating traditional evaluation metrics."""
    
    @staticmethod
    def bleu_score(n_gram: int = 4, smoothing: bool = True, **kwargs):
        """Create BLEU score metric."""
        return BleuMetric(n_gram=n_gram, smoothing=smoothing, **kwargs)
    
    @staticmethod
    def rouge_score(rouge_types: list = None, use_stemmer: bool = True, **kwargs):
        """Create ROUGE score metric."""
        if rouge_types is None:
            rouge_types = ["rouge1", "rouge2", "rougeL"]
        return RougeMetric(rouge_types=rouge_types, use_stemmer=use_stemmer, **kwargs)
    
    @staticmethod
    def meteor_score(**kwargs):
        """Create METEOR score metric."""
        return MeteorMetric(**kwargs)
    
    @staticmethod
    def semantic_similarity(model_name: str = "all-MiniLM-L6-v2", threshold: float = None, **kwargs):
        """Create semantic similarity metric."""
        return SemanticSimilarityMetric(model_name=model_name, threshold=threshold, **kwargs)
    
    @staticmethod
    def bert_score(model_type: str = "bert-base-uncased", **kwargs):
        """Create BERTScore metric."""
        return BertScoreMetric(model_type=model_type, **kwargs)
    
    @staticmethod
    def exact_match(case_sensitive: bool = False, **kwargs):
        """Create exact match metric."""
        return ExactMatchMetric(case_sensitive=case_sensitive, **kwargs)
    
    @staticmethod
    def levenshtein_distance(normalize: bool = True, **kwargs):
        """Create Levenshtein distance metric."""
        return LevenshteinMetric(normalize=normalize, **kwargs)

__all__ = [
    "TraditionalMetrics",
    "BleuMetric",
    "RougeMetric", 
    "MeteorMetric",
    "SemanticSimilarityMetric",
    "BertScoreMetric",
    "ExactMatchMetric",
    "LevenshteinMetric",
] 