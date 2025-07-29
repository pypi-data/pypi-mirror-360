"""
Integration tests for EvalX framework.

Tests complex workflows, metric combinations, and end-to-end functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any

from evalx.core.types import EvaluationInput, EvaluationResult
from evalx.core.suite import EvaluationSuite, MetricSuite
from evalx.metrics.traditional.bleu import BleuMetric
from evalx.metrics.traditional.rouge import RougeMetric
from evalx.metrics.traditional.exact_match import ExactMatchMetric
from evalx.metrics.traditional.levenshtein import LevenshteinMetric
from evalx.metrics.llm_judge.base import LLMJudgeMetric
from evalx.agents.orchestrator.intelligent_orchestrator import IntelligentOrchestrator


class TestEvaluationSuite:
    """Test EvaluationSuite integration."""
    
    def test_suite_initialization(self):
        """Test suite initialization with multiple metrics."""
        metrics = [
            BleuMetric(),
            RougeMetric(),
            ExactMatchMetric()
        ]
        
        suite = EvaluationSuite(metrics=metrics)
        assert len(suite.metrics) == 3
        assert suite.name == "evaluation_suite"
    
    def test_suite_single_evaluation(self):
        """Test single evaluation with multiple metrics."""
        metrics = [
            BleuMetric(),
            RougeMetric(),
            ExactMatchMetric()
        ]
        
        suite = EvaluationSuite(metrics=metrics)
        
        input_data = EvaluationInput(
            output_text="The cat sat on the mat",
            reference_text="The cat sat on the mat"
        )
        
        results = suite.evaluate(input_data)
        
        assert len(results) == 3
        assert all(isinstance(result, EvaluationResult) for result in results)
        assert all(result.score == 1.0 for result in results)  # Perfect matches
    
    def test_suite_batch_evaluation(self):
        """Test batch evaluation with multiple inputs."""
        metrics = [
            BleuMetric(),
            ExactMatchMetric()
        ]
        
        suite = EvaluationSuite(metrics=metrics)
        
        inputs = [
            EvaluationInput(
                output_text="The cat sat on the mat",
                reference_text="The cat sat on the mat"
            ),
            EvaluationInput(
                output_text="The dog ran",
                reference_text="The dog ran quickly"
            )
        ]
        
        results = suite.evaluate_batch(inputs)
        
        assert len(results) == 2  # Two inputs
        assert all(len(result_list) == 2 for result_list in results)  # Two metrics each
        
        # First input should have perfect scores
        assert all(result.score == 1.0 for result in results[0])
        
        # Second input should have partial scores
        assert all(0.0 < result.score < 1.0 for result in results[1])
    
    @pytest.mark.asyncio
    async def test_suite_async_evaluation(self):
        """Test async evaluation."""
        metrics = [
            BleuMetric(),
            RougeMetric()
        ]
        
        suite = EvaluationSuite(metrics=metrics)
        
        input_data = EvaluationInput(
            output_text="The cat sat on the mat",
            reference_text="The cat sat on the mat"
        )
        
        results = await suite.evaluate_async(input_data)
        
        assert len(results) == 2
        assert all(isinstance(result, EvaluationResult) for result in results)
        assert all(result.score == 1.0 for result in results)
    
    def test_suite_with_weights(self):
        """Test suite with metric weights."""
        metrics = [
            BleuMetric(),
            RougeMetric(),
            ExactMatchMetric()
        ]
        weights = [0.5, 0.3, 0.2]
        
        suite = EvaluationSuite(metrics=metrics, weights=weights)
        
        input_data = EvaluationInput(
            output_text="The cat sat on the mat",
            reference_text="The cat sat on the mat"
        )
        
        results = suite.evaluate(input_data)
        aggregate_score = suite.aggregate_scores(results)
        
        assert 0.0 <= aggregate_score <= 1.0
        assert aggregate_score == 1.0  # Perfect match should give 1.0
    
    def test_suite_error_handling(self):
        """Test error handling in suite evaluation."""
        class FailingMetric(BleuMetric):
            def _compute_score(self, input_data):
                raise ValueError("Test error")
        
        metrics = [
            BleuMetric(),
            FailingMetric(),
            ExactMatchMetric()
        ]
        
        suite = EvaluationSuite(metrics=metrics, continue_on_error=True)
        
        input_data = EvaluationInput(
            output_text="The cat sat on the mat",
            reference_text="The cat sat on the mat"
        )
        
        results = suite.evaluate(input_data)
        
        # Should have 2 successful results and 1 error result
        assert len(results) == 3
        assert sum(1 for r in results if r.error is None) == 2
        assert sum(1 for r in results if r.error is not None) == 1


class TestMetricSuite:
    """Test MetricSuite integration."""
    
    def test_metric_suite_initialization(self):
        """Test MetricSuite initialization."""
        suite = MetricSuite()
        assert len(suite.traditional_metrics) > 0
        assert len(suite.llm_judge_metrics) > 0
        assert len(suite.hybrid_metrics) > 0
    
    def test_metric_suite_get_by_category(self):
        """Test getting metrics by category."""
        suite = MetricSuite()
        
        traditional = suite.get_metrics_by_category("traditional")
        llm_judge = suite.get_metrics_by_category("llm_judge")
        hybrid = suite.get_metrics_by_category("hybrid")
        
        assert len(traditional) > 0
        assert len(llm_judge) > 0
        assert len(hybrid) > 0
    
    def test_metric_suite_get_by_name(self):
        """Test getting metrics by name."""
        suite = MetricSuite()
        
        bleu = suite.get_metric_by_name("bleu_score")
        rouge = suite.get_metric_by_name("rouge_score")
        
        assert bleu is not None
        assert rouge is not None
        assert isinstance(bleu, BleuMetric)
        assert isinstance(rouge, RougeMetric)
    
    def test_metric_suite_recommendation(self):
        """Test metric recommendation based on task type."""
        suite = MetricSuite()
        
        # Test different task types
        summarization_metrics = suite.recommend_metrics("summarization")
        translation_metrics = suite.recommend_metrics("translation")
        qa_metrics = suite.recommend_metrics("question_answering")
        
        assert len(summarization_metrics) > 0
        assert len(translation_metrics) > 0
        assert len(qa_metrics) > 0
        
        # Should include ROUGE for summarization
        assert any(isinstance(m, RougeMetric) for m in summarization_metrics)
        
        # Should include BLEU for translation
        assert any(isinstance(m, BleuMetric) for m in translation_metrics)


class TestIntelligentOrchestrator:
    """Test IntelligentOrchestrator integration."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = IntelligentOrchestrator()
        assert orchestrator.metric_suite is not None
        assert orchestrator.planner is not None
        assert orchestrator.interpreter is not None
    
    def test_orchestrator_natural_language_instruction(self):
        """Test processing natural language instructions."""
        orchestrator = IntelligentOrchestrator()
        
        instruction = "Evaluate the quality of this text generation using BLEU and ROUGE scores"
        
        plan = orchestrator.parse_instruction(instruction)
        
        assert plan is not None
        assert "metrics" in plan
        assert len(plan["metrics"]) > 0
        
        # Should include BLEU and ROUGE
        metric_names = [m.name for m in plan["metrics"]]
        assert "bleu_score" in metric_names
        assert "rouge_score" in metric_names
    
    def test_orchestrator_task_type_detection(self):
        """Test automatic task type detection."""
        orchestrator = IntelligentOrchestrator()
        
        # Translation task
        translation_input = EvaluationInput(
            output_text="Le chat est sur le tapis",
            reference_text="The cat is on the mat",
            task_type="translation"
        )
        
        task_type = orchestrator.detect_task_type(translation_input)
        assert task_type == "translation"
        
        # Summarization task
        summarization_input = EvaluationInput(
            output_text="Short summary",
            reference_text="Very long original text that needs to be summarized...",
            task_type="summarization"
        )
        
        task_type = orchestrator.detect_task_type(summarization_input)
        assert task_type == "summarization"
    
    def test_orchestrator_metric_selection(self):
        """Test automatic metric selection."""
        orchestrator = IntelligentOrchestrator()
        
        # Test for translation task
        translation_input = EvaluationInput(
            output_text="Le chat est sur le tapis",
            reference_text="The cat is on the mat",
            task_type="translation"
        )
        
        metrics = orchestrator.select_metrics(translation_input)
        
        assert len(metrics) > 0
        assert any(isinstance(m, BleuMetric) for m in metrics)
        
        # Test for exact match task
        exact_input = EvaluationInput(
            output_text="42",
            reference_text="42",
            task_type="exact_match"
        )
        
        metrics = orchestrator.select_metrics(exact_input)
        
        assert len(metrics) > 0
        assert any(isinstance(m, ExactMatchMetric) for m in metrics)
    
    @pytest.mark.asyncio
    async def test_orchestrator_full_workflow(self):
        """Test complete orchestrator workflow."""
        orchestrator = IntelligentOrchestrator()
        
        instruction = "Evaluate this translation using standard metrics"
        
        input_data = EvaluationInput(
            output_text="Le chat est sur le tapis",
            reference_text="The cat is on the mat",
            task_type="translation"
        )
        
        results = await orchestrator.evaluate_with_instruction(
            instruction=instruction,
            input_data=input_data
        )
        
        assert len(results) > 0
        assert all(isinstance(result, EvaluationResult) for result in results)
        
        # Should have interpretation
        interpretation = orchestrator.interpret_results(results)
        assert interpretation is not None
        assert "summary" in interpretation
        assert "recommendations" in interpretation


class TestMultiModalIntegration:
    """Test multimodal evaluation integration."""
    
    @pytest.mark.skip(reason="Multimodal metrics require additional setup")
    def test_vision_language_evaluation(self):
        """Test vision-language evaluation."""
        from evalx.metrics.multimodal.vision_language import VisionLanguageMetric
        
        metric = VisionLanguageMetric()
        
        input_data = EvaluationInput(
            output_text="A cat sitting on a mat",
            reference_text="A cat on a mat",
            image_path="test_image.jpg"
        )
        
        result = metric.evaluate(input_data)
        
        assert result.score is not None
        assert 0.0 <= result.score <= 1.0
    
    @pytest.mark.skip(reason="Code metrics require additional setup")
    def test_code_generation_evaluation(self):
        """Test code generation evaluation."""
        from evalx.metrics.multimodal.code_generation import CodeGenerationMetric
        
        metric = CodeGenerationMetric()
        
        input_data = EvaluationInput(
            output_text="def hello():\n    print('Hello, world!')",
            reference_text="def hello():\n    print('Hello, world!')",
            task_type="code_generation"
        )
        
        result = metric.evaluate(input_data)
        
        assert result.score is not None
        assert 0.0 <= result.score <= 1.0


class TestAsyncWorkflows:
    """Test async workflow integration."""
    
    @pytest.mark.asyncio
    async def test_concurrent_metric_evaluation(self):
        """Test concurrent evaluation of multiple metrics."""
        metrics = [
            BleuMetric(),
            RougeMetric(),
            ExactMatchMetric(),
            LevenshteinMetric()
        ]
        
        input_data = EvaluationInput(
            output_text="The cat sat on the mat",
            reference_text="The cat sat on the mat"
        )
        
        # Run all metrics concurrently
        tasks = [
            asyncio.create_task(metric.evaluate_async(input_data))
            for metric in metrics
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 4
        assert all(isinstance(result, EvaluationResult) for result in results)
        assert all(result.score == 1.0 for result in results)  # Perfect matches
    
    @pytest.mark.asyncio
    async def test_batch_async_evaluation(self):
        """Test async batch evaluation."""
        suite = EvaluationSuite(metrics=[BleuMetric(), RougeMetric()])
        
        inputs = [
            EvaluationInput(
                output_text="The cat sat on the mat",
                reference_text="The cat sat on the mat"
            ),
            EvaluationInput(
                output_text="The dog ran",
                reference_text="The dog ran quickly"
            ),
            EvaluationInput(
                output_text="Hello world",
                reference_text="Hello world"
            )
        ]
        
        results = await suite.evaluate_batch_async(inputs)
        
        assert len(results) == 3
        assert all(len(result_list) == 2 for result_list in results)  # Two metrics each


class TestErrorHandlingAndResilience:
    """Test error handling and system resilience."""
    
    def test_metric_failure_isolation(self):
        """Test that one metric failure doesn't affect others."""
        class FailingMetric(BleuMetric):
            def _compute_score(self, input_data):
                raise RuntimeError("Simulated failure")
        
        metrics = [
            BleuMetric(),
            FailingMetric(),
            RougeMetric()
        ]
        
        suite = EvaluationSuite(metrics=metrics, continue_on_error=True)
        
        input_data = EvaluationInput(
            output_text="The cat sat on the mat",
            reference_text="The cat sat on the mat"
        )
        
        results = suite.evaluate(input_data)
        
        # Should have 2 successful results and 1 error
        successful_results = [r for r in results if r.error is None]
        error_results = [r for r in results if r.error is not None]
        
        assert len(successful_results) == 2
        assert len(error_results) == 1
        assert all(r.score == 1.0 for r in successful_results)
    
    def test_timeout_handling(self):
        """Test timeout handling for slow metrics."""
        class SlowMetric(BleuMetric):
            def _compute_score(self, input_data):
                import time
                time.sleep(2)  # Simulate slow computation
                return super()._compute_score(input_data)
        
        suite = EvaluationSuite(
            metrics=[SlowMetric()],
            timeout=1.0  # 1 second timeout
        )
        
        input_data = EvaluationInput(
            output_text="The cat sat on the mat",
            reference_text="The cat sat on the mat"
        )
        
        results = suite.evaluate(input_data)
        
        # Should have timeout error
        assert len(results) == 1
        assert results[0].error is not None
        assert "timeout" in str(results[0].error).lower()
    
    def test_memory_management(self):
        """Test memory management with large inputs."""
        # Create a large input
        large_text = "The cat sat on the mat. " * 10000  # ~250KB text
        
        metrics = [
            BleuMetric(),
            RougeMetric(),
            LevenshteinMetric()
        ]
        
        suite = EvaluationSuite(metrics=metrics)
        
        input_data = EvaluationInput(
            output_text=large_text,
            reference_text=large_text
        )
        
        results = suite.evaluate(input_data)
        
        # Should complete without memory issues
        assert len(results) == 3
        assert all(r.error is None for r in results)
        assert all(r.score == 1.0 for r in results)  # Perfect matches


class TestPerformanceAndScaling:
    """Test performance and scaling characteristics."""
    
    def test_batch_processing_performance(self):
        """Test batch processing performance."""
        import time
        
        metrics = [BleuMetric(), RougeMetric()]
        suite = EvaluationSuite(metrics=metrics)
        
        # Create multiple inputs
        inputs = [
            EvaluationInput(
                output_text=f"The cat sat on the mat {i}",
                reference_text=f"The cat sat on the mat {i}"
            )
            for i in range(100)
        ]
        
        start_time = time.time()
        results = suite.evaluate_batch(inputs)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete in reasonable time (less than 10 seconds)
        assert processing_time < 10.0
        assert len(results) == 100
        assert all(len(result_list) == 2 for result_list in results)
    
    @pytest.mark.asyncio
    async def test_concurrent_processing_speedup(self):
        """Test that concurrent processing provides speedup."""
        import time
        
        metrics = [BleuMetric(), RougeMetric(), ExactMatchMetric()]
        
        input_data = EvaluationInput(
            output_text="The cat sat on the mat",
            reference_text="The cat sat on the mat"
        )
        
        # Sequential processing
        start_time = time.time()
        sequential_results = []
        for metric in metrics:
            result = metric.evaluate(input_data)
            sequential_results.append(result)
        sequential_time = time.time() - start_time
        
        # Concurrent processing
        start_time = time.time()
        tasks = [
            asyncio.create_task(metric.evaluate_async(input_data))
            for metric in metrics
        ]
        concurrent_results = await asyncio.gather(*tasks)
        concurrent_time = time.time() - start_time
        
        # Concurrent should be faster (or at least not significantly slower)
        assert concurrent_time <= sequential_time * 1.5  # Allow 50% overhead
        assert len(concurrent_results) == len(sequential_results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 