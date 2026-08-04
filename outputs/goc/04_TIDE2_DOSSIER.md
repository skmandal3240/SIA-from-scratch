# TIDE 2.0 Grant Application Dossier — SIA AI
> MeitY TIDE 2.0 (Technology Incubation and Development of Entrepreneurs) — up to ₹50L
> Status: 🟡 DRAFT — verify call/window, register on Startup India portal, submit through an incubator.
> Source: https://www.startupindia.gov.in (EiR/grant application id 5f300988e4b0703cc733e025, page updated Jul 15 2026).

---

## 1. Executive summary (100 words — paste into application)
SIA is an India-first AI startup building a private, on-device AI companion. Unlike
cloud chatbots that send user data to foreign servers, SIA's entire stack — tokenizer,
transformer, vision, audio, and code models — is built from scratch in India and runs
on consumer devices (phone, laptop, edge hardware). The product is a vernacular AI
assistant that works offline, protecting privacy and enabling Indian-language access.
We are seeking TIDE 2.0 incubation support to (a) fine-tune Indian-language small
models, (b) ship our first revenue app, and (c) move to Indian edge silicon.

## 2. Problem
- 900M+ Indians lack reliable high-speed internet; cloud AI is unusable offline.
- Privacy laws (DPDP 2023) and user distrust push consumers toward local processing.
- Existing assistants are English-first, cloud-locked, and not built for Indian languages/contexts.

## 3. Solution
- **SIA Core**: from-scratch multimodal transformer (text ✅, audio listen/gen ✅,
  vision encoder ✅, video ✅, code ✅) — all code in this repo, no black boxes.
- **SIA Edge**: INT4/INT8 quantized small models runnable on 8GB devices.
- **SIA Apps**: vernacular AI support platform as first revenue engine (Pillar 1 rule).

## 4. Innovation / tech differentiators
1. From-scratch stack (no OpenAI/Google wrappers) — full ownership, no API fees.
2. On-device privacy: inference + data stay local (differentiator vs cloud chatbots).
3. Audio-native: listens to music/voice, generates audio (multimodal by design).
4. India-first: Hindi/Indian-language tokenizer, Indian context, Indian silicon roadmap.

## 5. Market
- India AI market growing >25%/yr; edge/on-device AI is the fastest segment.
- B2C: freemium privacy-first companion. B2B: white-label edge AI for OEMs.
- No credible Indian on-device multimodal assistant today.

## 6. Business model
- Freemium app (privacy = premium feature). B2B licensing. Grants as non-dilutive fuel.
- Rule: 30–50% of margin reinvested into models (Pillar 2) and compute (Pillar 3).

## 7. Team
- Founder: Saurabh Mandal — full-stack builder, AI system architect, built the
  entire from-scratch framework (2k+ lines), plus 3 prior products (ASTRO, ALICE, SIA).

## 8. Traction / demo
- Working from-scratch transformer: 500-step nano model trained on CPU, 9-demo
  gauntlet passing (text, code, vision, audio-listen, audio-gen, image, video, tools, quantize).
- Audio→language loop live (hear → describe → reply → speak back).
- Live demos available on request (video walkthrough ready).

## 9. Fund request & use of funds (₹50L max)
| Use | ₹ |
|-----|---|
| GPU compute (Colab/GCP + IndiaAI subsidized) | 20L |
| LoRA fine-tuning + Indian-language data collection | 10L |
| Product dev (app + edge packaging) | 10L |
| Incubation fees, compliance, filings | 5L |
| Team (1–2 junior engineers) | 5L |
| **Total** | **50L** |

## 10. Milestones (12 months)
- M1 (0–3 mo): P1 LoRA trained ≥95% tool-call accuracy; SIA Edge INT8 demo on 8GB device.
- M2 (3–6 mo): First revenue app live (freemium vernacular assistant); 1k users.
- M3 (6–9 mo): B2B pilot with 1 Indian OEM; SIA Pro multilingual models.
- M4 (9–12 mo): 10k users; DLI/ASIC pre-feasibility; grant compliance report.

## 11. Alignment with TIDE 2.0 mandate
- Technology incubation: exactly our stage (prototype → product).
- Indian innovation + data residency: core design principle.
- Job creation: 1–2 junior engineers in year 1, growing with revenue.

---

## Application checklist
- [ ] Verify TIDE 2.0 call window (Startup India portal, application id 5f300988e4b0703cc733e025)
- [ ] Confirm incubator partner (51 TIDE incubators — pick nearest, likely Bihar/Patna or Bengaluru)
- [ ] DPIIT / Startup India registration number (gates IndiaAI + SAMRIDH too)
- [ ] Fill application form (startupindia.gov.in → AMS)
- [ ] Attach: this dossier + one-pager + demo video link
- [ ] Submit before window close; save confirmation ID

## One-liner for the form
"SIA — a from-scratch, on-device multimodal AI companion for Indian languages, built
in India, private by design, with a live demo and an edge-silicon roadmap."
