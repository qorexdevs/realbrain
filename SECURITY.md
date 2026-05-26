# Security Policy

RealBrain is a local-first memory toolkit. Security reports are welcome.

## Supported versions

RealBrain is pre-1.0. Please report security issues against `main` unless a release branch is created.

## Reporting a vulnerability

Please use GitHub's private vulnerability reporting for this repository if available. If it is not available, open a minimal issue that says you have a security report without including exploit details or secrets.

Do not post credentials, private vault contents, personal notes, API tokens, database dumps, or exploit payloads publicly.

## Security boundaries

RealBrain should not:

- store secrets;
- commit generated SQLite databases or private markdown vaults;
- expose a public network service by default;
- send messages, trade, modify calendars, make purchases, delete arbitrary files, or perform medical/financial authority;
- treat generated dream/consolidation output as fact;
- bypass host-runtime approval systems.

See [docs/SECURITY_AND_PRIVACY.md](docs/SECURITY_AND_PRIVACY.md) for the detailed model and publication checklist.

## Preferred fixes

Security fixes should include tests or checks where practical, especially for:

- path confinement;
- accidental secret/data ingestion;
- sensitivity labeling;
- hypothesis/fact separation;
- generated artifact exclusions.
