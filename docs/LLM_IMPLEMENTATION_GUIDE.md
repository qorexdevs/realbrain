# RealBrain LLM Implementation Guide

This guide is written for coding agents that are asked to integrate RealBrain into another runtime.

Follow it literally unless the human gives different instructions.

---

## Mission

Implement RealBrain as a local memory/tool layer for an AI agent runtime.

The finished integration should let the host agent:

1. record important events
2. search memory
3. add evidence-linked graph records
4. activate current workspace context
5. run safe dream/consolidation loops
6. write review/curiosity/workspace markdown reports

The integration must not let RealBrain bypass the host runtime's permissions.

---

## First files to inspect

Inspect these in order:

1. `README.md`
2. `realbrain_server/tools.py`
3. `realbrain/models.py`
4. `realbrain/store.py`
5. `realbrain/obsidian_adapter.py`
6. `realbrain/global_workspace.py`
7. `realbrain/dream_engine.py`
8. `examples/openclaw_tool_bridge_example.py`
9. `tests/`

Do not start by scanning unrelated user vault data.

---

## Minimal implementation checklist

- [ ] Install package locally: `pip install -e '.[dev]'`
- [ ] Run tests: `python -m unittest discover -s tests`
- [ ] Choose local vault path and SQLite path
- [ ] Set `REALBRAIN_ROOT`
- [ ] Set `REALBRAIN_DB`
- [ ] Expose host tools mapped to `realbrain_server.tools`
- [ ] Add smoke test for `record_event`
- [ ] Add smoke test for `search_memory`
- [ ] Add smoke test for `activate`
- [ ] Add smoke test for `dream`
- [ ] Confirm dreams are labelled as hypotheses
- [ ] Confirm no secrets are stored
- [ ] Confirm external actions remain host-owned

---

## Tool API surface

Use `realbrain_server.tools` as the public integration surface.

### `record_event(event)`

Use for important raw observations.

Input example:

```json
{
  "event_type": "conversation",
  "source": "discord:channel:123",
  "content": "User decided RealBrain should stay local-first.",
  "sensitivity": "personal",
  "evidence_refs": ["discord://message/123"]
}
```

### `search_memory(query, filters=None)`

Use before answering durable or context-sensitive questions.

Input example:

```json
{
  "query": "local first memory decisions",
  "filters": {"limit": 10}
}
```

### `add_neuron(candidate)`

Use when the agent has a specific evidence-backed memory node to add.

Input example:

```json
{
  "type": "decision",
  "title": "Keep RealBrain local-first",
  "summary": "The memory layer should work with local SQLite and markdown by default.",
  "confidence": 0.9,
  "importance": 8,
  "evidence_refs": ["event_abc123"]
}
```

### `add_synapse(candidate)`

Use to connect two existing neurons.

Input example:

```json
{
  "source_neuron_id": "neuron_a",
  "target_neuron_id": "neuron_b",
  "relation_type": "supports",
  "weight": 0.7,
  "confidence": 0.8,
  "evidence_refs": ["event_abc123"]
}
```

Allowed relation types are defined in `realbrain/models.py`.

### `activate(node_or_query, depth=1, budget=5)`

Use to surface active context before reasoning.

Input example:

```json
{
  "node_or_query": "RealBrain OpenClaw integration",
  "depth": 1,
  "budget": 5
}
```

### `dream(mode="rem_generation", budget=5, focus_area=None)`

Use for hypothesis generation only.

Input example:

```json
{
  "mode": "rem_generation",
  "budget": 5,
  "focus_area": "memory quality"
}
```

Required output handling:

- label as hypothesis/suggestion
- do not treat as fact
- do not execute external actions from dream output

### `extract_events(limit=20, dry_run=False)`

Use after recording events to create conservative memory candidates.

### `synapse_hygiene(...)`

Use to decay stale graph edges.

### `review_contradictions(limit=50)`

Use to generate a markdown queue of contradictory beliefs.

### `curiosity_queue(limit=20)`

Use to generate a markdown queue of questions and evidence gaps.

### `nightly_consolidation(...)`

Use as scheduled internal memory hygiene.

---

## OpenClaw integration recipe

If the host is OpenClaw:

1. Create a plugin/tool bridge that imports `realbrain_server.tools`.
2. Instantiate `RealBrainToolContext` from config or environment variables.
3. Map each OpenClaw tool schema to a wrapper function.
4. Let OpenClaw own approvals and external action gating.
5. Add a heartbeat/cron job to run `nightly_consolidation` if desired.
6. Keep RealBrain write permissions limited to its configured vault root and SQLite DB.

Recommended tool names:

```text
realbrain_record_event
realbrain_search_memory
realbrain_add_neuron
realbrain_add_synapse
realbrain_reinforce_synapse
realbrain_write_markdown_update
realbrain_activate
realbrain_get_global_workspace
realbrain_dream
realbrain_extract_events
realbrain_synapse_hygiene
realbrain_review_contradictions
realbrain_curiosity_queue
realbrain_nightly_consolidation
```

---

## MCP integration recipe

If the host is MCP-compatible:

1. Add an MCP server wrapper in a separate file/package.
2. Import functions from `realbrain_server.tools`.
3. Register each function as an MCP tool.
4. Keep the server local unless the human explicitly asks otherwise.
5. Do not expose arbitrary file read/write; only expose RealBrain functions.

Pseudo-code:

```python
ctx = RealBrainToolContext(brain_root="./vault")

@mcp.tool()
def realbrain_search_memory(query: str, filters: dict | None = None) -> dict:
    return search_memory(query, filters, ctx=ctx)
```

---

## Prompt template for coding agents

```text
You are implementing RealBrain into this agent runtime.

Read first:
- README.md
- docs/ARCHITECTURE.md
- docs/LLM_IMPLEMENTATION_GUIDE.md
- realbrain_server/tools.py
- realbrain/models.py
- realbrain/store.py

Requirements:
- local-first, no cloud dependency by default
- use REALBRAIN_ROOT and REALBRAIN_DB
- expose RealBrain functions as host tools
- keep host runtime responsible for external action approvals
- dreams/hypotheses are never facts
- do not ingest or store secrets
- add smoke tests for record/search/activate/dream
- run existing tests before final answer

Deliver:
- code changes
- test output
- integration notes
- any blockers
```

---

## Safety assertions to preserve

A correct implementation preserves these exact semantics:

- `BrainEvent` is evidence, not truth by itself.
- `Belief(status="hypothesis")` is not a fact.
- `DreamRun.generated_hypotheses` are not accepted changes.
- `DreamRun.accepted_changes` should stay empty unless a human/host review flow explicitly promotes something.
- `GlobalWorkspace` is active attention, not permanent truth.
- Markdown write-back must stay inside the configured vault root.
- Path traversal must be rejected.
- RealBrain cannot approve its own external actions.

---

## Common mistakes

### Mistake: store every chat message forever

Do not do this by default. Record only meaningful events or compressed summaries.

### Mistake: treat generated ideas as facts

Dreams, curiosity queues, and weak beliefs are suggestions until validated.

### Mistake: let RealBrain send messages or trade

RealBrain should not directly perform external actions. The host runtime owns those tools and approvals.

### Mistake: put the user's vault in the public repo

Never publish private markdown, SQLite DBs, `.env`, credentials, or personal notes.

### Mistake: hard-code local paths

Use environment variables or host config.

---

## Verification commands

```bash
python -m unittest discover -s tests
python examples/demo.py
python -m compileall realbrain realbrain_server
```

Optional secret/path scan before publishing:

```bash
grep -RInE 'api[_-]?key|secret|token|password|BEGIN (RSA|OPENSSH|PRIVATE)|/home/|\.openclaw|spesion|SPESION|NEXUS|Eric' . \
  --exclude-dir=.git --exclude='*.pyc'
```

Expected: no personal secrets and no user-specific paths in source files.
