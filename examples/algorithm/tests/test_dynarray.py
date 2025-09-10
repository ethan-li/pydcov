#!/usr/bin/env python3
"""
Test suite for dynamic array operations in the C algorithm library.
"""

import pytest
from examples.algorithm.tests.algorithm_test_utils import run_command, assert_command_success, assert_command_failure


class TestDynamicArrayOperations:
    """Test dynamic array operations."""
    
    def test_dynarray_create_basic(self):
        """Test dynamic array creation."""
        capacities = [1, 5, 10, 100]
        
        for capacity in capacities:
            result = assert_command_success(["dynarray", "create", str(capacity)])
            output = result.stdout.strip()
            assert f"Array created with capacity {capacity}" in output
    
    def test_dynarray_create_invalid(self):
        """Test dynamic array creation with invalid capacities."""
        invalid_capacities = [0, -1, -10]
        
        for capacity in invalid_capacities:
            assert_command_failure(["dynarray", "create", str(capacity)])
    
    def test_dynarray_push_single(self):
        """Test pushing single values to dynamic array."""
        # Create array
        assert_command_success(["dynarray", "create", "5"])
        
        # Push single values
        values = [1, 2, 3, 4, 5]
        for i, value in enumerate(values, 1):
            result = assert_command_success(["dynarray", "push", str(value)])
            output = result.stdout.strip()
            assert f"Pushed 1 values. Array size: {i}" in output
    
    def test_dynarray_push_multiple(self):
        """Test pushing multiple values at once."""
        # Create array
        assert_command_success(["dynarray", "create", "10"])
        
        # Push multiple values
        result = assert_command_success(["dynarray", "push", "1", "2", "3", "4", "5"])
        output = result.stdout.strip()
        assert "Pushed 5 values. Array size: 5" in output
        
        # Push more values
        result = assert_command_success(["dynarray", "push", "6", "7"])
        output = result.stdout.strip()
        assert "Pushed 2 values. Array size: 7" in output
    
    def test_dynarray_push_expansion(self):
        """Test array expansion when capacity is exceeded."""
        # Create small array
        assert_command_success(["dynarray", "create", "2"])
        
        # Push values that exceed initial capacity
        result = assert_command_success(["dynarray", "push", "1", "2", "3", "4", "5"])
        output = result.stdout.strip()
        assert "Pushed 5 values. Array size: 5" in output
    
    def test_dynarray_get_basic(self):
        """Test getting values from dynamic array."""
        # Create and populate array
        assert_command_success(["dynarray", "create", "10"])
        assert_command_success(["dynarray", "push", "10", "20", "30", "40", "50"])
        
        # Test getting values at different indices
        test_cases = [
            (0, 10),
            (1, 20),
            (2, 30),
            (3, 40),
            (4, 50)
        ]
        
        for index, expected_value in test_cases:
            result = assert_command_success(["dynarray", "get", str(index)])
            actual_value = int(result.stdout.strip())
            assert actual_value == expected_value, \
                f"get({index}) = {expected_value}, got {actual_value}"
    
    def test_dynarray_get_invalid_index(self):
        """Test getting values with invalid indices."""
        # Create and populate array
        assert_command_success(["dynarray", "create", "5"])
        assert_command_success(["dynarray", "push", "1", "2", "3"])
        
        # Test invalid indices
        invalid_indices = [-1, 3, 5, 10]  # Array has size 3, valid indices are 0, 1, 2
        
        for index in invalid_indices:
            assert_command_failure(["dynarray", "get", str(index)])
    
    def test_dynarray_pop_single(self):
        """Test popping single values from dynamic array."""
        # Create and populate array
        assert_command_success(["dynarray", "create", "5"])
        assert_command_success(["dynarray", "push", "10", "20", "30"])
        
        # Pop values (should return in LIFO order)
        expected_values = [30, 20, 10]
        
        for expected_value in expected_values:
            result = assert_command_success(["dynarray", "pop"])
            actual_value = int(result.stdout.strip())
            assert actual_value == expected_value, \
                f"pop() = {expected_value}, got {actual_value}"
    
    def test_dynarray_pop_multiple(self):
        """Test popping multiple values at once."""
        # Create and populate array
        assert_command_success(["dynarray", "create", "10"])
        assert_command_success(["dynarray", "push", "1", "2", "3", "4", "5"])
        
        # Pop 3 values
        result = assert_command_success(["dynarray", "pop", "3"])
        popped_values = [int(x) for x in result.stdout.strip().split()]
        expected_values = [5, 4, 3]  # LIFO order
        assert popped_values == expected_values, \
            f"pop(3) = {expected_values}, got {popped_values}"
        
        # Verify remaining values
        result = assert_command_success(["dynarray", "get", "0"])
        assert int(result.stdout.strip()) == 1
        
        result = assert_command_success(["dynarray", "get", "1"])
        assert int(result.stdout.strip()) == 2
    
    def test_dynarray_pop_empty(self):
        """Test popping from empty array."""
        # Create empty array
        assert_command_success(["dynarray", "create", "5"])
        
        # Try to pop from empty array
        assert_command_failure(["dynarray", "pop"])
        
        # Try to pop multiple from empty array
        assert_command_failure(["dynarray", "pop", "3"])
    
    def test_dynarray_pop_too_many(self):
        """Test popping more values than available."""
        # Create and populate array with 2 values
        assert_command_success(["dynarray", "create", "5"])
        assert_command_success(["dynarray", "push", "1", "2"])
        
        # Try to pop 3 values (more than available)
        assert_command_failure(["dynarray", "pop", "3"])
    
    def test_dynarray_operations_without_create(self):
        """Test operations without creating array first."""
        # Clean up any existing array first
        run_command(["dynarray", "cleanup"])

        # These should all fail because no array was created
        assert_command_failure(["dynarray", "push", "1"])
        assert_command_failure(["dynarray", "pop"])
        assert_command_failure(["dynarray", "get", "0"])
    
    def test_dynarray_recreate(self):
        """Test recreating array (should destroy previous one)."""
        # Create first array
        assert_command_success(["dynarray", "create", "5"])
        assert_command_success(["dynarray", "push", "1", "2", "3"])
        
        # Create second array (should replace first)
        assert_command_success(["dynarray", "create", "10"])
        
        # Previous data should be gone
        assert_command_failure(["dynarray", "get", "0"])  # Should fail because new array is empty
        
        # New array should work
        assert_command_success(["dynarray", "push", "100"])
        result = assert_command_success(["dynarray", "get", "0"])
        assert int(result.stdout.strip()) == 100
    
    def test_dynarray_comprehensive_workflow(self):
        """Test a comprehensive workflow using all dynamic array operations."""
        # Create array
        assert_command_success(["dynarray", "create", "3"])
        
        # Push some values (will trigger expansion)
        assert_command_success(["dynarray", "push", "10", "20", "30", "40", "50"])
        
        # Verify values
        for i, expected in enumerate([10, 20, 30, 40, 50]):
            result = assert_command_success(["dynarray", "get", str(i)])
            actual = int(result.stdout.strip())
            assert actual == expected
        
        # Pop some values
        result = assert_command_success(["dynarray", "pop", "2"])
        popped = [int(x) for x in result.stdout.strip().split()]
        assert popped == [50, 40]
        
        # Verify remaining values
        for i, expected in enumerate([10, 20, 30]):
            result = assert_command_success(["dynarray", "get", str(i)])
            actual = int(result.stdout.strip())
            assert actual == expected
        
        # Push more values
        assert_command_success(["dynarray", "push", "60", "70"])
        
        # Final verification
        for i, expected in enumerate([10, 20, 30, 60, 70]):
            result = assert_command_success(["dynarray", "get", str(i)])
            actual = int(result.stdout.strip())
            assert actual == expected
    
    def test_dynarray_error_cases(self):
        """Test error handling for dynamic array operations."""
        # Test missing arguments
        assert_command_failure(["dynarray", "create"])
        assert_command_failure(["dynarray", "get"])
        
        # Test too many arguments
        assert_command_failure(["dynarray", "create", "5", "10"])
        assert_command_failure(["dynarray", "get", "0", "1"])
        
        # Test invalid operation
        assert_command_failure(["dynarray", "invalid_op"])
    
    def test_dynarray_negative_values(self):
        """Test dynamic array with negative values."""
        # Create and populate with negative values
        assert_command_success(["dynarray", "create", "5"])
        assert_command_success(["dynarray", "push", "-10", "-20", "0", "10", "20"])
        
        # Verify negative values
        test_cases = [
            (0, -10),
            (1, -20),
            (2, 0),
            (3, 10),
            (4, 20)
        ]
        
        for index, expected in test_cases:
            result = assert_command_success(["dynarray", "get", str(index)])
            actual = int(result.stdout.strip())
            assert actual == expected
        
        # Pop and verify
        result = assert_command_success(["dynarray", "pop", "2"])
        popped = [int(x) for x in result.stdout.strip().split()]
        assert popped == [20, 10]
