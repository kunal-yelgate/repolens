"""Unit tests for AST and source code parsers."""

from pathlib import Path
from repolens.parsers.go import GoParser, RustParser
from repolens.parsers.javascript import JavaScriptParser
from repolens.parsers.python import PythonParser


def test_python_parser(tmp_path: Path) -> None:
    code = '''import os
from fastapi import FastAPI, Depends
from .services import UserService

app = FastAPI()

class User(BaseModel):
    id: int
    name: str

@app.get("/users")
async def get_users(db=Depends()):
    secret = os.getenv("DATABASE_URL")
    return []
'''
    py_file = tmp_path / "main.py"
    py_file.write_text(code, encoding="utf-8")

    parser = PythonParser()
    assert parser.can_parse(py_file)

    parsed = parser.parse(py_file, code, "main.py")
    assert parsed.syntax_valid
    assert len(parsed.routes) == 1
    assert parsed.routes[0].path == "/users"
    assert parsed.routes[0].http_method == "GET"
    assert "DATABASE_URL" in parsed.env_vars
    assert len(parsed.classes) == 1
    assert parsed.classes[0].name == "User"


def test_javascript_parser(tmp_path: Path) -> None:
    code = '''import React from 'react';
import express from 'express';

const app = express();

app.get('/api/items', (req, res) => {
    const key = process.env.API_SECRET;
    res.json([]);
});

export class ItemService extends BaseService {}
'''
    js_file = tmp_path / "server.js"
    parser = JavaScriptParser()
    assert parser.can_parse(js_file)

    parsed = parser.parse(js_file, code, "server.js")
    assert parsed.syntax_valid
    assert len(parsed.routes) == 1
    assert parsed.routes[0].path == "/api/items"
    assert parsed.routes[0].http_method == "GET"
    assert "API_SECRET" in parsed.env_vars
    assert len(parsed.classes) == 1


def test_go_parser(tmp_path: Path) -> None:
    code = '''package main

import (
    "os"
    "github.com/gin-gonic/gin"
)

type User struct {
    ID int
}

func main() {
    r := gin.Default()
    r.GET("/ping", func(c *gin.Context) {})
    dbUrl := os.Getenv("DB_HOST")
}
'''
    go_file = tmp_path / "main.go"
    parser = GoParser()
    parsed = parser.parse(go_file, code, "main.go")
    assert len(parsed.routes) == 1
    assert parsed.routes[0].path == "/ping"
    assert "DB_HOST" in parsed.env_vars
    assert len(parsed.classes) == 1
