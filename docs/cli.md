# RepoLens CLI Reference

Comprehensive guide to CLI commands and options.

## `repolens analyze`
Scans repository and generates full architecture intelligence and documentation.

```bash
repolens analyze [OPTIONS]
```

**Options:**
- `--path, -p PATH`: Path to repository (default: current directory).
- `--output, -o PATH`: Output directory for generated docs.
- `--format, -f [terminal|markdown|json]`: Output format.
- `--no-ai`: Run pure deterministic static analysis.
- `--llm [ollama|openai|anthropic|gemini|groq]`: Select AI provider.
- `--model, -m TEXT`: Specify model name.
- `--incremental, -i`: Enable hash-based incremental analysis.
- `--json`: Output as structured JSON.
- `--verbose, -v`: Show detailed debug logs.

## `repolens doctor`
Checks toolchains, runtimes, dependencies, and environment variable requirements.

## `repolens explain`
Explains repository architecture, request flow, and modules.

```bash
repolens explain "How does authentication work?"
```

## `repolens ask`
Answers codebase questions and pinpoints change locations.

```bash
repolens ask "Where should I add a new API endpoint?"
```

## `repolens find`
Searches codebase files, routes, classes, and functions with relevance scoring.

```bash
repolens find "user authentication"
```

## `repolens graph`
Visualizes module and dependency graphs.

```bash
repolens graph --module backend
repolens graph --file src/repolens/analysis/orchestrator.py
```

## `repolens test`
Executes safe test suites, captures output, analyzes test failures, and suggests actionable fixes.

## `repolens setup`
Guides interactive setup and dependency installation with confirmation.

## `repolens security`
Scans for hardcoded secrets and security risks.

## `repolens api`
Lists all detected REST/HTTP routes.
