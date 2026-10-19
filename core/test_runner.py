"""Sandboxed test runner using pytest to execute generated test suites safely."""

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Optional


class TestRunnerResult:
    """Encapsulates pytest execution metrics and output."""

    def __init__(
        self,
        exit_code: int,
        passed: int,
        failed: int,
        errors: int,
        skipped: int,
        duration: float,
        raw_stdout: str,
        raw_stderr: str,
        summary_line: str,
    ):
        self.exit_code = exit_code
        self.passed = passed
        self.failed = failed
        self.errors = errors
        self.skipped = skipped
        self.duration = duration
        self.raw_stdout = raw_stdout
        self.raw_stderr = raw_stderr
        self.summary_line = summary_line

    @property
    def is_success(self) -> bool:
        return self.exit_code == 0 and self.failed == 0 and self.errors == 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_success": self.is_success,
            "exit_code": self.exit_code,
            "passed": self.passed,
            "failed": self.failed,
            "errors": self.errors,
            "skipped": self.skipped,
            "duration": self.duration,
            "summary_line": self.summary_line,
        }


def run_tests_in_sandbox(
    test_code_content: str,
    timeout_seconds: int = 15
) -> TestRunnerResult:
    """Executes a standalone pytest script in an isolated temporary directory

    and captures structured pass/fail results.
    """
    temp_dir = tempfile.mkdtemp(prefix="ai_code_doc_test_")
    test_file_path = Path(temp_dir) / "test_suite.py"

    try:
        test_file_path.write_text(test_code_content, encoding="utf-8")

        start_time = time.time()
        # Run pytest via current python executable in subprocess
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(test_file_path),
            "-v",
            "--tb=short",
            "-o", "console_output_style=classic",
        ]

        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds,
            cwd=temp_dir,
        )
        elapsed = round(time.time() - start_time, 2)

        stdout = proc.stdout
        stderr = proc.stderr
        exit_code = proc.returncode

        # Parse counts from pytest output
        passed = 0
        failed = 0
        errors = 0
        skipped = 0
        summary_line = "Execution finished."

        # Scan lines from bottom
        lines = stdout.splitlines()
        for line in reversed(lines):
            line_strip = line.strip()
            if "=====" in line_strip and ("passed" in line_strip or "failed" in line_strip or "error" in line_strip):
                summary_line = line_strip.strip("=").strip()
                # Extract numbers
                import re
                p_match = re.search(r"(\d+)\s+passed", line_strip)
                f_match = re.search(r"(\d+)\s+failed", line_strip)
                e_match = re.search(r"(\d+)\s+error", line_strip)
                s_match = re.search(r"(\d+)\s+skipped", line_strip)

                if p_match:
                    passed = int(p_match.group(1))
                if f_match:
                    failed = int(f_match.group(1))
                if e_match:
                    errors = int(e_match.group(1))
                if s_match:
                    skipped = int(s_match.group(1))
                break

        return TestRunnerResult(
            exit_code=exit_code,
            passed=passed,
            failed=failed,
            errors=errors,
            skipped=skipped,
            duration=elapsed,
            raw_stdout=stdout,
            raw_stderr=stderr,
            summary_line=summary_line,
        )

    except subprocess.TimeoutExpired:
        return TestRunnerResult(
            exit_code=-1,
            passed=0,
            failed=0,
            errors=1,
            skipped=0,
            duration=float(timeout_seconds),
            raw_stdout="",
            raw_stderr=f"Test execution timed out after {timeout_seconds} seconds (possible infinite loop in user code).",
            summary_line=f"Timed out after {timeout_seconds}s.",
        )
    except Exception as exc:
        return TestRunnerResult(
            exit_code=-2,
            passed=0,
            failed=0,
            errors=1,
            skipped=0,
            duration=0.0,
            raw_stdout="",
            raw_stderr=f"Runner exception: {type(exc).__name__}: {str(exc)}",
            summary_line="Execution failed to initialize.",
        )
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)
