# AI Providers & Reasoning Architecture

RepoLens supports pluggable AI providers with strict privacy and no-hallucination guardrails.

## Supported Providers

### 1. Local Ollama (Offline / Private)
Run models locally without sending source code to any cloud provider:
```bash
repolens config --provider ollama --model qwen2.5-coder:latest
```

### 2. OpenAI
```bash
export OPENAI_API_KEY="sk-..."
repolens analyze --llm openai --model gpt-4o-mini
```

### 3. Anthropic Claude
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
repolens analyze --llm anthropic --model claude-3-5-sonnet-20241022
```

### 4. Google Gemini
```bash
export GEMINI_API_KEY="..."
repolens analyze --llm gemini --model gemini-2.0-flash
```

### 5. Groq
```bash
export GROQ_API_KEY="gsk_..."
repolens analyze --llm groq --model llama-3.3-70b-versatile
```

### 6. Deterministic Mode (Default)
When run with `--no-ai` or without configured API keys, RepoLens uses 100% deterministic static analysis and knowledge graph reasoning without calling any external LLMs.
