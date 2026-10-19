"""Unit tests for the sandboxed test runner."""

from core.test_runner import run_tests_in_sandbox


def test_sandbox_passing_tests():
    test_code = """
import pytest

def add(a, b):
    return a + b

def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, -1) == -2
"""
    result = run_tests_in_sandbox(test_code, timeout_seconds=10)
    assert result.is_success is True
    assert result.passed == 2
    assert result.failed == 0
    assert result.errors == 0
    assert result.exit_code == 0


def test_sandbox_failing_tests():
    test_code = """
def test_failing():
    assert 1 == 2
"""
    result = run_tests_in_sandbox(test_code, timeout_seconds=10)
    assert result.is_success is False
    assert result.failed == 1
    assert result.exit_code != 0


def test_sandbox_timeout_handling():
    # Infinite loop code
    test_code = """
def test_loop():
    while True:
        pass
"""
    result = run_tests_in_sandbox(test_code, timeout_seconds=2)
    assert result.is_success is False
    assert result.exit_code == -1
    assert "timed out" in result.raw_stderr.lower()
