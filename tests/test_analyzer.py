"""Unit tests for AST static analyzer, diff generation, and test synthesizers."""

import pytest
from core.analyzer import (
    analyze_python_code_ast,
    build_unified_diff,
    create_executable_test_code,
    extract_code_fence,
)


def test_ast_analysis_valid_code():
    code = """def add(a: int, b: int) -> int:
    return a + b

class Calculator:
    def multiply(self, x, y):
        return x * y
"""
    result = analyze_python_code_ast(code)
    assert result.is_valid_syntax is True
    assert result.syntax_error is None
    assert result.loc > 0
    assert len(result.functions) == 1
    assert result.functions[0]["name"] == "add"
    assert result.functions[0]["args"] == ["a", "b"]
    assert len(result.classes) == 1
    assert result.classes[0]["name"] == "Calculator"
    assert "multiply" in result.classes[0]["methods"]


def test_ast_analysis_syntax_error():
    broken_code = """def broken_func(a, b
    return a + b
"""
    result = analyze_python_code_ast(broken_code)
    assert result.is_valid_syntax is False
    assert result.syntax_error is not None
    assert "SyntaxError" in result.syntax_error


def test_ast_analysis_empty_code():
    result = analyze_python_code_ast("")
    assert result.is_valid_syntax is False
    assert "Empty code" in result.syntax_error


def test_extract_code_fence_with_markdown():
    markdown_text = """Here is the generated test:
```python
import pytest

def test_add():
    assert 1 + 1 == 2
```
Hope this helps!
"""
    extracted = extract_code_fence(markdown_text)
    assert "def test_add():" in extracted
    assert "```" not in extracted
    assert "Hope this helps" not in extracted


def test_extract_code_fence_raw_code():
    raw_code = "def test_foo():\n    assert True"
    extracted = extract_code_fence(raw_code)
    assert extracted == raw_code


def test_build_unified_diff():
    original = "def foo():\n    return 1\n"
    refactored = "def foo():\n    # Fixed\n    return 2\n"
    diff = build_unified_diff(original, refactored)
    assert "--- Original" in diff
    assert "+++ Refactored" in diff
    assert "+    # Fixed" in diff


def test_create_executable_test_code():
    source = "def square(n):\n    return n * n"
    test_code = "def test_square():\n    assert square(3) == 9"

    combined = create_executable_test_code(source, test_code)
    assert "AUTO-INLINE SOURCE CODE" in combined
    assert "def square(n):" in combined
    assert "def test_square():" in combined
