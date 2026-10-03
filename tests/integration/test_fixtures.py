"""Integration tests verifying analysis against various project structures."""

from pathlib import Path
from repolens.analysis.orchestrator import AnalysisOrchestrator
from repolens.config.models import RepoLensConfig


def test_fastapi_react_fullstack_fixture(tmp_path: Path) -> None:
    # 1. Setup Backend
    backend = tmp_path / "backend" / "app"
    backend.mkdir(parents=True)
    (backend.parent / "requirements.txt").write_text("fastapi>=0.100.0\nuvicorn\nsqlalchemy\npsycopg2-binary\npytest\n", encoding="utf-8")
    (backend.parent / ".env.example").write_text("DATABASE_URL=postgresql://localhost:5432/mydb\nSECRET_KEY=devsecret\n", encoding="utf-8")
    (backend / "main.py").write_text("""
import os
from fastapi import FastAPI, Depends
from .routes import router

app = FastAPI(title="DemoApp")
app.include_router(router)
""", encoding="utf-8")
    (backend / "routes.py").write_text("""
from fastapi import APIRouter

router = APIRouter()

@router.get("/api/v1/users")
def get_users():
    return []
""", encoding="utf-8")

    # 2. Setup Frontend
    frontend = tmp_path / "frontend" / "src"
    frontend.mkdir(parents=True)
    (frontend.parent / "package.json").write_text("""
{
  "name": "frontend",
  "dependencies": {
    "react": "^18.2.0",
    "vite": "^5.0.0"
  },
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "test": "vitest"
  }
}
""", encoding="utf-8")
    (frontend / "main.jsx").write_text("""
import React from 'react';
import ReactDOM from 'react-dom/client';
ReactDOM.createRoot(document.getElementById('root')).render(<div />);
""", encoding="utf-8")

    cfg = RepoLensConfig()
    cfg.project.root = tmp_path

    orchestrator = AnalysisOrchestrator(cfg)
    result = orchestrator.analyze()

    assert "Full-stack web application" in result.repository.project_types
    assert "FastAPI" in result.repository.frameworks
    assert "React" in result.repository.frameworks
    assert any("PostgreSQL" in d.technology for d in result.database)
    assert any(ep.path == "/api/v1/users" for ep in result.endpoints)
    assert len(result.entry_points) >= 2
    assert "DATABASE_URL" in [ev.name for ev in result.environment_variables]
