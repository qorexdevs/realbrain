# Agents Need Operating Memory, Not Transcript Slop

Repo: https://github.com/ericfly02/realbrain

Most AI agents have two bad memory modes.

The first is statelessness. Every new session starts cold. The user repeats the same project context, decisions, preferences, constraints, and caveats over and over again.

The second is worse: memory slop. Everything gets stored. Raw transcripts, draft ideas, hallucinated summaries, stale decisions, temporary moods, and generated guesses all become retrievable “context.” Eventually the agent starts treating old or weak claims as if they were true.

RealBrain is an attempt to build the missing middle layer: local-first operating memory for AI agents.

It is not consciousness. It is not an autonomous authority system. It is not a hosted memory service. It is a small Python toolkit for recording explicit memory events, linking them into a graph, surfacing active context, and producing reviewable consolidation outputs while keeping the human-readable source of truth in markdown.

## The problem with naive agent memory

Long-term memory sounds simple: save what happened, retrieve it later.

In practice, durable memory for agents needs answers to several hard questions:

- What deserves to be remembered?
- What is the evidence?
- Is the claim a fact, inference, hypothesis, stale belief, or disproven belief?
- Who or what system is allowed to act on it?
- When should it be reviewed?
- Can a human inspect and edit the source of truth?

A raw transcript store does not answer those questions. A vector database alone does not answer them either. Retrieval is useful, but memory quality is not just nearest-neighbor search.

Real agent memory needs structure, status, evidence, freshness, and authority boundaries.

## RealBrain's model

RealBrain stores local operational memory in SQLite and writes reviewable markdown outputs for humans.

The core objects are:

- `BrainEvent`: an explicit observation or internal event with source, sensitivity, and evidence refs.
- `Neuron`: a durable concept, project, decision, person, tool, question, or episode.
- `Synapse`: a typed relationship between neurons.
- `Belief`: a claim with status, confidence, source quality, review date, and contradictions.
- `GlobalWorkspaceItem`: active context that should be visible to the host agent right now.
- `DreamRun`: bounded consolidation output that generates hypotheses and review candidates.

This lets a host runtime ask more careful questions:

- What do we know?
- Why do we think we know it?
- Is it fresh?
- Is it just a hypothesis?
- What should the agent pay attention to right now?

## Markdown stays human-readable

RealBrain is local-first. The recommended setup keeps markdown or Obsidian as the human-readable source of truth, while SQLite acts as an operational index.

That matters because memory should be auditable. If an agent creates a workspace report, curiosity queue, contradiction review, or dream summary, a human should be able to open it, read it, edit it, and delete it without depending on a proprietary hosted memory UI.

A typical vault layout looks like this:

```text
REALBRAIN_ROOT/
  brain/
    global-workspace/
      current.md
    curiosity/
      current.md
    dreams/
      YYYY-MM-DD.md
    sleep-reports/
      YYYY-MM-DD.md
    reviews/
      contradictions/
        YYYY-MM-DD.md
  ops/
    brain/
      realbrain.sqlite
```

## Dream output is not truth

RealBrain includes dream/consolidation loops, but the word “dream” is deliberately bounded.

A dream run can propose hypotheses, cross-domain connections, review items, or consolidation candidates. It cannot promote a claim to fact. It cannot authorize external action. It cannot send messages, trade, modify calendars, make purchases, delete files, or make medical decisions.

Dream output is suggestion-only.

That boundary is important. The goal is not to make an agent more mystical. The goal is to make memory hygiene visible and reviewable.

## Host runtimes own authority

RealBrain is designed to be embedded in host runtimes such as OpenClaw, MCP-compatible assistants, CLI agents, FastAPI bridges, or custom multi-agent systems.

The host runtime owns:

- user identity;
- authentication;
- approvals;
- external tools;
- secrets;
- network exposure;
- high-impact real-world actions.

RealBrain owns:

- operational memory records;
- graph/search state;
- belief status;
- workspace reports;
- contradiction and curiosity queues;
- suggestion-only consolidation.

That separation is the main safety model.

## Quickstart

```bash
git clone https://github.com/ericfly02/realbrain.git
cd realbrain
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m unittest discover -s tests
python examples/demo.py
```

Minimal tool-layer example:

```python
from realbrain_server.tools import RealBrainToolContext, record_event, search_memory, activate, dream

ctx = RealBrainToolContext(
    brain_root="./realbrain_vault",
    db_path="./realbrain_vault/ops/brain/realbrain.sqlite",
)

record_event({
    "event_type": "conversation",
    "source": "my-agent",
    "content": "RealBrain should remember durable facts with evidence refs.",
    "sensitivity": "personal",
    "evidence_refs": ["chat://123"],
}, ctx=ctx)

print(search_memory("durable facts evidence", ctx=ctx))
print(activate("RealBrain", ctx=ctx))
print(dream(mode="rem_generation", budget=3, focus_area="RealBrain", ctx=ctx))
```

## What I am looking for

RealBrain is early. The highest-leverage contribution areas are:

- MCP server wrapper;
- OpenClaw plugin example;
- FastAPI and CLI adapter examples;
- benchmark fixtures for extraction, retrieval, contradiction review, and consolidation;
- demo GIFs/screenshots;
- PyPI packaging;
- docs and safety tests.

Starter issues are here: https://github.com/ericfly02/realbrain/issues

Release: https://github.com/ericfly02/realbrain/releases/tag/v0.1.0

If you care about local-first agents, MCP tools, Obsidian workflows, or memory safety, I would love feedback on the model and the boundaries.

Repo: https://github.com/ericfly02/realbrain
