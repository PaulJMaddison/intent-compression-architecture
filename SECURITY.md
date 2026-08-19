# Security Policy

## Scope

This is a reference/archive repository. It contains an offline Python implementation, documentation, schemas, examples and benchmark tooling; it is not a hosted production service.

Security reports should still be treated seriously where they affect consumers of the reference package, generated artefacts, local tooling, or accidental data exposure.

## Reporting

Use GitHub's repository security reporting facilities where available. Do not place credentials, exploit secrets, private customer data, or sensitive trace contents in a public issue.

## Credentials

Normal tests, examples and local validation require **no live provider credential**. Never commit `.env` files, API keys, tokens, cloud credentials, production cookies, customer datasets, or copied secrets.

Provider-key fields exist only to make future/experimental adapter construction possible. The bundled provider remains offline and deterministic.

## Trace data

Tracing is disabled by default. For `JSONLTraceSink`:

- query text is hashed by default
- clarifying-question text is hashed by default
- request metadata is excluded by default
- raw query text requires an explicit query-trace mode
- raw clarifier text requires a separate explicit opt-in

The built-in redaction helper is coarse debugging assistance, not a DLP, anonymisation or compliance system. Any real deployment must define retention, deletion, encryption, access-control, consent and data-classification requirements separately.

## Dependency and archive risk

Pinned versions in `requirements.lock` reproduce the archive's artefact/evaluation toolchain; they are not a promise that those versions remain suitable for future production systems. Consumers should perform their own dependency and vulnerability review.
