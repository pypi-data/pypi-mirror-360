"""
Structured output parser for LLM responses.
"""

import json
import re
from typing import Dict, Any


class StructuredOutputParser:
    """Parses structured output from LLM responses."""
    
    def __init__(self, scale: str = "binary"):
        self.scale = scale
    
    def get_format_instructions(self) -> str:
        """Get format instructions for the LLM."""
        if self.scale == "binary":
            return "Respond with a JSON object: {\"score\": <0 or 1>, \"reasoning\": \"<explanation>\"}"
        elif self.scale == "continuous":
            return "Respond with a JSON object: {\"score\": <number between 0.0 and 1.0>, \"reasoning\": \"<explanation>\"}"
        else:
            return "Respond with a JSON object: {\"score\": <your score>, \"reasoning\": \"<explanation>\"}"
    
    def parse(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured format."""
        try:
            # Try to parse as JSON first
            if "{" in response and "}" in response:
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group()
                    parsed = json.loads(json_str)
                    return parsed
            
            # Fallback: extract score and use full response as reasoning
            score = self._extract_score(response)
            return {
                "score": score,
                "reasoning": response
            }
            
        except Exception:
            # Final fallback
            score = self._extract_score(response)
            return {
                "score": score,
                "reasoning": response
            }
    
    def _extract_score(self, response: str) -> float:
        """Extract numeric score from response."""
        # Look for decimal numbers
        numbers = re.findall(r'\b0?\.\d+\b|\b[01]\b', response)
        if numbers:
            try:
                score = float(numbers[0])
                if 0 <= score <= 1:
                    return score
            except ValueError:
                pass
        
        # Look for integers on a scale
        integers = re.findall(r'\b([1-9]|10)\b', response)
        if integers:
            try:
                score = int(integers[0])
                if score <= 5:
                    return (score - 1) / 4  # 1-5 scale
                else:
                    return (score - 1) / 9  # 1-10 scale
            except ValueError:
                pass
        
        return 0.0  # Default 