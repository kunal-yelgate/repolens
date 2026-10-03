"""Database and ORM detection without secret exposure."""

from typing import Dict, List, Optional, Set

from repolens.detectors.base import BaseDetector, DatabaseInfo
from repolens.parsers.base import ParsedSource
from repolens.scanner.metadata import RepositoryInventory
from repolens.utils.filesystem import read_file_safely

DB_KEYWORDS = {
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mysql": "MySQL",
    "sqlite": "SQLite",
    "sqlite3": "SQLite",
    "mongodb": "MongoDB",
    "mongo": "MongoDB",
    "redis": "Redis",
    "dynamodb": "DynamoDB",
    "supabase": "Supabase",
    "firebase": "Firebase",
    "cassandra": "Cassandra",
    "neo4j": "Neo4j",
    "mariadb": "MariaDB",
}

ORM_KEYWORDS = {
    "sqlalchemy": "SQLAlchemy",
    "prisma": "Prisma",
    "mongoose": "Mongoose",
    "django.db": "Django ORM",
    "drizzle": "Drizzle ORM",
    "typeorm": "TypeORM",
    "tortoise": "Tortoise ORM",
    "peewee": "Peewee",
    "gorm": "Gorm",
    "diesel": "Diesel",
    "sea-orm": "SeaORM",
    "hibernate": "Hibernate",
    "persistence": "JPA / Hibernate",
    "mybatis": "MyBatis",
    "entityframework": "Entity Framework Core",
    "dapper": "Dapper",
    "eloquent": "Eloquent ORM",
    "doctrine": "Doctrine ORM",
    "activerecord": "ActiveRecord",
    "ecto": "Ecto",
}


class DatabaseDetector(BaseDetector):
    """Detects database engines, ORMs, schemas, models, and migrations."""

    def detect(
        self,
        inventory: RepositoryInventory,
        parsed_sources: Dict[str, ParsedSource],
    ) -> List[DatabaseInfo]:
        findings: List[DatabaseInfo] = []
        detected_dbs: Set[str] = set()
        detected_orms: Set[str] = set()
        all_models: List[str] = []
        config_files: List[str] = []
        migrations_dir: Optional[str] = None

        # Check directories for migrations
        for d in inventory.directories:
            d_lower = d.lower()
            if "alembic" in d_lower or "migrations" in d_lower:
                migrations_dir = d
                break

        # Check parsed sources for models & ORM imports
        for rel_path, parsed in parsed_sources.items():
            if parsed.db_models:
                all_models.extend(parsed.db_models)

            for imp in parsed.imports:
                mod_lower = imp.module.lower()
                for k, v in ORM_KEYWORDS.items():
                    if k in mod_lower:
                        detected_orms.add(v)
                for k, v in DB_KEYWORDS.items():
                    if k in mod_lower:
                        detected_dbs.add(v)

            # Check database config keywords in file path or content
            path_lower = rel_path.lower()
            if "database" in path_lower or "db." in path_lower or "datasource" in path_lower or "prisma/schema" in path_lower:
                config_files.append(rel_path)

        # Inspect requirements/package.json for drivers
        for rel_path, fmeta in inventory.files.items():
            content = read_file_safely(fmeta.full_path)
            if not content:
                continue

            content_lower = content.lower()
            if fmeta.filename.lower() in {"requirements.txt", "package.json", "pyproject.toml", "cargo.toml", "go.mod"}:
                if "psycopg" in content_lower or "asyncpg" in content_lower or "pg" in content_lower:
                    detected_dbs.add("PostgreSQL")
                if "pymysql" in content_lower or "mysql2" in content_lower:
                    detected_dbs.add("MySQL")
                if "aiosqlite" in content_lower or "sqlite3" in content_lower:
                    detected_dbs.add("SQLite")
                if "pymongo" in content_lower or "mongodb" in content_lower:
                    detected_dbs.add("MongoDB")
                if "redis" in content_lower or "ioredis" in content_lower:
                    detected_dbs.add("Redis")

            # Check Prisma datasource
            if fmeta.extension == ".prisma":
                detected_orms.add("Prisma")
                if 'provider = "postgresql"' in content_lower:
                    detected_dbs.add("PostgreSQL")
                elif 'provider = "sqlite"' in content_lower:
                    detected_dbs.add("SQLite")
                elif 'provider = "mysql"' in content_lower:
                    detected_dbs.add("MySQL")
                elif 'provider = "mongodb"' in content_lower:
                    detected_dbs.add("MongoDB")

        # Combine detected databases
        primary_orm = next(iter(detected_orms), None)
        if not detected_dbs and not detected_orms and not all_models:
            return []

        if detected_dbs:
            for db in detected_dbs:
                findings.append(
                    DatabaseInfo(
                        technology=db,
                        orm=primary_orm,
                        confidence=0.90,
                        models=list(set(all_models))[:30],
                        config_files=config_files[:5],
                        migrations_dir=migrations_dir,
                    )
                )
        elif detected_orms or all_models:
            findings.append(
                DatabaseInfo(
                    technology="Relational Database (SQL)",
                    orm=primary_orm or "ORM",
                    confidence=0.80,
                    models=list(set(all_models))[:30],
                    config_files=config_files[:5],
                    migrations_dir=migrations_dir,
                )
            )

        return findings
