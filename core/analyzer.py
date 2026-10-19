"""Core analysis, code inspection, and AST validation engine for AI Code Doctor."""

import ast
import difflib
import re
from typing import Any, Dict, List, Optional, Tuple


class StaticAnalysisResult:
    """Encapsulates static syntax and structural analysis metrics."""

    def __init__(
        self,
        is_valid_syntax: bool,
        syntax_error: Optional[str] = None,
        functions: Optional[List[Dict[str, Any]]] = None,
        classes: Optional[List[Dict[str, Any]]] = None,
        imports: Optional[List[str]] = None,
        loc: int = 0,
        complexity_hints: Optional[List[str]] = None,
    ):
        self.is_valid_syntax = is_valid_syntax
        self.syntax_error = syntax_error
        self.functions = functions or []
        self.classes = classes or []
        self.imports = imports or []
        self.loc = loc
        self.complexity_hints = complexity_hints or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid_syntax": self.is_valid_syntax,
            "syntax_error": self.syntax_error,
            "functions": self.functions,
            "classes": self.classes,
            "imports": self.imports,
            "loc": self.loc,
            "complexity_hints": self.complexity_hints,
        }


def analyze_python_code_ast(code: str) -> StaticAnalysisResult:
    """Performs fast offline AST static analysis on user Python code."""
    if not code or not code.strip():
        return StaticAnalysisResult(
            is_valid_syntax=False,
            syntax_error="Empty code provided.",
            loc=0
        )

    lines = code.splitlines()
    loc = len([line for line in lines if line.strip() and not line.strip().startswith("#")])

    try:
        tree = ast.parse(code)
    except SyntaxError as se:
        error_msg = f"SyntaxError at line {se.lineno}, col {se.offset}: {se.msg}"
        return StaticAnalysisResult(
            is_valid_syntax=False,
            syntax_error=error_msg,
            loc=loc
        )

    functions = []
    classes = []
    imports = []
    complexity_hints = []

    # Separate top-level functions vs class methods
    for item in tree.body:
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [a.arg for a in item.args.args]
            functions.append({
                "name": item.name,
                "lineno": item.lineno,
                "args": args,
                "is_async": isinstance(item, ast.AsyncFunctionDef),
            })
        elif isinstance(item, ast.ClassDef):
            classes.append({
                "name": item.name,
                "lineno": item.lineno,
                "methods": [
                    m.name for m in item.body
                    if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))
                ],
            })

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check for high cyclomatic hints (nested branches / loops)
            branch_count = sum(
                1 for child in ast.walk(node)
                if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With))
            )
            if branch_count >= 5:
                complexity_hints.append(
                    f"Function `{node.name}` has {branch_count} branching/loop constructs. Consider decomposing."
                )

        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}" if module else alias.name)

    return StaticAnalysisResult(
        is_valid_syntax=True,
        functions=functions,
        classes=classes,
        imports=imports,
        loc=loc,
        complexity_hints=complexity_hints,
    )


def extract_code_fence(text: str, default_lang: str = "python") -> str:
    """Robustly cleans markdown fences and surrounding commentary from LLM output."""
    if not text:
        return ""

    text = text.strip()

    # Look for ```python or ``` block
    pattern = rf"```(?:{default_lang}|py)?\s*([\s\S]*?)```"
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    if matches:
        # Return the longest code block found
        return max(matches, key=len).strip()

    # If starts with ``` and hasn't closed
    text = re.sub(r"^```[a-zA-Z0-9_-]*\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def build_unified_diff(original: str, refactored: str, from_title: str = "Original", to_title: str = "Refactored") -> str:
    """Generates a standard unified diff between original code and fixed/refactored code."""
    from_lines = original.splitlines(keepends=True)
    to_lines = refactored.splitlines(keepends=True)

    diff = difflib.unified_diff(
        from_lines,
        to_lines,
        fromfile=from_title,
        tofile=to_title,
        lineterm=""
    )
    return "".join(diff)


def create_executable_test_code(source_code: str, test_code: str) -> str:
    """Wraps test code with source code imports or inlines source definitions

    ensuring test functions can execute self-contained without NameError.
    """
    cleaned_test = extract_code_fence(test_code)
    cleaned_source = source_code.strip()

    # Check if test code already imports or embeds the functions
    # If not, embed the user code header so pytest can run seamlessly
    banner = (
        "# ====================================================================\n"
        "# AUTO-INLINE SOURCE CODE (Generated for standalone pytest execution)\n"
        "# ====================================================================\n"
    )
    separator = (
        "\n# ====================================================================\n"
        "# PYTEST TEST SUITE\n"
        "# ====================================================================\n"
    )

    if cleaned_source in cleaned_test:
        return cleaned_test

    return f"{banner}{cleaned_source}\n{separator}\n{cleaned_test}\n"
