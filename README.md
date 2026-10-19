# 🧪 AI Code Doctor

[![CI Quality & Test Suite](https://github.com/ayushjoshi0118/ai-code-doctor/actions/workflows/ci.yml/badge.svg)](https://github.com/ayushjoshi0118/ai-code-doctor/actions/workflows/ci.yml)

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

**AI Code Doctor** is a modern, developer-first AI quality engineering suite built with Python, Streamlit, Google Gemini AI (GenAI SDK), and Pytest. It autonomously inspects Python code, identifies hidden runtime defects and logical vulnerabilities, generates executable `pytest` test suites, validates execution in a secure sandbox, and automatically refactors code to production-grade PEP 8 standards with unified visual diffs.

---

## ✨ Features

- 🐞 **Intelligent Defect Diagnosis**: Identifies syntax errors, runtime exceptions (`IndexError`, `ZeroDivisionError`, `KeyError`), dangerous mutable default arguments, off-by-one errors, and unhandled edge cases.
- ⚡ **AST Static Inspector (Pre-flight)**: Local AST parsing runs immediately as you type, detecting syntax errors, LOC metrics, callable signatures, and branching complexity before making any LLM call.
- 🧪 **Self-Contained Pytest Generator**: Generates clean, parameterized pytest test suites with boundary and edge case assertions. Automatically inlines required source definitions so tests never fail with `NameError`.
- ▶️ **Sandboxed Test Runner**: Executes generated pytest suites directly from your browser inside an isolated temporary directory, capturing real-time test execution time, stdout, and pass/fail tallies.
- 🔧 **Auto-Refactoring & Unified Diffs**: Automatically rewrites flawed Python code with PEP 8 standards, Google-style docstrings, and strict type annotations, alongside a side-by-side unified diff.
- 📈 **Big-O Complexity & Architecture**: Computes algorithmic time and space complexity, flags O(N²) bottlenecks, and suggests idiomatic Python optimizations.
- 📚 **Curated Defect Presets**: Load real-world code snippets demonstrating mutable defaults, off-by-one binary search loops, float calculation bugs, and dictionary lookup flaws.
- 📦 **Audit Export**: Export complete session logs, AST metrics, test suites, and refactored code to a single `.json` audit artifact.
- 🛡️ **Model Failover & Resiliency**: Designed with multi-model failover (`gemini-3.5-flash-lite`, `gemini-3.8-flash`, etc.) for uninterrupted uptime.

---

## 🏗️ Architecture

```
AI_Unit_Test_Bug_Detector/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   └── feature_request.yml
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       └── ci.yml
├── core/
│   ├── __init__.py          # Public API export
│   ├── analyzer.py          # AST static analysis, diff builder, test synthesizer
│   ├── gemini_service.py    # Google GenAI client with model fallback & prompts
│   ├── sample_codes.py      # Pre-curated bug presets
│   └── test_runner.py       # Isolated sandboxed pytest runner
├── generated_tests/
│   └── .gitkeep             # Directory for local generated test exports
├── tests/
│   ├── test_analyzer.py     # Unit tests for AST and code utilities
│   ├── test_gemini_service.py # Unit tests for Gemini client wrapper
│   └── test_runner.py       # Unit tests for sandboxed test runner
├── .env.example             # Safe environment template
├── .gitignore               # Strict exclusion of caches and secrets
├── app.py                   # Streamlit UI application
├── CHANGELOG.md             # Version history
├── CODE_OF_CONDUCT.md       # Community guidelines
├── CONTRIBUTING.md          # Contribution workflow
├── LICENSE                  # MIT License
├── pytest.ini               # Test configuration
├── README.md                # Project documentation
└── requirements.txt         # Pinned production dependencies
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10, 3.11, or 3.12
- A free Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)

### 2. Clone the Repository
```bash
git clone https://github.com/<your-username>/ai-code-doctor.git
cd ai-code-doctor
```

### 3. Set Up Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure API Key
Copy the example environment configuration and supply your Gemini API key:
```bash
cp .env.example .env
```
Edit `.env`:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

### 6. Run the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running Tests & Quality Checks

Run the automated test suite locally:
```bash
pytest
```

Run test suite with code coverage:
```bash
pytest --cov=core tests/
```

---

## 🔒 Security & Privacy

- **No Key Exposure**: API keys are loaded via local `.env` or input directly through password-masked fields. Keys are never logged, exported, or transmitted to any third party.
- **Local Isolation**: Sandboxed test execution runs locally in temporary directories with subprocess timeouts to prevent CPU-hogging infinite loops.

---

## 🤝 Contributing

Contributions are welcomed! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for pull request guidelines, and review our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

---

## 📄 License

This project is open-source and licensed under the [MIT License](LICENSE).
