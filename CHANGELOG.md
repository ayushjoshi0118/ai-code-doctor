# Changelog

All notable changes to **AI Code Doctor** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-10-19

### Added
- **Interactive Sandbox Execution**: Run generated pytest suites directly in an isolated temporary environment with real-time pass/fail metrics and stdout/stderr capture.
- **AST Static Analysis Inspector**: Real-time syntax validation, LOC calculation, callable extraction, and cyclomatic complexity warnings before sending code to the LLM.
- **Self-Contained Test Synthesizer**: Automatically links/inlines user code into `test_generated.py` so tests run standalone without `NameError`.
- **Automated Refactoring & Unified Diff**: Generate PEP 8 compliant, type-annotated, bug-fixed code with a side-by-side unified diff view.
- **Algorithmic Complexity & Architecture Analyzer**: Detailed Big-O time and space complexity breakdown with bottleneck analysis.
- **Curated Bug Presets**: Instant loading for classic collections, mutable default arguments, binary search off-by-one errors, and authentication flaws.
- **Script File Uploader**: Direct `.py` file drag-and-drop support.
- **Session Export**: Complete JSON report download bundling AST analysis, bug diagnosis, test suites, and refactored code.
- **Multi-Model Support & Fallback**: Support for `gemini-3.5-flash-lite`, `gemini-3.8-flash`, and dynamic fallback mechanisms.
- **Automated CI/CD Workflow**: GitHub Actions workflow testing on Python 3.10, 3.11, and 3.12.
- **Unit Test Suite**: 14 comprehensive tests covering core analyzers, sandbox runner, and Gemini services.

### Changed
- Refactored monolithic `app.py` into modular architecture (`core/` package).
- Migrated legacy/deprecated models to modern `google-genai` SDK endpoints.
- Replaced basic styling with a responsive glassmorphism dark/light design system.
- Hardened `.gitignore` to prevent secret leaks and cached artifacts from entering version control.

### Fixed
- Fixed `NameError` preventing generated tests from executing independently in pytest.
- Fixed 404 client errors caused by decommissioned Gemini model strings.
- Fixed missing requirements and untracked dependencies.

## [1.0.0] - Prior Release
- Initial basic prototype with bug detection and test generation.
