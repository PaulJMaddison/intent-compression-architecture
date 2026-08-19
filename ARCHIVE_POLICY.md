# Archive Policy

## Why this repo is kept

This repo is both a historical record and a working reference example.

We want people to be able to understand and run the old ICA work, but we do **not** want later edits to rewrite what happened at the time.

## Three types of content

### 1. Frozen historical copies

Everything in `docs/legacy/` is a point-in-time copy of the old documentation.

Do not edit those files to improve wording, links or terminology. If something needs explaining, add the explanation to a current document and link to the old copy.

### 2. Published historical files

The proposal PDF/DOCX, architecture image and published pilot results are part of the historical record.

If an old result or statement is later found to be wrong, keep the original and clearly document the correction. Do not quietly replace the old version with a better-looking one.

### 3. Maintained reference files

These files can be improved so the archive stays useful:

- `README.md` and `index.html`
- `EVOLUTION.md`, `ARCHIVE_POLICY.md`, `SECURITY.md` and `CONTRIBUTING.md`
- the offline `ica-core` Python code
- schemas and validation scripts
- tests and local validation helpers

If a bug or security fix changes the behaviour of the reference code, record it in `CHANGELOG.md`.

## Rules for maintaining the archive

1. **Keep the history.** Do not remove an old idea simply because the current product has moved on.
2. **Do not depend on one developer's computer.** Public docs must not rely on private folders or local machine paths.
3. **Keep normal testing offline.** Live API tests must always be optional.
4. **Never add secrets or private data.** This includes API keys, tokens, customer data, private prompts and production traces.
5. **Keep the contract consistent.** The JSON Schema and the Python model must describe the same structure.
6. **Explain corrections.** Preserve the old result and document what changed and why.
7. **Keep validation local.** GitHub Actions were deliberately removed from this archive. Local validation is the normal test path.
8. **Use safe Git practices.** Do not destroy unrelated or uncommitted work to make an archive change easier.

## If benchmark results change

Explain:

- what changed
- why it changed
- whether the old and new numbers can still be compared
- whether it was a bug fix, data correction, method change or a new experiment
- which file is the original historical result
- which file contains the corrected or new result

Never replace an old published result simply because a newer result looks better.

## If the reference code changes

Good changes improve correctness, safety, privacy, validation, portability or failure handling.

Avoid redesigning the old ICA code just to make it look like the current Clarity Gateway. This repo is useful because it shows the path between the two.
