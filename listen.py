"""SIA listen.py — the audio→language loop. SIA hears a WAV, says what it heard, answers.

Reuses the trained nano model: DSP 'listening' (modalities.analyze_audio) feeds a
text prompt into the transformer, SIA replies about what it heard, and optionally
speaks its reply back (audio diffusion head → Griffin-Lim).

Usage:
    .venv/bin/python listen.py --audio outputs/demo_music_input.wav
    .venv/bin/python listen.py --audio any.wav --reply-wav outputs/sia_reply.wav
"""
import argparse
import os
from pathlib import Path

import numpy as np
import torch

from sia import SIA, SIAConfig
from tokenizer import SIATokenizer
import modalities as M
from generate import load_model

PROMPT_TEMPLATE = (
    "You are SIA, a private on-device AI companion. You just listened to an audio "
    "recording. Here is what your audio analysis detected: duration {dur}s, dominant "
    "frequency {hz} Hz (musical note {note}), {onsets} onsets, tempo about {bpm} BPM. "
    "Describe in two short sentences what kind of sound this is and what it might mean."
)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--audio", required=True, help="input WAV to listen to")
    p.add_argument("--checkpoint", default="checkpoints/sia_nano_demo/sia.pt")
    p.add_argument("--tokenizer", default="tokenizer/tokenizer.json")
    p.add_argument("--max_new", type=int, default=80)
    p.add_argument("--reply-wav", default="", help="if set, generate a spoken-style reply WAV")
    p.add_argument("--seed", type=int, default=7)
    args = p.parse_args()

    torch.manual_seed(args.seed)

    samples, sr = M.read_wav(args.audio)
    info = M.analyze_audio(samples, sr=sr)
    print(f"[SIA hears] {args.audio}: {info}")

    tok = SIATokenizer(args.tokenizer)
    cfg = SIAConfig.nano()
    cfg.vocab_size = tok.vocab_size
    cfg.eos_id = tok.eos_id
    model = load_model(args.checkpoint, cfg)
    model.eval()

    prompt = PROMPT_TEMPLATE.format(
        dur=info["duration_s"], hz=info["dominant_hz"], note=info["note"],
        onsets=info["onsets"], bpm=info["tempo_bpm"],
    )
    ids = tok.encode(prompt)
    out = model.generate_text(torch.tensor([ids]), max_new=args.max_new, temp=0.7, top_k=40)
    new_ids = out[0].tolist()[len(ids):]  # only newly generated tokens, not the echoed prompt
    reply = tok.decode(new_ids).strip() or "(model produced no new tokens)"
    print(f"[SIA says] {reply}")

    os.makedirs("outputs", exist_ok=True)
    Path("outputs/listen_transcript.txt").write_text(
        f"AUDIO: {args.audio}\nANALYSIS: {info}\n\nPROMPT: {prompt}\n\nSIA: {reply}\n", encoding="utf-8"
    )
    print("saved outputs/listen_transcript.txt")

    if args.reply_wav:
        # SIA 'speaks': diffusion head conditioned on its own reply → mel → WAV
        hidden = model.forward(torch.tensor([ids]))
        mel = model.generate_audio(hidden, steps=20, n_mels=64, frames=64)
        wav = M.griffin_lim(mel[0, 0].numpy(), n_mels=64)
        M.write_wav(args.reply_wav, wav, sr=16000)
        print(f"saved {args.reply_wav} (reply 'spoken' via audio diffusion head)")


if __name__ == "__main__":
    main()
