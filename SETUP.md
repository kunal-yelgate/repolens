# Setup & Execution Guide — repolens

## 1. Prerequisites
- Python runtime environment

## 2. Installation Steps
### Step 1: Install Python Dependencies
```bash
pip install -e .
```

## 3. Environment Configuration
Create a `.env` file from `.env.example` and configure the following variables:

| Variable Name | Status | Used In |
| :--- | :--- | :--- |
| `ANTHROPIC_API_KEY` | Required | `src/repolens/ai/factory.py, src/repolens/config/loader.py` |
| `GEMINI_API_KEY` | Required | `src/repolens/ai/factory.py, src/repolens/config/loader.py` |
| `GROQ_API_KEY` | Required | `src/repolens/ai/factory.py, src/repolens/config/loader.py` |
| `OPENAI_API_KEY` | Required | `src/repolens/ai/factory.py, src/repolens/config/loader.py` |
| `OPENAI_BASE_URL` | Required | `src/repolens/config/loader.py` |
| `REPOLENS_API_KEY` | Required | `src/repolens/config/loader.py` |
| `REPOLENS_BASE_URL` | Required | `src/repolens/config/loader.py` |
| `REPOLENS_LLM_PROVIDER` | Required | `src/repolens/config/loader.py` |
| `REPOLENS_MODEL` | Required | `src/repolens/config/loader.py` |
| `REPOLENS_PROVIDER` | Required | `src/repolens/config/loader.py` |
| `no_ai` | Required | `src/repolens/config/loader.py` |
| `output_dir` | Required | `src/repolens/config/loader.py` |

## 4. Running the Development Server
**Python**:
```bash
python -m repolens analyze
```

## 5. Verification
To verify your local setup, run the test suite:
```bash
pytest
```