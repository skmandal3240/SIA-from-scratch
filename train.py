"""
SIA Training Pipeline — text, multimodal, and swarm training.
Supports: pretrain, SFT, DPO, multimodal fine-tune, swarm RL.
"""
import json
import os
import yaml
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any, List, Iterator

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, IterableDataset
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from torch.cuda.amp import GradScaler, autocast
from accelerate import Accelerator
from huggingface_hub import hf_hub_download

from sia import SIA, SIAConfig, count_params


# ============================================================
# Config
# ============================================================
@dataclass
class TrainConfig:
    # Model
    model_config: str = "nano"  # nano, small, base, large, xl
    custom_config: Optional[Dict] = None

    # Data
    train_data: str = ""  # path or hf dataset name
    val_data: str = ""
    tokenizer_path: str = ""
    max_seq_len: int = 2048
    batch_size: int = 8
    micro_batch_size: int = 1

    # Training
    lr: float = 3e-4
    min_lr: float = 3e-5
    weight_decay: float = 0.1
    beta1: float = 0.9
    beta2: float = 0.95
    grad_clip: float = 1.0
    warmup_steps: int = 1000
    max_steps: int = 100000
    save_every: int = 5000
    eval_every: int = 1000
    log_every: int = 10

    # Mixed precision
    dtype: str = "bf16"  # bf16, fp16, fp32

    # Multimodal
    use_vision: bool = False
    use_audio: bool = False
    image_size: int = 336
    audio_mel_bins: int = 128

    # Swarm
    swarm_agents: int = 1
    swarm_mode: bool = False

    # Output
    out_dir: str = "checkpoints"
    wandb_project: str = ""
    wandb_run: str = ""

    # Resume
    resume_from: str = ""

    def __post_init__(self):
        assert self.batch_size % self.micro_batch_size == 0
        self.grad_accum = self.batch_size // self.micro_batch_size

    @classmethod
    def from_yaml(cls, path: str) -> "TrainConfig":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            yaml.dump(asdict(self), f)


# ============================================================
# Tokenizer (wraps HF tokenizer)
# ============================================================
class SIATokenizer:
    def __init__(self, path: str = ""):
        if path and os.path.exists(path):
            from tokenizers import Tokenizer
            self.tok = Tokenizer.from_file(path)
        else:
            # Default: LLaMA-3 tokenizer
            from transformers import AutoTokenizer
            self.tok = AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")
            self.tok.pad_token = self.tok.eos_token

    @property
    def vocab_size(self) -> int:
        return self.tok.get_vocab_size() if hasattr(self.tok, "get_vocab_size") else len(self.tok.get_vocab())

    def encode(self, text: str) -> List[int]:
        return self.tok.encode(text).ids if hasattr(self.tok, "encode") else self.tok(text).input_ids

    def decode(self, ids: List[int]) -> str:
        return self.tok.decode(ids) if hasattr(self.tok, "decode") else self.tok.decode(ids)

    def save(self, path: str):
        if hasattr(self.tok, "save"):
            self.tok.save(path)


# ============================================================
# Datasets
# ============================================================
class TextDataset(IterableDataset):
    """Streaming text dataset from .bin files or HF datasets"""
    def __init__(self, path: str, seq_len: int, tokenizer: SIATokenizer, shuffle: bool = True):
        self.path = path
        self.seq_len = seq_len
        self.tokenizer = tokenizer
        self.shuffle = shuffle

    def __iter__(self) -> Iterator[Dict[str, torch.Tensor]]:
        if self.path.endswith(".bin"):
            # Memory-mapped binary tokens
            data = np.memmap(self.path, dtype=np.uint16, mode="r")
            tokens = torch.from_numpy(data.astype(np.int64))
        else:
            # HF dataset
            from datasets import load_dataset
            ds = load_dataset(self.path, split="train", streaming=True)
            if self.shuffle:
                ds = ds.shuffle(buffer_size=10000)
            tokens = []
            for ex in ds:
                tokens.extend(self.tokenizer.encode(ex["text"]))
                if len(tokens) > 1000000:
                    break
            tokens = torch.tensor(tokens, dtype=torch.long)

        n = len(tokens) - self.seq_len - 1
        indices = torch.randperm(n) if self.shuffle else torch.arange(n)
        for i in indices:
            x = tokens[i:i + self.seq_len]
            y = tokens[i + 1:i + 1 + self.seq_len]
            yield {"input_ids": x, "labels": y}


class MultimodalDataset(IterableDataset):
    """Image-text, audio-text pairs from JSONL or HF datasets"""
    def __init__(
        self,
        path: str,
        seq_len: int,
        tokenizer: SIATokenizer,
        image_size: int = 336,
        audio_mel_bins: int = 128,
        modality: str = "vision",  # vision, audio
    ):
        self.path = path
        self.seq_len = seq_len
        self.tokenizer = tokenizer
        self.image_size = image_size
        self.audio_mel_bins = audio_mel_bins
        self.modality = modality

    def __iter__(self) -> Iterator[Dict[str, torch.Tensor]]:
        import json
        from PIL import Image
        import torchaudio

        with open(self.path) as f:
            for line in f:
                ex = json.loads(line)
                text = ex.get("text", "")
                ids = self.tokenizer.encode(text)
                ids = ids[:self.seq_len] + [self.tokenizer.tok.pad_token_id] * max(0, self.seq_len - len(ids))
                input_ids = torch.tensor(ids[:-1], dtype=torch.long)
                labels = torch.tensor(ids[1:], dtype=torch.long)

                item = {"input_ids": input_ids, "labels": labels}

                if self.modality == "vision" and "image" in ex:
                    img = Image.open(ex["image"]).convert("RGB").resize((self.image_size, self.image_size))
                    img = torch.tensor(np.array(img)).permute(2, 0, 1).float() / 255.0
                    item["images"] = img

                if self.modality == "audio" and "audio" in ex:
                    waveform, sr = torchaudio.load(ex["audio"])
                    mel = torchaudio.transforms.MelSpectrogram(n_mels=self.audio_mel_bins)(waveform)
                    item["audio"] = mel

                yield item


# ============================================================
# Training Loop
# ============================================================
def train(config: TrainConfig):
    accelerator = Accelerator(
        mixed_precision=config.dtype if config.dtype != "fp32" else "no",
        gradient_accumulation_steps=config.grad_accum,
        log_with="wandb" if config.wandb_project else None,
        project_dir=config.out_dir,
    )

    if accelerator.is_main_process:
        os.makedirs(config.out_dir, exist_ok=True)
        config.to_yaml(f"{config.out_dir}/train_config.yaml")

    # Model
    if config.model_config in ["nano", "small", "base", "large", "xl"]:
        cfg_cls = getattr(SIAConfig, config.model_config)
        model_cfg = cfg_cls()
    else:
        model_cfg = SIAConfig(**config.custom_config)

    if config.custom_config:
        for k, v in config.custom_config.items():
            setattr(model_cfg, k, v)

    model_cfg.max_seq_len = config.max_seq_len
    model = SIA(model_cfg)
    accelerator.print(f"Model params: {count_params(model):,}")

    # Tokenizer
    tokenizer = SIATokenizer(config.tokenizer_path)
    if model_cfg.vocab_size != tokenizer.vocab_size:
        accelerator.print(f"Warning: model vocab {model_cfg.vocab_size} != tokenizer vocab {tokenizer.vocab_size}")

    # Data
    train_ds = TextDataset(config.train_data, config.max_seq_len, tokenizer) if not config.use_vision else \
        MultimodalDataset(config.train_data, config.max_seq_len, tokenizer, config.image_size, config.audio_mel_bins, "vision")
    val_ds = TextDataset(config.val_data, config.max_seq_len, tokenizer, shuffle=False) if config.val_data else None

    train_loader = DataLoader(train_ds, batch_size=config.micro_batch_size, num_workers=4)
    val_loader = DataLoader(val_ds, batch_size=config.micro_batch_size, num_workers=2) if val_ds else None

    # Optimizer
    optimizer = AdamW(
        model.parameters(),
        lr=config.lr,
        betas=(config.beta1, config.beta2),
        weight_decay=config.weight_decay,
        fused=True,
    )

    # Scheduler
    scheduler = CosineAnnealingLR(optimizer, T_max=config.max_steps, eta_min=config.min_lr)

    # Scaler
    scaler = GradScaler(enabled=config.dtype == "fp16")

    # Prepare
    model, optimizer, train_loader, scheduler = accelerator.prepare(
        model, optimizer, train_loader, scheduler
    )
    if val_loader:
        val_loader = accelerator.prepare(val_loader)

    # Resume
    step = 0
    if config.resume_from:
        accelerator.load_state(config.resume_from)
        step = int(config.resume_from.split("_")[-1].split(".")[0])

    # Wandb
    if accelerator.is_main_process and config.wandb_project:
        import wandb
        wandb.init(project=config.wandb_project, name=config.wandb_run, config=asdict(config))

    accelerator.print("Starting training...")
    model.train()

    for batch in train_loader:
        if step >= config.max_steps:
            break

        with accelerator.accumulate(model):
            with autocast(enabled=config.dtype != "fp32", dtype=getattr(torch, config.dtype)):
                input_ids = batch["input_ids"]
                labels = batch["labels"]
                images = batch.get("images")
                audio = batch.get("audio")

                # Forward
                logits = model(input_ids, images=images, audio=audio)
                loss = F.cross_entropy(logits.view(-1, logits.size(-1)), labels.view(-1))

            # Backward
            accelerator.backward(loss)

            if accelerator.sync_gradients:
                accelerator.clip_grad_norm_(model.parameters(), config.grad_clip)

            optimizer.step()
            scheduler.step()
            optimizer.zero_grad()

        # Logging
        if step % config.log_every == 0:
            lr = optimizer.param_groups[0]["lr"]
            accelerator.log({"train/loss": loss.item(), "train/lr": lr}, step=step)
            if accelerator.is_main_process:
                accelerator.print(f"Step {step}/{config.max_steps} | Loss: {loss.item():.4f} | LR: {lr:.2e}")

        # Eval
        if step % config.eval_every == 0 and step > 0 and val_loader:
            model.eval()
            val_losses = []
            with torch.no_grad():
                for i, batch in enumerate(val_loader):
                    if i >= 50:
                        break
                    with autocast(enabled=config.dtype != "fp32", dtype=getattr(torch, config.dtype)):
                        logits = model(batch["input_ids"], images=batch.get("images"), audio=batch.get("audio"))
                        loss = F.cross_entropy(logits.view(-1, logits.size(-1)), batch["labels"].view(-1))
                    val_losses.append(loss.item())
            val_loss = sum(val_losses) / len(val_losses)
            accelerator.log({"val/loss": val_loss}, step=step)
            if accelerator.is_main_process:
                accelerator.print(f"  >>> Val Loss: {val_loss:.4f}")
            model.train()

        # Save
        if step % config.save_every == 0 and step > 0:
            accelerator.save_state(f"{config.out_dir}/step_{step}")
            if accelerator.is_main_process:
                accelerator.print(f"Saved checkpoint: step_{step}")

        step += 1

    # Final save
    accelerator.save_state(f"{config.out_dir}/final")
    accelerator.print("Training complete.")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    args = parser.parse_args()

    config = TrainConfig.from_yaml(args.config)
    train(config)


if __name__ == "__main__":
    main()