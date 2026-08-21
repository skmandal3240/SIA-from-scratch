# AI 5-PILLAR PLAN — India-First, Self-Funded (SIA + Mandal Ecosystem)

**Source video:** "OpenAI's TRILLION Dollar Comeback : How Altman Turned a $27B Loss Into an EMPIRE?" — Think School (youtu.be/opLMb_oYfMI)
**Date:** 03 Aug 2026

## What the video actually says (transcript summary)

OpenAI's core problem = **inference cost** (training is one-time; inference scales with every user). They're stuck in the **landlord trap** — renting Microsoft DCs + NVIDIA chips, so margins stay thin. 4 strategic moves in 90 days:
1. **GPT-5.6 Sol** — matches rival performance at a fraction of cost
2. **Codex** — primary dev tool to drive deeper engagement
3. **ChatGPT Work** — unified email/docs/code workspace for lock-in
4. **Jalapeño chip** — custom inference-only AI chip with Broadcom, ~50% inference cost cut

Road ahead = **Jevons paradox**: as AI gets cheaper, usage explodes — so cost-cutting is a treadmill, not a destination.

**Mapping to our 5 pillars:** the video's lesson is *inference cost is the moat*. Our pillars answer it India-style: cheaper models (SIA-edge quantised), custom silicon (our RISC-V edge ASIC = our Jalapeño), escape the landlord trap (rent Indian compute now → own DC later), and apps that fund it all (ChatGPT Work analog = revenue products). Jevons paradox is good news for us: every 10x we cut inference cost, our addressable market (India's price-sensitive market) grows faster than the cost saved.

---

## The 5 Pillars (stack order, bottom → top)

| # | Pillar | India lever | Status (Aug 2026) |
|---|--------|-------------|-------------------|
| 5 | Energy | Nuclear criticality (PFBR) | PFBR Kalpakkam 500 MWe first criticality 6 Apr 2026 (indigenous, BHAVINI/DAE). Nuclear Mission: 100 GW by 2047. Bharat Small Reactors (220 MWe) opening to private sector |
| 4 | Hardware | Tata silicon + LPU/optical + custom software | Tata-PSMC Dholera 28nm fab: trial production Dec 2026, ~50K wafers/mo by 2028. Tata OSAT Assam. India Semiconductor Mission ₹76,000 Cr |
| 3 | Infrastructure | Rent Indian govt/company compute | IndiaAI Compute and C-DAC/AIRAWAT are potential routes; current GPU inventory, eligibility, allocation, providers, and prices must be verified from official portals at application time. |
| 2 | Models | SIA Edge AI everywhere (drones, cameras, networks) | SIA-from-scratch transformer core in progress (/root/SIA-from-scratch) |
| 1 | Applications | Revenue → funds all R&D | None yet — this is the engine |

---

## Three reality corrections (say once, build accordingly)

1. **LPU ≠ optical processor.** Groq's LPU is an SRAM-based tensor streaming chip (no HBM) — it ships today and is real. Photonic/optical processors (Lightmatter, Lightelligence) are separate, lab/early-commercial tech, and India has no optical chip maker yet. Plan: adopt SRAM/LPU-class inference thinking now; treat optical as 2028+ R&D with IITs/IISc, never a product dependency.
2. **Tata's fab can't make datacenter GPUs** (28nm, no EUV, no HBM, no advanced packaging). It CAN make edge AI ASICs for cameras/drones/phones. So: design our own edge accelerator on 28nm, manufacture with Tata; rent NVIDIA-class GPUs for training.
3. **Nuclear criticality ≠ cheap power at our socket.** PFBR must ramp to full power; grid tariffs still apply. Solar PPAs (~₹2.5–3/kWh) are the near-term cheap power. Nuclear = 2030s baseload bet, aligned with Bharat Small Reactor commercialisation.

---

## PILLAR 5 — ENERGY (India nuclear criticality)

**Fact base:** PFBR Kalpakkam reached first criticality 6 Apr 2026 (start of controlled fission chain reaction), built by BHAVINI/DAE — the world's biggest step in India's 3-stage nuclear program (thorium path). 5 more reactors approved (Kudankulam 3–4, Kaiga 5–6, Gorakhpur 1–2). Bharat Small Reactors (BSR, 220 MWe) opening to private industry — first SMRs targeted 2033.

**Step by step:**
1. **Now — don't chase reactors.** Cut energy cost at the model level: quantised edge models (INT4/INT8) = 10–50x less energy per inference; train on IndiaAI-subsidised compute where energy is already priced in.
2. **12–24 mo:** sign a green PPA (IEX green market or SECI) for future own-DC; site DC near cheap power (Rajasthan/Gujarat solar, Himachal hydro); liquid cooling, target PUE < 1.3.
3. **24–60 mo:** when BSR private participation opens (2030s), apply as anchor tenant / strategic investor for dedicated nuclear power allocation (NPCIL). Keep a DC siting plan for a Tamil Nadu campus near Kalpakkam for the nuclear-adjacent future.
4. **KPI:** blended ₹/kWh delivered; target < ₹4/kWh.

---

## PILLAR 4 — HARDWARE (Tata chip collab + LPU/optical + custom software)

**Fact base:** Dholera 28nm fab trial production Dec 2026, commercial ramp 2027–28, 50K wafers/mo. Design Linked Incentive (DLI) covers up to ~50% of design cost. No EUV → mature nodes only.

**Step by step:**
1. **Now:** define the SIA Edge silicon target — RISC-V + NPU edge accelerator, 28nm class, for cameras/drones/phones. Partners: InCore/C-DAC for RISC-V cores, Tata Electronics for manufacture. Design is cheap; fab is the long pole — start design NOW.
2. **Now:** hardware-agnostic software layer so nothing locks to NVIDIA: inference on ONNX Runtime / llama.cpp / vLLM; models portable to our ASIC/LPU later via a config change, not a rewrite.
3. **12–24 mo:** approach Tata Electronics innovation team with ONE concrete ask: tape out one edge AI SoC on Dholera 28nm, first silicon 2027–28. Use DLI + Make-in-India PLI.
4. **24–60 mo:** optical/LPU track — fund 1–2 research collaborations (IIT Madras photonics, IISc) on photonic tensor cores; adopt only when a working Indian fab partner exists. Evaluate LPU-class SRAM inference only if cost beats GPU.
5. **Deliverable markers:** RTL spec → FPGA prototype → tape-out → first silicon running SIA-Edge.

---

## PILLAR 3 — INFRASTRUCTURE (rent Indian, build later)

**Verification rule:** IndiaAI Compute and C-DAC/AIRAWAT may offer public or subsidised access, but eligibility, allocation, providers, capacity, and prices are time-sensitive. Use the registration PoC’s source-backed planner and verify the official portal before acting.

**Step by step:**
1. **Week 1:** prepare a small benchmark and workload dossier, then verify IndiaAI Compute, C-DAC/AIRAWAT, incubator, and university routes. Apply only where the current eligibility and call fit; do not assume DPIIT recognition, a discount, or compute allocation.
2. **Month 1–12:** run ALL training on rented Indian GPU (Jio / Yotta / E2E). Keep workloads portable: K8s/Slurm + containerised training so switching provider = config change.
3. **Month 12–24:** when GPU spend exceeds ~₹10–15L/month sustained, colocate racks (CtrlS / Yotta / NxtGen) instead of building. Stay in India for DPDP Act data residency — it's a selling point.
4. **Own DC trigger:** revenue covers 100% of capex, or a grant is secured. Then build greenfield DC near cheap power (Pillar 5) with our ASIC inference racks (Pillar 4).
5. **Rule:** never buy GPUs before utilisation > 70% and revenue covers depreciation.

---

## PILLAR 2 — MODELS (SIA Edge AI for everything)

**Strategy:** not one giant model — a family:
- **SIA-lite** (0.5–1B): cameras, drones, IoT, microcontrollers
- **SIA-edge** (3–8B): on-prem servers, phones, edge boxes
- **SIA-pro** (fine-tuned open 70B-class): cloud API

Multimodal in stages: text → vision → audio → video/code.

**Step by step:**
1. **Now:** finish the SIA-from-scratch transformer core (tokenizer → attention → training) — in progress. Add Hindi + 22 scheduled-language tokenizer using AI4Bharat/Bhashini corpora.
2. **Month 3–6:** LoRA fine-tune a 7–8B open model (Qwen/Llama/Mistral) on Indian data → SIA-pro API. Days, not months, on one rented GPU. This is our IP: weights + Indian datasets + deployment stack.
3. **Month 6–12:** SIA-edge 3B quantised INT4/INT8 (llama.cpp/ONNX); deploy on drone/edge hardware (Jetson / RK3588 / RISC-V); add vision (SigLIP/ViT) + audio (Whisper fine-tuned on Indian accents).
4. **Month 12+:** SIA-lite distillation for cameras/IoT; video + codegen; swap to our ASIC backend (Pillar 4).
5. **Do NOT** pretrain a 70B from scratch yet — $10M+ and no moat. Skip until revenue justifies.

---

## PILLAR 1 — APPLICATIONS (revenue engine → funds all R&D)

**Rule:** one profitable app before scaling anything. Sell outcomes, not tokens. Reinvest 30–50% of margin into Pillars 2–4 (your stated rule).

**Step by step:**
1. **Now — pick ONE app with a paying customer this quarter.** Recommended order:
   - **#1 (chosen): Vernacular AI support/agent platform** — Hindi + regional-language voice/text agents for Indian enterprises & BPOs. Fastest cash: every Indian company has a support budget; sell per-resolution. No hardware, no permissions, pure SaaS.
   - #2 (mo 6–12): Drone/camera edge analytics (agri inspection, smart-city, security) on SIA-edge — matches the "SIA everywhere" vision, but needs hardware + pilots → slower.
   - #3: Govt/PSU document processing (Hindi/regional) — tender-friendly but long sales cycles.
   - #4: Inference API for Indian-language models.
2. **This quarter:** build app #1 MVP on top of SIA-pro (fine-tune in parallel); sign 1 anchor enterprise; bill via UPI/invoice. Report revenue weekly.
3. **Month 6+:** second app from the same model family (near-zero new model cost). Scale with data residency + vernacular as the wedge.
4. **All entities Indian:** SIA AI Pvt Ltd (models) + Mandal Devices (hardware) + Akasha Runtime (agents) under Saurabh Mandal Holdings.

---

## EXECUTION ORDER (money-first, cheapest first)

| Phase | Window | Focus |
|-------|--------|-------|
| 0 | weeks 1–4 | IndiaAI compute credits + grants; finish SIA core; app #1 POC to 5 customers |
| 1 | mo 2–6 | App #1 live + first revenue; SIA-pro LoRA fine-tune; edge quantisation |
| 2 | mo 6–12 | App #2 (drone/camera); SIA-edge on hardware; RISC-V SoC design start; FPGA demo |
| 3 | yr 2 | Tape-out edge ASIC (28nm, DLI subsidy); colocation; SIA-lite family |
| 4 | yr 3–5 | Own DC near green power; optical R&D; Bharat Small Reactor application; export to Global South |

---

## COST TABLE (indicative ₹)

| Item | Cost | When |
|------|------|------|
| IndiaAI public/discounted compute | Verify current portal terms | now, subject to allocation |
| SIA-pro LoRA fine-tune | Estimate from verified route and actual workload | mo 3 |
| SIA-edge quantise + deploy | ₹2–5L (devkits) | mo 6–12 |
| Edge ASIC design + FPGA | ₹40–80L (DLI covers ~50%) | yr 2 |
| 28nm tape-out with Tata | ₹15–30 Cr (shared w/ partners) | yr 2–3 |
| Colocation racks | ₹3–6L/mo per rack | yr 2 |
| Own DC | ₹50–150 Cr | yr 4+ (revenue-funded) |

---

## FIRST 7 DAYS

1. Prepare and verify an IndiaAI/C-DAC/incubator compute application using the registration PoC’s workload planner; confirm current eligibility and allocation rules.
2. Review Bihar Startup Policy, SISFS, TIDE 2.0, NIDHI-linked, and later-stage accelerator routes; classify each as grant, loan, equity, incubator support, or in-kind compute and track current calls.
3. Ship SIA transformer core smoke test (on track).
4. List 20 candidate app #1 customers; call 5.
5. Draft intro emails: Tata Electronics innovation team + InCore.
6. Read PFBR / Bharat Small Reactor private-participation policy (energy roadmap file).
7. Update this file weekly; report skipped items explicitly.
