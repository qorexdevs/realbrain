# RealBrain Launch Posting Queue

Use this to publish from the maintainer's own accounts. Do not automate spam, buy stars, or post from accounts you do not own.

Repo: https://github.com/ericfly02/realbrain
Release: https://github.com/ericfly02/realbrain/releases/tag/v0.1.0
Discussion: https://github.com/ericfly02/realbrain/discussions/11
Starter issues: https://github.com/ericfly02/realbrain/issues

## Before posting

- [ ] Confirm README quickstart still works.
- [ ] Confirm release URL is live.
- [ ] Confirm discussion/issue links are live.
- [ ] Prepare to reply to comments for 1-2 hours after posting.
- [ ] Do not ask friends to upvote, star, or comment artificially.
- [ ] Do not cross-post identical text everywhere.

## Priority 1: Hacker News

Best window: when you can reply quickly for the next 1-2 hours.

Title:

```text
Show HN: RealBrain – local-first operating memory for AI agents
```

URL:

```text
https://github.com/ericfly02/realbrain
```

First comment:

```text
I built RealBrain because agent memory often falls into two failure modes: no durable memory at all, or raw transcript slop that later gets treated as truth.

RealBrain is a small Python toolkit for local-first, evidence-linked operational memory. It stores typed events, neurons, synapses, beliefs, dream runs, and global workspace items in SQLite, while keeping markdown/Obsidian as the human-readable source of truth. It is intended to be embedded in host runtimes like OpenClaw, MCP servers, CLI agents, or custom assistant backends.

Important boundary: RealBrain is not consciousness and does not execute external actions. Dreams/consolidation are suggestions only. The host runtime still owns auth, approvals, secrets, and external tools.

I would especially appreciate feedback on the data model, MCP/OpenClaw integration shape, and safety boundaries around agent memory.
```

## Priority 2: LinkedIn

Post:

```text
I’m opening up RealBrain, a local-first operating-memory toolkit for AI agents.

The problem: most assistants either start every session cold, or they store too much unreviewed context and eventually retrieve stale or hallucinated “facts.” RealBrain takes a more conservative approach: record explicit events, connect them into evidence-linked graph memory, mark claims by status and confidence, surface active context through a global workspace, and keep dream/consolidation output as reviewable suggestions rather than facts.

It is designed to be embedded in host runtimes such as OpenClaw, MCP-compatible assistants, CLI agents, or custom FastAPI bridges. The host owns identity, approvals, external tools, and high-impact actions. RealBrain owns memory quality.

GitHub: https://github.com/ericfly02/realbrain
Release: https://github.com/ericfly02/realbrain/releases/tag/v0.1.0

Useful contribution areas: MCP server wrapper, OpenClaw plugin example, adapter examples, benchmarks, demo screenshots/GIFs, docs, and PyPI packaging.
```

## Priority 3: X / Twitter

Thread starter:

```text
Agents usually have two memory modes:

1. forget everything
2. remember everything badly

I built RealBrain as a local-first operating-memory layer for agents: evidence-linked events, graph memory, global workspace, and suggestion-only consolidation loops that keep markdown/Obsidian as the human-readable source of truth.

https://github.com/ericfly02/realbrain
```

Follow-up:

```text
It’s not consciousness and it doesn’t take external actions.

The goal is much more practical: help host runtimes like OpenClaw, MCP servers, CLI agents, or custom assistants remember useful context without turning transcripts into memory slop.
```

Follow-up:

```text
Looking for contributors on:

- MCP server wrapper
- OpenClaw plugin example
- benchmarks
- demo GIFs/screenshots
- PyPI packaging
- docs and safety tests

Starter issues: https://github.com/ericfly02/realbrain/issues
```

## Priority 4: Reddit r/LocalLLaMA

Only post if the account has normal participation history and the community rules allow it. Use `Resources` flair if available; do not label as news.

Title:

```text
I built a local-first memory layer for AI agents that keeps markdown/Obsidian as source of truth
```

Post:

```text
I open-sourced RealBrain, a small Python toolkit for local-first operating memory in AI agents.

The problem I’m trying to solve: assistants usually either forget everything between sessions, or they remember too much badly by storing raw transcript slop and later treating it as truth.

RealBrain records explicit events, evidence-linked graph nodes/edges, beliefs with status/confidence, global workspace context, and suggestion-only dream/consolidation reports. SQLite acts as the operational index; markdown/Obsidian can remain the human-readable source of truth.

It is meant to be embedded in host runtimes like OpenClaw, MCP-compatible assistants, CLI agents, or custom backends. It does not send messages, make decisions, or bypass approvals.

Repo: https://github.com/ericfly02/realbrain
Release: https://github.com/ericfly02/realbrain/releases/tag/v0.1.0

I’d love technical feedback on:

- whether the memory model is too simple/too complex;
- MCP wrapper design;
- local-first safety boundaries;
- benchmark ideas for memory quality.
```

## Priority 5: Obsidian community

Angle: markdown source-of-truth and local knowledge base safety.

Title:

```text
RealBrain: local agent memory with Obsidian/markdown as source of truth
```

Post:

```text
I built RealBrain, a local-first memory toolkit for AI agents that can write reviewable workspace, curiosity, contradiction, dream, and consolidation reports into markdown.

The design goal is to avoid treating a black-box transcript store as truth. SQLite is only the operational index; markdown/Obsidian remains the human-readable layer.

Repo: https://github.com/ericfly02/realbrain

I’d especially appreciate feedback from Obsidian users on vault layout, review queues, and what not to automate.
```

## Priority 6: Medium / blog

Publish `docs/BLOG_POST_AGENT_MEMORY.md` as a technical article. Link to GitHub at the top and bottom. Do not make it sound like a press release.

Suggested title:

```text
Agents Need Operating Memory, Not Transcript Slop
```

## Follow-up responses

If someone says “is this just a vector DB?”:

```text
No. RealBrain can complement vector search, but the core focus is typed memory records: events, graph nodes/edges, beliefs with status/confidence, global workspace items, and reviewable markdown outputs. It is about memory quality and authority boundaries more than nearest-neighbor retrieval.
```

If someone says “this sounds like consciousness hype”:

```text
Agreed that the space has too much hype. RealBrain explicitly avoids consciousness claims. It is an engineering layer for local, evidence-linked memory and review queues. Dreams/consolidation are suggestions only, not facts or autonomous actions.
```

If someone asks “why not just use Obsidian?”:

```text
Obsidian/markdown is the human-readable source of truth. RealBrain adds an operational layer around it: event records, graph links, belief status, activation/workspace context, and review queues that an agent runtime can call programmatically.
```

If someone asks “how can I help?”:

```text
Best starter areas are MCP wrapper, OpenClaw plugin example, adapter examples, benchmarks, demo assets, packaging, and docs. Issues are here: https://github.com/ericfly02/realbrain/issues
```

## Cadence

Do not post everywhere at once. Recommended order:

1. LinkedIn or X first.
2. Hacker News when you can monitor replies.
3. One Reddit community after checking rules.
4. Medium/blog article.
5. One targeted Discord/Slack community where launches are welcome.
6. Follow-up update after real feedback lands.
