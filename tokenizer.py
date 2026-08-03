"""
SIA Tokenizer — unified BPE tokenizer for text, code, and multimodal special tokens.
Single implementation shared by train.py, generate.py, tools.py, demos.py.
"""
import os
from typing import List, Optional

from tokenizers import Tokenizer, models, trainers, pre_tokenizers, decoders

SPECIAL_TOKENS = {
    "<|pad|>": 0,
    "<|eos|>": 1,
    "<|bos|>": 2,
    "<|unk|>": 3,
    "<|system|>": 4,
    "<|user|>": 5,
    "<|assistant|>": 6,
    "<|image|>": 7,
    "<|audio|>": 8,
    "<|video|>": 9,
    "<|code|>": 10,
    "<|tool_call|>": 11,
    "<|tool_result|>": 12,
    "<|agent|>": 13,
    "<|agent_end|>": 14,
    "<|patch_start|>": 15,
    "<|patch_end|>": 16,
}


class SIATokenizer:
    def __init__(self, path: Optional[str] = None):
        if path and os.path.exists(path):
            self.tok = Tokenizer.from_file(path)
        else:
            self.tok = Tokenizer(models.BPE())
            self.tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
            self.tok.decoder = decoders.ByteLevel()

    @property
    def vocab_size(self) -> int:
        return self.tok.get_vocab_size()

    @property
    def eos_id(self) -> int:
        return SPECIAL_TOKENS["<|eos|>"]

    @property
    def bos_id(self) -> int:
        return SPECIAL_TOKENS["<|bos|>"]

    @property
    def pad_id(self) -> int:
        return SPECIAL_TOKENS["<|pad|>"]

    def train(self, files: List[str], vocab_size: int = 8192):
        specials = list(SPECIAL_TOKENS.keys())
        trainer = trainers.BpeTrainer(vocab_size=vocab_size, min_frequency=2, special_tokens=specials)
        self.tok.train(files, trainer)

    def save(self, path: str):
        self.tok.save(path)

    def encode(self, text: str) -> List[int]:
        return self.tok.encode(text).ids

    def decode(self, ids: List[int]) -> str:
        return self.tok.decode(ids)


def build_tokenizer(corpus_file: str, out_path: str, vocab_size: int = 8192) -> SIATokenizer:
    """Train BPE on a corpus file and save a single-file tokenizer.json."""
    tok = SIATokenizer()
    tok.train([corpus_file], vocab_size=vocab_size)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    tok.save(out_path)
    print(f"Tokenizer saved: {out_path} (vocab {tok.vocab_size})")
    return tok


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python tokenizer.py <corpus.txt> <tokenizer.json> [vocab_size]")
        sys.exit(1)
    vocab_size = int(sys.argv[3]) if len(sys.argv) > 3 else 8192
    build_tokenizer(sys.argv[1], sys.argv[2], vocab_size)
