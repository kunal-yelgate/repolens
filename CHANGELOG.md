# Changelog

All notable changes to **RepoLens** will be documented in this file.

## [0.1.0] - 2026-10-03

### Added
- Core CLI framework built with Typer and Rich formatting.
- Deterministic repository scanner with ignore filter support (`.gitignore`, `.repolensignore`, defaults).
- AST and source code parsers for Python, JavaScript, TypeScript, Go, Rust, and generic languages.
- Detectors for Languages, Frameworks, Project Types, Entry Points, Databases, REST APIs, Testing, CI/CD, Monorepos, Environment Variables, and Commands.
- Directed Repository Knowledge Graph and dependency query engine built on NetworkX.
- Architectural diagram generator with ASCII and Mermaid formats.
- Documentation generator for `REPOLENS.md`, `ARCHITECTURE.md`, `SETUP.md`, `TESTING.md`, `API.md`, and `ONBOARDING.md`.
- Static security scanner and secret pattern detector with automatic string redaction.
- Local Ollama and Cloud LLM provider abstraction (OpenAI, Anthropic, Gemini, Groq) with fallback deterministic reasoning.
- Autonomous test runner and failure analyzer (`repolens test`).
- Autonomous setup assistant with confirmation guardrails (`repolens setup`).
- Repository environment diagnostic tool (`repolens doctor`).
- Incremental hash-based caching in `.repolens/`.
- Full test suite with unit tests, fixture integration tests, and self-analysis validation.
