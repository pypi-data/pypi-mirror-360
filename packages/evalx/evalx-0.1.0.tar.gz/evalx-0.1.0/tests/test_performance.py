"""
Performance tests for EvalX framework.

Tests performance characteristics, memory usage, and scalability.
"""

import pytest
import time
import asyncio
import psutil
import gc
from typing import List
from unittest.mock import patch

from evalx.core.types import EvaluationInput
from evalx.core.suite import EvaluationSuite
from evalx.metrics.traditional.bleu import BleuMetric
from evalx.metrics.traditional.rouge import RougeMetric
from evalx.metrics.traditional.exact_match import ExactMatchMetric
from evalx.metrics.traditional.levenshtein import LevenshteinMetric


class TestMetricPerformance:
    """Test individual metric performance."""
    
    def test_bleu_performance(self):
        """Test BLEU metric performance."""
        metric = BleuMetric()
        
        # Test with various text lengths
        test_cases = [
            ("Short text", "Short text"),
            ("Medium length text with multiple words and sentences.", 
             "Medium length text with multiple words and sentences."),
            ("Long text " * 100, "Long text " * 100),  # ~1000 words
        ]
        
        for output_text, reference_text in test_cases:
            input_data = EvaluationInput(
                output_text=output_text,
                reference_text=reference_text
            )
            
            start_time = time.time()
            result = metric.evaluate(input_data)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Should complete within reasonable time
            assert processing_time < 1.0  # Less than 1 second
            assert result.score is not None
    
    def test_rouge_performance(self):
        """Test ROUGE metric performance."""
        metric = RougeMetric()
        
        # Test with various text lengths
        test_cases = [
            ("Short", "Short"),
            ("Medium text with several words", "Medium text with several words"),
            ("Long text " * 50, "Long text " * 50),  # ~500 words
        ]
        
        for output_text, reference_text in test_cases:
            input_data = EvaluationInput(
                output_text=output_text,
                reference_text=reference_text
            )
            
            start_time = time.time()
            result = metric.evaluate(input_data)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Should complete within reasonable time
            assert processing_time < 2.0  # Less than 2 seconds
            assert result.score is not None
    
    def test_levenshtein_performance(self):
        """Test Levenshtein metric performance."""
        metric = LevenshteinMetric()
        
        # Test with various string lengths
        test_cases = [
            ("short", "short"),
            ("medium length string", "medium length string"),
            ("long string " * 20, "long string " * 20),  # ~200 characters
        ]
        
        for output_text, reference_text in test_cases:
            input_data = EvaluationInput(
                output_text=output_text,
                reference_text=reference_text
            )
            
            start_time = time.time()
            result = metric.evaluate(input_data)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Should complete within reasonable time
            assert processing_time < 0.5  # Less than 0.5 seconds
            assert result.score is not None
    
    def test_exact_match_performance(self):
        """Test Exact Match metric performance."""
        metric = ExactMatchMetric()
        
        # Test with various text lengths
        test_cases = [
            ("Short text", "Short text"),
            ("Medium length text with multiple words", 
             "Medium length text with multiple words"),
            ("Very long text " * 100, "Very long text " * 100),  # ~1000 words
        ]
        
        for output_text, reference_text in test_cases:
            input_data = EvaluationInput(
                output_text=output_text,
                reference_text=reference_text
            )
            
            start_time = time.time()
            result = metric.evaluate(input_data)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Should complete very quickly
            assert processing_time < 0.1  # Less than 0.1 seconds
            assert result.score is not None


class TestBatchPerformance:
    """Test batch processing performance."""
    
    def test_small_batch_performance(self):
        """Test performance with small batches."""
        metrics = [BleuMetric(), RougeMetric(), ExactMatchMetric()]
        suite = EvaluationSuite(metrics=metrics)
        
        # Create 10 inputs
        inputs = [
            EvaluationInput(
                output_text=f"The cat sat on the mat {i}",
                reference_text=f"The cat sat on the mat {i}"
            )
            for i in range(10)
        ]
        
        start_time = time.time()
        results = suite.evaluate_batch(inputs)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete quickly
        assert processing_time < 5.0  # Less than 5 seconds
        assert len(results) == 10
        assert all(len(result_list) == 3 for result_list in results)
    
    def test_medium_batch_performance(self):
        """Test performance with medium batches."""
        metrics = [BleuMetric(), ExactMatchMetric()]
        suite = EvaluationSuite(metrics=metrics)
        
        # Create 100 inputs
        inputs = [
            EvaluationInput(
                output_text=f"Test text {i}",
                reference_text=f"Test text {i}"
            )
            for i in range(100)
        ]
        
        start_time = time.time()
        results = suite.evaluate_batch(inputs)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete in reasonable time
        assert processing_time < 30.0  # Less than 30 seconds
        assert len(results) == 100
        assert all(len(result_list) == 2 for result_list in results)
    
    @pytest.mark.slow
    def test_large_batch_performance(self):
        """Test performance with large batches."""
        metrics = [ExactMatchMetric()]  # Use fastest metric
        suite = EvaluationSuite(metrics=metrics)
        
        # Create 1000 inputs
        inputs = [
            EvaluationInput(
                output_text=f"Test {i}",
                reference_text=f"Test {i}"
            )
            for i in range(1000)
        ]
        
        start_time = time.time()
        results = suite.evaluate_batch(inputs)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete in reasonable time
        assert processing_time < 60.0  # Less than 1 minute
        assert len(results) == 1000
        assert all(len(result_list) == 1 for result_list in results)


class TestAsyncPerformance:
    """Test async performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_async_vs_sync_performance(self):
        """Compare async vs sync performance."""
        metrics = [BleuMetric(), RougeMetric(), ExactMatchMetric()]
        
        input_data = EvaluationInput(
            output_text="The cat sat on the mat",
            reference_text="The cat sat on the mat"
        )
        
        # Test sync performance
        start_time = time.time()
        sync_results = []
        for metric in metrics:
            result = metric.evaluate(input_data)
            sync_results.append(result)
        sync_time = time.time() - start_time
        
        # Test async performance
        start_time = time.time()
        tasks = [
            asyncio.create_task(metric.evaluate_async(input_data))
            for metric in metrics
        ]
        async_results = await asyncio.gather(*tasks)
        async_time = time.time() - start_time
        
        # Async should be faster or comparable
        assert async_time <= sync_time * 1.5  # Allow 50% overhead
        assert len(async_results) == len(sync_results)
    
    @pytest.mark.asyncio
    async def test_concurrent_batch_processing(self):
        """Test concurrent batch processing."""
        suite = EvaluationSuite(metrics=[BleuMetric(), ExactMatchMetric()])
        
        # Create multiple batches
        batches = [
            [
                EvaluationInput(
                    output_text=f"Batch {batch_id} text {i}",
                    reference_text=f"Batch {batch_id} text {i}"
                )
                for i in range(10)
            ]
            for batch_id in range(5)
        ]
        
        start_time = time.time()
        
        # Process batches concurrently
        tasks = [
            asyncio.create_task(suite.evaluate_batch_async(batch))
            for batch in batches
        ]
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete in reasonable time
        assert processing_time < 15.0  # Less than 15 seconds
        assert len(results) == 5  # 5 batches
        assert all(len(batch_results) == 10 for batch_results in results)
    
    @pytest.mark.asyncio
    async def test_async_throughput(self):
        """Test async processing throughput."""
        metric = ExactMatchMetric()
        
        # Create many inputs
        inputs = [
            EvaluationInput(
                output_text=f"Text {i}",
                reference_text=f"Text {i}"
            )
            for i in range(100)
        ]
        
        start_time = time.time()
        
        # Process all inputs concurrently
        tasks = [
            asyncio.create_task(metric.evaluate_async(input_data))
            for input_data in inputs
        ]
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        processing_time = end_time - start_time
        throughput = len(inputs) / processing_time
        
        # Should achieve reasonable throughput
        assert throughput > 10  # At least 10 evaluations per second
        assert len(results) == 100


class TestMemoryPerformance:
    """Test memory usage and management."""
    
    def get_memory_usage(self):
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def test_memory_usage_single_evaluation(self):
        """Test memory usage for single evaluation."""
        metric = BleuMetric()
        
        initial_memory = self.get_memory_usage()
        
        input_data = EvaluationInput(
            output_text="The cat sat on the mat",
            reference_text="The cat sat on the mat"
        )
        
        # Perform evaluation
        result = metric.evaluate(input_data)
        
        # Force garbage collection
        gc.collect()
        
        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Should not increase memory significantly
        assert memory_increase < 50  # Less than 50MB increase
        assert result.score is not None
    
    def test_memory_usage_batch_evaluation(self):
        """Test memory usage for batch evaluation."""
        suite = EvaluationSuite(metrics=[BleuMetric(), ExactMatchMetric()])
        
        initial_memory = self.get_memory_usage()
        
        # Create batch of inputs
        inputs = [
            EvaluationInput(
                output_text=f"Test text {i}",
                reference_text=f"Test text {i}"
            )
            for i in range(100)
        ]
        
        # Perform batch evaluation
        results = suite.evaluate_batch(inputs)
        
        # Force garbage collection
        gc.collect()
        
        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Should not increase memory excessively
        assert memory_increase < 200  # Less than 200MB increase
        assert len(results) == 100
    
    def test_memory_cleanup_after_evaluation(self):
        """Test memory cleanup after evaluation."""
        metric = BleuMetric()
        
        initial_memory = self.get_memory_usage()
        
        # Perform multiple evaluations
        for i in range(50):
            input_data = EvaluationInput(
                output_text=f"Test text {i}",
                reference_text=f"Test text {i}"
            )
            result = metric.evaluate(input_data)
            
            # Clear references
            del input_data
            del result
        
        # Force garbage collection
        gc.collect()
        
        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Memory should not grow significantly
        assert memory_increase < 100  # Less than 100MB increase
    
    def test_large_input_memory_handling(self):
        """Test memory handling with large inputs."""
        metric = ExactMatchMetric()  # Use simple metric
        
        initial_memory = self.get_memory_usage()
        
        # Create large input
        large_text = "The cat sat on the mat. " * 10000  # ~250KB
        
        input_data = EvaluationInput(
            output_text=large_text,
            reference_text=large_text
        )
        
        # Perform evaluation
        result = metric.evaluate(input_data)
        
        # Clear references
        del input_data
        del large_text
        
        # Force garbage collection
        gc.collect()
        
        final_memory = self.get_memory_usage()
        memory_increase = final_memory - initial_memory
        
        # Should handle large inputs without excessive memory usage
        assert memory_increase < 50  # Less than 50MB increase
        assert result.score is not None


class TestScalabilityLimits:
    """Test framework scalability limits."""
    
    def test_maximum_input_length(self):
        """Test handling of very long inputs."""
        metric = ExactMatchMetric()
        
        # Create very long input (1MB)
        very_long_text = "A" * (1024 * 1024)
        
        input_data = EvaluationInput(
            output_text=very_long_text,
            reference_text=very_long_text
        )
        
        start_time = time.time()
        result = metric.evaluate(input_data)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete without error
        assert result.score is not None
        assert result.error is None
        # Should complete in reasonable time
        assert processing_time < 5.0  # Less than 5 seconds
    
    def test_maximum_batch_size(self):
        """Test handling of very large batches."""
        suite = EvaluationSuite(metrics=[ExactMatchMetric()])
        
        # Create large batch (10,000 inputs)
        large_batch = [
            EvaluationInput(
                output_text=f"Text {i}",
                reference_text=f"Text {i}"
            )
            for i in range(10000)
        ]
        
        start_time = time.time()
        results = suite.evaluate_batch(large_batch)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Should complete without error
        assert len(results) == 10000
        assert all(len(result_list) == 1 for result_list in results)
        # Should complete in reasonable time
        assert processing_time < 300.0  # Less than 5 minutes
    
    def test_concurrent_limit(self):
        """Test concurrent processing limits."""
        metric = ExactMatchMetric()
        
        # Create many concurrent tasks
        input_data = EvaluationInput(
            output_text="Test text",
            reference_text="Test text"
        )
        
        async def run_concurrent_test():
            # Create 1000 concurrent tasks
            tasks = [
                asyncio.create_task(metric.evaluate_async(input_data))
                for _ in range(1000)
            ]
            
            start_time = time.time()
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Should complete without major issues
            successful_results = [r for r in results if not isinstance(r, Exception)]
            assert len(successful_results) >= 950  # At least 95% success rate
            assert processing_time < 60.0  # Less than 1 minute
        
        asyncio.run(run_concurrent_test())


class TestPerformanceRegression:
    """Test for performance regressions."""
    
    def test_baseline_performance(self):
        """Test baseline performance metrics."""
        # Define baseline expectations
        baselines = {
            "bleu_single": 0.1,      # 0.1 seconds for single BLEU
            "rouge_single": 0.2,     # 0.2 seconds for single ROUGE
            "exact_match_single": 0.01,  # 0.01 seconds for single exact match
            "batch_100": 5.0,        # 5 seconds for batch of 100
        }
        
        # Test BLEU single
        metric = BleuMetric()
        input_data = EvaluationInput(
            output_text="The cat sat on the mat",
            reference_text="The cat sat on the mat"
        )
        
        start_time = time.time()
        metric.evaluate(input_data)
        bleu_time = time.time() - start_time
        
        assert bleu_time < baselines["bleu_single"]
        
        # Test ROUGE single
        metric = RougeMetric()
        start_time = time.time()
        metric.evaluate(input_data)
        rouge_time = time.time() - start_time
        
        assert rouge_time < baselines["rouge_single"]
        
        # Test Exact Match single
        metric = ExactMatchMetric()
        start_time = time.time()
        metric.evaluate(input_data)
        exact_time = time.time() - start_time
        
        assert exact_time < baselines["exact_match_single"]
        
        # Test batch processing
        suite = EvaluationSuite(metrics=[ExactMatchMetric()])
        inputs = [input_data] * 100
        
        start_time = time.time()
        suite.evaluate_batch(inputs)
        batch_time = time.time() - start_time
        
        assert batch_time < baselines["batch_100"]
    
    def test_performance_with_different_text_lengths(self):
        """Test performance scaling with text length."""
        metric = BleuMetric()
        
        # Test with different text lengths
        lengths = [10, 100, 1000, 5000]  # words
        times = []
        
        for length in lengths:
            text = "word " * length
            input_data = EvaluationInput(
                output_text=text,
                reference_text=text
            )
            
            start_time = time.time()
            metric.evaluate(input_data)
            end_time = time.time()
            
            times.append(end_time - start_time)
        
        # Performance should scale reasonably (not exponentially)
        # Each 10x increase in length should not cause more than 10x increase in time
        for i in range(1, len(times)):
            length_ratio = lengths[i] / lengths[i-1]
            time_ratio = times[i] / times[i-1]
            
            assert time_ratio <= length_ratio * 2  # Allow 2x overhead


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not slow"]) 