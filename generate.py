"""SIA Generation / Inference CLI — text, code, image, audio, video."""
import argparse
import os
from pathlib import Path

import numpy as np
import torch
from PIL import Image

from sia import SIA, SIAConfig, count_params
from tokenizer import SIATokenizer
from modalities import griffin_lim, read_wav, save_mel_wav, to_mel_tensor


def load_model(ckpt_path: str, config: SIAConfig) -> SIA:
    model = SIA(config)
    state = torch.load(ckpt_path, map_location="cpu")
    model.load_state_dict(state.get("model", state))
    model.eval()
    return model


def load_image(path: str, size: int = 336) -> torch.Tensor:
    img = Image.open(path).convert("RGB").resize((size, size), Image.LANCZOS)
    arr = np.array(img).astype(np.float32) / 255.0
    return torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint", required=True)
    p.add_argument("--config", default="nano", choices=["nano", "small", "base", "large", "xl"])
    p.add_argument("--tokenizer", default="tokenizer/tokenizer.json")
    p.add_argument("--prompt", default="")
    p.add_argument("--image", help="input image path (vision)")
    p.add_argument("--audio", help="input audio path (listening)")
    p.add_argument("--modality", choices=["text", "code", "image", "audio", "video"], default="text")
    p.add_argument("--max_new", type=int, default=128)
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--top_k", type=int, default=50)
    p.add_argument("--seed", type=int, default=1337)
    p.add_argument("--out", default="outputs")
    args = p.parse_args()

    torch.manual_seed(args.seed)
    os.makedirs(args.out, exist_ok=True)

    cfg = getattr(SIAConfig, args.config)()
    tok = SIATokenizer(args.tokenizer)
    cfg.vocab_size = tok.vocab_size
    cfg.eos_id = tok.eos_id
    print(f"Tokenizer vocab {tok.vocab_size}")

    model = load_model(args.checkpoint, cfg)
    print(f"Model params: {count_params(model):,}")

    if args.modality in ("text", "code"):
        prompt = args.prompt or ("Write a Python function that returns the nth Fibonacci number.\n\n```python\ndef fibonacci(n):"
                                 if args.modality == "code" else "Hello, I am SIA.")
        ids = tok.encode(prompt)
        input_ids = torch.tensor([ids], dtype=torch.long)
        out = model.generate_text(input_ids, max_new=args.max_new, temp=args.temperature, top_k=args.top_k)
        text = tok.decode(out[0].tolist())
        print(f"\n--- {args.modality.upper()} ---\n{text}")
        Path(args.out, f"gen_{args.modality}.txt").write_text(text, encoding="utf-8")
        print(f"saved outputs/gen_{args.modality}.txt")

    elif args.modality == "image":
        ids = tok.encode(args.prompt or "a green field")
        input_ids = torch.tensor([ids], dtype=torch.long)
        hidden = model.forward(input_ids)
        latents = model.generate_image(hidden, steps=20)
        np.save(Path(args.out, "gen_image_latents.npy"), latents.cpu().numpy())
        # No VAE in the from-scratch core: export a normalized latent preview PNG.
        preview = latents[0, :3].permute(1, 2, 0)
        preview = (preview - preview.min()) / (preview.max() - preview.min() + 1e-6)
        Image.fromarray((preview.numpy() * 255).astype(np.uint8)).resize((256, 256), Image.NEAREST).save(Path(args.out, "gen_image_preview.png"))
        print("image latents -> outputs/gen_image_latents.npy + preview PNG (VAE decode not in core)")

    elif args.modality == "audio":
        ids = tok.encode(args.prompt or "a soft chord")
        input_ids = torch.tensor([ids], dtype=torch.long)
        hidden = model.forward(input_ids)
        mel = model.generate_audio(hidden, steps=20, n_mels=64, frames=64)
        wav = griffin_lim(mel[0, 0].numpy(), n_mels=64)
        save_mel_wav(Path(args.out, "gen_audio.wav"), wav, sr=16000)
        print("audio mel -> outputs/gen_audio.wav (Griffin-Lim decode)")

    elif args.modality == "video":
        ids = tok.encode(args.prompt or "a field at sunrise")
        input_ids = torch.tensor([ids], dtype=torch.long)
        hidden = model.forward(input_ids)
        frames = []
        for i in range(12):
            lat = model.generate_image(hidden, steps=10)
            fr = lat[0, :3].permute(1, 2, 0)
            fr = (fr - fr.min()) / (fr.max() - fr.min() + 1e-6)
            frames.append(Image.fromarray((fr.numpy() * 255).astype(np.uint8)).resize((128, 128), Image.NEAREST))
        frames[0].save(Path(args.out, "gen_video.gif"), save_all=True, append_images=frames[1:], duration=150, loop=0)
        print("video frames -> outputs/gen_video.gif (frame-wise latent animation)")

    if args.image:
        img = load_image(args.image, cfg.img_size)
        h = model.forward(torch.tensor([[tok.bos_id]]), images=img)
        print(f"vision encode: input {tuple(img.shape)} -> hidden {tuple(h.shape)}")

    if args.audio:
        samples, sr = read_wav(args.audio)
        mel = to_mel_tensor(samples, sr=sr)
        h = model.forward(torch.tensor([[tok.bos_id]]), audio=mel)
        print(f"audio encode: {len(samples)} samples @{sr} -> hidden {tuple(h.shape)}")


if __name__ == "__main__":
    main()
