#!/usr/bin/env python3
"""Build SFT chat dataset for SIA companion LoRA fine-tune.

Reads data/assistant_corpus.txt (<|user|>...<|assistant|>... blocks) and
emits a sharegpt-style JSONL (messages: system/user/assistant) that TRL's
SFTTrainer consumes directly with response-only masking.

Usage:
    .venv/bin/python finetune/build_sft_dataset.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "assistant_corpus.txt"
OUT = ROOT / "finetune" / "sia_chat_train.jsonl"
SYSTEM = (
    "You are SIA, a private on-device AI companion built in India. "
    "You work offline, you protect the user's privacy, and you answer in "
    "Hindi or English as the user prefers. Be concise and helpful."
)

BLOCK_RE = re.compile(r"<\|user\|>(.*?)<\|assistant\|>(.*?)(?=<\|user\|>|\Z)", re.S)


def main() -> None:
    text = SRC.read_text(encoding="utf-8", errors="ignore")
    out = OUT.parent
    out.mkdir(parents=True, exist_ok=True)

    n = 0
    with OUT.open("w", encoding="utf-8") as f:
        for m in BLOCK_RE.finditer(text):
            user = m.group(1).strip()
            assistant = m.group(2).strip()
            if not user or not assistant:
                continue
            rec = {
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": user},
                    {"role": "assistant", "content": assistant},
                ]
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            n += 1

    print(f"Wrote {n} conversations -> {OUT}")


if __name__ == "__main__":
    main()
