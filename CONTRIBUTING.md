# Contributing to RepoLens

Thank you for your interest in contributing to RepoLens!

## Development Setup

1. Clone repository:
   ```bash
   git clone https://github.com/repolens/repolens.git
   cd repolens
   ```

2. Install in editable mode with development dependencies:
   ```bash
   pip install -e ".[all]"
   ```

3. Run the test suite:
   ```bash
   pytest
   ```

## Development Guidelines

- All detectors and parsers must handle invalid syntax and unexpected file encodings gracefully without crashing.
- Write unit tests for new language detectors, frameworks, or parsers in `tests/unit/`.
- Ensure new features work across Windows, Linux, and macOS without relying on Unix-only CLI tools.
- Run tests and self-analysis before opening a pull request.
