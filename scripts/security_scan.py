#!/usr/bin/env python3
"""Lightweight safety scan for public RealBrain contributions.

This is not a proof that code is safe. It catches common high-risk patterns,
accidental secrets, private paths, and suspicious dynamic execution before a
maintainer performs human/agent review.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", ".ruff_cache", ".venv", "venv", "demo_vault", "realbrain_vault"}
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".yml",
    ".yaml",
    ".toml",
    ".txt",
    ".json",
    ".ini",
    ".cfg",
    ".sh",
}

SECRET_PATTERNS = [
    ("private key block", re.compile(r"BEGIN (RSA|OPENSSH|DSA|EC|PGP|PRIVATE) KEY")),
    ("GitHub token", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9_]{20,}\b")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9_-]{32,}\b")),
    ("Slack token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    (
        "hardcoded credential assignment",
        re.compile(r"(?i)\b(api[_-]?key|secret|token|password|passwd)\b\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
    ),
    ("private OpenClaw path", re.compile(r"/home/[^\s'\"]+/\.openclaw|/home/node/\.openclaw|/home/node/\.config")),
]

SUSPICIOUS_TEXT_PATTERNS = [
    ("curl pipe shell", re.compile(r"curl\b[^\n|;]*(\||;)\s*(sh|bash)\b")),
    ("wget pipe shell", re.compile(r"wget\b[^\n|;]*(\||;)\s*(sh|bash)\b")),
    ("recursive force delete", re.compile(r"\brm\s+-rf\s+(/|~|\$HOME|\.)")),
    ("chmod recursive broad", re.compile(r"\bchmod\s+-R\s+7[0-7]{2}\b")),
    ("base64 decode execution", re.compile(r"base64\s+(-d|--decode).*(sh|bash|python|exec)", re.I)),
]

DANGEROUS_AST_CALLS = {
    "eval": "dynamic eval",
    "exec": "dynamic exec",
    "compile": "dynamic compile",
}

DANGEROUS_ATTR_CALLS = {
    ("os", "system"): "os.system shell execution",
    ("pickle", "load"): "pickle load on untrusted data",
    ("pickle", "loads"): "pickle loads on untrusted data",
    ("marshal", "loads"): "marshal loads dynamic code/data",
}


def iter_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        files.append(path)
    return files


def scan_text(path: Path, text: str) -> tuple[list[str], list[str]]:
    critical: list[str] = []
    warnings: list[str] = []
    for label, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            critical.append(f"{path}:{line}: possible {label}")
    for label, pattern in SUSPICIOUS_TEXT_PATTERNS:
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            warnings.append(f"{path}:{line}: suspicious pattern: {label}")
    return critical, warnings


def call_name(node: ast.AST) -> str | tuple[str, str] | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
        return (node.value.id, node.attr)
    return None


def scan_python_ast(path: Path, text: str) -> tuple[list[str], list[str]]:
    critical: list[str] = []
    warnings: list[str] = []
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        critical.append(f"{path}:{exc.lineno}: Python syntax error: {exc.msg}")
        return critical, warnings

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = call_name(node.func)
        if isinstance(name, str) and name in DANGEROUS_AST_CALLS:
            critical.append(f"{path}:{getattr(node, 'lineno', '?')}: {DANGEROUS_AST_CALLS[name]}")
        elif isinstance(name, tuple) and name in DANGEROUS_ATTR_CALLS:
            critical.append(f"{path}:{getattr(node, 'lineno', '?')}: {DANGEROUS_ATTR_CALLS[name]}")

        if name == ("subprocess", "run") or name == ("subprocess", "Popen"):
            for kw in node.keywords:
                if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                    critical.append(f"{path}:{getattr(node, 'lineno', '?')}: subprocess with shell=True")
    return critical, warnings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", default=["."], help="Files or directories to scan")
    args = parser.parse_args()

    files: list[Path] = []
    for raw in args.paths:
        p = Path(raw)
        if not p.exists():
            continue
        if p.is_dir():
            files.extend(iter_files(p))
        elif p.suffix.lower() in TEXT_SUFFIXES:
            files.append(p)

    critical: list[str] = []
    warnings: list[str] = []
    for path in sorted(set(files)):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        c, w = scan_text(path, text)
        critical.extend(c)
        warnings.extend(w)
        if path.suffix == ".py":
            c, w = scan_python_ast(path, text)
            critical.extend(c)
            warnings.extend(w)

    if warnings:
        print("Warnings:")
        for item in warnings:
            print(f"  - {item}")
    if critical:
        print("Critical findings:")
        for item in critical:
            print(f"  - {item}")
        return 1
    print(f"Safety scan passed for {len(set(files))} text files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
