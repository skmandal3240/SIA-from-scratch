"""Build SIA training corpus + tokenizer + .bin token files from available text sources."""
from pathlib import Path

import numpy as np

from tokenizer import build_tokenizer, SIATokenizer

ROOT = Path(__file__).parent
CORPUS = ROOT / "data" / "corpus.txt"
TOK_PATH = ROOT / "tokenizer" / "tokenizer.json"
TRAIN_BIN = ROOT / "data" / "train.bin"
VAL_BIN = ROOT / "data" / "val.bin"
VOCAB = 8192
VAL_FRAC = 0.05


def gather_corpus() -> str:
    parts = []
    sh = ROOT / "data" / "shakespeare.txt"
    if sh.exists():
        parts.append(sh.read_text(encoding="utf-8", errors="ignore"))
    # Code + docs teach the model codegen structure
    for p in sorted(ROOT.glob("*.py")) + sorted(ROOT.glob("*.md")) + sorted(ROOT.glob("*.yaml")):
        if p.name == "corpus.txt":
            continue
        parts.append(p.read_text(encoding="utf-8", errors="ignore"))
    for p in sorted((ROOT / "docs").glob("*.md")):
        parts.append(p.read_text(encoding="utf-8", errors="ignore"))
    return "\n\n".join(parts)


def main():
    corpus = gather_corpus()
    CORPUS.parent.mkdir(exist_ok=True)
    CORPUS.write_text(corpus, encoding="utf-8")
    print(f"corpus: {len(corpus):,} chars")

    if not TOK_PATH.exists():
        build_tokenizer(str(CORPUS), str(TOK_PATH), VOCAB)
    tok = SIATokenizer(str(TOK_PATH))

    ids = [i for i in tok.encode(corpus) if i < 65536]
    arr = np.array(ids, dtype=np.uint16)
    n_val = max(1, int(len(arr) * VAL_FRAC))
    arr[:-n_val].tofile(TRAIN_BIN)
    arr[-n_val:].tofile(VAL_BIN)
    print(f"tokens: {len(arr):,} -> train {len(arr)-n_val:,} val {n_val:,}")
    print(f"vocab: {tok.vocab_size} eos:{tok.eos_id} bos:{tok.bos_id}")


if __name__ == "__main__":
    main()
