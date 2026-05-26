# RealBrain Launch Playbook

This playbook is for preparing a public launch without fake popularity, paid stars, spam, or posting from someone else's identity.

## Launch goals

- Explain the problem clearly: agents either forget everything or remember too much badly.
- Show a concrete local demo with fake data.
- Invite useful contributors for MCP, OpenClaw, packaging, examples, benchmarks, and docs.
- Keep claims conservative: RealBrain is a memory/control-plane layer, not consciousness or autonomous authority.

## Pre-launch checklist

- [ ] README has problem, quickstart, OpenClaw/MCP use cases, safety boundaries, and contribution CTA.
- [ ] `CONTRIBUTING.md` exists.
- [ ] `SECURITY.md` exists.
- [ ] `docs/ROADMAP.md` exists.
- [ ] `docs/LAUNCH_COPY.md` exists.
- [ ] GitHub issue templates exist.
- [ ] Tests pass.
- [ ] Compile check passes.
- [ ] Demo runs with fake local data.
- [ ] Privacy scan has no actual secrets, private vaults, generated DBs, or user-specific paths.
- [ ] Labels and launch issues are created.
- [ ] Release notes are drafted.

## Suggested launch sequence

1. Publish the repo with docs and starter issues.
2. Create a GitHub release or prerelease for `v0.1.0` if the owner approves.
3. Post launch copy manually from the owner's accounts only after review.
4. Share in relevant communities once, with context and no engagement bait.
5. Respond to issues and questions with implementation evidence, not hype.

## Demo assets to prepare

- Terminal GIF: install, run tests, run `python examples/demo.py`.
- Screenshot: generated `demo_vault/brain/global-workspace/current.md`.
- Diagram: host runtime → RealBrain tools → SQLite + markdown vault.
- Short fake-data example: record event, search memory, activate workspace, run dream.

## Launch claims to use

Safe:

- local-first operating memory for AI agents;
- evidence-linked graph memory;
- markdown/Obsidian-compatible durable truth;
- dream/consolidation as suggestion-only hygiene;
- host-owned approvals and external actions.

Avoid:

- sentient/conscious/AGI claims;
- “autonomous brain” positioning;
- guarantees of correctness;
- implying secrets or private transcripts are safe to dump by default;
- fake popularity, paid stars, or synthetic testimonials.

## Manual approval points

The owner should manually approve before:

- posting on X, LinkedIn, Reddit, Hacker News, Discord, or any community;
- cutting a GitHub release;
- publishing to PyPI;
- enabling GitHub private vulnerability reporting if not already enabled;
- adding cloud services, telemetry, analytics, or external network defaults.
