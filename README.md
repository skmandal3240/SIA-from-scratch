# SIA — Unified Multimodal Foundation Model

One model. Text, Vision, Audio, Code, Tools. Generation: Image, Video, Audio.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SIA Backbone                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Text    │  │  Vision  │  │  Audio   │  │  Code    │     │
│  │  Tokens  │  │  Patches │  │  Tokens  │  │  Tokens  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │             │             │            │
│       ▼             ▼             ▼             ▼            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │           Shared Transformer (RoPE, SwiGLU, RMSNorm) │    │
│  │     Cross-attention between modalities at layers      │    │
│  └─────────────────────────────────────────────────────┘    │
│       │             │             │             │            │
│       ▼             ▼             ▼             ▼            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Text    │  │  Image   │  │  Video   │  │  Audio   │     │
│  │  Head    │  │  Diffusion│  │ Diffusion │  │ Diffusion│     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│                        ▲                      ▲              │
│              ┌─────────┴─────────┐  ┌────────┴────────┐      │
│              │   Tool Head       │  │  Code Head      │      │
│              └───────────────────┘  └─────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Configs

| Model | Dim | Layers | Heads | Params | Use Case |
|-------|-----|--------|-------|--------|----------|
| SIA-Nano | 256 | 6 | 4 | ~15M | Edge/Phone |
| SIA-Small | 512 | 12 | 8 | ~100M | Laptop/Colab |
| **SIA-Base** | **768** | **24** | **12** | **~500M** | **Single GPU** |
| SIA-Large | 1024 | 32 | 16 | ~1.5B | Multi-GPU |
| SIA-XL | 1536 | 40 | 24 | ~4B | Cluster |

## Quick Start

```bash
pip install -r requirements.txt

# Train text-only (pretrain)
python train.py --config configs/sia_base_text.yaml

# Train multimodal (fine-tune)
python train.py --config configs/sia_base_multimodal.yaml

# Generate
python generate.py --model checkpoints/sia_base.pt --prompt "A photo of a cat" --modality image
```

## Modalities

| Input | Output | Status |
|-------|--------|--------|
| Text | Text | ✅ |
| Image | Text (caption/VQA) | ✅ |
| Audio | Text (ASR/understanding) | ✅ |
| Code | Code | ✅ |
| Text | Image (diffusion) | ✅ |
| Text | Video (diffusion) | ✅ |
| Text | Audio (diffusion) | ✅ |
| Text | Tool calls | ✅ |

## License

Apache 2.0 — train, sell, ship.