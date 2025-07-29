"""
METEOR score metric implementation.

METEOR (Metric for Evaluation of Translation with Explicit ORdering) is a metric
for machine translation evaluation that considers unigram matching, stemming,
synonymy, and word order.
"""

import re
from typing import Dict, List, Optional, Set, Tuple
from collections import defaultdict

from ...core.base import BaseMetric
from ...core.types import EvaluationInput

try:
    import nltk
    from nltk.corpus import wordnet
    from nltk.stem import PorterStemmer
    from nltk.tokenize import word_tokenize
    
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)
        
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


class MeteorMetric(BaseMetric):
    """
    METEOR score metric.
    
    METEOR evaluates translation quality by considering:
    1. Exact word matches
    2. Stemmed word matches  
    3. Synonym matches
    4. Word order via fragmentation penalty
    
    Args:
        alpha: Weight for precision vs recall (default: 0.9)
        beta: Weight for fragmentation penalty (default: 3.0)
        gamma: Weight for exact/stem/synonym matches (default: 0.5)
        use_stemming: Whether to use stemming (default: True)
        use_synonyms: Whether to use synonyms (default: True)
        language: Language for tokenization (default: 'english')
    """
    
    def __init__(
        self,
        alpha: float = 0.9,
        beta: float = 3.0,
        gamma: float = 0.5,
        use_stemming: bool = True,
        use_synonyms: bool = True,
        language: str = 'english',
        **kwargs
    ):
        super().__init__(
            name="meteor_score",
            description="METEOR score with stemming and synonym matching",
            required_inputs=["output_text", "reference_text"],
            **kwargs
        )
        
        if not NLTK_AVAILABLE:
            raise ImportError(
                "NLTK is required for METEOR metric. Install with: pip install nltk"
            )
        
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.use_stemming = use_stemming
        self.use_synonyms = use_synonyms
        self.language = language
        
        # Initialize stemmer
        self.stemmer = PorterStemmer() if use_stemming else None
    
    def _preprocess_text(self, text: str) -> List[str]:
        """Preprocess text by tokenizing and lowercasing."""
        if not text:
            return []
        
        # Tokenize and lowercase
        tokens = word_tokenize(text.lower(), language=self.language)
        
        # Remove punctuation and empty tokens
        tokens = [token for token in tokens if token.isalnum()]
        
        return tokens
    
    def _get_stems(self, tokens: List[str]) -> List[str]:
        """Get stemmed versions of tokens."""
        if not self.stemmer or not tokens:
            return tokens
        
        return [self.stemmer.stem(token) for token in tokens]
    
    def _get_synonyms(self, word: str) -> Set[str]:
        """Get synonyms for a word using WordNet."""
        if not self.use_synonyms:
            return set()
        
        synonyms = set()
        try:
            for syn in wordnet.synsets(word):
                for lemma in syn.lemmas():
                    synonyms.add(lemma.name().lower().replace('_', ' '))
        except Exception:
            pass
        
        return synonyms
    
    def _find_alignments(
        self, 
        hypothesis: List[str], 
        reference: List[str]
    ) -> Tuple[List[Tuple[int, int]], int]:
        """
        Find word alignments between hypothesis and reference.
        
        Returns:
            alignments: List of (hyp_idx, ref_idx) tuples
            matches: Number of matched words
        """
        h_len = len(hypothesis)
        r_len = len(reference)
        
        if h_len == 0 or r_len == 0:
            return [], 0
        
        # Create alignment matrix
        alignments = []
        h_matched = [False] * h_len
        r_matched = [False] * r_len
        
        # Stage 1: Exact matches
        for i, h_word in enumerate(hypothesis):
            if h_matched[i]:
                continue
            for j, r_word in enumerate(reference):
                if r_matched[j]:
                    continue
                if h_word == r_word:
                    alignments.append((i, j))
                    h_matched[i] = True
                    r_matched[j] = True
                    break
        
        # Stage 2: Stem matches (if enabled)
        if self.use_stemming and self.stemmer:
            h_stems = self._get_stems(hypothesis)
            r_stems = self._get_stems(reference)
            
            for i, h_stem in enumerate(h_stems):
                if h_matched[i]:
                    continue
                for j, r_stem in enumerate(r_stems):
                    if r_matched[j]:
                        continue
                    if h_stem == r_stem:
                        alignments.append((i, j))
                        h_matched[i] = True
                        r_matched[j] = True
                        break
        
        # Stage 3: Synonym matches (if enabled)
        if self.use_synonyms:
            for i, h_word in enumerate(hypothesis):
                if h_matched[i]:
                    continue
                h_synonyms = self._get_synonyms(h_word)
                for j, r_word in enumerate(reference):
                    if r_matched[j]:
                        continue
                    r_synonyms = self._get_synonyms(r_word)
                    
                    # Check if words are synonyms
                    if (h_word in r_synonyms or r_word in h_synonyms or 
                        bool(h_synonyms & r_synonyms)):
                        alignments.append((i, j))
                        h_matched[i] = True
                        r_matched[j] = True
                        break
        
        return alignments, len(alignments)
    
    def _calculate_fragmentation(self, alignments: List[Tuple[int, int]]) -> float:
        """Calculate fragmentation penalty based on alignment order."""
        if len(alignments) <= 1:
            return 0.0
        
        # Sort alignments by hypothesis position
        sorted_alignments = sorted(alignments, key=lambda x: x[0])
        
        # Count chunks (consecutive alignments)
        chunks = 1
        for i in range(1, len(sorted_alignments)):
            # If reference positions are not consecutive, it's a new chunk
            if sorted_alignments[i][1] != sorted_alignments[i-1][1] + 1:
                chunks += 1
        
        # Fragmentation penalty
        return chunks / len(alignments)
    
    def _compute_score(self, input_data: EvaluationInput) -> Dict:
        """Compute METEOR score."""
        try:
            hypothesis_text = input_data.output_text
            reference_text = input_data.reference_text
            
            if not hypothesis_text or not reference_text:
                return {
                    "score": 0.0,
                    "precision": 0.0,
                    "recall": 0.0,
                    "f_mean": 0.0,
                    "fragmentation": 0.0,
                    "matches": 0,
                    "hypothesis_length": 0,
                    "reference_length": 0
                }
            
            # Preprocess texts
            hypothesis = self._preprocess_text(hypothesis_text)
            reference = self._preprocess_text(reference_text)
            
            h_len = len(hypothesis)
            r_len = len(reference)
            
            if h_len == 0 or r_len == 0:
                return {
                    "score": 0.0,
                    "precision": 0.0,
                    "recall": 0.0,
                    "f_mean": 0.0,
                    "fragmentation": 0.0,
                    "matches": 0,
                    "hypothesis_length": h_len,
                    "reference_length": r_len
                }
            
            # Find alignments
            alignments, matches = self._find_alignments(hypothesis, reference)
            
            # Calculate precision and recall
            precision = matches / h_len if h_len > 0 else 0.0
            recall = matches / r_len if r_len > 0 else 0.0
            
            # Calculate F-mean
            if precision + recall == 0:
                f_mean = 0.0
            else:
                f_mean = (precision * recall) / (self.alpha * precision + (1 - self.alpha) * recall)
            
            # Calculate fragmentation penalty
            fragmentation = self._calculate_fragmentation(alignments)
            
            # Calculate final METEOR score
            penalty = self.gamma * (fragmentation ** self.beta)
            meteor_score = f_mean * (1 - penalty)
            
            return {
                "score": max(0.0, meteor_score),  # Ensure non-negative
                "precision": precision,
                "recall": recall,
                "f_mean": f_mean,
                "fragmentation": fragmentation,
                "penalty": penalty,
                "matches": matches,
                "hypothesis_length": h_len,
                "reference_length": r_len,
                "alignments": len(alignments)
            }
            
        except Exception as e:
            return {
                "score": 0.0,
                "error": str(e),
                "precision": 0.0,
                "recall": 0.0,
                "f_mean": 0.0,
                "fragmentation": 0.0,
                "matches": 0,
                "hypothesis_length": 0,
                "reference_length": 0
            } 