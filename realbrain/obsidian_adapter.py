from __future__ import annotations

import re
from pathlib import Path


class ObsidianSafetyError(ValueError):
    pass


class ObsidianAdapter:
    """Safe markdown adapter for the Obsidian vault.

    The adapter only reads/writes within `brain_root`. It intentionally exposes
    small operations so higher-level RealBrain code can keep provenance and
    approval policy explicit.
    """

    def __init__(self, brain_root: str | Path):
        self.brain_root = Path(brain_root).resolve()
        self.brain_root.mkdir(parents=True, exist_ok=True)

    def resolve(self, relative_path: str | Path) -> Path:
        target = (self.brain_root / relative_path).resolve()
        if target != self.brain_root and self.brain_root not in target.parents:
            raise ObsidianSafetyError("path escapes brain root")
        return target

    def relative(self, path: str | Path) -> str:
        return str(Path(path).resolve().relative_to(self.brain_root))

    def read_markdown(self, relative_path: str, max_chars: int | None = None) -> dict:
        target = self.resolve(relative_path)
        if not target.is_file():
            raise FileNotFoundError(relative_path)
        text = target.read_text(encoding="utf-8", errors="replace")
        truncated = False
        if max_chars is not None and len(text) > max_chars:
            text = text[:max_chars]
            truncated = True
        return {"path": str(target), "relative_path": self.relative(target), "content": text, "truncated": truncated}

    def write_markdown(
        self,
        relative_path: str,
        content: str,
        *,
        overwrite: bool = False,
        evidence_refs: list[str] | None = None,
    ) -> dict:
        target = self.resolve(relative_path)
        if target.exists() and not overwrite:
            raise FileExistsError(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        final = content.rstrip() + "\n"
        if evidence_refs:
            final += "\n---\nEvidence refs:\n" + "\n".join(f"- {ref}" for ref in evidence_refs) + "\n"
        target.write_text(final, encoding="utf-8")
        return {"path": str(target), "relative_path": self.relative(target), "bytes": len(final.encode("utf-8"))}

    def upsert_section(self, relative_path: str, heading: str, body: str, *, level: int = 2) -> dict:
        if level < 1 or level > 6:
            raise ValueError("heading level must be 1..6")
        target = self.resolve(relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        marker = "#" * level
        header = f"{marker} {heading.strip()}"
        block = f"{header}\n{body.strip()}\n"
        text = target.read_text(encoding="utf-8", errors="replace") if target.exists() else ""
        pattern = re.compile(rf"(^|\n){re.escape(header)}\n.*?(?=\n#{{1,6}}\s|\Z)", re.DOTALL)
        if pattern.search(text):
            new_text = pattern.sub("\n" + block.rstrip(), text).strip() + "\n"
            action = "updated"
        else:
            new_text = text.rstrip() + ("\n\n" if text.strip() else "") + block
            action = "inserted"
        target.write_text(new_text, encoding="utf-8")
        return {"path": str(target), "relative_path": self.relative(target), "heading": heading, "action": action}

    def search_markdown(self, query: str, *, subpath: str = "", limit: int = 20) -> list[dict]:
        root = self.resolve(subpath)
        if not root.exists():
            return []
        q = query.lower()
        hits: list[dict] = []
        paths = root.rglob("*.md") if root.is_dir() else [root]
        for path in sorted(paths):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            haystack = f"{path.name}\n{text}".lower()
            if q in haystack:
                idx = haystack.find(q)
                start = max(0, idx - 120)
                end = min(len(text), idx + 240)
                hits.append({"path": str(path), "relative_path": self.relative(path), "snippet": text[start:end]})
            if len(hits) >= limit:
                break
        return hits

    def resolve_canonical_path(self, title_or_path: str) -> str | None:
        candidate = self.resolve(title_or_path)
        if candidate.is_file():
            return self.relative(candidate)
        stem = Path(title_or_path).stem.lower()
        normalized = re.sub(r"[^a-z0-9]+", "-", stem).strip("-")
        for path in sorted(self.brain_root.rglob("*.md")):
            path_stem = path.stem.lower()
            path_norm = re.sub(r"[^a-z0-9]+", "-", path_stem).strip("-")
            if path_stem == stem or path_norm == normalized:
                return self.relative(path)
        return None
