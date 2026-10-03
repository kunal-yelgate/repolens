"""Framework and library detection using manifest analysis and source evidence."""

import json
from pathlib import Path
from typing import Dict, List, Set

from repolens.detectors.base import BaseDetector
from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory
from repolens.utils.filesystem import read_file_safely

# Manifest package keywords mapped to Framework names
PYTHON_FRAMEWORK_MAP: Dict[str, str] = {
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "tornado": "Tornado",
    "starlette": "Starlette",
    "litestar": "Litestar",
    "pytorch": "PyTorch",
    "torch": "PyTorch",
    "tensorflow": "TensorFlow",
    "keras": "Keras",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "scipy": "SciPy",
    "scikit-learn": "Scikit-Learn",
    "sqlalchemy": "SQLAlchemy",
    "sqlmodel": "SQLModel",
    "pydantic": "Pydantic",
    "celery": "Celery",
    "redis": "Redis",
    "typer": "Typer",
    "click": "Click",
    "streamlit": "Streamlit",
    "langchain": "LangChain",
    "transformers": "Hugging Face Transformers",
    "alembic": "Alembic",
    "pytest": "pytest",
    "uvicorn": "Uvicorn",
    "gunicorn": "Gunicorn",
}

JS_FRAMEWORK_MAP: Dict[str, str] = {
    "react": "React",
    "next": "Next.js",
    "vue": "Vue",
    "nuxt": "Nuxt",
    "@angular/core": "Angular",
    "svelte": "Svelte",
    "@sveltejs/kit": "SvelteKit",
    "express": "Express",
    "@nestjs/core": "NestJS",
    "fastify": "Fastify",
    "vite": "Vite",
    "webpack": "Webpack",
    "electron": "Electron",
    "tailwindcss": "TailwindCSS",
    "@prisma/client": "Prisma",
    "prisma": "Prisma",
    "drizzle-orm": "Drizzle ORM",
    "typeorm": "TypeORM",
    "mongoose": "Mongoose",
    "redux": "Redux",
    "@reduxjs/toolkit": "Redux Toolkit",
    "zustand": "Zustand",
    "tanstack": "TanStack Query",
    "@tanstack/react-query": "TanStack Query",
    "jest": "Jest",
    "vitest": "Vitest",
    "mocha": "Mocha",
    "cypress": "Cypress",
    "@playwright/test": "Playwright",
}

GO_FRAMEWORK_MAP: Dict[str, str] = {
    "github.com/gin-gonic/gin": "Gin",
    "github.com/labstack/echo": "Echo",
    "github.com/gofiber/fiber": "Fiber",
    "github.com/go-chi/chi": "Chi",
    "gorm.io/gorm": "Gorm",
    "github.com/spf13/cobra": "Cobra",
}

RUST_FRAMEWORK_MAP: Dict[str, str] = {
    "actix-web": "Actix Web",
    "axum": "Axum",
    "rocket": "Rocket",
    "tokio": "Tokio",
    "diesel": "Diesel",
    "sea-orm": "SeaORM",
    "clap": "Clap",
}

PHP_FRAMEWORK_MAP: Dict[str, str] = {
    "laravel/framework": "Laravel",
    "symfony/symfony": "Symfony",
    "yiisoft/yii2": "Yii",
    "codeigniter4/framework": "CodeIgniter",
    "cakephp/cakephp": "CakePHP",
    "slim/slim": "Slim",
}

RUBY_FRAMEWORK_MAP: Dict[str, str] = {
    "rails": "Ruby on Rails",
    "sinatra": "Sinatra",
    "hanami": "Hanami",
    "sidekiq": "Sidekiq",
}

CSHARP_FRAMEWORK_MAP: Dict[str, str] = {
    "microsoft.aspnetcore": "ASP.NET Core",
    "entityframeworkcore": "Entity Framework Core",
    "entityframework": "Entity Framework",
    "dapper": "Dapper",
    "microsoft.maui": "MAUI",
}

DART_FRAMEWORK_MAP: Dict[str, str] = {
    "flutter": "Flutter",
    "get": "GetX",
    "provider": "Provider",
    "flutter_bloc": "Bloc",
}

ELIXIR_FRAMEWORK_MAP: Dict[str, str] = {
    "phoenix": "Phoenix",
    "ecto": "Ecto",
    "absinthe": "Absinthe",
}


class FrameworkDetector(BaseDetector):
    """Detects frameworks by analyzing manifests (package.json, requirements.txt, pyproject.toml, composer.json, etc.) and source imports."""

    def detect(
        self,
        inventory: RepositoryInventory,
        parsed_sources: Dict[str, ParsedSource],
    ) -> List[str]:
        frameworks: Set[str] = set()

        # 1. Inspect manifests
        for path_str, fmeta in inventory.files.items():
            fname_lower = fmeta.filename.lower()

            if fname_lower == "package.json":
                content = read_file_safely(fmeta.full_path)
                if content:
                    try:
                        data = json.loads(content)
                        all_deps = {}
                        all_deps.update(data.get("dependencies", {}))
                        all_deps.update(data.get("devDependencies", {}))

                        for dep_name in all_deps:
                            dep_lower = dep_name.lower()
                            if dep_lower in JS_FRAMEWORK_MAP:
                                frameworks.add(JS_FRAMEWORK_MAP[dep_lower])
                            for k, v in JS_FRAMEWORK_MAP.items():
                                if k in dep_lower:
                                    frameworks.add(v)
                    except Exception:
                        pass

            # 2. Python requirements / pyproject / Pipfile
            elif fname_lower in {"requirements.txt", "requirements-dev.txt", "pipfile", "pyproject.toml"}:
                content = read_file_safely(fmeta.full_path)
                if content:
                    for line in content.splitlines():
                        cleaned = line.lower().strip()
                        if cleaned and not cleaned.startswith("#") and not cleaned.startswith("["):
                            pkg_name = cleaned.split("==")[0].split(">=")[0].split("<=")[0].split("~=")[0].split(";")[0].strip('",\' ')
                            for k, v in PYTHON_FRAMEWORK_MAP.items():
                                if k == pkg_name or f'"{k}"' in cleaned or f"'{k}'" in cleaned or k in pkg_name:
                                    frameworks.add(v)

            # 3. Go mod
            elif fname_lower == "go.mod":
                content = read_file_safely(fmeta.full_path)
                if content:
                    for k, v in GO_FRAMEWORK_MAP.items():
                        if k in content:
                            frameworks.add(v)

            # 4. Cargo.toml
            elif fname_lower == "cargo.toml":
                content = read_file_safely(fmeta.full_path)
                if content:
                    for k, v in RUST_FRAMEWORK_MAP.items():
                        if k in content:
                            frameworks.add(v)

            # 5. Java pom.xml / build.gradle
            elif fname_lower in {"pom.xml", "build.gradle", "build.gradle.kts"}:
                content = read_file_safely(fmeta.full_path)
                if content:
                    content_lower = content.lower()
                    if "spring-boot" in content_lower:
                        frameworks.add("Spring Boot")
                    elif "org.springframework" in content_lower:
                        frameworks.add("Spring")
                    if "quarkus" in content_lower:
                        frameworks.add("Quarkus")
                    if "micronaut" in content_lower:
                        frameworks.add("Micronaut")

            # 6. PHP composer.json
            elif fname_lower == "composer.json":
                content = read_file_safely(fmeta.full_path)
                if content:
                    content_lower = content.lower()
                    for k, v in PHP_FRAMEWORK_MAP.items():
                        if k in content_lower:
                            frameworks.add(v)

            # 7. Ruby Gemfile
            elif fname_lower in {"gemfile", "gemfile.lock"}:
                content = read_file_safely(fmeta.full_path)
                if content:
                    content_lower = content.lower()
                    for k, v in RUBY_FRAMEWORK_MAP.items():
                        if k in content_lower:
                            frameworks.add(v)

            # 8. C# .csproj
            elif fname_lower.endswith(".csproj") or fname_lower == "packages.config":
                content = read_file_safely(fmeta.full_path)
                if content:
                    content_lower = content.lower()
                    for k, v in CSHARP_FRAMEWORK_MAP.items():
                        if k in content_lower:
                            frameworks.add(v)

            # 9. Dart pubspec.yaml
            elif fname_lower == "pubspec.yaml":
                content = read_file_safely(fmeta.full_path)
                if content:
                    content_lower = content.lower()
                    for k, v in DART_FRAMEWORK_MAP.items():
                        if k in content_lower:
                            frameworks.add(v)

            # 10. Elixir mix.exs
            elif fname_lower == "mix.exs":
                content = read_file_safely(fmeta.full_path)
                if content:
                    content_lower = content.lower()
                    for k, v in ELIXIR_FRAMEWORK_MAP.items():
                        if k in content_lower:
                            frameworks.add(v)

        # 11. Check parsed routes and imports
        for parsed in parsed_sources.values():
            for route in parsed.routes:
                if route.framework and route.framework != "unknown":
                    frameworks.add(route.framework)

            for imp in parsed.imports:
                mod_lower = imp.module.lower()
                if mod_lower in PYTHON_FRAMEWORK_MAP:
                    frameworks.add(PYTHON_FRAMEWORK_MAP[mod_lower])
                elif mod_lower in JS_FRAMEWORK_MAP:
                    frameworks.add(JS_FRAMEWORK_MAP[mod_lower])

        return sorted(list(frameworks))
