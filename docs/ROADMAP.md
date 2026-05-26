# RealBrain Roadmap

This roadmap is intentionally practical: make RealBrain easy to try, safe to embed, and useful to agent builders without overclaiming autonomy.

## Now: v0.1 public foundation

- Core Pydantic models for events, neurons, synapses, beliefs, dreams, and workspace items.
- SQLite operational store.
- Markdown/Obsidian adapter with path confinement.
- Optional GBrain adapter with markdown fallback.
- Tool-layer functions for host runtimes.
- Global workspace, dream engine, extraction, hygiene, contradiction, curiosity, and nightly consolidation loops.
- Unit tests and fake-data demo.
- Public contribution docs, launch copy, issue templates, and security policy.

## Next: v0.2 integration polish

High-value contribution areas:

- First-class MCP server wrapper.
- OpenClaw plugin package or documented plugin skeleton.
- CLI commands: `realbrain record`, `search`, `activate`, `dream`, `consolidate`.
- JSON schema exports for tool contracts.
- Adapter examples for FastAPI, CLI agents, and desktop MCP clients.
- Better README screenshots/GIFs.
- PyPI package publishing workflow.

## Later: v0.3 quality and scale

- Pluggable extractors and scoring policies.
- Evidence-span support for markdown/source refs.
- Optional local embeddings/reranking adapter.
- Rebuild SQLite from markdown/events.
- Belief explanation API.
- Benchmark fixtures for retrieval, extraction, hygiene, and contradiction review.
- Policy hooks for write authority and retention.

## Non-goals

- Hosted SaaS by default.
- Autonomous external actions.
- Storing secrets or full private transcripts by default.
- Treating dream output as truth.
- Replacing a user's source-of-truth knowledge base.

## How to choose work

Pick work that improves one of these:

1. Trust: evidence, status, confidence, freshness, reviewability.
2. Local-first usability: fast setup, clear examples, fewer dependencies.
3. Integration surface: OpenClaw, MCP, CLI, FastAPI, tests.
4. Safety: path confinement, secret avoidance, host-owned approvals.
