# SIA India Registration and Funding PoC

## What this adds

This repository now includes a local Flask proof of concept for a student-founded AI startup whose genuine operating base is Madhubani, Bihar. It is designed to help prepare a reviewable company-registration package and an early-stage support plan without pretending to be a government filing service.

The PoC covers a company profile, Private Limited structure gates, address and document-status checklist, conservative government-support matching, a GPU workload estimator, and a structured JSON export for professional review.

## Run locally

From the repository root:

```bash
python3 -m pip install -r requirements.txt
python3 poc_app.py
```

Then open `http://127.0.0.1:5000/`. The app stores the local demo draft in `.poc_state/draft.json`, which is ignored by Git. Use the **Reset demo draft** action on the review page to clear it.

If Flask is already available in the environment, the server can be started directly. The existing SIA model CLI remains unchanged and is still documented in the root README.

## Demo workflow

| Step | Page | Result |
|---|---|---|
| 1 | Company setup | Enter the working name, AI product, target users, founder profile, second member/director, genuine Madhubani address, and capital notes |
| 2 | Documents | Record safe proof metadata and office-proof flags; do not upload real identity documents in this PoC |
| 3 | Support finder | See conditional routes for DPIIT, SISFS, Bihar support, NIDHI-linked routes, MeitY programs, and compute access |
| 4 | GPU planner | Enter model size, workload, hours, storage, and budget to get a transparent memory/workload estimate |
| 5 | Review & export | Inspect blockers and download `sia-registration-review.json` |

## Deliberate boundaries

The PoC does not reserve a company name, submit MCA forms, generate final MOA/AOA legal language, sign declarations, calculate a final government fee, submit a grant application, process payment, reserve a GPU, or guarantee a grant or discount. It also does not treat student or OBC status as a universal eligibility condition.

The first version stores only a local draft and document-status flags. A production version would need authenticated accounts, encrypted storage, strict per-company access control, retention/deletion rules, audit logging, privacy notices, and a professional compliance review before collecting identity documents.

## Rule and source maintenance

- `poc_data.py` contains the default profile, checklist, source URLs, and qualitative scheme catalogue.
- `poc_rules.py` contains the versioned readiness, support-matching, and GPU rules.
- Every external route includes an official source URL and is shown as conditional or requires verification unless the current profile facts and route conditions are sufficient for a narrower result.
- Monetary amounts, deadlines, GPU prices, discounts, and quotas are intentionally not hardcoded in the PoC. Recheck the official source immediately before acting.
- The repository’s `outputs/goc/02_GRANTS_TRACKER.md` and `outputs/goc/05_INCORPORATION_KIT.md` are aligned with the same Bihar-first, support-type-aware approach.

## Tests

Run the rule and HTTP smoke tests with:

```bash
PYTHONPATH=. python3 -m unittest discover -s tests -v
```

The tests cover the second-member/second-director gates, under-18 blocking, Bihar support classification, support-type separation, GPU estimation, core routes, local-save behavior, and JSON export.

## Professional review gate

Before filing, signing, paying, or applying, have a qualified Indian CA/CS/lawyer verify the current MCA process, people and address evidence, capital/shareholding, objects, forms, declarations, tax registrations, and post-incorporation requirements. Separately verify each grant, incubator, concessional-finance, and public-compute route against its current official notice and terms.

## Primary sources

- [Ministry of Corporate Affairs](https://www.mca.gov.in/)
- [DPIIT Startup Recognition](https://www.startupindia.gov.in/content/sih/en/startupgov/startup_recognition_page.html)
- [Startup India Scheme](https://www.startupindia.gov.in/content/sih/en/startup-scheme.html)
- [Startup India Seed Fund Scheme](https://seedfund.startupindia.gov.in/)
- [Startup India Government Schemes](https://www.startupindia.gov.in/content/sih/en/government-schemes.html)
- [Bihar Startup Portal](https://startup.bihar.gov.in/)
- [MeitY TIDE 2.0](https://msh.meity.gov.in/schemes/tide)
- [MeitY SAMRIDH](https://msh.meity.gov.in/schemes/samridh)
- [IndiaAI Compute Capacity](https://indiaai.gov.in/hub/indiaai-compute-capacity)
- [C-DAC AIRAWAT outreach](https://airawat.cdac.in/airawat/outreachandeducation)
