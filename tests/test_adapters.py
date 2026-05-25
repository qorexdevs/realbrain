import subprocess
import tempfile
from pathlib import Path

from realbrain.gbrain_adapter import GBrainAdapter
from realbrain.obsidian_adapter import ObsidianAdapter, ObsidianSafetyError


def test_markdown_adapter_safe_write_search_and_path_escape():
    with tempfile.TemporaryDirectory() as tmp:
        adapter = ObsidianAdapter(tmp)
        written = adapter.write_markdown("concepts/real-brain.md", "# Real Brain\n\nEvidence-backed graph memory.", evidence_refs=["test://source"])
        assert written["relative_path"] == "concepts/real-brain.md"
        read = adapter.read_markdown("concepts/real-brain.md")
        assert "Evidence-backed" in read["content"]
        assert "test://source" in read["content"]
        hits = adapter.search_markdown("graph memory")
        assert hits[0]["relative_path"] == "concepts/real-brain.md"
        assert adapter.resolve_canonical_path("Real Brain") == "concepts/real-brain.md"
        try:
            adapter.write_markdown("../escape.md", "nope")
            raise AssertionError("expected ObsidianSafetyError")
        except ObsidianSafetyError:
            pass


def test_gbrain_adapter_uses_runner_and_markdown_fallback():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "projects").mkdir()
        (root / "projects" / "Example.md").write_text("# Example\n\nRealBrain architecture", encoding="utf-8")
        def fake_runner(args: list[str]) -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(args, 0, stdout="[0.99] projects/Example -- RealBrain", stderr="")
        adapter = GBrainAdapter(root, runner=fake_runner)
        result = adapter.search("RealBrain")
        assert "projects/Example" in result["gbrain_output"]
        assert result["obsidian_hits"][0]["relative_path"] == "projects/Example.md"
