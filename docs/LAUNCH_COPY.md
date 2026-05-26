# RealBrain Launch Copy

Draft only. Do not post automatically.

## X / Twitter

Agents usually have two memory modes: forget everything, or remember everything badly.

I built RealBrain as a local-first operating-memory layer for agents: evidence-linked events, graph memory, global workspace, and suggestion-only consolidation loops that keep markdown/Obsidian as the human-readable source of truth.

It is not consciousness and it does not take external actions. It helps host runtimes like OpenClaw, MCP servers, or custom agents remember useful context without turning transcripts into memory slop.

Repo: https://github.com/ericfly02/realbrain

Looking for contributions on MCP, OpenClaw plugin examples, benchmarks, demo GIFs, docs, and PyPI packaging.

## LinkedIn

I am opening up RealBrain, a local-first operating-memory toolkit for AI agents.

The problem: most assistants either start every session cold, or they store too much unreviewed context and eventually retrieve stale or hallucinated “facts.” RealBrain takes a more conservative approach: record explicit events, connect them into evidence-linked graph memory, mark claims by status and confidence, surface active context through a global workspace, and keep dream/consolidation output as reviewable suggestions rather than facts.

It is designed to be embedded in host runtimes such as OpenClaw, MCP-compatible assistants, CLI agents, or custom FastAPI bridges. The host owns identity, approvals, external tools, and high-impact actions. RealBrain owns memory quality.

GitHub: https://github.com/ericfly02/realbrain

Useful contribution areas: MCP server wrapper, OpenClaw plugin example, adapter examples, benchmarks, demo screenshots/GIFs, docs, and PyPI packaging.

## Hacker News

Title: Show HN: RealBrain – local-first operating memory for AI agents

Post:

I built RealBrain because agent memory often falls into two failure modes: no durable memory at all, or raw transcript slop that later gets treated as truth.

RealBrain is a small Python toolkit for local-first, evidence-linked operational memory. It stores typed events, neurons, synapses, beliefs, dream runs, and global workspace items in SQLite, while keeping markdown/Obsidian as the human-readable source of truth. It is intended to be embedded in host runtimes like OpenClaw, MCP servers, CLI agents, or custom assistant backends.

Important boundary: RealBrain is not consciousness and does not execute external actions. Dreams/consolidation are suggestions only. The host runtime still owns auth, approvals, secrets, and external tools.

Repo: https://github.com/ericfly02/realbrain

I would especially appreciate feedback on the data model, MCP/OpenClaw integration shape, and safety boundaries around agent memory.

## Reddit

Suggested communities: r/LocalLLaMA, r/MachineLearning, r/ObsidianMD, or agent-builder communities where self-promotion is allowed. Check each community's rules first.

Post:

I open-sourced RealBrain, a local-first operating-memory layer for AI agents.

The goal is to help agents remember durable context without dumping every transcript into a black box. It records evidence-linked events, graph nodes/edges, beliefs with status/confidence, global workspace context, and suggestion-only dream/consolidation reports. Markdown/Obsidian can remain the human-readable source of truth, while SQLite acts as the operational index.

It is meant for host runtimes like OpenClaw, MCP-compatible assistants, CLI agents, or custom backends. It does not send messages, make decisions, or bypass approvals.

Repo: https://github.com/ericfly02/realbrain

Feedback wanted: MCP wrapper design, OpenClaw integration, benchmark ideas, and memory safety edge cases.

## Discord

I’m opening up RealBrain: a local-first operating-memory layer for AI agents.

It’s for builders who want evidence-linked agent memory without storing every raw chat as future “truth.” It includes typed events, graph memory, beliefs, global workspace, markdown/Obsidian integration, and suggestion-only consolidation/dream loops.

Repo: https://github.com/ericfly02/realbrain

If anyone wants to help, the best starter areas are docs, MCP wrapper, OpenClaw plugin example, demo screenshots/GIFs, benchmarks, and packaging.

## GitHub release notes draft

# RealBrain v0.1.0

Initial public foundation for RealBrain, a local-first operating-memory toolkit for AI agents.

## Highlights

- Pydantic schemas for events, neurons, synapses, beliefs, dream runs, and workspace items.
- SQLite operational store.
- Markdown/Obsidian adapter with path confinement.
- Optional GBrain adapter with markdown fallback.
- Host-agent tool layer in `realbrain_server.tools`.
- Global workspace activation.
- Dream engine with hypothesis/suggestion-only outputs.
- Extraction, synapse hygiene, contradiction review, curiosity queue, and nightly consolidation loops.
- Fake-data demo and unit tests.
- Public docs for architecture, security/privacy, roadmap, launch, and contribution.

## Safety boundaries

RealBrain is not consciousness, not an autonomous authority layer, and not a hosted memory service. Host runtimes own identity, approvals, secrets, and external actions. Dream/consolidation output must not be treated as fact without evidence review.

## Looking for contributors

- MCP server wrapper.
- OpenClaw plugin package/example.
- Adapter examples.
- Benchmarks.
- Demo GIFs/screenshots.
- PyPI packaging.
- Docs and safety tests.
