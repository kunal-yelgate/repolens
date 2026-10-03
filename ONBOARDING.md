# Developer Onboarding Guide — repolens

## 1. What this project does
**repolens** is a **CLI tool** with 96 files and 7096 lines of code.

## 2. Technology Stack
- **Python**: 100.0%
- **Frameworks & Libraries**: Pydantic, Typer, pytest

## 3. Repository Structure
```text
repolens/
├── docs/
│   ├── ai.md
│   ├── architecture.md
│   ├── cli.md
│   ├── detectors.md
├── src/
│   ├── repolens/
│   │   ├── __init__.py
├── tests/
│   ├── integration/
│   │   ├── test_fixtures.py
│   │   ├── test_self_analysis.py
│   ├── unit/
│   │   ├── test_cli.py
│   │   ├── test_detectors.py
│   │   ├── test_ignore.py
│   │   └── ... (4 more files)
├── pyproject.toml
├── repolens.toml
├── API.md
├── ARCHITECTURE.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── README.md
├── SETUP.md
├── .gitignore
├── CODE_OF_CONDUCT.md
├── LICENSE
├── ONBOARDING.md
├── REPOLENS.md
├── SECURITY.md
└── TESTING.md
```

## 4. How the Application Starts (Entry Points)
- `pyproject.toml`: Declared console script 'repolens' in pyproject.toml
- `tests/unit/test_parsers.py`: Instantiates FastAPI application
- `tests/unit/test_detectors.py`: Instantiates FastAPI application
- `tests/integration/test_fixtures.py`: Instantiates FastAPI application
- `src/repolens/detectors/entrypoint.py`: Instantiates FastAPI application
- `src/repolens/cli/main.py`: Python executable block (if __name__ == '__main__':)

## 5. Architecture & Data Flow
```text
┌───────────────────────────────────┐
│  API Layer: API / Routing Layer   │
└─────────────────┬─────────────────┘
                  │
                  ↓
┌───────────────────────────────────┐
│  Database: Relational Database (SQL)│
└───────────────────────────────────┘
```

## 6. How to Run Locally
**Install Dependencies (Python)**:
```bash
pip install -e .
```
**Development Server (Python)**:
```bash
python -m repolens analyze
```

## 7. How to Run Tests
**Run Tests (Python)**:
```bash
pytest
```

## 8. Where to Make Changes
- **To add or modify API routes**: Look in route handlers listed in `API.md`.
- **To update database schemas**: Check models in database persistence layer.
- **To configure environment**: Inspect `.env.example`.

## 9. Things to Be Careful About
- Ensure environment variables are configured before running development server.