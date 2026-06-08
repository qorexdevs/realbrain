# Changelog

## 0.1.1

First release that runs cleanly across the supported Python versions.

### Fixed
- Package failed to import on Python 3.10 because of `from datetime import UTC`, which only exists on 3.11+. Switched to `timezone.utc` everywhere, so 3.10/3.11/3.12 all work.
- SQLite connections are now closed via a context manager, which fixes file locks and temp-dir cleanup on Windows.
- Obsidian vault paths use posix separators, so relative paths are stable on Windows.
- `reinforce_synapse` rounds the weight to avoid float drift.

### Added
- GitHub Actions CI on Linux and Windows across Python 3.10/3.11/3.12, running the documented install, unit tests, and demo.
- Quickstart smoke test that runs `examples/demo.py` in a temp dir and checks the vault is created.
- README section explaining what the demo run produces.

## 0.1.0

Initial public layout. Note: this tag does not import on Python 3.10; use 0.1.1.
