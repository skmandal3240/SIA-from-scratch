# SIA AI — Company Blueprint (v1)

> One page that defines the AI company. Every repo, agent, cron, and grant application
> should trace back to a line in this file. Updates go through PRD/TRD workflow.

## 1. Identity
- **Company name:** SIA AI (working title; legal name TBD at incorporation)
- **Legal form (India):** Private Limited Company (Pvt Ltd), registered office Bengaluru (India AI hub)
- **Parent group:** MANDAL HOLDINGS
- **Brand tagline:** *"Your private intelligence, on your device."*

## 2. Mission
Build an India-first, private, on-device AI companion that processes text, audio,
image, and video locally — no cloud, no data leaving the device — and monetize it
through one profitable application before scaling (Pillar 1 rule).

## 3. What we are NOT
- Not a cloud-hosted chatbot reselling OpenAI APIs.
- Not a data-harvesting ad platform.
- Not a "wrapper" company — the model stack is built from scratch (tokenizer → attention → tools → multimodal).

## 4. Products (Pillar 1 = revenue engine first)
| Priority | Product | Status |
|----------|---------|--------|
| P0 | SIA companion app (MVP: chat + tools + on-device) | in progress |
| P1 | SIA Edge (INT4/INT8 deployable small models) | framework done, LoRA pending |
| P2 | SIA Pro (fine-tuned Indian-language models) | not started |
| P3 | SIA Swarm (multi-agent on-device) | scaffold |

## 5. Business model
- **B2C:** freemium companion app (privacy as the premium feature).
- **B2B:** white-label edge AI for Indian OEMs / enterprise fleets.
- **Grants (non-dilutive):** SISFS, MeitY TIDE 2.0 / SAMRIDH, IndiaAI, NIDHI-PRAYAS, Karnataka state schemes.
- Rule: reinvest 30–50% of margin into Pillars 2–4.

## 6. Roadmap (Pillar 2, from SIA-from-scratch)
text ✅ → audio listen ✅ / gen ✅ (pipeline) → vision encoder ✅ (VAE next) →
video ✅ (frames) → code ✅ → SIA-edge INT4/INT8 deploy → SIA-pro LoRA fine-tune
on Indian data → ASIC backend (Pillar 4).

## 7. Daily intelligence (agents + crons)
| Job | Schedule (UTC) | Coverage |
|-----|----------------|----------|
| SIA AI-India Daily Brief | 04:00 | grants, policy, edge AI |
| AUTOBOTS EV Brief | 04:30 | EV policy, launches, infra |
| SIA 5-Pillar Digest | 02:30 | internal pillar status |

## 8. Open decisions
- [ ] Legal entity name + incorporation state (Bengaluru confirmed)
- [ ] Founder equity structure
- [ ] Domain / brand assets
- [ ] First paid app feature (what users pay for)
