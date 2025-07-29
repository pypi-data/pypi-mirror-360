"""
Basic tests for EvalX framework.
"""

import pytest
import sys
import os

# Add the parent directory to the path so we can import evalx
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_import_evalx():
    """Test that we can import the main evalx module."""
    try:
        import evalx
        assert hasattr(evalx, '__version__')
        print(f"✅ Successfully imported EvalX version {evalx.__version__}")
    except ImportError as e:
        pytest.fail(f"Failed to import evalx: {e}")

def test_import_core_components():
    """Test that we can import core components."""
    try:
        from evalx.core.types import EvaluationInput, EvaluationResult
        from evalx.core.base import BaseMetric, BaseEvaluator
        print("✅ Successfully imported core components")
    except ImportError as e:
        pytest.fail(f"Failed to import core components: {e}")

def test_import_metrics():
    """Test that we can import metrics."""
    try:
        from evalx.metrics.traditional.bleu import BLEUMetric
        from evalx.metrics.llm_judge.base import LLMJudgeMetric
        print("✅ Successfully imported metrics")
    except ImportError as e:
        pytest.fail(f"Failed to import metrics: {e}")

def test_import_multimodal():
    """Test that we can import multimodal components."""
    try:
        from evalx.metrics.multimodal import MultimodalInput, ImageTextAlignmentMetric
        print("✅ Successfully imported multimodal components")
    except ImportError as e:
        pytest.fail(f"Failed to import multimodal components: {e}")

def test_import_meta_evaluation():
    """Test that we can import meta-evaluation components."""
    try:
        from evalx.meta_evaluation import MetaEvaluator, MetricQualityReport
        print("✅ Successfully imported meta-evaluation components")
    except ImportError as e:
        pytest.fail(f"Failed to import meta-evaluation components: {e}")

def test_basic_functionality():
    """Test basic functionality with simple evaluation."""
    try:
        from evalx.core.types import EvaluationInput
        from evalx.metrics.traditional.exact_match import ExactMatchMetric
        
        # Create a simple input
        input_data = EvaluationInput(
            input_text="What is the capital of France?",
            output_text="Paris",
            reference_text="Paris"
        )
        
        # Create and test exact match metric
        metric = ExactMatchMetric()
        result = metric.evaluate(input_data)
        
        assert result.numeric_value == 1.0  # Should be exact match
        print("✅ Basic evaluation functionality works")
        
    except Exception as e:
        pytest.fail(f"Basic functionality test failed: {e}")

if __name__ == "__main__":
    # Run tests directly
    test_import_evalx()
    test_import_core_components()
    test_import_metrics()
    test_import_multimodal()
    test_import_meta_evaluation()
    test_basic_functionality()
    print("\n🎉 All basic tests passed!") 