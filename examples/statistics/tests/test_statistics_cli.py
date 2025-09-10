#!/usr/bin/env python3
"""
Test suite for statistics CLI operations.
"""

import pytest
import math
import sys
from pathlib import Path

# Add current directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent))

from examples.statistics.tests.statistics_test_utils import (
    assert_statistics_command_success,
    assert_statistics_command_failure,
    parse_statistics_output,
    assert_statistics_dict_close,
    calculate_expected_statistics
)


class TestStatisticsCreate:
    """Test statistics create command."""
    
    def test_create_basic(self):
        """Test basic create command with simple dataset."""
        result = assert_statistics_command_success(["create", "1", "2", "3", "4", "5"])
        output = result.stdout
        
        # Should contain creation confirmation and statistics
        assert "Created array with 5 values" in output
        assert "Statistics Summary:" in output
        
        # Parse and verify statistics
        stats = parse_statistics_output(output)
        expected = calculate_expected_statistics([1, 2, 3, 4, 5])
        assert_statistics_dict_close(stats, expected)
    
    def test_create_single_value(self):
        """Test create with single value."""
        result = assert_statistics_command_success(["create", "42"])
        stats = parse_statistics_output(result.stdout)
        
        expected = {
            'count': 1,
            'mean': 42.0,
            'median': 42.0,
            'std_deviation': 0.0,
            'min': 42,
            'max': 42
        }
        assert_statistics_dict_close(stats, expected)
    
    def test_create_negative_values(self):
        """Test create with negative values."""
        result = assert_statistics_command_success(["create", "-5", "-3", "-1", "1", "3", "5"])
        stats = parse_statistics_output(result.stdout)
        
        expected = calculate_expected_statistics([-5, -3, -1, 1, 3, 5])
        assert_statistics_dict_close(stats, expected)
    
    def test_create_decimal_values(self):
        """Test create with decimal values (truncated to integers)."""
        result = assert_statistics_command_success(["create", "1.5", "2.5", "3.5"])
        stats = parse_statistics_output(result.stdout)

        # Decimal values are truncated to integers: 1.5->1, 2.5->2, 3.5->3
        expected = calculate_expected_statistics([1, 2, 3])
        assert_statistics_dict_close(stats, expected)
    
    def test_create_large_dataset(self, large_dataset):
        """Test create with large dataset."""
        args = ["create"] + [str(x) for x in large_dataset[:100]]  # Limit to 100 for performance
        result = assert_statistics_command_success(args)
        
        assert "Created array with 100 values" in result.stdout
        assert "Statistics Summary:" in result.stdout
    
    def test_create_empty_args(self):
        """Test create with no arguments."""
        assert_statistics_command_failure(["create"])
    
    def test_create_invalid_numbers(self):
        """Test create with invalid number formats."""
        assert_statistics_command_failure(["create", "abc", "def"])
        assert_statistics_command_failure(["create", "1", "abc", "3"])


class TestStatisticsAnalyze:
    """Test statistics analyze command."""
    
    def test_analyze_after_algorithm_create(self, algorithm_cli_path, temp_array_file):
        """Test analyze command after creating array with algorithm CLI."""
        if not algorithm_cli_path:
            pytest.skip("Algorithm CLI not available")
        
        import subprocess
        
        # Create array using algorithm CLI
        subprocess.run([algorithm_cli_path, "dynarray", "create", "10"], check=True)
        subprocess.run([algorithm_cli_path, "dynarray", "push", "10", "20", "30", "40", "50"], check=True)
        
        # Analyze with statistics CLI
        result = assert_statistics_command_success(["analyze"])
        stats = parse_statistics_output(result.stdout)
        
        expected = calculate_expected_statistics([10, 20, 30, 40, 50])
        assert_statistics_dict_close(stats, expected)
    
    def test_analyze_no_array_file(self):
        """Test analyze when no array file exists."""
        # Clean up any existing file
        import os
        temp_file = "/tmp/pydcov_array.dat"
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        assert_statistics_command_failure(["analyze"])


class TestStatisticsCompare:
    """Test statistics compare command."""
    
    def test_compare_basic(self):
        """Test basic array comparison."""
        result = assert_statistics_command_success([
            "compare", "1", "2", "3", "|", "10", "20", "30"
        ])
        output = result.stdout
        
        # Should contain statistics for both arrays
        assert "Array 1 Statistics:" in output
        assert "Array 2 Statistics:" in output
        
        # Verify both sets of statistics are present
        lines = output.split('\n')
        array1_section = False
        array2_section = False
        
        for line in lines:
            if "Array 1 Statistics:" in line:
                array1_section = True
            elif "Array 2 Statistics:" in line:
                array2_section = True
        
        assert array1_section and array2_section
    
    def test_compare_different_sizes(self):
        """Test comparing arrays of different sizes."""
        result = assert_statistics_command_success([
            "compare", "1", "2", "|", "10", "20", "30", "40", "50"
        ])
        output = result.stdout
        
        assert "Array 1 Statistics:" in output
        assert "Array 2 Statistics:" in output
    
    def test_compare_single_values(self):
        """Test comparing single-value arrays."""
        result = assert_statistics_command_success([
            "compare", "5", "|", "10"
        ])
        stats_text = result.stdout
        
        # Both should have std deviation of 0
        assert "Std Deviation: 0.00" in stats_text
    
    def test_compare_no_separator(self):
        """Test compare without separator."""
        assert_statistics_command_failure(["compare", "1", "2", "3", "4", "5"])
    
    def test_compare_empty_arrays(self):
        """Test compare with empty arrays."""
        assert_statistics_command_failure(["compare", "|"])
        assert_statistics_command_failure(["compare", "1", "2", "|"])
        assert_statistics_command_failure(["compare", "|", "1", "2"])
    
    def test_compare_invalid_numbers(self):
        """Test compare with invalid numbers."""
        assert_statistics_command_failure(["compare", "1", "abc", "|", "2", "3"])


class TestIndividualStatistics:
    """Test individual statistics commands."""
    
    def test_mean_command(self):
        """Test mean calculation command."""
        result = assert_statistics_command_success(["mean", "1", "2", "3", "4", "5"])
        mean_value = float(result.stdout.strip())
        assert abs(mean_value - 3.0) < 0.01
    
    def test_median_command(self):
        """Test median calculation command."""
        # Odd number of elements
        result = assert_statistics_command_success(["median", "1", "2", "3", "4", "5"])
        median_value = float(result.stdout.strip())
        assert abs(median_value - 3.0) < 0.01
        
        # Even number of elements
        result = assert_statistics_command_success(["median", "1", "2", "3", "4"])
        median_value = float(result.stdout.strip())
        assert abs(median_value - 2.5) < 0.01
    
    def test_stddev_command(self):
        """Test standard deviation calculation command."""
        result = assert_statistics_command_success(["stddev", "1", "2", "3", "4", "5"])
        stddev_value = float(result.stdout.strip())
        expected_stddev = math.sqrt(2.0)  # For [1,2,3,4,5]
        assert abs(stddev_value - expected_stddev) < 0.01
    
    def test_min_command(self):
        """Test minimum value command."""
        result = assert_statistics_command_success(["min", "5", "2", "8", "1", "9"])
        min_value = float(result.stdout.strip())
        assert abs(min_value - 1.0) < 0.01
    
    def test_max_command(self):
        """Test maximum value command."""
        result = assert_statistics_command_success(["max", "5", "2", "8", "1", "9"])
        max_value = float(result.stdout.strip())
        assert abs(max_value - 9.0) < 0.01
    
    def test_individual_stats_empty_args(self):
        """Test individual statistics commands with no arguments."""
        commands = ["mean", "median", "stddev", "min", "max"]
        for cmd in commands:
            assert_statistics_command_failure([cmd])
    
    def test_individual_stats_invalid_numbers(self):
        """Test individual statistics commands with invalid numbers."""
        commands = ["mean", "median", "stddev", "min", "max"]
        for cmd in commands:
            assert_statistics_command_failure([cmd, "abc", "def"])


class TestStatisticsErrorHandling:
    """Test error handling scenarios."""
    
    def test_invalid_command(self):
        """Test invalid command."""
        assert_statistics_command_failure(["invalid_command"])
    
    def test_no_arguments(self):
        """Test running with no arguments."""
        assert_statistics_command_failure([])
    
    def test_help_command(self):
        """Test help command (should show usage)."""
        result = assert_statistics_command_failure(["help"])
        # Should contain usage information in stdout (not stderr)
        assert "Usage:" in result.stdout or "usage:" in result.stdout.lower()


class TestStatisticsCalculationAccuracy:
    """Test accuracy of statistical calculations."""
    
    def test_known_dataset_calculations(self):
        """Test calculations with known datasets."""
        test_cases = [
            {
                'data': [1, 2, 3, 4, 5],
                'expected': {
                    'count': 5,
                    'mean': 3.0,
                    'median': 3.0,
                    'std_deviation': math.sqrt(2.0),
                    'min': 1,
                    'max': 5
                }
            },
            {
                'data': [10, 10, 10, 10],
                'expected': {
                    'count': 4,
                    'mean': 10.0,
                    'median': 10.0,
                    'std_deviation': 0.0,
                    'min': 10,
                    'max': 10
                }
            },
            {
                'data': [1, 100],
                'expected': {
                    'count': 2,
                    'mean': 50.5,
                    'median': 50.5,
                    'std_deviation': 49.5,
                    'min': 1,
                    'max': 100
                }
            }
        ]
        
        for case in test_cases:
            args = ["create"] + [str(x) for x in case['data']]
            result = assert_statistics_command_success(args)
            stats = parse_statistics_output(result.stdout)
            assert_statistics_dict_close(stats, case['expected'], tolerance=0.01)
    
    def test_precision_with_decimals(self):
        """Test precision with decimal values (truncated to integers)."""
        result = assert_statistics_command_success(["create", "0.1", "0.2", "0.3"])
        stats = parse_statistics_output(result.stdout)

        # Decimal values are truncated to integers: 0.1->0, 0.2->0, 0.3->0
        expected = calculate_expected_statistics([0, 0, 0])
        assert_statistics_dict_close(stats, expected, tolerance=0.001)


class TestStatisticsComprehensiveWorkflow:
    """Test comprehensive workflows combining multiple operations."""
    
    def test_full_statistics_workflow(self):
        """Test a complete statistics workflow."""
        # Test create command
        dataset = [5, 2, 8, 1, 9, 3, 7, 4, 6]
        args = ["create"] + [str(x) for x in dataset]
        result = assert_statistics_command_success(args)
        
        # Verify the output contains all expected statistics
        output = result.stdout
        assert "Created array with 9 values" in output
        assert "Statistics Summary:" in output
        assert "Count: 9" in output
        assert "Mean:" in output
        assert "Median:" in output
        assert "Std Deviation:" in output
        assert "Min: 1" in output
        assert "Max: 9" in output
        
        # Test individual statistics commands
        mean_result = assert_statistics_command_success(["mean"] + [str(x) for x in dataset])
        median_result = assert_statistics_command_success(["median"] + [str(x) for x in dataset])
        
        # Verify individual results match the create output
        stats = parse_statistics_output(output)
        individual_mean = float(mean_result.stdout.strip())
        individual_median = float(median_result.stdout.strip())
        
        assert abs(stats['mean'] - individual_mean) < 0.01
        assert abs(stats['median'] - individual_median) < 0.01


class TestStatisticsParameterized:
    """Parameterized tests for various datasets."""

    @pytest.mark.parametrize("dataset_name,dataset", [
        ("simple", [1, 2, 3, 4, 5]),
        ("negative", [-5, -3, -1, 1, 3, 5]),
        ("decimal", [1, 2, 3, 4, 5]),  # Decimal inputs truncated to integers
        ("duplicates", [1, 1, 2, 2, 3, 3]),
        ("zeros", [0, 0, 0, 1, 2]),
    ])
    def test_create_various_datasets(self, dataset_name, dataset):
        """Test create command with various datasets."""
        args = ["create"] + [str(x) for x in dataset]
        result = assert_statistics_command_success(args)

        stats = parse_statistics_output(result.stdout)
        expected = calculate_expected_statistics(dataset)
        assert_statistics_dict_close(stats, expected)

    @pytest.mark.parametrize("command", ["mean", "median", "stddev", "min", "max"])
    def test_individual_commands_consistency(self, command):
        """Test that individual commands produce consistent results."""
        dataset = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]

        # Get result from create command
        create_args = ["create"] + [str(x) for x in dataset]
        create_result = assert_statistics_command_success(create_args)
        create_stats = parse_statistics_output(create_result.stdout)

        # Get result from individual command
        individual_args = [command] + [str(x) for x in dataset]
        individual_result = assert_statistics_command_success(individual_args)
        individual_value = float(individual_result.stdout.strip())

        # Map command names to stats keys
        command_map = {
            'mean': 'mean',
            'median': 'median',
            'stddev': 'std_deviation',
            'min': 'min',
            'max': 'max'
        }

        expected_value = create_stats[command_map[command]]
        assert abs(individual_value - expected_value) < 0.01


class TestStatisticsEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_very_large_numbers(self):
        """Test with very large numbers."""
        large_numbers = [1e6, 2e6, 3e6]
        args = ["create"] + [str(x) for x in large_numbers]
        result = assert_statistics_command_success(args)

        stats = parse_statistics_output(result.stdout)
        assert stats['mean'] == 2e6
        assert stats['min'] == 1e6
        assert stats['max'] == 3e6

    def test_very_small_numbers(self):
        """Test with very small numbers (scientific notation parsed as integers)."""
        small_numbers = [1e-6, 2e-6, 3e-6]  # Parsed as 1, 2, 3
        args = ["create"] + [str(x) for x in small_numbers]
        result = assert_statistics_command_success(args)

        stats = parse_statistics_output(result.stdout)
        # Scientific notation is parsed as integers: 1e-6->1, 2e-6->2, 3e-6->3
        expected = calculate_expected_statistics([1, 2, 3])
        assert_statistics_dict_close(stats, expected)

    def test_mixed_precision(self):
        """Test with mixed precision numbers (decimals truncated to integers)."""
        mixed_numbers = [1, 1.1, 1.11, 1.111]  # Truncate to [1, 1, 1, 1]
        args = ["create"] + [str(x) for x in mixed_numbers]
        result = assert_statistics_command_success(args)

        stats = parse_statistics_output(result.stdout)
        # All decimal values truncate to 1
        expected = calculate_expected_statistics([1, 1, 1, 1])
        assert_statistics_dict_close(stats, expected, tolerance=0.001)

    def test_maximum_array_size(self):
        """Test with maximum reasonable array size."""
        # Test with 1000 elements
        large_dataset = list(range(1, 1001))
        args = ["create"] + [str(x) for x in large_dataset[:500]]  # Limit for performance
        result = assert_statistics_command_success(args)

        assert "Created array with 500 values" in result.stdout
        stats = parse_statistics_output(result.stdout)
        assert stats['count'] == 500
        assert stats['min'] == 1
        assert stats['max'] == 500


class TestStatisticsInterModuleDependency:
    """Test inter-module dependencies and integration."""

    def test_statistics_with_algorithm_array(self, algorithm_cli_path):
        """Test statistics analysis of algorithm-created arrays."""
        if not algorithm_cli_path:
            pytest.skip("Algorithm CLI not available for inter-module testing")

        import subprocess
        import os

        # Clean up any existing array file
        temp_file = "/tmp/pydcov_array.dat"
        if os.path.exists(temp_file):
            os.remove(temp_file)

        try:
            # Create array with algorithm CLI
            subprocess.run([algorithm_cli_path, "dynarray", "create", "5"], check=True)
            subprocess.run([algorithm_cli_path, "dynarray", "push", "10", "20", "30", "40", "50"], check=True)

            # Analyze with statistics CLI
            result = assert_statistics_command_success(["analyze"])
            stats = parse_statistics_output(result.stdout)

            # Verify statistics for [10, 20, 30, 40, 50]
            expected = calculate_expected_statistics([10, 20, 30, 40, 50])
            assert_statistics_dict_close(stats, expected)

        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_algorithm_dependency_in_statistics(self):
        """Test that statistics module correctly uses algorithm module functions."""
        # This test verifies that the statistics module can use dynamic array
        # functions from the algorithm module (since statistics depends on algorithm)

        # Create a dataset that exercises the dynamic array functionality
        dataset = list(range(1, 21))  # 20 elements to test array expansion
        args = ["create"] + [str(x) for x in dataset]
        result = assert_statistics_command_success(args)

        stats = parse_statistics_output(result.stdout)
        expected = calculate_expected_statistics(dataset)
        assert_statistics_dict_close(stats, expected)

        # Verify that all 20 elements were processed correctly
        assert stats['count'] == 20
        assert stats['min'] == 1
        assert stats['max'] == 20
