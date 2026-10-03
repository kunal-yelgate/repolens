# RepoLens Internal Architecture

RepoLens follows a decoupled, staged static-analysis and knowledge graph architecture:

```text
CLI (Typer + Rich)
       ↓
Application Orchestrator
       ↓
Repository Scanner (Filesystem & Ignores)
       ↓
Language Parsers (Python AST, JS/TS, Go, Rust, Generic)
       ↓
Knowledge Graph Builder (NetworkX Graph)
       ↓
Detectors (Language, Framework, Type, Entrypoint, DB, API, Tests, Env, Commands, Security)
       ↓
Ranking & Context Budgeting Engine
       ↓
AI Reasoning Agents (Architecture, Q&A, Onboarding)
       ↓
Validation & Documentation Generator
```

## Core Modules

1. **`repolens.scanner`**: Recursively discovers files, calculates hashes, applies ignores, and builds `RepositoryInventory`.
2. **`repolens.parsers`**: Extracts imports, classes, functions, route decorators, database models, and environment lookups from ASTs.
3. **`repolens.graph`**: Builds a directed knowledge graph linking repositories, directories, files, APIs, database models, and environment variables.
4. **`repolens.detectors`**: Analyzes manifests and source evidence to infer project types, frameworks, databases, entrypoints, and command definitions.
5. **`repolens.security`**: Identifies hardcoded secrets and static code vulnerabilities with redaction.
6. **`repolens.ai`**: Pluggable provider interface supporting Ollama, OpenAI, Anthropic, Gemini, Groq, and offline deterministic modes.
7. **`repolens.documentation`**: Generates high-quality Markdown documents (`REPOLENS.md`, `ARCHITECTURE.md`, `SETUP.md`, `TESTING.md`, `API.md`, `ONBOARDING.md`).
