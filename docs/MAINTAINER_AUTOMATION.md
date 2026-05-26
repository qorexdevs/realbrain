# Maintainer Automation

RealBrain uses two layers of automated maintenance:

1. GitHub-native CI and safety scans.
2. An OpenClaw scheduled maintainer agent for issue/PR triage and review comments.

The goal is fast, helpful maintainer response without spam, fake activity, auto-merging, or unsafe execution of untrusted code.

## GitHub checks

### CI

`.github/workflows/ci.yml` runs on pull requests and pushes to `main`:

- install package with `python -m pip install -e .`;
- run `python -m unittest discover -s tests`;
- run `python -m compileall realbrain realbrain_server examples tests`;
- run `python examples/demo.py`.

The workflow uses `pull_request`, not `pull_request_target`, and checkout disables credential persistence.

### Safety scan

`.github/workflows/safety-scan.yml` runs `python scripts/security_scan.py .`.

The scan catches common high-risk patterns:

- private key blocks;
- common API/token formats;
- suspicious credential assignments;
- private local paths;
- dynamic `eval`/`exec`/`compile`;
- `os.system`, `shell=True`, unsafe pickle/marshal loads;
- shell snippets such as curl-to-shell or broad `rm -rf`.

This is not a proof that code is safe. It is a tripwire before human/agent review.

## Scheduled maintainer agent policy

The OpenClaw maintainer agent should:

- check open PRs, issues, and recent comments for this repo only;
- acknowledge new contributors politely;
- review PR diffs with blast-radius-first retrieval;
- inspect CI/safety results;
- look for malicious or risky code patterns;
- request changes when behavior, tests, or safety boundaries are unclear;
- approve only small, low-risk PRs with green checks and clear scope;
- never auto-merge without explicit owner instruction;
- never run untrusted PR code locally with credentials available;
- never post repetitive comments just to appear active.

Allowed public actions:

- issue comments;
- PR review comments;
- labels such as `needs-human-review`, `security-risk`, `ci-failed`, `automated-review`;
- approvals for obviously safe, small PRs after CI passes.

Disallowed public actions:

- spam or duplicate comments;
- fake enthusiasm or manufactured popularity;
- auto-merge;
- running untrusted PR code on the maintainer host;
- exposing tokens, private config, private vaults, or OpenClaw internals.

## Manual escalation

Escalate to the owner when a PR:

- changes GitHub Actions or release/publishing behavior;
- adds dependencies, networking, subprocess execution, dynamic code execution, or serialization of untrusted data;
- touches security/privacy docs or boundaries in a questionable way;
- changes package metadata or publishing workflows;
- has failing CI but looks strategically important;
- contains anything suspicious or obfuscated.
