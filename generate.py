"""
SIA Generation / Inference Script
"""
import argparse
import json
import os
from pathlib import Path

import torch
from PIL import Image
import torchaudio

from sia import SIA, SIAConfig, count_params
from tokenizer import SIATokenizer


def load_model(ckpt_path: str, config: SIAConfig, device: str = "cuda"):
    model = SIA(config).to(device)
    state = torch.load(ckpt_path, map_location=device)
    model.load_state_dict(state.get("model", state))
    model.eval()
    return model


def load_image(path: str, size: int = 336) -> torch.Tensor:
    img = Image.open(path).convert("RGB")
    img = img.resize((size, size), Image.LANCZOS)
    img = torch.from_numpy(np.array(img)).float() / 255.0
    img = img.permute(2, 0, 1).unsqueeze(0)  # (1, 3, H, W)
    return img


def load_audio(path: str, target_sr: int = 16000, target_len: int = 1024) -> torch.Tensor:
    waveform, sr = torchaudio.load(path)
    if sr != target_sr:
        waveform = torchaudio.transforms.Resample(sr, target_sr)(waveform)
    # Convert to mono
    if waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    # Mel spectrogram
    mel_transform = torchaudio.transforms.MelSpectrogram(
        sample_rate=target_sr,
        n_fft=400,
        hop_length=160,
        n_mels=128,
    )
    mel = mel_transform(waveform)  # (1, n_mels, time)
    # Pad/truncate
    if mel.shape[-1] > target_len:
        mel = mel[..., :target_len]
    else:
        mel = F.pad(mel, (0, target_len - mel.shape[-1]))
    return mel.unsqueeze(0)  # (1, 1, n_mels, time)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", required=True, help="Path to model checkpoint")
    parser.add_argument("--config", default="nano", help="Model config: nano, small, base, large, xl")
    parser.add_argument("--tokenizer", default="tokenizer/tokenizer.json")
    parser.add_argument("--prompt", default="", help="Text prompt")
    parser.add_argument("--image", help="Input image path (for multimodal)")
    parser.add_argument("--audio", help="Input audio path")
    parser.add_argument("--modality", choices=["text", "image", "video", "audio"], default="text")
    parser.add_argument("--max_new", type=int, default=512)
    parser.add_argument("--temperature", type=float, default=0.8)
    parser.add_argument("--top_k", type=int, default=50)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--seed", type=int, default=1337)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    device = args.device if torch.cuda.is_available() else "cpu"

    # Load config
    if args.config == "nano":
        config = SIAConfig.nano()
    elif args.config == "small":
        config = SIAConfig.small()
    elif args.config == "base":
        config = SIAConfig.base()
    elif args.config == "large":
        config = SIAConfig.large()
    elif args.config == "xl":
        config = SIAConfig.xl()
    else:
        raise ValueError(f"Unknown config: {args.config}")

    # Load model
    print(f"Loading model from {args.checkpoint}...")
    model = load_model(args.checkpoint, config, device)
    print(f"Model params: {count_params(model):,}")

    # Load tokenizer
    tokenizer = SIATokenizer(args.tokenizer)
    config.vocab_size = tokenizer.vocab_size

    # Prepare inputs
    input_ids = None
    if args.prompt:
        ids = tokenizer.encode(args.prompt)
        input_ids = torch.tensor([ids], device=device)

    images = None
    if args.image:
        images = load_image(args.image, config.img_size).to(device)

    audio = None
    if args.audio:
        audio = load_audio(args.audio).to(device)

    # Generate
    with torch.no_grad():
        if args.modality == "text":
            if input_ids is None:
                input_ids = torch.tensor([[tokenizer.tok.bos_token_id]], device=device)
            out = model.generate_text(input_ids, max_new=args.max_new, temp=args.temperature, top_k=args.top_k)
            text = tokenizer.decode(out[0].tolist())
            print(f"\n--- Generated Text ---\n{text}")

        elif args.modality == "image":
            if input_ids is None:
                input_ids = torch.tensor([[tokenizer.tok.bos_token_id]], device=device)
            # Encode text prompt
            prompt_embeds = model.forward(input_ids, images=images)
            latents = model.generate_image(prompt_embeds)
            print(f"Generated image latents: {latents.shape}")
            # Would need VAE decode here

        elif args.modality == "audio":
            if input_ids is None:
                input_ids = torch.tensor([[tokenizer.tok.bos_token_id]], device=device)
            prompt_embeds = model.forward(input_ids)
            mel = model.generate_audio(prompt_embeds)
            print(f"Generated audio mel: {mel.shape}")
            # Would need vocoder here

    print("\nDone!")


if __name__ == "__main__":
    import numpy as np
    import torch.nn.functional as F
    main()