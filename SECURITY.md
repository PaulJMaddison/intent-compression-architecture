# Security

## What this policy covers

This is a historical reference repo, not a live hosted service.

It still contains runnable Python code, local tools, example data and trace support, so security problems should still be taken seriously.

## Reporting a security problem

Use GitHub's private security-reporting feature if it is available for this repository.

Do **not** put API keys, passwords, customer data, private prompts, sensitive traces or working exploit secrets in a public issue.

## Credentials

Normal tests and examples need **no real API credentials**.

Never commit:

- `.env` files containing secrets
- API keys or access tokens
- cloud credentials
- production cookies or session data
- customer datasets
- copied passwords or other secrets

The configuration contains fields for provider keys because the old design allowed future provider adapters. The provider included in this archive is offline and deterministic.

## Trace data

Tracing is off by default.

When JSONL tracing is enabled:

- the user's query is hashed by default
- the clarification question is hashed by default
- request metadata is left out by default
- saving the raw query requires an explicit setting
- saving the raw clarification question requires a separate explicit setting

The built-in redaction helper only removes a few obvious patterns for debugging. It is **not** a full anonymisation, compliance or data-loss-prevention system.

A real production system would still need proper rules for data retention, deletion, encryption, access, consent and classification.

## Old dependency versions

`requirements.lock` pins versions used by the archived benchmark/document toolchain so the old work is easier to reproduce.

That does not mean those versions should be used in a new production system. Anyone reusing this code should run their own current dependency and vulnerability checks.
