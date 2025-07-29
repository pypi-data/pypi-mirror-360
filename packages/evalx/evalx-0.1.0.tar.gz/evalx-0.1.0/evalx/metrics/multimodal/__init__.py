"""
Multimodal evaluation metrics for EvalX.

This module provides metrics for evaluating multimodal AI systems including
vision-language models, audio processing, and code generation.
"""

from typing import Dict, List, Any, Optional, Union
import numpy as np
from PIL import Image
import torch
from transformers import CLIPProcessor, CLIPModel
import cv2
import librosa
from dataclasses import dataclass

from ...core.base import BaseMetric
from ...core.types import EvaluationInput, MetricResult


@dataclass
class MultimodalInput(EvaluationInput):
    """Extended input for multimodal evaluation."""
    image: Optional[Union[Image.Image, np.ndarray, str]] = None  # PIL Image, numpy array, or path
    audio: Optional[Union[np.ndarray, str]] = None  # Audio array or path
    code: Optional[str] = None  # Code string
    video: Optional[Union[np.ndarray, str]] = None  # Video array or path
    
    def load_image(self) -> Optional[Image.Image]:
        """Load image from various formats."""
        if self.image is None:
            return None
        
        if isinstance(self.image, str):
            return Image.open(self.image)
        elif isinstance(self.image, np.ndarray):
            return Image.fromarray(self.image)
        elif isinstance(self.image, Image.Image):
            return self.image
        else:
            raise ValueError(f"Unsupported image type: {type(self.image)}")
    
    def load_audio(self) -> Optional[np.ndarray]:
        """Load audio from various formats."""
        if self.audio is None:
            return None
        
        if isinstance(self.audio, str):
            audio, _ = librosa.load(self.audio, sr=22050)
            return audio
        elif isinstance(self.audio, np.ndarray):
            return self.audio
        else:
            raise ValueError(f"Unsupported audio type: {type(self.audio)}")


class ImageTextAlignmentMetric(BaseMetric):
    """Evaluates alignment between images and text using CLIP."""
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        super().__init__(
            name="image_text_alignment",
            description="Measures semantic alignment between images and text using CLIP embeddings",
            required_inputs=["image", "output_text"]
        )
        self.model = CLIPModel.from_pretrained(model_name)
        self.processor = CLIPProcessor.from_pretrained(model_name)
    
    def _compute_score(self, input_data: MultimodalInput) -> Dict[str, float]:
        """Compute CLIP similarity score."""
        image = input_data.load_image()
        if image is None or not input_data.output_text:
            return {"alignment_score": 0.0, "confidence": 0.0}
        
        # Process inputs
        inputs = self.processor(
            text=[input_data.output_text],
            images=[image],
            return_tensors="pt",
            padding=True
        )
        
        # Get embeddings
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits_per_image = outputs.logits_per_image
            probs = logits_per_image.softmax(dim=1)
        
        alignment_score = float(probs[0][0])
        
        return {
            "alignment_score": alignment_score,
            "confidence": min(alignment_score * 2, 1.0),  # Confidence heuristic
            "clip_logit": float(logits_per_image[0][0])
        }


class ImageCaptionQualityMetric(BaseMetric):
    """Evaluates quality of image captions using multiple criteria."""
    
    def __init__(self):
        super().__init__(
            name="image_caption_quality",
            description="Comprehensive evaluation of image caption quality",
            required_inputs=["image", "output_text"]
        )
        self.clip_metric = ImageTextAlignmentMetric()
    
    def _compute_score(self, input_data: MultimodalInput) -> Dict[str, float]:
        """Compute comprehensive caption quality score."""
        if not input_data.output_text:
            return {"overall_quality": 0.0}
        
        # Get CLIP alignment
        clip_scores = self.clip_metric._compute_score(input_data)
        
        # Analyze caption properties
        caption = input_data.output_text.strip()
        
        # Length appropriateness (penalize too short/long)
        length_score = self._evaluate_length(caption)
        
        # Descriptiveness (presence of adjectives, specific nouns)
        descriptiveness_score = self._evaluate_descriptiveness(caption)
        
        # Grammatical correctness (basic heuristics)
        grammar_score = self._evaluate_grammar(caption)
        
        # Combine scores
        overall_quality = (
            clip_scores["alignment_score"] * 0.4 +
            length_score * 0.2 +
            descriptiveness_score * 0.2 +
            grammar_score * 0.2
        )
        
        return {
            "overall_quality": overall_quality,
            "alignment_score": clip_scores["alignment_score"],
            "length_score": length_score,
            "descriptiveness_score": descriptiveness_score,
            "grammar_score": grammar_score,
            "word_count": len(caption.split())
        }
    
    def _evaluate_length(self, caption: str) -> float:
        """Evaluate caption length appropriateness."""
        word_count = len(caption.split())
        if 5 <= word_count <= 20:
            return 1.0
        elif 3 <= word_count <= 30:
            return 0.8
        elif word_count < 3:
            return 0.3
        else:
            return max(0.1, 1.0 - (word_count - 30) * 0.02)
    
    def _evaluate_descriptiveness(self, caption: str) -> float:
        """Evaluate descriptiveness of caption."""
        words = caption.lower().split()
        
        # Count descriptive elements
        adjectives = sum(1 for word in words if word.endswith(('ing', 'ed', 'ly', 'ful', 'ous')))
        specific_nouns = sum(1 for word in words if len(word) > 4 and word.isalpha())
        
        descriptiveness = min(1.0, (adjectives + specific_nouns) / len(words) * 3)
        return descriptiveness
    
    def _evaluate_grammar(self, caption: str) -> float:
        """Basic grammar evaluation."""
        # Simple heuristics
        if not caption:
            return 0.0
        
        # Check capitalization
        starts_with_capital = caption[0].isupper()
        
        # Check punctuation
        ends_with_punctuation = caption[-1] in '.!?'
        
        # Check for basic sentence structure
        has_verb = any(word.endswith(('s', 'ed', 'ing')) for word in caption.split())
        
        score = (starts_with_capital + ends_with_punctuation + has_verb) / 3
        return score


class CodeCorrectnessMetric(BaseMetric):
    """Evaluates code correctness through execution and analysis."""
    
    def __init__(self, timeout: float = 5.0):
        super().__init__(
            name="code_correctness",
            description="Evaluates code correctness through execution and static analysis",
            required_inputs=["code", "input_text"]
        )
        self.timeout = timeout
    
    def _compute_score(self, input_data: MultimodalInput) -> Dict[str, float]:
        """Compute code correctness score."""
        if not input_data.code:
            return {"correctness_score": 0.0}
        
        # Syntax check
        syntax_score = self._check_syntax(input_data.code)
        
        # Execution check (if test cases provided)
        execution_score = self._check_execution(input_data.code, input_data.input_text)
        
        # Static analysis
        static_score = self._static_analysis(input_data.code)
        
        # Security analysis
        security_score = self._security_analysis(input_data.code)
        
        # Combine scores
        overall_score = (
            syntax_score * 0.3 +
            execution_score * 0.4 +
            static_score * 0.2 +
            security_score * 0.1
        )
        
        return {
            "correctness_score": overall_score,
            "syntax_score": syntax_score,
            "execution_score": execution_score,
            "static_analysis_score": static_score,
            "security_score": security_score
        }
    
    def _check_syntax(self, code: str) -> float:
        """Check if code has valid syntax."""
        try:
            compile(code, '<string>', 'exec')
            return 1.0
        except SyntaxError:
            return 0.0
        except Exception:
            return 0.5  # Other compilation issues
    
    def _check_execution(self, code: str, test_input: Optional[str]) -> float:
        """Check if code executes without errors."""
        try:
            # Create a restricted execution environment
            exec_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'list': list,
                    'dict': dict,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'sum': sum,
                    'max': max,
                    'min': min,
                }
            }
            
            exec(code, exec_globals)
            return 1.0
        except Exception as e:
            # Partial credit for specific error types
            if isinstance(e, (NameError, AttributeError)):
                return 0.3
            elif isinstance(e, (TypeError, ValueError)):
                return 0.5
            else:
                return 0.0
    
    def _static_analysis(self, code: str) -> float:
        """Perform basic static analysis."""
        lines = code.split('\n')
        score = 1.0
        
        # Check for best practices
        if not any('def ' in line for line in lines):
            score -= 0.2  # No function definitions
        
        if not any('#' in line for line in lines):
            score -= 0.1  # No comments
        
        # Check for common issues
        if 'eval(' in code or 'exec(' in code:
            score -= 0.3  # Dangerous functions
        
        return max(0.0, score)
    
    def _security_analysis(self, code: str) -> float:
        """Basic security analysis."""
        dangerous_patterns = [
            'import os', 'import sys', 'import subprocess',
            'open(', 'file(', '__import__',
            'eval(', 'exec(', 'compile(',
            'input(', 'raw_input('
        ]
        
        security_score = 1.0
        for pattern in dangerous_patterns:
            if pattern in code:
                security_score -= 0.2
        
        return max(0.0, security_score)


class AudioQualityMetric(BaseMetric):
    """Evaluates audio quality using signal processing metrics."""
    
    def __init__(self):
        super().__init__(
            name="audio_quality",
            description="Evaluates audio quality using signal processing metrics",
            required_inputs=["audio"]
        )
    
    def _compute_score(self, input_data: MultimodalInput) -> Dict[str, float]:
        """Compute audio quality metrics."""
        audio = input_data.load_audio()
        if audio is None:
            return {"quality_score": 0.0}
        
        # Signal-to-noise ratio
        snr = self._calculate_snr(audio)
        
        # Dynamic range
        dynamic_range = self._calculate_dynamic_range(audio)
        
        # Spectral centroid (brightness)
        spectral_centroid = self._calculate_spectral_centroid(audio)
        
        # Zero crossing rate (speech quality indicator)
        zcr = self._calculate_zcr(audio)
        
        # Normalize and combine metrics
        snr_score = min(1.0, max(0.0, (snr + 20) / 40))  # Normalize SNR
        dr_score = min(1.0, dynamic_range / 60)  # Normalize dynamic range
        sc_score = min(1.0, spectral_centroid / 4000)  # Normalize spectral centroid
        zcr_score = min(1.0, zcr * 10)  # Normalize ZCR
        
        overall_quality = (snr_score + dr_score + sc_score + zcr_score) / 4
        
        return {
            "quality_score": overall_quality,
            "snr": snr,
            "dynamic_range": dynamic_range,
            "spectral_centroid": spectral_centroid,
            "zero_crossing_rate": zcr,
            "snr_score": snr_score,
            "dynamic_range_score": dr_score,
            "spectral_centroid_score": sc_score,
            "zcr_score": zcr_score
        }
    
    def _calculate_snr(self, audio: np.ndarray) -> float:
        """Calculate signal-to-noise ratio."""
        # Simple SNR calculation
        signal_power = np.mean(audio ** 2)
        noise_power = np.var(audio - np.mean(audio))
        
        if noise_power == 0:
            return 60.0  # Very high SNR
        
        snr = 10 * np.log10(signal_power / noise_power)
        return float(snr)
    
    def _calculate_dynamic_range(self, audio: np.ndarray) -> float:
        """Calculate dynamic range."""
        max_amplitude = np.max(np.abs(audio))
        min_amplitude = np.min(np.abs(audio[audio != 0]))
        
        if min_amplitude == 0:
            return 60.0  # Maximum dynamic range
        
        dynamic_range = 20 * np.log10(max_amplitude / min_amplitude)
        return float(dynamic_range)
    
    def _calculate_spectral_centroid(self, audio: np.ndarray) -> float:
        """Calculate spectral centroid."""
        spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=22050)[0]
        return float(np.mean(spectral_centroids))
    
    def _calculate_zcr(self, audio: np.ndarray) -> float:
        """Calculate zero crossing rate."""
        zcr = librosa.feature.zero_crossing_rate(audio)[0]
        return float(np.mean(zcr))


# Export all multimodal metrics
__all__ = [
    "MultimodalInput",
    "ImageTextAlignmentMetric",
    "ImageCaptionQualityMetric",
    "CodeCorrectnessMetric",
    "AudioQualityMetric",
] 