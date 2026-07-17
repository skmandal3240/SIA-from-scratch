"""
SIA Tokenizer — unified tokenizer for text, code, and multimodal tokens.
"""
import os
import json
from typing import List, Dict, Optional

from tokenizers import Tokenizer, models, trainers, pre_tokenizers, decoders, processors
from tokenizers.implementations import ByteLevelBPETokenizer


SPECIAL_TOKENS = {
    # Standard
    "<|pad|>": 0,
    "<|eos|>": 1,
    "<|bos|>": 2,
    "<|unk|>": 3,
    # Chat
    "<|system|>": 4,
    "<|user|>": 5,
    "<|assistant|>": 6,
    # Multimodal
    "<|image|>": 7,
    "<|audio|>": 8,
    "<|video|>": 9,
    "<|code|>": 10,
    "<|tool_call|>": 11,
    "<|tool_result|>": 12,
    "<|agent|>": 13,
    "<|agent_end|>": 14,
    # Vision patches (dynamic)
    "<|patch_start|>": 15,
    "<|patch_end|>": 16,
}


class SIATokenizer:
    def __init__(self, vocab_size: int = 128256):
        self.vocab_size = vocab_size
        self.tok = ByteLevelBPETokenizer()
        self.special_tokens = SPECIAL_TOKENS

    def train(self, files: List[str], vocab_size: int = 128256, special_tokens: Optional[Dict] = None):
        vocab_size = vocab_size or self.vocab_size
        special = special_tokens or SPECIAL_TOKENS

        self.tok.train(
            files=files,
            vocab_size=vocab_size,
            min_frequency=2,
            special_tokens=list(special.keys()),
            show_progress=True,
        )

        # Save
        self.tok.save_model("tokenizer")

    def save(self, path: str):
        self.tok.save_model(path)

    @classmethod
    def load(cls, path: str):
        tok = cls()
        tok.tok = ByteLevelBPETokenizer.from_file(
            os.path.join(path, "vocab.json"),
            os.path.join(path, "merges.txt"),
        )
        return tok

    def encode(self, text: str):
        return self.tok.encode(text)

    def decode(self, ids: List[int]) -> str:
        return self.tok.decode(ids)

    def __len__(self):
        return self.tok.get_vocab_size()


def build_tokenizer(data_dir: str, out_dir: str, vocab_size: int = 128256):
    """Build tokenizer from text files in data_dir"""
    files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith(".txt")]
    if not files:
        raise ValueError(f"No .txt files found in {data_dir}")

    tok = SIATokenizer(vocab_size)
    tok.train(files, vocab_size)
    tok.save(out_dir)

    # Save as HuggingFace format too
    hf_tok = Tokenizer(models.BPE())
    hf_tok.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)
    hf_tok.decoder = decoders.ByteLevel()
    hf_tok.post_processor = processors.TemplateProcessing(
        single="<|bos|> $A <|eos|>",
        pair="<|bos|> $A <|eos|> $B <|eos|>",
        special_tokens=[(k, v) for k, v in SPECIAL_TOKENS.items()],
    )
    hf_tok.save(os.path.join(out_dir, "tokenizer.json"))

    print(f"Tokenizer saved to {out_dir}")
    return tok


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python tokenizer.py <data_dir> <out_dir> [vocab_size]")
        sys.exit(1)
    data_dir = sys.argv[1]
    out_dir = sys.argv[2]
    vocab_size = int(sys.argv[3]) if len(sys.argv) > 3 else 128256
    build_tokenizer(data_dir, out_dir, vocab_size)