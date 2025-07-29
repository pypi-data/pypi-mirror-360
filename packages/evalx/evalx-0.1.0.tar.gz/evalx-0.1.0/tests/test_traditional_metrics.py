"""
Comprehensive unit tests for traditional metrics.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from evalx.core.types import EvaluationInput
from evalx.metrics.traditional.meteor import MeteorMetric
from evalx.metrics.traditional.bert_score import BertScoreMetric
from evalx.metrics.traditional.levenshtein import LevenshteinMetric
from evalx.metrics.traditional.bleu import BleuMetric
from evalx.metrics.traditional.rouge import RougeMetric
from evalx.metrics.traditional.exact_match import ExactMatchMetric
from evalx.metrics.traditional.semantic_similarity import SemanticSimilarityMetric


class TestMeteorMetric:
    """Test METEOR metric implementation."""
    
    def test_meteor_initialization(self):
        """Test METEOR metric initialization."""
        metric = MeteorMetric()
        assert metric.name == "meteor_score"
        assert metric.alpha == 0.9
        assert metric.beta == 3.0
        assert metric.gamma == 0.5
        assert metric.use_stemming is True
        assert metric.use_synonyms is True
    
    def test_meteor_custom_parameters(self):
        """Test METEOR with custom parameters."""
        metric = MeteorMetric(
            alpha=0.8,
            beta=2.0,
            gamma=0.3,
            use_stemming=False,
            use_synonyms=False
        )
        assert metric.alpha == 0.8
        assert metric.beta == 2.0
        assert metric.gamma == 0.3
        assert metric.use_stemming is False
        assert metric.use_synonyms is False
    
    def test_meteor_preprocess_text(self):
        """Test text preprocessing."""
        metric = MeteorMetric()
        
        # Test normal text
        tokens = metric._preprocess_text("Hello world!")
        assert tokens == ["hello", "world"]
        
        # Test empty text
        tokens = metric._preprocess_text("")
        assert tokens == []
        
        # Test text with punctuation
        tokens = metric._preprocess_text("Hello, world! How are you?")
        assert tokens == ["hello", "world", "how", "are", "you"]
    
    def test_meteor_exact_match(self):
        """Test METEOR with exact match."""
        metric = MeteorMetric()
        input_data = EvaluationInput(
            output_text="The cat sat on the mat",
            reference_text="The cat sat on the mat"
        )
        
        result = metric.evaluate(input_data)
        assert result.score == 1.0  # Perfect match
        assert result.details["precision"] == 1.0
        assert result.details["recall"] == 1.0
        assert result.details["matches"] == 6
    
    def test_meteor_partial_match(self):
        """Test METEOR with partial match."""
        metric = MeteorMetric()
        input_data = EvaluationInput(
            output_text="The cat sat",
            reference_text="The cat sat on the mat"
        )
        
        result = metric.evaluate(input_data)
        assert 0.0 < result.score < 1.0
        assert result.details["matches"] == 3
        assert result.details["precision"] == 1.0  # All output words match
        assert result.details["recall"] < 1.0  # Not all reference words match
    
    def test_meteor_no_match(self):
        """Test METEOR with no match."""
        metric = MeteorMetric()
        input_data = EvaluationInput(
            output_text="dog",
            reference_text="cat"
        )
        
        result = metric.evaluate(input_data)
        assert result.score == 0.0
        assert result.details["matches"] == 0
        assert result.details["precision"] == 0.0
        assert result.details["recall"] == 0.0
    
    def test_meteor_empty_inputs(self):
        """Test METEOR with empty inputs."""
        metric = MeteorMetric()
        
        # Empty output
        input_data = EvaluationInput(
            output_text="",
            reference_text="The cat sat"
        )
        result = metric.evaluate(input_data)
        assert result.score == 0.0
        
        # Empty reference
        input_data = EvaluationInput(
            output_text="The cat sat",
            reference_text=""
        )
        result = metric.evaluate(input_data)
        assert result.score == 0.0
    
    @patch('evalx.metrics.traditional.meteor.NLTK_AVAILABLE', False)
    def test_meteor_nltk_not_available(self):
        """Test METEOR when NLTK is not available."""
        with pytest.raises(ImportError):
            MeteorMetric()


class TestBertScoreMetric:
    """Test BERTScore metric implementation."""
    
    def test_bertscore_initialization(self):
        """Test BERTScore initialization."""
        metric = BertScoreMetric()
        assert metric.name == "bert_score"
        assert metric.model_type == "bert-base-uncased"
        assert metric.num_layers == 8
        assert metric.rescale_with_baseline is True
    
    def test_bertscore_custom_parameters(self):
        """Test BERTScore with custom parameters."""
        metric = BertScoreMetric(
            model_type="roberta-base",
            num_layers=12,
            rescale_with_baseline=False
        )
        assert metric.model_type == "roberta-base"
        assert metric.num_layers == 12
        assert metric.rescale_with_baseline is False
    
    @patch('evalx.metrics.traditional.bert_score.AutoTokenizer')
    @patch('evalx.metrics.traditional.bert_score.AutoModel')
    def test_bertscore_model_loading(self, mock_model, mock_tokenizer):
        """Test model loading."""
        mock_tokenizer.from_pretrained.return_value = Mock()
        mock_model_instance = Mock()
        mock_model.from_pretrained.return_value = mock_model_instance
        
        metric = BertScoreMetric()
        metric._load_model()
        
        assert metric._model_loaded is True
        mock_tokenizer.from_pretrained.assert_called_once()
        mock_model.from_pretrained.assert_called_once()
        mock_model_instance.to.assert_called_once()
        mock_model_instance.eval.assert_called_once()
    
    @patch('evalx.metrics.traditional.bert_score.AutoTokenizer')
    @patch('evalx.metrics.traditional.bert_score.AutoModel')
    def test_bertscore_identical_texts(self, mock_model, mock_tokenizer):
        """Test BERTScore with identical texts."""
        # Mock tokenizer
        mock_tokenizer_instance = Mock()
        mock_tokenizer_instance.return_value = {
            'input_ids': Mock(),
            'attention_mask': Mock()
        }
        mock_tokenizer.from_pretrained.return_value = mock_tokenizer_instance
        
        # Mock model
        mock_model_instance = Mock()
        mock_outputs = Mock()
        mock_outputs.last_hidden_state = Mock()
        mock_model_instance.return_value = mock_outputs
        mock_model.from_pretrained.return_value = mock_model_instance
        
        metric = BertScoreMetric()
        input_data = EvaluationInput(
            output_text="The cat sat on the mat",
            reference_text="The cat sat on the mat"
        )
        
        # This will fail without proper mocking of the entire pipeline
        # But we can test the structure
        result = metric.evaluate(input_data)
        assert "score" in result.details
        assert "precision" in result.details
        assert "recall" in result.details
        assert "f1" in result.details
    
    def test_bertscore_empty_inputs(self):
        """Test BERTScore with empty inputs."""
        metric = BertScoreMetric()
        
        input_data = EvaluationInput(
            output_text="",
            reference_text="The cat sat"
        )
        result = metric.evaluate(input_data)
        assert result.score == 0.0
        assert result.details["precision"] == 0.0
        assert result.details["recall"] == 0.0
    
    def test_bertscore_baseline_rescaling(self):
        """Test baseline rescaling."""
        metric = BertScoreMetric(rescale_with_baseline=True)
        
        # Test rescaling with known baseline
        precision, recall, f1 = metric._rescale_scores(0.9, 0.9, 0.9)
        assert precision >= 0.0
        assert recall >= 0.0
        assert f1 >= 0.0
        
        # Test rescaling without baseline
        metric.rescale_with_baseline = False
        precision, recall, f1 = metric._rescale_scores(0.9, 0.9, 0.9)
        assert precision == 0.9
        assert recall == 0.9
        assert f1 == 0.9


class TestLevenshteinMetric:
    """Test Levenshtein distance metric implementation."""
    
    def test_levenshtein_initialization(self):
        """Test Levenshtein initialization."""
        metric = LevenshteinMetric()
        assert metric.name == "levenshtein_distance"
        assert metric.normalize is True
        assert metric.case_sensitive is False
        assert metric.word_level is False
        assert metric.return_similarity is True
    
    def test_levenshtein_custom_parameters(self):
        """Test Levenshtein with custom parameters."""
        metric = LevenshteinMetric(
            normalize=False,
            case_sensitive=True,
            word_level=True,
            return_similarity=False
        )
        assert metric.normalize is False
        assert metric.case_sensitive is True
        assert metric.word_level is True
        assert metric.return_similarity is False
    
    def test_levenshtein_preprocess_text(self):
        """Test text preprocessing."""
        metric = LevenshteinMetric()
        
        # Character level
        result = metric._preprocess_text("Hello World!")
        assert result == "hello world"
        
        # Word level
        metric.word_level = True
        result = metric._preprocess_text("Hello World!")
        assert result == ["hello", "world"]
        
        # Case sensitive
        metric.case_sensitive = True
        result = metric._preprocess_text("Hello World!")
        assert result == ["Hello", "World"]
    
    def test_levenshtein_identical_strings(self):
        """Test Levenshtein with identical strings."""
        metric = LevenshteinMetric()
        
        distance = metric._compute_levenshtein_distance("hello", "hello")
        assert distance == 0
        
        # Test with lists (word level)
        distance = metric._compute_levenshtein_distance(["hello", "world"], ["hello", "world"])
        assert distance == 0
    
    def test_levenshtein_basic_operations(self):
        """Test basic edit operations."""
        metric = LevenshteinMetric()
        
        # Insertion
        distance = metric._compute_levenshtein_distance("cat", "cats")
        assert distance == 1
        
        # Deletion
        distance = metric._compute_levenshtein_distance("cats", "cat")
        assert distance == 1
        
        # Substitution
        distance = metric._compute_levenshtein_distance("cat", "bat")
        assert distance == 1
        
        # Multiple operations
        distance = metric._compute_levenshtein_distance("kitten", "sitting")
        assert distance == 3
    
    def test_levenshtein_empty_strings(self):
        """Test Levenshtein with empty strings."""
        metric = LevenshteinMetric()
        
        distance = metric._compute_levenshtein_distance("", "hello")
        assert distance == 5
        
        distance = metric._compute_levenshtein_distance("hello", "")
        assert distance == 5
        
        distance = metric._compute_levenshtein_distance("", "")
        assert distance == 0
    
    def test_levenshtein_normalization(self):
        """Test distance normalization."""
        metric = LevenshteinMetric(normalize=True)
        
        normalized = metric._compute_normalized_distance(3, "hello", "world")
        assert normalized == 3 / 5  # 3 edits / max(5, 5) length
        
        metric.normalize = False
        normalized = metric._compute_normalized_distance(3, "hello", "world")
        assert normalized == 3.0
    
    def test_levenshtein_similarity_conversion(self):
        """Test similarity score conversion."""
        metric = LevenshteinMetric(return_similarity=True)
        
        similarity = metric._compute_similarity(0.4)  # 40% distance
        assert similarity == 0.6  # 60% similarity
        
        metric.return_similarity = False
        similarity = metric._compute_similarity(0.4)
        assert similarity == 0.4  # Return distance as-is
    
    def test_levenshtein_detailed_analysis(self):
        """Test detailed operation analysis."""
        metric = LevenshteinMetric()
        
        analysis = metric._compute_detailed_analysis("cat", "cats")
        assert analysis["insertions"] == 1
        assert analysis["deletions"] == 0
        assert analysis["substitutions"] == 0
        assert analysis["matches"] == 3
    
    def test_levenshtein_full_evaluation(self):
        """Test complete evaluation."""
        metric = LevenshteinMetric()
        
        input_data = EvaluationInput(
            output_text="The cat sat",
            reference_text="The cat sat on the mat"
        )
        
        result = metric.evaluate(input_data)
        assert 0.0 < result.score < 1.0  # Partial similarity
        assert "distance" in result.details
        assert "normalized_distance" in result.details
        assert "similarity" in result.details
        assert "operations" in result.details
    
    def test_levenshtein_word_level(self):
        """Test word-level distance."""
        metric = LevenshteinMetric(word_level=True)
        
        input_data = EvaluationInput(
            output_text="The cat sat",
            reference_text="The cat sat on the mat"
        )
        
        result = metric.evaluate(input_data)
        assert result.details["distance"] == 2  # Missing "on" and "the mat"
        assert result.details["output_length"] == 3
        assert result.details["reference_length"] == 6


class TestBleuMetric:
    """Test BLEU metric implementation."""
    
    def test_bleu_initialization(self):
        """Test BLEU initialization."""
        metric = BleuMetric()
        assert metric.name == "bleu_score"
        assert metric.max_n == 4
        assert metric.smooth is True
    
    def test_bleu_perfect_match(self):
        """Test BLEU with perfect match."""
        metric = BleuMetric()
        
        input_data = EvaluationInput(
            output_text="The cat sat on the mat",
            reference_text="The cat sat on the mat"
        )
        
        result = metric.evaluate(input_data)
        assert result.score == 1.0
        assert result.details["bleu_1"] == 1.0
        assert result.details["bleu_2"] == 1.0
        assert result.details["bleu_3"] == 1.0
        assert result.details["bleu_4"] == 1.0


class TestRougeMetric:
    """Test ROUGE metric implementation."""
    
    def test_rouge_initialization(self):
        """Test ROUGE initialization."""
        metric = RougeMetric()
        assert metric.name == "rouge_score"
        assert "rouge1" in metric.rouge_types
        assert "rouge2" in metric.rouge_types
        assert "rougeL" in metric.rouge_types
    
    def test_rouge_perfect_match(self):
        """Test ROUGE with perfect match."""
        metric = RougeMetric()
        
        input_data = EvaluationInput(
            output_text="The cat sat on the mat",
            reference_text="The cat sat on the mat"
        )
        
        result = metric.evaluate(input_data)
        assert result.score == 1.0
        assert result.details["rouge1"]["fmeasure"] == 1.0
        assert result.details["rouge2"]["fmeasure"] == 1.0
        assert result.details["rougeL"]["fmeasure"] == 1.0


class TestExactMatchMetric:
    """Test Exact Match metric implementation."""
    
    def test_exact_match_initialization(self):
        """Test Exact Match initialization."""
        metric = ExactMatchMetric()
        assert metric.name == "exact_match"
        assert metric.ignore_case is True
        assert metric.ignore_punctuation is True
    
    def test_exact_match_identical(self):
        """Test exact match with identical texts."""
        metric = ExactMatchMetric()
        
        input_data = EvaluationInput(
            output_text="The cat sat on the mat",
            reference_text="The cat sat on the mat"
        )
        
        result = metric.evaluate(input_data)
        assert result.score == 1.0
        assert result.details["exact_match"] is True
    
    def test_exact_match_different(self):
        """Test exact match with different texts."""
        metric = ExactMatchMetric()
        
        input_data = EvaluationInput(
            output_text="The cat sat",
            reference_text="The cat sat on the mat"
        )
        
        result = metric.evaluate(input_data)
        assert result.score == 0.0
        assert result.details["exact_match"] is False
    
    def test_exact_match_case_insensitive(self):
        """Test case insensitive matching."""
        metric = ExactMatchMetric(ignore_case=True)
        
        input_data = EvaluationInput(
            output_text="THE CAT SAT",
            reference_text="the cat sat"
        )
        
        result = metric.evaluate(input_data)
        assert result.score == 1.0


class TestSemanticSimilarityMetric:
    """Test Semantic Similarity metric implementation."""
    
    def test_semantic_similarity_initialization(self):
        """Test Semantic Similarity initialization."""
        metric = SemanticSimilarityMetric()
        assert metric.name == "semantic_similarity"
        assert metric.model_name == "all-MiniLM-L6-v2"
        assert metric.similarity_threshold == 0.5
    
    @patch('evalx.metrics.traditional.semantic_similarity.SentenceTransformer')
    def test_semantic_similarity_model_loading(self, mock_sentence_transformer):
        """Test model loading."""
        mock_model = Mock()
        mock_sentence_transformer.return_value = mock_model
        
        metric = SemanticSimilarityMetric()
        metric._load_model()
        
        assert metric._model_loaded is True
        mock_sentence_transformer.assert_called_once_with("all-MiniLM-L6-v2")
    
    @patch('evalx.metrics.traditional.semantic_similarity.SentenceTransformer')
    def test_semantic_similarity_computation(self, mock_sentence_transformer):
        """Test similarity computation."""
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3], [0.1, 0.2, 0.3]])
        mock_sentence_transformer.return_value = mock_model
        
        metric = SemanticSimilarityMetric()
        
        input_data = EvaluationInput(
            output_text="The cat sat",
            reference_text="The cat sat"
        )
        
        result = metric.evaluate(input_data)
        assert "score" in result.details
        assert "similarity" in result.details
        assert "above_threshold" in result.details


if __name__ == "__main__":
    pytest.main([__file__]) 