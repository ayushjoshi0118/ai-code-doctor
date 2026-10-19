"""Gemini AI API service client handling prompt construction, model fallback, and streaming."""

import os
from typing import Any, Dict, Generator, List, Optional
from google import genai
from google.genai import errors


# Ranked fallback models for high availability
FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-flash-latest",
    "gemini-3.1-flash-lite",
]


class GeminiService:
    """Enterprise wrapper for the modern Google GenAI Client."""

    def __init__(self, api_key: Optional[str] = None, default_model: str = "gemini-3.5-flash-lite"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.default_model = default_model
        self._client: Optional[genai.Client] = None

    @property
    def client(self) -> Optional[genai.Client]:
        if self._client is None and self.api_key:
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    def test_connection(self) -> Dict[str, Any]:
        """Tests API authentication and latency against the designated model."""
        if not self.is_configured():
            return {
                "success": False,
                "model": self.default_model,
                "message": "GEMINI_API_KEY is not set. Please provide a key in .env or the UI.",
            }

        try:
            client = self.client
            assert client is not None
            response = client.models.generate_content(
                model=self.default_model,
                contents="Reply with: Connection OK"
            )
            text = response.text.strip() if response and response.text else "No text response"
            return {
                "success": True,
                "model": self.default_model,
                "message": f"Successfully connected to {self.default_model}! Response: '{text}'",
            }
        except errors.ClientError as ce:
            # Handle model deprecation/migration hints
            msg = str(ce)
            return {
                "success": False,
                "model": self.default_model,
                "message": f"Client error: {msg}",
            }
        except Exception as e:
            return {
                "success": False,
                "model": self.default_model,
                "message": f"{type(e).__name__}: {str(e)}",
            }

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        """Executes generation with automatic fallback to secondary models if one is busy or unavailable."""
        if not self.is_configured():
            raise ValueError("GEMINI_API_KEY is required to contact Google Gemini API.")

        models_to_try = [model] if model else [self.default_model]
        for m in FALLBACK_MODELS:
            if m not in models_to_try:
                models_to_try.append(m)

        last_error = None
        for target_model in models_to_try:
            try:
                client = self.client
                assert client is not None
                config: Dict[str, Any] = {"temperature": temperature}
                if system_instruction:
                    config["system_instruction"] = system_instruction

                response = client.models.generate_content(
                    model=target_model,
                    contents=prompt,
                    config=config,
                )
                if response and response.text:
                    return response.text
                return "ERROR: Gemini returned an empty response."
            except errors.ServerError as se:
                # 503 Overloaded or temporarily unavailable - try fallback model
                last_error = se
                continue
            except errors.ClientError as ce:
                # If 404 model not found or deprecated, try next model in fallback list
                if "404" in str(ce) or "not found" in str(ce).lower():
                    last_error = ce
                    continue
                raise ce
            except Exception as e:
                last_error = e
                continue

        if last_error:
            raise RuntimeError(f"All model attempts exhausted. Last error: {last_error}")
        return "ERROR: Failed to obtain completion."

    def detect_bugs(self, code: str, model: Optional[str] = None) -> str:
        """Performs deep bug diagnosis, root cause analysis, and triage."""
        prompt = f"""You are a Principal Software Quality Engineer and Python Security Specialist.

Analyze the following Python program systematically for all defects, bugs, edge-case failures, and architectural vulnerabilities.

Inspect specifically for:
1. Syntax and indentation errors
2. Runtime exceptions (NameError, TypeError, ZeroDivisionError, IndexError, KeyError, AttributeError)
3. Logical defects and flawed conditions or loops
4. Off-by-one errors and boundary condition violations
5. Dangerous default mutable arguments
6. Unhandled empty inputs (empty lists, empty strings, None)
7. Silent type coercions and floating point inaccuracies
8. Resource leaks (unclosed files/sockets)

Format your output in clean, structured Markdown:

### 📊 Bug Overview
A quick 1-2 sentence assessment of code health, identifying the total bug count and primary failure modes.

### 🐛 Detailed Findings
For each distinct issue, provide:
- **Bug #**: Name of the issue
- **Location**: Function or line context
- **Severity**: Critical / High / Medium / Low
- **Problem**: Clear description of what is wrong
- **Root Cause**: Why this behavior occurs under Python semantics
- **Reproduction**: Input that triggers the failure
- **Expected vs Actual**: Expected return/state vs actual return/crash
- **Suggested Fix**: Short code snippet or explanation

If no bugs are detected, state: "✅ No critical bugs detected. The code demonstrates sound logic and edge case handling."

---
Python Code Under Review:
```python
{code}
```
"""
        return self.generate(prompt=prompt, model=model, temperature=0.1)

    def generate_pytest_suite(
        self,
        code: str,
        test_framework: str = "pytest",
        include_edge_cases: bool = True,
        include_benchmarks: bool = False,
        model: Optional[str] = None,
    ) -> str:
        """Generates a complete, production-grade test suite for the supplied code."""
        prompt = f"""You are an expert Test Automation Engineer specializing in {test_framework}.

Create a comprehensive, production-grade {test_framework} test suite for the Python program below.

Strict Requirements:
1. Provide ONLY valid, executable Python code.
2. Include ALL necessary imports (pytest, etc.).
3. If helper imports are needed, import them safely.
4. Test happy path cases, typical usage, and normal values.
5. {"Test edge cases: empty collections, None values, negative numbers, extreme boundaries, large inputs." if include_edge_cases else ""}
6. Use pytest.raises() to verify expected exceptions (e.g. ZeroDivisionError, ValueError, TypeError).
7. Use pytest.mark.parametrize where applicable to test multiple input-output pairs cleanly.
8. Use descriptive, self-documenting test function names prefixed with `test_`.
9. Do not use markdown explanations outside the code block.

Python Code to Test:
```python
{code}
```
"""
        return self.generate(prompt=prompt, model=model, temperature=0.2)

    def generate_refactored_code(self, code: str, bug_report: str = "", model: Optional[str] = None) -> str:
        """Generates clean, idiomatic, PEP 8 compliant, bug-fixed code."""
        prompt = f"""You are a Senior Python Architect.

Refactor and fix the provided Python code to resolve any bugs, handle all edge cases, and adhere to PEP 8 standards, modern type hinting, and robust error handling.

Instructions:
1. Fix all logical, runtime, and edge-case errors.
2. Add Python 3.10+ type annotations to all parameters and return types.
3. Add clean docstrings (Google or Sphinx style) describing arguments, returns, and exceptions raised.
4. Preserve the original function names and public API contracts so external callers don't break.
5. Provide ONLY the refactored Python code inside a markdown python code block.
6. Provide a concise summary of changes below the code block.

Original Python Code:
```python
{code}
```

Known Bug Context (if any):
{bug_report}
"""
        return self.generate(prompt=prompt, model=model, temperature=0.1)

    def explain_code_and_complexity(self, code: str, model: Optional[str] = None) -> str:
        """Explains time and space complexity, algorithmic design, and architectural improvements."""
        prompt = f"""You are an Algorithms and Systems Performance Specialist.

Analyze the computational complexity and design of this Python program:

1. **Time Complexity**: Big-O analysis for each major function (best, average, worst case).
2. **Space Complexity**: Memory footprint and auxiliary space requirements.
3. **Bottlenecks & Optimization**: Inefficiencies (e.g. O(N^2) loops, unnecessary allocations).
4. **Architectural Improvements**: Idiomatic Python patterns (generators, built-ins, standard library modules) that would improve efficiency.

Python Code:
```python
{code}
```
"""
        return self.generate(prompt=prompt, model=model, temperature=0.2)
