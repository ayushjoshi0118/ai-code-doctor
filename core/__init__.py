"""Core analysis and testing engine for AI Code Doctor."""

from core.analyzer import (
    StaticAnalysisResult,
    analyze_python_code_ast,
    build_unified_diff,
    create_executable_test_code,
    extract_code_fence,
)
from core.gemini_service import GeminiService
from core.sample_codes import SAMPLE_SNIPPETS
from core.test_runner import TestRunnerResult, run_tests_in_sandbox

__all__ = [
    "StaticAnalysisResult",
    "analyze_python_code_ast",
    "build_unified_diff",
    "create_executable_test_code",
    "extract_code_fence",
    "GeminiService",
    "SAMPLE_SNIPPETS",
    "TestRunnerResult",
    "run_tests_in_sandbox",
]
