# RepoLens

<p align="center">
  <b>Autonomous Codebase Analysis & Architecture Intelligence Agent</b>
</p>

<p align="center">
  <a href="#key-features">Key Features</a> •
  <a href="#how-it-works">How It Works</a> •
  <a href="#installation--setup">Installation & Setup</a> •
  <a href="#usage--commands">Usage & Commands</a> •
  <a href="#local-ai-with-ollama">Local AI Setup</a> •
  <a href="#generated-documentation">Generated Docs</a> •
  <a href="#license">License</a>
</p>

---

```text
Clone any repository → Run one command → Understand the codebase.
```

```bash
cd my-project

repolens analyze
```

---

## 🎯 What is RepoLens?

When a developer opens or clones a large or unfamiliar software repository, they face common questions:
- *What does this project actually do?*
- *Which languages, frameworks, and database models are used?*
- *Where is the application entry point and how do requests flow?*
- *Which environment variables and services are required to run it?*
- *How do I install dependencies, run development servers, and execute tests?*
- *Where are potential circular dependencies or architectural smells?*

**RepoLens solves this instantly with a single command.**

It scans the codebase deterministically, parses source code ASTs, builds a **Repository Knowledge Graph**, extracts API endpoints and database schemas, verifies setup requirements, and generates comprehensive architectural documentation.

---

## ✨ Key Features

- **🚀 Instant Codebase Intelligence (`repolens analyze`)**: Automatically detects languages, frameworks, entry points, configuration requirements, database schemas, and test suites.
- **📊 Repository Knowledge Graph**: Constructs a directed dependency graph using NetworkX to map module relationships and detect circular dependencies.
- **🔍 Multi-Language AST Parsing**: Supports Python, JavaScript, TypeScript, Go, Rust, Java, C/C++, PHP, Ruby, Kotlin, Swift, Shell, and more.
- **⚡ 100% Privacy & Offline First**: Runs in pure deterministic static analysis mode without sending source code to any external API.
- **🤖 Local AI Reasoning (Ollama Mistral)**: Pluggable AI abstraction supporting local Ollama (`mistral`), OpenAI, Anthropic, Gemini, or Groq.
- **🛡️ Static Security & Secret Scanner (`repolens security`)**: Detects hardcoded API keys, tokens, and unsafe code patterns with **strict string redaction**.
- **🧪 Autonomous Test Runner & Failure Analyzer (`repolens test`)**: Safely executes test suites, captures output, analyzes test failures, and suggests actionable fixes.
- **🛠️ Autonomous Setup Assistant (`repolens setup`)**: Detects runtimes, package managers, and missing dependencies, prompting confirmation before installing.
- **🩺 Repository Health Diagnostics (`repolens doctor`)**: Checks toolchains (Python, Node.js, npm, Docker, Git) and environment variable configurations.
- **📝 Automated Documentation Generator**: Generates 6 clean, structured Markdown documents (`REPOLENS.md`, `ARCHITECTURE.md`, `SETUP.md`, `TESTING.md`, `API.md`, and `ONBOARDING.md`).

---

## 🏗️ How It Works

RepoLens does **not** rely on brute-force LLM context dumping. Instead, it follows a deterministic static-analysis pipeline:

```text
Repository Filesystem
        ↓
Deterministic Static Scanner (.gitignore & .repolensignore)
        ↓
AST & Source Parsers (Python, JS/TS, Go, Rust, Generic)
        ↓
Repository Knowledge Graph (NetworkX Graph)
        ↓
Feature Detectors (Frameworks, Entry Points, DB, APIs, Commands, Security)
        ↓
Ranked & Budgeted Context Retrieval
        ↓
AI Reasoning (Local Ollama Mistral / Cloud LLMs / Offline Fallback)
        ↓
Validated Architecture Diagrams & Markdown Documentation
```

---

## 💻 Installation & Setup

### Prerequisites

- **Python**: Version 3.11, 3.12, or 3.13 installed.
- **Git**: Installed and available in your PATH.

### 1. Standard Installation

Clone the repository and install `repolens` in editable mode:

```bash
git clone https://github.com/kunal-yelgate/repolens.git
cd repolens

pip install -e .
```

Verify the installation:

```bash
repolens --help
```

---

## 🦙 Local AI Setup with Ollama (Mistral)

RepoLens can run 100% locally with **Ollama** using the `mistral` model.

### 1. Install Ollama & Pull Mistral

If you have [Ollama](https://ollama.com) installed:

```bash
ollama pull mistral
```

### 2. Configure RepoLens to Use Mistral

Run:

```bash
repolens config --provider ollama --model mistral
```

Verify your setup with `repolens doctor`:

```bash
repolens doctor
```

Output:
```text
RepoLens Doctor

✓ Python 3.13.7
✓ Git
✓ Node.js (v22.23.1)
✓ npm
✓ Docker
✓ Project structure analyzed
✓ Environment variables configuration
✓ AI Provider (ollama / mistral)
```

---

## 🚀 Usage & Commands

### 1. `repolens analyze`
Scan the current directory, reconstruct architecture, and generate documentation.

```bash
repolens analyze
```

**Options:**
- `--path, -p <path>`: Specify target repository directory.
- `--output, -o <dir>`: Save generated documentation to a custom directory.
- `--no-ai`: Run pure deterministic static analysis (no LLM calls).
- `--llm <provider>`: Select provider (`ollama`, `openai`, `anthropic`, `gemini`, `groq`).
- `--model, -m <name>`: Model name to use.
- `--incremental, -i`: Enable fast SHA-256 hash-based caching.
- `--json`: Output full analysis result as JSON.

---

### 2. `repolens doctor`
Diagnose local runtimes, dependencies, environment variable setup, and tools.

```bash
repolens doctor
```

---

### 3. `repolens ask`
Ask questions about how components work or where to make code changes.

```bash
repolens ask "Where is user authentication implemented?"
repolens ask "I want to add Google OAuth. Where should I change the code?"
```

---

### 4. `repolens explain`
Explain high-level architecture, component flows, or specific features.

```bash
repolens explain
repolens explain "How does data flow from frontend to backend?"
```

---

### 5. `repolens find`
Perform ranked codebase search across files, API routes, classes, and functions.

```bash
repolens find "database connection"
```

---

### 6. `repolens graph`
Visualize module dependency graphs and inspect file imports.

```bash
# View high-level module graph
repolens graph

# View dependency graph for a specific module or file
repolens graph --module backend
repolens graph --file src/repolens/analysis/orchestrator.py
```

---

### 7. `repolens test`
Safely execute test suites, capture stdout/stderr, analyze failures, and suggest fixes.

```bash
repolens test
```

---

### 8. `repolens setup`
Interactive setup assistant to detect runtimes, verify dependencies, and prompt confirmation before running install.

```bash
repolens setup
```

---

### 9. `repolens security`
Scan codebase for hardcoded secrets, API tokens, and static vulnerability risks.

```bash
repolens security
```

---

### 10. `repolens api`
List all discovered HTTP & REST API routes across backend frameworks.

```bash
repolens api
```

---

### 11. `repolens git`
Analyze Git commit history, contributor activity, and active development hotspots.

```bash
repolens git
```

---

### 12. `repolens onboarding`
Generate a standalone developer onboarding guide (`ONBOARDING.md`).

```bash
repolens onboarding
```

---

### 13. `repolens config`
View or update RepoLens settings.

```bash
repolens config --provider ollama --model mistral
```

---

### 14. `repolens init`
Initialize `repolens.toml` and `.repolensignore` in the current repository.

```bash
repolens init
```

---

## 📄 Generated Documentation Files

Executing `repolens analyze` creates 6 clean Markdown documents in your project:

| Document | Purpose |
| :--- | :--- |
| [`REPOLENS.md`](file:///c:/Users/yelga/Desktop/repolens/REPOLENS.md) | **Primary Overview**: Project summary, tech stack, directory tree, entry points, commands, and architecture diagrams |
| [`ARCHITECTURE.md`](file:///c:/Users/yelga/Desktop/repolens/ARCHITECTURE.md) | **Detailed Architecture**: Layer responsibilities, control flow, database persistence, and architectural concerns |
| [`SETUP.md`](file:///c:/Users/yelga/Desktop/repolens/SETUP.md) | **Setup Guide**: Prerequisites, environment variables table, installation steps, and server launch |
| [`TESTING.md`](file:///c:/Users/yelga/Desktop/repolens/TESTING.md) | **Testing Guide**: Test frameworks, test directories, run-all commands, and single-test templates |
| [`API.md`](file:///c:/Users/yelga/Desktop/repolens/API.md) | **API Reference**: Table of all HTTP methods, paths, handlers, frameworks, and auth requirements |
| [`ONBOARDING.md`](file:///c:/Users/yelga/Desktop/repolens/ONBOARDING.md) | **Developer Onboarding**: 10-step guide for new contributors joining the codebase |

---

## ⚙️ Configuration (`repolens.toml`)

RepoLens can be configured via `repolens.toml` in the project root:

```toml
[project]
name = "my-project"

[analysis]
max_file_size = 500000
max_depth = 15
incremental = true

[ai]
provider = "ollama"
model = "mistral"

[security]
scan_secrets = true
scan_vulnerabilities = true

[output]
directory = "."
format = "markdown"
```

---

## 🧪 Running Tests

RepoLens includes a complete test suite with unit tests, fixture integration tests, and self-analysis tests:

```bash
pytest
```

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](file:///c:/Users/yelga/Desktop/repolens/CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](file:///c:/Users/yelga/Desktop/repolens/CODE_OF_CONDUCT.md) before submitting pull requests.

---

## 📜 License

Distributed under the MIT License. See [LICENSE](file:///c:/Users/yelga/Desktop/repolens/LICENSE) for details.
