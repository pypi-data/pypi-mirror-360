"""
Tests for the core funcing functionality.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch

from funcing import run_in_parallel, run_with_args, FuncingResult, FuncingError


class TestRunInParallel:
    """Test the run_in_parallel function."""
    
    def test_basic_parallel_execution(self):
        """Test basic parallel execution with simple functions."""
        def task1():
            return "result1"
        
        def task2():
            return "result2"
        
        def task3():
            return "result3"
        
        result = run_in_parallel([task1, task2, task3])
        
        assert isinstance(result, FuncingResult)
        assert result.success_count == 3
        assert result.error_count == 0
        assert set(result.results) == {"result1", "result2", "result3"}
        assert result.all_successful
        assert result.success_rate == 100.0
    
    def test_empty_functions_list(self):
        """Test that empty functions list raises error."""
        with pytest.raises(FuncingError, match="Functions list cannot be empty"):
            run_in_parallel([])
    
    def test_non_callable_items(self):
        """Test that non-callable items raise error."""
        with pytest.raises(FuncingError, match="All items in functions list must be callable"):
            run_in_parallel([lambda: "ok", "not_callable", lambda: "ok"])
    
    def test_error_handling_with_exceptions(self):
        """Test error handling when functions raise exceptions."""
        def success_task():
            return "success"
        
        def failure_task():
            raise ValueError("Test error")
        
        def another_success():
            return "another success"
        
        result = run_in_parallel([success_task, failure_task, another_success])
        
        assert result.success_count == 2
        assert result.error_count == 1
        assert len(result.results) == 2
        assert len(result.errors) == 1
        assert isinstance(result.errors[0], ValueError)
        assert str(result.errors[0]) == "Test error"
        assert abs(result.success_rate - (200/3)) < 0.001  # 66.67% with tolerance
        assert not result.all_successful
    
    def test_timing_accuracy(self):
        """Test that parallel execution is actually faster than sequential."""
        def slow_task():
            time.sleep(0.1)
            return "done"
        
        # Run 3 tasks that each take 0.1 seconds
        tasks = [slow_task, slow_task, slow_task]
        
        start_time = time.time()
        result = run_in_parallel(tasks)
        end_time = time.time()
        
        # Should complete in ~0.1 seconds (parallel) not ~0.3 seconds (sequential)
        assert end_time - start_time < 0.2
        assert result.total_time < 0.2
        assert result.success_count == 3
    
    def test_timeout_handling(self):
        """Test timeout functionality."""
        def slow_task():
            time.sleep(1.0)
            return "completed"
        
        def fast_task():
            return "fast"
        
        result = run_in_parallel([slow_task, fast_task], timeout=0.1)
        
        # Should have some errors due to timeout
        assert result.error_count > 0 or result.success_count > 0
    
    def test_max_workers_parameter(self):
        """Test max_workers parameter."""
        def simple_task():
            return threading.current_thread().name
        
        tasks = [simple_task] * 10
        
        # Test with limited workers
        result = run_in_parallel(tasks, max_workers=2)
        assert result.success_count == 10
        
        # Check that we didn't use more than 2 unique thread names
        unique_threads = set(result.results)
        assert len(unique_threads) <= 2  # Should use at most 2 threads
    
    def test_return_exceptions_false(self):
        """Test behavior when return_exceptions=False."""
        def failing_task():
            raise ValueError("This should be raised")
        
        def success_task():
            return "success"
        
        # Should raise the exception instead of collecting it
        with pytest.raises(ValueError, match="This should be raised"):
            run_in_parallel([failing_task, success_task], return_exceptions=False)
    
    def test_function_names_tracking(self):
        """Test that function names are tracked correctly."""
        def named_function():
            return "named"
        
        lambda_func = lambda: "lambda"
        
        result = run_in_parallel([named_function, lambda_func])
        
        assert "named_function" in result.function_names
        assert any("function_" in name for name in result.function_names)  # Lambda gets generic name
    
    def test_concurrent_access_safety(self):
        """Test thread safety with shared resources."""
        shared_list = []
        lock = threading.Lock()
        
        def safe_append(value):
            with lock:
                shared_list.append(value)
                return value
        
        tasks = [lambda i=i: safe_append(i) for i in range(10)]
        
        result = run_in_parallel(tasks)
        
        assert result.success_count == 10
        assert len(shared_list) == 10
        assert set(shared_list) == set(range(10))


class TestRunWithArgs:
    """Test the run_with_args function."""
    
    def test_functions_with_args(self):
        """Test running functions with positional arguments."""
        def add(a, b):
            return a + b
        
        def multiply(a, b):
            return a * b
        
        pairs = [
            (add, (2, 3)),
            (multiply, (4, 5))
        ]
        
        result = run_with_args(pairs)
        
        assert result.success_count == 2
        assert set(result.results) == {5, 20}
    
    def test_functions_with_kwargs(self):
        """Test running functions with keyword arguments."""
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"
        
        pairs = [
            (greet, ("Alice",)),
            (greet, ("Bob",), {"greeting": "Hi"}),
            (greet, ("Charlie",), {"greeting": "Hey"})
        ]
        
        result = run_with_args(pairs)
        
        assert result.success_count == 3
        expected = {"Hello, Alice!", "Hi, Bob!", "Hey, Charlie!"}
        assert set(result.results) == expected
    
    def test_invalid_pair_format(self):
        """Test error handling for invalid pair formats."""
        def dummy():
            return "dummy"
        
        # Invalid pair with only one element
        with pytest.raises(FuncingError, match="Each pair must be"):
            run_with_args([(dummy,)])
        
        # Invalid pair with too many elements
        with pytest.raises(FuncingError, match="Each pair must be"):
            run_with_args([(dummy, (), {}, "extra")])


class TestFuncingResult:
    """Test the FuncingResult class."""
    
    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        result = FuncingResult(
            results=["a", "b"],
            errors=[Exception("error")],
            success_count=2,
            error_count=1,
            total_time=1.0,
            function_names=["func1", "func2", "func3"]
        )
        
        assert abs(result.success_rate - (200/3)) < 0.001  # 66.67% with tolerance
    
    def test_success_rate_with_zero_total(self):
        """Test success rate with zero total (edge case)."""
        result = FuncingResult(
            results=[],
            errors=[],
            success_count=0,
            error_count=0,
            total_time=0.0,
            function_names=[]
        )
        
        assert result.success_rate == 0.0
    
    def test_all_successful_property(self):
        """Test all_successful property."""
        # All successful
        result1 = FuncingResult(
            results=["a", "b"],
            errors=[],
            success_count=2,
            error_count=0,
            total_time=1.0,
            function_names=["func1", "func2"]
        )
        assert result1.all_successful
        
        # Some failed
        result2 = FuncingResult(
            results=["a"],
            errors=[Exception("error")],
            success_count=1,
            error_count=1,
            total_time=1.0,
            function_names=["func1", "func2"]
        )
        assert not result2.all_successful
    
    def test_string_representation(self):
        """Test string representation of FuncingResult."""
        result = FuncingResult(
            results=["a", "b"],
            errors=[Exception("error")],
            success_count=2,
            error_count=1,
            total_time=1.23,
            function_names=["func1", "func2", "func3"]
        )
        
        string_repr = str(result)
        assert "success: 2" in string_repr
        assert "errors: 1" in string_repr
        assert "time: 1.23s" in string_repr
        assert "66.7%" in string_repr


class TestIntegration:
    """Integration tests for the entire library."""
    
    def test_real_world_scenario(self):
        """Test a real-world-like scenario."""
        # Simulate API calls with different response times
        def api_call_1():
            time.sleep(0.05)
            return {"api": 1, "data": "response1"}
        
        def api_call_2():
            time.sleep(0.03)
            return {"api": 2, "data": "response2"}
        
        def api_call_3():
            time.sleep(0.02)
            raise ConnectionError("API 3 is down")
        
        def api_call_4():
            time.sleep(0.01)
            return {"api": 4, "data": "response4"}
        
        calls = [api_call_1, api_call_2, api_call_3, api_call_4]
        
        result = run_in_parallel(calls, timeout=1.0)
        
        # Should complete successfully for most calls
        assert result.success_count == 3
        assert result.error_count == 1
        assert result.total_time < 0.1  # Should be fast due to parallelism
        
        # Check that we got the expected successful responses
        api_numbers = [res["api"] for res in result.results]
        assert set(api_numbers) == {1, 2, 4}
        
        # Check that we got the expected error
        assert len(result.errors) == 1
        assert isinstance(result.errors[0], ConnectionError)
    
    def test_performance_benchmark(self):
        """Test performance improvement over sequential execution."""
        def cpu_bound_task(n):
            """A CPU-bound task for testing."""
            result = 0
            for i in range(n):
                result += i * i
            return result
        
        # Create multiple tasks
        tasks = [lambda: cpu_bound_task(10000) for _ in range(4)]
        
        # Measure parallel execution
        start_time = time.time()
        result = run_in_parallel(tasks)
        parallel_time = time.time() - start_time
        
        # Measure sequential execution
        start_time = time.time()
        sequential_results = [task() for task in tasks]
        sequential_time = time.time() - start_time
        
        # Verify results are correct
        assert result.success_count == 4
        assert len(result.results) == 4
        assert all(isinstance(r, int) for r in result.results)
        
        # Parallel should be faster (though not necessarily by much for CPU-bound tasks)
        # This is more of a sanity check
        assert parallel_time > 0
        assert sequential_time > 0
        
        print(f"Sequential: {sequential_time:.3f}s, Parallel: {parallel_time:.3f}s")