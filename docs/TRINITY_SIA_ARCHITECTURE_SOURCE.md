# TRINITY — SIA Architecture Source (from Founder Design Notes, Aug 2026)

> Source of truth for the investor report's product/architecture chapters.
> Five handwritten design pages digitized: Applications, Model Tiers, Hardware
> Roadmap, Chip Landscape, Energy Context. Kept verbatim-faithful.

---

## 1. Applications (Pillar 1 — what SIA ships)

| Module | Role |
|--------|------|
| **SIA Edge** | Local on-device AI model (the delivery vehicle) |
| **SIA Core** | Central orchestration and synchronization |
| **SIA Cloud** | Advanced reasoning when local isn't enough (fallback, cloud tier) |
| **SIA Studio / SDK** | For developers: embed SIA into apps and IoT products |
| **SIA Memory** | Consistent, personalized experience across devices |
| **SIA Vision** | Multimodal perception and recognition + synthesis |
| **SIA Voice** | Speech recognition + synthesis |
| **SIA Agent** | Autonomous task execution |

## 2. Model — "SIA: An AI Operating System"

Hardware-tiered model family, **shared everything**:

| Tier | Size | Target |
|------|------|--------|
| **SIA Nano** | 0.5B – 1B | Wearables, IoT, microcontrollers |
| **SIA Edge** | 2B – 4B | Phones, PCs, laptops |
| **SIA Pro** | 8B – 14B | Workstations, local GPUs |
| **SIA Cloud** | 70B+ | Data centers, advanced reasoning |

**All of them share:**
- The same tokenizer
- The same architecture
- The same tool-calling interface
- The same memory formats (compatible memory across tiers)
- A common runtime that synchronizes knowledge

→ This is the "family of models, not one giant model" thesis made concrete.

## 3. Infrastructure — Compute roadmap (Pillar 1/3)

| Horizon | Action |
|---------|--------|
| Years 1–2 | **Rent GPU** (Yotta, E2E, or international) — focus on model development |
| Years 2–4 | **Build software infrastructure** — distributed training, inference platform, MLOps, data pipelines |
| Years 4–6 | **Small private GPU cluster** (~100–500 GPUs) for predictable workloads |
| Years 6–10 | **Hyperscale AI campus** — thousands of GPUs, high-speed networking, dedicated substations, liquid cooling, peta-scale storage |

## 4. Chips — Compute landscape (founder's knowledge base)

| Chip | Role |
|------|------|
| **CPU** | Computing brain; low latency; best for OS; 4–128 cores |
| **GPU** | Main AI training processor today; thousands of small cores, parallel identical ops; best for training + running AI |
| **TPU** | Google-designed for AI; very high throughput, tensor-optimized; best for training AI |
| **NPU** | Runs AI locally without CPU; phones, laptops, robots, cars, IoT; best for local LLM, face check, speech |
| **Optical / Photonic** | Massive speed, huge bandwidth, very low latency; best for LLMs in data centers; future AI growth |

## 5. Compute — Energy alignment (nuclear path)

India's 3-stage nuclear program (context to the energy thesis):
- Stage 1: Pressurised Heavy Water Reactor (PHWR) — natural uranium
- Stage 2: Fast Breeder Reactors (e.g. PFBR) — plutonium + breeding
- Stage 3: Advanced reactors using Uranium-233 bred from thorium
- **GOAL: 100 GW** (Nuclear Mission, PFBR first criticality 6 Apr 2026)

---

## How this maps to TRINITY's five pillars
1. **Compute** ← §3 infra roadmap + §4 chip choices + §5 energy math
2. **Data** → SIA Memory (cross-device, personalized, compatible formats)
3. **Models** → §2 model family (Nano → Cloud), shared stack
4. **Agents/OS** → SIA Agent + SIA Studio/SDK + common runtime
5. **Applications** → §1 apps (health, edu, agri, industry via embedded SDK)

## Open decisions
- [ ] Confirm "SIA Cloud" is a planned tier vs rented (Year 1–2 rent-first says rented)
- [ ] 70B+ cloud tier training plan (₹₹₹ — grant/partner funded?)
- [ ] Photonic chip positioning: thesis only, or an actual R&D line?