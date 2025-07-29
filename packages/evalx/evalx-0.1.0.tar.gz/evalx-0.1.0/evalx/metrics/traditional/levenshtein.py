"""
Levenshtein distance metric implementation.

Levenshtein distance measures the minimum number of single-character edits
(insertions, deletions, or substitutions) required to transform one string into another.
"""

from typing import Dict, List, Optional, Union
import re

from ...core.base import BaseMetric
from ...core.types import EvaluationInput


class LevenshteinMetric(BaseMetric):
    """
    Levenshtein distance metric.
    
    Computes the edit distance between two strings, with options for:
    - Character-level or word-level distance
    - Normalization by maximum possible distance
    - Case sensitivity control
    - Similarity score (1 - normalized distance)
    
    Args:
        normalize: Whether to normalize by maximum possible distance (default: True)
        case_sensitive: Whether comparison is case sensitive (default: False)
        word_level: Whether to compute word-level distance (default: False)
        return_similarity: Whether to return similarity (1-distance) instead of distance (default: True)
        ignore_punctuation: Whether to ignore punctuation (default: False)
        ignore_whitespace: Whether to ignore extra whitespace (default: True)
    """
    
    def __init__(
        self,
        normalize: bool = True,
        case_sensitive: bool = False,
        word_level: bool = False,
        return_similarity: bool = True,
        ignore_punctuation: bool = False,
        ignore_whitespace: bool = True,
        **kwargs
    ):
        super().__init__(
            name="levenshtein_distance",
            description="Levenshtein edit distance with normalization options",
            required_inputs=["output_text", "reference_text"],
            **kwargs
        )
        
        self.normalize = normalize
        self.case_sensitive = case_sensitive
        self.word_level = word_level
        self.return_similarity = return_similarity
        self.ignore_punctuation = ignore_punctuation
        self.ignore_whitespace = ignore_whitespace
    
    def _preprocess_text(self, text: str) -> Union[str, List[str]]:
        """Preprocess text according to configuration."""
        if not text:
            return "" if not self.word_level else []
        
        # Handle case sensitivity
        if not self.case_sensitive:
            text = text.lower()
        
        # Handle whitespace
        if self.ignore_whitespace:
            text = re.sub(r'\s+', ' ', text.strip())
        
        # Handle punctuation
        if self.ignore_punctuation:
            text = re.sub(r'[^\w\s]', '', text)
        
        # Return as words or characters
        if self.word_level:
            return text.split()
        else:
            return text
    
    def _compute_levenshtein_distance(
        self, 
        s1: Union[str, List[str]], 
        s2: Union[str, List[str]]
    ) -> int:
        """
        Compute Levenshtein distance using dynamic programming.
        
        Args:
            s1: First string/sequence
            s2: Second string/sequence
            
        Returns:
            Edit distance between s1 and s2
        """
        # Convert to lists for uniform handling
        if isinstance(s1, str):
            s1 = list(s1)
        if isinstance(s2, str):
            s2 = list(s2)
        
        len1, len2 = len(s1), len(s2)
        
        # Handle empty strings
        if len1 == 0:
            return len2
        if len2 == 0:
            return len1
        
        # Create distance matrix
        # dp[i][j] = distance between s1[:i] and s2[:j]
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        # Initialize base cases
        for i in range(len1 + 1):
            dp[i][0] = i  # Distance from s1[:i] to empty string
        for j in range(len2 + 1):
            dp[0][j] = j  # Distance from empty string to s2[:j]
        
        # Fill the matrix
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                # Cost of substitution (0 if characters match, 1 if they don't)
                cost = 0 if s1[i-1] == s2[j-1] else 1
                
                # Minimum of three operations
                dp[i][j] = min(
                    dp[i-1][j] + 1,      # Deletion
                    dp[i][j-1] + 1,      # Insertion
                    dp[i-1][j-1] + cost  # Substitution
                )
        
        return dp[len1][len2]
    
    def _compute_normalized_distance(
        self, 
        distance: int, 
        s1: Union[str, List[str]], 
        s2: Union[str, List[str]]
    ) -> float:
        """Compute normalized distance."""
        if not self.normalize:
            return float(distance)
        
        # Get lengths
        len1 = len(s1)
        len2 = len(s2)
        
        # Maximum possible distance is the length of the longer string
        max_distance = max(len1, len2)
        
        if max_distance == 0:
            return 0.0
        
        return distance / max_distance
    
    def _compute_similarity(self, normalized_distance: float) -> float:
        """Convert normalized distance to similarity score."""
        if self.return_similarity:
            return 1.0 - normalized_distance
        else:
            return normalized_distance
    
    def _compute_detailed_analysis(
        self, 
        s1: Union[str, List[str]], 
        s2: Union[str, List[str]]
    ) -> Dict:
        """Compute detailed analysis of the differences."""
        # Convert to lists for analysis
        if isinstance(s1, str):
            s1_list = list(s1)
        else:
            s1_list = s1
        if isinstance(s2, str):
            s2_list = list(s2)
        else:
            s2_list = s2
        
        len1, len2 = len(s1_list), len(s2_list)
        
        # Compute operations needed
        if len1 == 0 and len2 == 0:
            return {
                "insertions": 0,
                "deletions": 0,
                "substitutions": 0,
                "matches": 0
            }
        
        # Create DP table to track operations
        dp = [[0] * (len2 + 1) for _ in range(len1 + 1)]
        
        # Initialize
        for i in range(len1 + 1):
            dp[i][0] = i
        for j in range(len2 + 1):
            dp[0][j] = j
        
        # Fill table
        for i in range(1, len1 + 1):
            for j in range(1, len2 + 1):
                cost = 0 if s1_list[i-1] == s2_list[j-1] else 1
                dp[i][j] = min(
                    dp[i-1][j] + 1,      # Deletion
                    dp[i][j-1] + 1,      # Insertion
                    dp[i-1][j-1] + cost  # Substitution
                )
        
        # Backtrack to count operations
        insertions = deletions = substitutions = matches = 0
        i, j = len1, len2
        
        while i > 0 or j > 0:
            if i > 0 and j > 0:
                if s1_list[i-1] == s2_list[j-1]:
                    matches += 1
                    i -= 1
                    j -= 1
                elif dp[i][j] == dp[i-1][j-1] + 1:
                    substitutions += 1
                    i -= 1
                    j -= 1
                elif dp[i][j] == dp[i-1][j] + 1:
                    deletions += 1
                    i -= 1
                else:
                    insertions += 1
                    j -= 1
            elif i > 0:
                deletions += 1
                i -= 1
            else:
                insertions += 1
                j -= 1
        
        return {
            "insertions": insertions,
            "deletions": deletions,
            "substitutions": substitutions,
            "matches": matches
        }
    
    def _compute_score(self, input_data: EvaluationInput) -> Dict:
        """Compute Levenshtein distance/similarity score."""
        try:
            output_text = input_data.output_text
            reference_text = input_data.reference_text
            
            if output_text is None or reference_text is None:
                return {
                    "score": 0.0,
                    "distance": float('inf'),
                    "normalized_distance": 1.0,
                    "similarity": 0.0,
                    "output_length": 0,
                    "reference_length": 0,
                    "operations": {
                        "insertions": 0,
                        "deletions": 0,
                        "substitutions": 0,
                        "matches": 0
                    }
                }
            
            # Preprocess texts
            s1 = self._preprocess_text(output_text)
            s2 = self._preprocess_text(reference_text)
            
            # Compute distance
            distance = self._compute_levenshtein_distance(s1, s2)
            
            # Normalize distance
            normalized_distance = self._compute_normalized_distance(distance, s1, s2)
            
            # Compute similarity
            similarity = self._compute_similarity(normalized_distance)
            
            # Detailed analysis
            operations = self._compute_detailed_analysis(s1, s2)
            
            # Determine primary score
            primary_score = similarity if self.return_similarity else normalized_distance
            
            return {
                "score": primary_score,
                "distance": distance,
                "normalized_distance": normalized_distance,
                "similarity": similarity,
                "output_length": len(s1),
                "reference_length": len(s2),
                "operations": operations,
                "config": {
                    "normalize": self.normalize,
                    "case_sensitive": self.case_sensitive,
                    "word_level": self.word_level,
                    "return_similarity": self.return_similarity,
                    "ignore_punctuation": self.ignore_punctuation,
                    "ignore_whitespace": self.ignore_whitespace
                }
            }
            
        except Exception as e:
            return {
                "score": 0.0,
                "error": str(e),
                "distance": float('inf'),
                "normalized_distance": 1.0,
                "similarity": 0.0,
                "output_length": 0,
                "reference_length": 0,
                "operations": {
                    "insertions": 0,
                    "deletions": 0,
                    "substitutions": 0,
                    "matches": 0
                }
            } 