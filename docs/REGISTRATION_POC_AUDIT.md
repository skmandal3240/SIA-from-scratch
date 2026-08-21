# Registration PoC Repository Audit

**Branch:** `feat/india-company-registration-poc`

**Audit date:** 2026-08-21 (runtime date)

## Baseline

The repository is a Python-first, from-scratch multimodal AI framework rather than an existing web application. Its core surface is the SIA model, tokenizer, training scripts, modality demos, and grant/company collateral. There is no existing HTTP server, database schema, authentication flow, document workflow, or registration UI to extend.

| Area | Finding |
|---|---|
| Runtime | Python project with PyTorch/numpy/Accelerate-oriented dependencies |
| Existing product surface | CLI model training, generation, tools, audio/vision/code demos |
| Existing company material | India incorporation kit, company blueprint, five-pillar plan, grants tracker, TIDE dossier |
| Existing automation | A daily digest script reads the five-pillar plan and grants tracker |
| Baseline syntax | `python3 -m compileall -q .` passed |
| Package manager | `requirements.txt`; no `package.json` or frontend scaffold |
| Sensitive-data posture | Existing documents contain planning assumptions but no application database or secure document vault |

## Required corrections carried into the PoC

The existing incorporation kit assumes Bengaluru/Karnataka and a single 100% founder. The approved scope changes the primary base to Madhubani, Bihar and requires the interface to stop at a clear second-member/second-director gate for a Private Limited Company. Existing grant notes also mix grants, loans, accelerator support, and in-kind compute; the new catalogue will classify those support types separately and attach a source plus verification timestamp.

The first implementation will therefore add a small Flask-based local web PoC beside the existing AI CLI. It will use safe local JSON persistence for demo state, masked/test document metadata, deterministic validation rules, source-backed scheme records, and a printable review/export view. This avoids rewriting the model framework while making the registration/funding workflow runnable with the repository’s current Python ecosystem.

## Planned files

- `poc_app.py`: local Flask server, routes, demo persistence, validation, and export.
- `poc_rules.py`: versioned registration-readiness and support-matching rules.
- `poc_data.py`: Bihar-focused defaults, checklist, and source-backed program catalogue.
- `templates/`: accessible registration, dashboard, support, GPU, and review pages.
- `static/poc.css`: responsive visual system for the private founder workspace.
- `tests/test_poc_rules.py`: deterministic rule tests and safety checks.
- `docs/REGISTRATION_POC.md`: setup, scope, privacy limits, and next steps.

The implementation must not use real PAN/Aadhaar values, submit MCA or grant applications, make payments, or claim that a result is legal advice or a funding award.
