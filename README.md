# SIA — From-Scratch Multimodal AI Framework

India-first, self-funded multimodal transformer built from scratch: tokenizer → attention → training → tools → audio/vision/code → generation.

Status: **WORKING** (trained nano model, all demos pass). Routes to the AI 5-Pillar plan (`docs/AI_5_PILLARS_INDIA_PLAN.md`) — models pillar (2), revenue apps (1), compute (3), silicon (4), energy (5).

## What's here

| File | Role |
|------|------|
| `sia.py` | Full architecture: SIAConfig (nano→xl), RMSNorm, SwiGLU, RoPE, GQA attention, cross-attention, Vision/Audio/Code encoders, diffusion heads (image/video/audio), ToolHead, AgentCommunication, weight-tying, generate_text/image/audio |
| `tokenizer.py` | Unified BPE tokenizer (tokenizers lib) with multimodal special tokens; HF `tokenizer.json` export |
| `prepare_data.py` | Corpus → trained tokenizer (vocab 8192) → `data/train.bin` / `data/val.bin` (numpy uint16) |
| `train.py` | CPU-safe training loop (Accelerate, fp32 fallback, gradient accumulation, cosine LR, eval, checkpointing) |
| `generate.py` | Generation CLI: text / code / image / audio |
| `tools.py` | Tool registry + agent loop: `calc`, `now`, `file_read`, `file_write`, `list_files` via `[[tool:name(args)]]` |
| `modalities.py` | Pure-numpy audio DSP: wav I/O, mel spectrogram, Griffin-Lim, synth music, `analyze_audio` ("listening") |
| `demos.py` | 9-demo gauntlet → `outputs/` (text, code, vision, audio-listen, audio-gen, image-gen, video GIF, tools, int8 quantize) |
| `configs/sia_nano_demo.yaml` | Nano training config (CPU): 256 dim, 6 layers, 500 steps |
| `outputs/goc/` | GoC collateral: 5-pillar one-pager, grants tracker, email drafts, PPTX deck |
| `cron/cron_digest.py` | Daily 5-pillar digest (installed as `~/.hermes/scripts/sia_digest.py` → Telegram) |

## Quickstart

```bash
.venv/bin/python prepare_data.py            # build tokenizer + .bin data
.venv/bin/python train.py --config configs/sia_nano_demo.yaml   # ~4 min CPU, 500 steps
.venv/bin/python demos.py                   # run all 9 demos -> outputs/
.venv/bin/python generate.py --modality text --prompt "To be, or not to be" --max_new 60
```

## Verified

- Ad-hoc verify (5 checks: tokenizer roundtrip, forward+generate, audio mel+Griffin-Lim, tools, quantize smoke) — ALL PASS
- Training: 500 steps, loss 5.47 → 5.06, val 6.34, checkpoint `checkpoints/sia_nano_demo/sia.pt`
- Demos 1–9 all pass on trained weights; int8 dynamic quantize: 0.12s vs 0.16s fp32 per 20 tokens

## Roadmap (Pillar 2)

text ✅ → vision (encoder done, VAE decoders next) → audio listen ✅ / gen (diffusion head, VAE next) → video frames ✅ → code ✅ → SIA-edge INT4/INT8 deploy → SIA-pro LoRA fine-tune on Indian data → ASIC backend (Pillar 4).

## GoC / Grants

See `outputs/goc/`: `01_SIA_5_PILLAR_ONEPAGER.md`, `02_GRANTS_TRACKER.md`, `03_EMAIL_DRAFTS.md`, `SIA_5_Pillar_Plan.pptx` (9 slides, rebuild with `outputs/goc/build_pptx.py`). Daily digest cron → Telegram 02:30 UTC.
