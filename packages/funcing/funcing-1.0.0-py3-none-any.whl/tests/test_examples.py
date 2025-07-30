"""
Tests for the examples module to ensure all examples work correctly.
"""

import pytest
import time
from unittest.mock import patch, Mock
import io
import sys
from contextlib import redirect_stdout

from funcing import examples


class TestExamples:
    """Test all the example functions."""
    
    def test_demo_basic_usage(self):
        """Test that basic usage demo runs without errors."""
        # Capture output
        with redirect_stdout(io.StringIO()) as captured_output:
            examples.demo_basic_usage()
        
        output = captured_output.getvalue()
        assert "Basic Usage Demo" in output
        assert "Execution completed" in output
        assert "Success rate: 100.0%" in output
    
    def test_demo_error_handling(self):
        """Test that error handling demo runs without errors."""
        with redirect_stdout(io.StringIO()) as captured_output:
            examples.demo_error_handling()
        
        output = captured_output.getvalue()
        assert "Error Handling Demo" in output
        assert "Successes: 2" in output
        assert "Errors: 1" in output
        assert "Success rate: 66.7%" in output
    
    def test_demo_with_arguments(self):
        """Test that arguments demo runs without errors."""
        with redirect_stdout(io.StringIO()) as captured_output:
            examples.demo_with_arguments()
        
        output = captured_output.getvalue()
        assert "Functions with Arguments Demo" in output
        assert "Results:" in output
        assert "5 + 3 = 8" in output
        assert "4 × 7 = 28" in output
        assert "Hi, Alice!" in output
    
    @patch('random.uniform')
    @patch('random.random')
    def test_demo_simulation(self, mock_random, mock_uniform):
        """Test web scraping simulation with mocked randomness."""
        # Mock the random functions to make test deterministic
        mock_uniform.return_value = 0.1  # Always return 0.1 for delay
        mock_random.return_value = 0.5   # Always return 0.5 (no failures)
        
        with redirect_stdout(io.StringIO()) as captured_output:
            examples.demo_simulation()
        
        output = captured_output.getvalue()
        assert "Web Scraping Simulation" in output
        assert "Fetching 5 URLs" in output
        assert "Completed in" in output
        assert "Success rate:" in output
    
    def test_demo_performance_comparison(self):
        """Test performance comparison demo."""
        with redirect_stdout(io.StringIO()) as captured_output:
            examples.demo_performance_comparison()
        
        output = captured_output.getvalue()
        assert "Performance Comparison" in output
        assert "Sequential time:" in output
        assert "Parallel time:" in output
        assert "Speedup:" in output
    
    def test_main_function(self):
        """Test that main function runs all demos."""
        with redirect_stdout(io.StringIO()) as captured_output:
            examples.main()
        
        output = captured_output.getvalue()
        assert "Funcing Library Demonstrations" in output
        assert "Basic Usage Demo" in output
        assert "Error Handling Demo" in output
        assert "Functions with Arguments Demo" in output
        assert "Web Scraping Simulation" in output
        assert "Performance Comparison" in output
        assert "All demonstrations completed!" in output


class TestExampleHelpers:
    """Test helper functions in examples."""
    
    def test_individual_example_functions(self):
        """Test that individual example functions work correctly."""
        
        # Test that we can import and call each demo function
        demo_functions = [
            examples.demo_basic_usage,
            examples.demo_error_handling,
            examples.demo_with_arguments,
            examples.demo_simulation,
            examples.demo_performance_comparison
        ]
        
        for demo_func in demo_functions:
            # Each demo should run without raising exceptions
            try:
                with redirect_stdout(io.StringIO()):
                    demo_func()
            except Exception as e:
                pytest.fail(f"Demo function {demo_func.__name__} failed: {e}")
    
    def test_simulation_error_handling(self):
        """Test that simulation handles errors gracefully."""
        
        # Patch to force some failures
        with patch('random.random', return_value=0.05):  # Force failures
            with patch('random.uniform', return_value=0.1):  # Short delays
                with redirect_stdout(io.StringIO()) as captured_output:
                    examples.demo_simulation()
                
                output = captured_output.getvalue()
                # Should still complete and show some failures
                assert "Completed in" in output
                assert "Success rate:" in output