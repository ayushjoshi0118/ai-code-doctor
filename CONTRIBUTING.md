# Contributing to AI Code Doctor

Thank you for your interest in improving **AI Code Doctor**! As an open-source project, we welcome bug reports, feature proposals, documentation improvements, and pull requests.

## Code of Conduct

By participating in this project, you agree to abide by standard open source community guidelines, maintaining a respectful, harassment-free environment for everyone.

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/<your-username>/ai-code-doctor.git
   cd ai-code-doctor
   ```
3. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
4. **Install dependencies in editable mode**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Add your Gemini API Key in .env
   ```

## Development Workflow

- Run the Streamlit web application:
  ```bash
  streamlit run app.py
  ```
- Run automated unit tests:
  ```bash
  pytest
  ```
- Check test coverage:
  ```bash
  pytest --cov=core tests/
  ```

## Submitting Pull Requests

1. Create a descriptive feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Write clean, readable Python code adhering to PEP 8 standards.
3. Include unit tests in `tests/` for any new logic added to `core/`.
4. Ensure all test suites pass (`pytest`).
5. Commit your changes with meaningful messages:
   ```bash
   git commit -m "feat(sandbox): add execution timeout and memory safety"
   ```
6. Push to your fork and submit a Pull Request against `main`.

Thank you for helping make automated code quality accessible to all developers!
