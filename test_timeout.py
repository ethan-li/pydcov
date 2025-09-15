#!/usr/bin/env python3
"""
Test script to verify timeout parameter functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from pydcov.cli import validate_timeout, parse_arguments

def test_timeout_validation():
    """Test the timeout validation function"""
    print("Testing timeout validation...")
    
    # Test valid timeouts
    valid_timeouts = [1, 60, 600, 1200, 3600, 7200]
    for timeout in valid_timeouts:
        result = validate_timeout(timeout)
        print(f"  timeout={timeout}: {'PASS' if result else 'FAIL'}")
        assert result, f"Expected timeout {timeout} to be valid"
    
    # Test invalid timeouts
    invalid_timeouts = [0, -1, -100, 7201, 10000]
    for timeout in invalid_timeouts:
        result = validate_timeout(timeout)
        print(f"  timeout={timeout}: {'PASS' if not result else 'FAIL'}")
        assert not result, f"Expected timeout {timeout} to be invalid"
    
    print("✓ Timeout validation tests passed")

def test_argument_parsing():
    """Test argument parsing with timeout parameter"""
    print("\nTesting argument parsing...")
    
    # Test default timeout
    args = parse_arguments(['add', 'echo', 'test'])
    assert args.timeout == 600, f"Expected default timeout 600, got {args.timeout}"
    print("  ✓ Default timeout (600) parsed correctly")
    
    # Test custom timeout
    args = parse_arguments(['add', '--timeout', '1200', 'echo', 'test'])
    assert args.timeout == 1200, f"Expected timeout 1200, got {args.timeout}"
    print("  ✓ Custom timeout (1200) parsed correctly")
    
    # Test timeout with test args
    args = parse_arguments(['add', '--timeout', '300', 'python', '-m', 'pytest', 'tests/'])
    assert args.timeout == 300, f"Expected timeout 300, got {args.timeout}"
    assert args.test_args == ['python', '-m', 'pytest', 'tests/'], f"Test args not parsed correctly: {args.test_args}"
    print("  ✓ Timeout with test args parsed correctly")
    
    print("✓ Argument parsing tests passed")

if __name__ == '__main__':
    test_timeout_validation()
    test_argument_parsing()
    print("\n🎉 All tests passed!")
