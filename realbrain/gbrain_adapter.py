from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Callable

from .obsidian_adapter import ObsidianAdapter

Runner = Callable[[list[str]], subprocess.CompletedProcess[str] | str]


class GBrainAdapter:
    """Small GBrain wrapper with Obsidian fallback.

    Tests can inject a runner; production uses the configured `gbrain` binary if
    available. Failures are returned as warnings rather than silently converted
    into durable truth.
    """

    def __init__(
        self,
        brain_root: str | Path,
        *,
        gbrain_binary: str | None = None,
        workdir: str | Path | None = None,
        bun_binary: str | None = None,
        gbrain_home: str | Path | None = None,
        runner: Runner | None = None,
    ):
        self.brain_root = Path(brain_root).resolve()
        self.obsidian = ObsidianAdapter(self.brain_root)
        # GBrain is optional and must be configured explicitly. Do not auto-discover
        # user-local binaries from PATH in the public package; that can leak a
        # developer's private vault into demos/tests.
        self.gbrain_binary = gbrain_binary
        self.bun_binary = bun_binary or (shutil.which("bun") if self.gbrain_binary else None)
        self.workdir = Path(workdir).resolve() if workdir else None
        if gbrain_home:
            self.gbrain_home = Path(gbrain_home).resolve()
        elif self.gbrain_binary and Path(self.gbrain_binary).parts[-3:-1] == (".bun", "bin"):
            self.gbrain_home = Path(self.gbrain_binary).resolve().parents[2]
        else:
            self.gbrain_home = Path.home()
        self.runner = runner

    def _run(self, args: list[str]) -> tuple[str, list[str]]:
        if self.runner:
            result = self.runner(args)
            if isinstance(result, str):
                return result, []
            warnings: list[str] = []
            if result.returncode != 0:
                warnings.append(result.stderr.strip() or f"gbrain exited {result.returncode}")
            return result.stdout.strip(), warnings
        if not self.gbrain_binary or not Path(self.gbrain_binary).exists():
            return "", ["gbrain binary unavailable; used Obsidian fallback only"]
        path_parts = [
            str(Path(self.gbrain_binary).parent),
            str(Path(self.bun_binary).parent) if self.bun_binary else "",
            os.environ.get("PATH", ""),
        ]
        env = {
            **os.environ,
            "HOME": str(self.gbrain_home),
            "BUN_INSTALL": str(self.gbrain_home / ".bun"),
            "PATH": ":".join(part for part in path_parts if part),
        }
        cmd = [self.gbrain_binary, *args]
        if self.bun_binary and Path(self.bun_binary).exists():
            cmd = [self.bun_binary, self.gbrain_binary, *args]
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.workdir) if self.workdir else None,
                env=env,
                capture_output=True,
                text=True,
                timeout=45,
                check=False,
            )
        except Exception as exc:  # pragma: no cover - exercised by integration, not unit tests
            return "", [f"gbrain command failed: {type(exc).__name__}: {exc}"]
        warnings = [] if proc.returncode == 0 else [proc.stderr.strip() or proc.stdout.strip() or f"gbrain exited {proc.returncode}"]
        return proc.stdout.strip(), warnings

    def search(self, query: str, *, limit: int = 10) -> dict:
        stdout, warnings = self._run(["search", query])
        fallback_hits = self.obsidian.search_markdown(query, limit=limit)
        return {
            "query": query,
            "gbrain_output": stdout,
            "obsidian_hits": fallback_hits,
            "warnings": warnings,
        }

    def query(self, question: str) -> dict:
        stdout, warnings = self._run(["query", question])
        return {"question": question, "gbrain_output": stdout, "warnings": warnings}

    def resolve_canonical_path(self, title_or_path: str) -> dict:
        direct = self.obsidian.resolve_canonical_path(title_or_path)
        if direct:
            return {"query": title_or_path, "canonical_path": direct, "source": "obsidian_exact", "warnings": []}
        result = self.search(title_or_path, limit=5)
        first_hit = result["obsidian_hits"][0]["relative_path"] if result["obsidian_hits"] else None
        return {
            "query": title_or_path,
            "canonical_path": first_hit,
            "source": "obsidian_search" if first_hit else "unresolved",
            "warnings": result["warnings"],
            "gbrain_output": result["gbrain_output"],
        }
