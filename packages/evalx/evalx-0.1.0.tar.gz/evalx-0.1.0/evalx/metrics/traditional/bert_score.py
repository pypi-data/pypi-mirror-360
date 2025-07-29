"""
BERTScore metric implementation.

BERTScore leverages contextual embeddings from BERT to evaluate text similarity
by computing token-level semantic similarity and aggregating to sentence-level scores.
"""

import warnings
from typing import Dict, List, Optional, Tuple, Union

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
import numpy as np

from ...core.base import BaseMetric
from ...core.types import EvaluationInput

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)


class BertScoreMetric(BaseMetric):
    """
    BERTScore metric using contextual embeddings.
    
    BERTScore computes similarity between candidate and reference texts using
    contextual embeddings from pre-trained BERT models. It provides:
    - Token-level semantic similarity
    - Precision, recall, and F1 scores
    - Support for multiple BERT model variants
    
    Args:
        model_type: Pre-trained model name (default: "bert-base-uncased")
        num_layers: Number of layers to use for embeddings (default: 8)
        use_idf: Whether to use inverse document frequency weighting (default: False)
        lang: Language code for model selection (default: "en")
        rescale_with_baseline: Whether to rescale with baseline (default: True)
        device: Device to run model on (default: auto-detect)
        batch_size: Batch size for processing (default: 32)
        max_length: Maximum sequence length (default: 512)
    """
    
    def __init__(
        self,
        model_type: str = "bert-base-uncased",
        num_layers: int = 8,
        use_idf: bool = False,
        lang: str = "en",
        rescale_with_baseline: bool = True,
        device: Optional[str] = None,
        batch_size: int = 32,
        max_length: int = 512,
        **kwargs
    ):
        super().__init__(
            name="bert_score",
            description="BERTScore using contextual embeddings",
            required_inputs=["output_text", "reference_text"],
            **kwargs
        )
        
        self.model_type = model_type
        self.num_layers = num_layers
        self.use_idf = use_idf
        self.lang = lang
        self.rescale_with_baseline = rescale_with_baseline
        self.batch_size = batch_size
        self.max_length = max_length
        
        # Set device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        # Initialize model and tokenizer
        self._model = None
        self._tokenizer = None
        self._model_loaded = False
        
        # Baseline scores for rescaling (computed from common datasets)
        self._baseline_scores = {
            "bert-base-uncased": {"precision": 0.85, "recall": 0.85, "f1": 0.85},
            "bert-large-uncased": {"precision": 0.87, "recall": 0.87, "f1": 0.87},
            "roberta-base": {"precision": 0.86, "recall": 0.86, "f1": 0.86},
            "roberta-large": {"precision": 0.88, "recall": 0.88, "f1": 0.88},
        }
    
    def _load_model(self):
        """Load the BERT model and tokenizer."""
        if self._model_loaded:
            return
        
        try:
            self._tokenizer = AutoTokenizer.from_pretrained(
                self.model_type, 
                do_lower_case=True
            )
            self._model = AutoModel.from_pretrained(self.model_type)
            self._model.to(self.device)
            self._model.eval()
            self._model_loaded = True
            
        except Exception as e:
            raise RuntimeError(f"Failed to load model {self.model_type}: {str(e)}")
    
    def _get_embeddings(self, texts: List[str]) -> torch.Tensor:
        """Get contextual embeddings for texts."""
        if not texts:
            return torch.empty(0, 768)  # Default BERT hidden size
        
        # Tokenize texts
        encoded = self._tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )
        
        # Move to device
        input_ids = encoded["input_ids"].to(self.device)
        attention_mask = encoded["attention_mask"].to(self.device)
        
        # Get embeddings
        with torch.no_grad():
            outputs = self._model(input_ids=input_ids, attention_mask=attention_mask)
            
            # Use specific layer or average of last N layers
            if self.num_layers == 1:
                embeddings = outputs.last_hidden_state
            else:
                # Average last N layers
                hidden_states = outputs.hidden_states[-self.num_layers:]
                embeddings = torch.stack(hidden_states).mean(dim=0)
        
        return embeddings, attention_mask
    
    def _compute_similarity_matrix(
        self, 
        ref_embeddings: torch.Tensor, 
        hyp_embeddings: torch.Tensor,
        ref_mask: torch.Tensor,
        hyp_mask: torch.Tensor
    ) -> torch.Tensor:
        """Compute cosine similarity matrix between reference and hypothesis tokens."""
        # Normalize embeddings
        ref_norm = F.normalize(ref_embeddings, p=2, dim=-1)
        hyp_norm = F.normalize(hyp_embeddings, p=2, dim=-1)
        
        # Compute similarity matrix
        similarity = torch.matmul(ref_norm, hyp_norm.transpose(-2, -1))
        
        # Apply masks to ignore padding tokens
        ref_mask_expanded = ref_mask.unsqueeze(-1).expand_as(similarity)
        hyp_mask_expanded = hyp_mask.unsqueeze(-2).expand_as(similarity)
        mask = ref_mask_expanded & hyp_mask_expanded
        
        # Set masked positions to very low similarity
        similarity = similarity.masked_fill(~mask, -1e9)
        
        return similarity
    
    def _compute_bert_score(
        self, 
        ref_embeddings: torch.Tensor, 
        hyp_embeddings: torch.Tensor,
        ref_mask: torch.Tensor,
        hyp_mask: torch.Tensor
    ) -> Tuple[float, float, float]:
        """Compute BERTScore precision, recall, and F1."""
        # Compute similarity matrix
        similarity = self._compute_similarity_matrix(
            ref_embeddings, hyp_embeddings, ref_mask, hyp_mask
        )
        
        # Compute precision (max similarity for each hypothesis token)
        precision_scores = similarity.max(dim=1)[0]  # Max over reference tokens
        valid_hyp_mask = hyp_mask.bool()
        precision = precision_scores[valid_hyp_mask].mean().item()
        
        # Compute recall (max similarity for each reference token)
        recall_scores = similarity.max(dim=2)[0]  # Max over hypothesis tokens
        valid_ref_mask = ref_mask.bool()
        recall = recall_scores[valid_ref_mask].mean().item()
        
        # Compute F1
        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * precision * recall / (precision + recall)
        
        return precision, recall, f1
    
    def _rescale_scores(
        self, 
        precision: float, 
        recall: float, 
        f1: float
    ) -> Tuple[float, float, float]:
        """Rescale scores using baseline if enabled."""
        if not self.rescale_with_baseline:
            return precision, recall, f1
        
        baseline = self._baseline_scores.get(self.model_type)
        if baseline is None:
            # Use default baseline for unknown models
            baseline = {"precision": 0.85, "recall": 0.85, "f1": 0.85}
        
        # Rescale to [0, 1] range
        precision_rescaled = (precision - baseline["precision"]) / (1 - baseline["precision"])
        recall_rescaled = (recall - baseline["recall"]) / (1 - baseline["recall"])
        f1_rescaled = (f1 - baseline["f1"]) / (1 - baseline["f1"])
        
        # Ensure scores are in [0, 1]
        precision_rescaled = max(0.0, min(1.0, precision_rescaled))
        recall_rescaled = max(0.0, min(1.0, recall_rescaled))
        f1_rescaled = max(0.0, min(1.0, f1_rescaled))
        
        return precision_rescaled, recall_rescaled, f1_rescaled
    
    def _compute_score(self, input_data: EvaluationInput) -> Dict:
        """Compute BERTScore."""
        try:
            # Load model if not already loaded
            self._load_model()
            
            hypothesis_text = input_data.output_text
            reference_text = input_data.reference_text
            
            if not hypothesis_text or not reference_text:
                return {
                    "score": 0.0,
                    "precision": 0.0,
                    "recall": 0.0,
                    "f1": 0.0,
                    "model_type": self.model_type,
                    "rescaled": self.rescale_with_baseline
                }
            
            # Get embeddings
            ref_embeddings, ref_mask = self._get_embeddings([reference_text])
            hyp_embeddings, hyp_mask = self._get_embeddings([hypothesis_text])
            
            # Compute BERTScore
            precision, recall, f1 = self._compute_bert_score(
                ref_embeddings, hyp_embeddings, ref_mask, hyp_mask
            )
            
            # Rescale scores if enabled
            if self.rescale_with_baseline:
                precision, recall, f1 = self._rescale_scores(precision, recall, f1)
            
            return {
                "score": f1,  # F1 as primary score
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "model_type": self.model_type,
                "num_layers": self.num_layers,
                "rescaled": self.rescale_with_baseline,
                "device": str(self.device)
            }
            
        except Exception as e:
            return {
                "score": 0.0,
                "error": str(e),
                "precision": 0.0,
                "recall": 0.0,
                "f1": 0.0,
                "model_type": self.model_type,
                "rescaled": self.rescale_with_baseline
            }
    
    def __del__(self):
        """Cleanup model from memory."""
        if hasattr(self, '_model') and self._model is not None:
            del self._model
        if hasattr(self, '_tokenizer') and self._tokenizer is not None:
            del self._tokenizer
        if torch.cuda.is_available():
            torch.cuda.empty_cache() 