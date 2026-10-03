# repolens — Codebase Intelligence

> Generated automatically by **RepoLens** autonomous codebase analysis agent.

## 1. Project Overview
- **Project Name**: `repolens`
- **Type**: CLI tool
- **Files**: 96 files (7096 total lines of code)
- **Git Branch**: `main`

## 2. Technology Stack
### Languages
- **Python**: 100.0%

### Frameworks & Libraries
- Pydantic
- Typer
- pytest

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

## 4. High-Level Architecture
- **Modular CLI Application** (Confidence: 90%)
  - Evidence: Command line entrypoint and CLI structure

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

## 5. Main Entry Points
- `pyproject.toml`: Declared console script 'repolens' in pyproject.toml *(Confidence: 95%)*
- `tests/unit/test_parsers.py`: Instantiates FastAPI application *(Confidence: 95%)*
- `tests/unit/test_detectors.py`: Instantiates FastAPI application *(Confidence: 95%)*
- `tests/integration/test_fixtures.py`: Instantiates FastAPI application *(Confidence: 95%)*
- `src/repolens/detectors/entrypoint.py`: Instantiates FastAPI application *(Confidence: 95%)*
- `src/repolens/cli/main.py`: Python executable block (if __name__ == '__main__':) *(Confidence: 85%)*

## 6. Database & Persistence
- **Technology**: `Relational Database (SQL)`
- **ORM**: `Ecto`
- **Models / Schemas**: `LLMResponse`, `RepositoryInfo`, `AgentResponse`, `DiscoveredEndpoint`, `SecurityConfig`, `SecurityFinding`, `GraphNode`, `ProjectConfig`, `TestFailureItem`, `CICDInfo`, `EntryPointInfo`, `DirectoryMetadata`, `MonorepoInfo`, `EvidenceRecord`, `FindingEvidence`

## 7. Environment Variables
- `ANTHROPIC_API_KEY` (Required) — Used by: `src/repolens/ai/factory.py`, `src/repolens/config/loader.py`
- `GEMINI_API_KEY` (Required) — Used by: `src/repolens/ai/factory.py`, `src/repolens/config/loader.py`
- `GROQ_API_KEY` (Required) — Used by: `src/repolens/ai/factory.py`, `src/repolens/config/loader.py`
- `OPENAI_API_KEY` (Required) — Used by: `src/repolens/ai/factory.py`, `src/repolens/config/loader.py`
- `OPENAI_BASE_URL` (Required) — Used by: `src/repolens/config/loader.py`
- `REPOLENS_API_KEY` (Required) — Used by: `src/repolens/config/loader.py`
- `REPOLENS_BASE_URL` (Required) — Used by: `src/repolens/config/loader.py`
- `REPOLENS_LLM_PROVIDER` (Required) — Used by: `src/repolens/config/loader.py`
- `REPOLENS_MODEL` (Required) — Used by: `src/repolens/config/loader.py`
- `REPOLENS_PROVIDER` (Required) — Used by: `src/repolens/config/loader.py`
- `no_ai` (Required) — Used by: `src/repolens/config/loader.py`
- `output_dir` (Required) — Used by: `src/repolens/config/loader.py`

## 8. Setup & Development Commands
### Install Dependencies
**Python**:
```bash
pip install -e .
```

### Run Development Server
**Python**:
```bash
python -m repolens analyze
```

### Run Test Suite
**Python**:
```bash
pytest
```

## 9. CI/CD & Infrastructure
- **CI/CD Platform**: None detected
- **Docker Support**: No
- **Docker Compose**: No
- **Kubernetes**: No
- **Terraform**: No

## 10. Potential Architectural Concerns
- No critical architectural smells detected.

## 11. Architecture Diagram
```mermaid
graph TD
    API["API Layer (REST API)"]
    DB[("Database (Relational Database (SQL))")]
    API --> DB
```

---
*Analysis generated on 2026-10-04 01:15:43*