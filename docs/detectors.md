# Detectors & Heuristics in RepoLens

RepoLens uses multiple heuristic and AST detectors to analyze codebases:

## 1. Language Detector (`repolens.detectors.language`)
Calculates lines of code (LOC) and percentage breakdown across 30+ programming languages.

## 2. Framework Detector (`repolens.detectors.framework`)
Inspects manifests (`package.json`, `requirements.txt`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`) and AST imports for frameworks including:
- **Python**: FastAPI, Django, Flask, PyTorch, TensorFlow, SQLAlchemy, Pydantic, Celery, Typer, pytest
- **JS/TS**: React, Next.js, Vue, Angular, Express, NestJS, Vite, TailwindCSS, Prisma, Drizzle
- **Go/Rust/Java**: Gin, Actix, Axum, Spring Boot

## 3. Entry Point Detector (`repolens.detectors.entrypoint`)
Locates application entry points, web server mounts, CLI binaries, and script entrypoints.

## 4. Database & ORM Detector (`repolens.detectors.database`)
Identifies database engines (PostgreSQL, MySQL, SQLite, MongoDB, Redis) and ORM models/migrations without exposing secrets.

## 5. API Detector (`repolens.detectors.api`)
Extracts HTTP methods, route paths, handlers, and authentication requirements across frameworks.

## 6. Testing Detector (`repolens.detectors.testing`)
Detects testing frameworks, test directories, run-all commands, and single-test execution templates.

## 7. Security Scanner (`repolens.security.scanner`)
Detects hardcoded API keys, tokens, and unsafe code patterns with automatic redaction.
