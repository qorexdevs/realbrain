# RealBrain Security and Privacy

RealBrain is intended to run locally and store only memory records the user wants their agent to remember.

This document defines the security and privacy posture expected from integrations.

---

## Core principles

1. **Local-first by default**: no network service is required for core operation.
2. **No secrets in memory**: never store API keys, tokens, passwords, private keys, or seed phrases.
3. **Evidence, not omniscience**: records should cite evidence refs and confidence.
4. **Hypotheses stay hypotheses**: generated ideas are not facts.
5. **Host-owned authority**: external actions require the host runtime's approval layer.
6. **Path confinement**: markdown writes must remain inside the configured vault root.

---

## Data stored locally

RealBrain may store:

- event summaries
- evidence refs
- memory graph nodes
- memory graph edges
- beliefs with status/confidence
- dream run summaries
- active workspace context
- markdown reports and queues

RealBrain should not store:

- raw credentials
- private keys
- raw personal data dumps unless explicitly approved
- full chat logs by default
- unredacted financial/medical records unless the user intentionally configures that
- private vault contents in a public repo

---

## SQLite database

Default recommended path:

```text
$REALBRAIN_ROOT/ops/brain/realbrain.sqlite
```

Publishing rule:

- do not commit `*.sqlite`
- do not commit `*.db`
- do not commit generated `realbrain_vault/` or `demo_vault/`

The provided `.gitignore` excludes these.

---

## Markdown vault safety

`ObsidianAdapter` resolves paths under a configured root and rejects path traversal.

Correct:

```text
brain/global-workspace/current.md
brain/curiosity/current.md
brain/reviews/contradictions/YYYY-MM-DD.md
```

Incorrect:

```text
../secrets.md
/etc/passwd
/home/user/.ssh/id_rsa
```

Integrations should expose only high-level RealBrain write functions, not arbitrary filesystem access.

---

## External action boundary

RealBrain must not directly perform high-impact external actions.

Forbidden as RealBrain-native capabilities:

- sending messages/emails
- creating/deleting calendar events
- placing trades or moving money
- making purchases
- changing passwords or secrets
- deleting arbitrary files
- submitting forms externally
- making medical decisions

The host runtime may have tools for those things, but the host runtime must enforce user approval and policy.

---

## Dream engine safety

Dream outputs must be treated as:

- hypothesis
- suggestion
- question
- consolidation candidate

They must not be treated as:

- fact
- user instruction
- permission grant
- external action plan that can execute without review

Required warning language for host UIs:

```text
Dream output is hypothesis/suggestion only. It did not execute actions and must not be treated as fact without evidence review.
```

---

## Recommended deployment modes

### Personal local mode

- local markdown vault
- local SQLite DB
- no server exposed to LAN/WAN
- host agent calls RealBrain as in-process Python functions

### Local service mode

- localhost-only API wrapper
- authentication if any process beyond the owner can call it
- file permissions limiting vault/DB access
- no public network exposure

### Team mode

Not implemented by default. If adding team support, add:

- per-user identity
- access control
- audit logs
- namespace isolation
- retention policies
- deletion/export flows

---

## Pre-publication checklist

Before publishing a repo containing RealBrain:

- [ ] `grep` for secrets and private paths
- [ ] remove generated SQLite DBs
- [ ] remove personal vault notes
- [ ] remove `.env`
- [ ] remove private configs
- [ ] run tests
- [ ] run demo with fake data
- [ ] confirm examples use fake paths/data only

Suggested scan:

```bash
grep -RInE 'api[_-]?key|secret|token|password|BEGIN (RSA|OPENSSH|PRIVATE)|/home/|\.openclaw|spesion|SPESION|NEXUS|Eric' . \
  --exclude-dir=.git --exclude='*.pyc'
```

A few security docs may include the search terms as examples; no actual credentials or private personal files should appear.

---

## Incident response

If private data is accidentally committed:

1. remove it from the working tree
2. rotate any exposed credentials immediately
3. rewrite git history if the repo was pushed publicly
4. invalidate affected tokens/keys
5. add regression tests or pre-commit checks

---

## License and warranty

RealBrain is provided under MIT terms. It is a memory architecture and software toolkit, not professional legal, financial, medical, or security advice.
