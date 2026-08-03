# SIA — AI 5-Pillar Plan: One-Pager
**Saurabh Mandal Holdings | 03 Aug 2026 | Confidential Draft**

## The thesis in one line
OpenAI's moat is *inference cost* (Jevons paradox: cheaper AI → exploding usage).
SIA answers it India-style: cheaper models, Indian silicon, rented Indian compute now, own DC later — with a revenue app funding it all.

## The 5 Pillars (stack order)

| # | Pillar | India lever | Status (Aug 2026) |
|---|--------|-------------|-------------------|
| 5 | Energy | Nuclear criticality (PFBR) | PFBR Kalpakkam 500 MWe critical 6 Apr 2026; Nuclear Mission 100 GW by 2047; Bharat Small Reactors opening to private sector |
| 4 | Hardware | Tata silicon + LPU/optical + custom software | Tata-PSMC Dholera 28nm fab trial production Dec 2026; Tata OSAT Assam; India Semiconductor Mission ₹76,000 Cr |
| 3 | Infrastructure | Rent Indian govt/company compute | IndiaAI Mission 38,000+ GPUs; startups up to 40% off → ₹65–92/hr (H100 on-demand ~₹217/hr, spot ~₹70/hr) |
| 2 | Models | SIA Edge AI everywhere | SIA-from-scratch transformer core IN PROGRESS (this repo) |
| 1 | Applications | Revenue → funds all R&D | None yet — this is the engine |

## Three reality corrections
1. **LPU ≠ optical.** Groq LPU is SRAM-based, ships today. Photonic = 2028+ R&D, never a dependency.
2. **Tata's 28nm fab can't make datacenter GPUs** (no EUV/HBM). It CAN make edge AI ASICs → design our own edge accelerator, fab with Tata, rent NVIDIA-class GPUs for training.
3. **PFBR criticality ≠ cheap power at our socket.** Solar PPAs (~₹2.5–3/kWh) are the near-term play; nuclear = 2030s baseload bet.

## Pillar 2: Model family (the core)
- **SIA-lite** (0.5–1B): cameras, drones, IoT
- **SIA-edge** (3–8B): on-prem, phones, edge boxes
- **SIA-pro** (fine-tuned 70B-class): cloud API
- Multimodal in stages: text → vision → audio → video/code
- **Do NOT** pretrain 70B from scratch yet — $10M+ and no moat

## Pillar 1: First app (chosen)
**Vernacular AI support/agent platform** — Hindi + regional voice/text agents for Indian enterprises & BPOs. Per-resolution pricing, no hardware, pure SaaS. MVP this quarter on SIA-pro; 1 anchor enterprise; bill via UPI.

## Execution order (money-first)
| Phase | Window | Focus |
|-------|--------|-------|
| 0 | weeks 1–4 | IndiaAI credits + grants; finish SIA core; app POC to 5 customers |
| 1 | mo 2–6 | App live + first revenue; SIA-pro LoRA; edge quantisation |
| 2 | mo 6–12 | App #2 (drone/camera); SIA-edge on hardware; RISC-V SoC design |
| 3 | yr 2 | Tape-out edge ASIC (28nm, DLI); colocation |
| 4 | yr 3–5 | Own DC near green power; optical R&D; BSR application; Global South export |

## Cost table (indicative ₹)
| Item | Cost | When |
|------|------|------|
| IndiaAI GPU | ₹65–92/hr | now |
| SIA-pro LoRA | ~₹20–60K | mo 3 |
| SIA-edge quantise | ₹2–5L | mo 6–12 |
| Edge ASIC design+FPGA | ₹40–80L (DLI ~50%) | yr 2 |
| 28nm tape-out w/ Tata | ₹15–30 Cr | yr 2–3 |
| Colocation | ₹3–6L/mo/rack | yr 2 |
| Own DC | ₹50–150 Cr | yr 4+ |

## First 7 days
1. Apply IndiaAI compute portal (need DPIIT/Startup India number)
2. Apply SAMRIDH / TIDE 2.0 / IndiaAI grants
3. Ship SIA transformer core smoke test — ON TRACK
4. List 20 app #1 customers; call 5
5. Draft intros: Tata Electronics + InCore
6. Read PFBR / BSR private-participation policy
7. Update this file weekly; report skipped items

---
*Generated from `docs/AI_5_PILLARS_INDIA_PLAN.md` — SIA-from-scratch repo.*
