"""SIA framework demo gauntlet — runs every capability and writes outputs/."""
import os
import sys
import time
from pathlib import Path

import numpy as np
import torch
from PIL import Image

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from sia import SIA, SIAConfig, count_params
from tokenizer import SIATokenizer
import modalities as M
import tools as T


def banner(t):
    print("\n" + "=" * 70)
    print(" " + t)
    print("=" * 70)


def main():
    os.makedirs(ROOT / "outputs", exist_ok=True)
    cfg = SIAConfig.nano()
    tok = SIATokenizer(str(ROOT / "tokenizer" / "tokenizer.json"))
    cfg.vocab_size = tok.vocab_size
    cfg.eos_id = tok.eos_id

    ckpt = ROOT / "checkpoints" / "sia_nano_demo" / "sia.pt"
    if ckpt.exists():
        model = SIA(cfg)
        model.load_state_dict(torch.load(ckpt, map_location="cpu"))
        print(f"Loaded trained checkpoint {ckpt}")
    else:
        model = SIA(cfg)
        print("No checkpoint yet — using randomly-initialized weights (framework checks only)")
    model.eval()
    print(f"params: {count_params(model):,}")

    # 1. TEXT
    banner("1) TEXT — generation")
    prompt = "To be, or not to be"
    ids = tok.encode(prompt)
    out = model.generate_text(torch.tensor([ids]), max_new=60, temp=0.8, top_k=50)
    txt = tok.decode(out[0].tolist())
    print(txt)
    (ROOT / "outputs" / "demo_text.txt").write_text(txt)

    # 2. CODE
    banner("2) CODE — codegen")
    cprompt = "<|code|>Write a Python fibonacci function.\ndef fibonacci(n):"
    ids = tok.encode(cprompt)
    out = model.generate_text(torch.tensor([ids]), max_new=60, temp=0.7, top_k=40)
    ctxt = tok.decode(out[0].tolist())
    print(ctxt)
    (ROOT / "outputs" / "demo_code.py.txt").write_text(ctxt)

    # 3. VISION
    banner("3) VISION — encode a synthetic image")
    img = Image.new("RGB", (336, 336), (120, 200, 90))
    for i in range(0, 336, 28):
        for j in range(0, 336, 28):
            if (i + j) % 56 == 0:
                for di in range(10):
                    for dj in range(10):
                        if i + di < 336 and j + dj < 336:
                            img.putpixel((j + dj, i + di), (220, 80, 40))
    arr = np.array(img).astype(np.float32) / 255.0
    t_img = torch.from_numpy(arr).permute(2, 0, 1).unsqueeze(0)
    h = model.forward(torch.tensor([[tok.bos_id]]), images=t_img)
    print(f"image (1,3,336,336) -> vision tokens -> hidden {tuple(h.shape)}")
    img.save(ROOT / "outputs" / "demo_input_image.png")

    # 4. AUDIO — listen
    banner("4) AUDIO — listen & understand a WAV")
    music = M.synthesize_music(2.0, (261.63, 329.63, 392.00))
    M.write_wav(ROOT / "outputs" / "demo_music_input.wav", music)
    info = M.analyze_audio(music)
    print(f"SIA heard: {info}")
    mel = M.to_mel_tensor(music, target_frames=128)
    h = model.forward(torch.tensor([[tok.bos_id]]), audio=mel)
    print(f"mel (1,1,64,128) -> audio tokens -> hidden {tuple(h.shape)}")

    # 5. AUDIO GEN
    banner("5) AUDIO — generate WAV from text prompt")
    ids = tok.encode("a soft chord")
    hidden = model.forward(torch.tensor([ids]))
    mel_gen = model.generate_audio(hidden, steps=20, n_mels=64, frames=64)
    wav = M.griffin_lim(mel_gen[0, 0].numpy(), n_mels=64)
    M.write_wav(ROOT / "outputs" / "demo_gen_audio.wav", wav)
    print("saved outputs/demo_gen_audio.wav")

    # 6. IMAGE GEN
    banner("6) IMAGE — latent generation")
    ids = tok.encode("a green field at sunrise")
    hidden = model.forward(torch.tensor([ids]))
    lat = model.generate_image(hidden, steps=15)
    preview = lat[0, :3].permute(1, 2, 0)
    preview = (preview - preview.min()) / (preview.max() - preview.min() + 1e-6)
    Image.fromarray((preview.numpy() * 255).astype(np.uint8)).resize((256, 256), Image.NEAREST).save(ROOT / "outputs" / "demo_gen_image.png")
    print("saved outputs/demo_gen_image.png (latent preview; VAE not in core)")

    # 7. VIDEO
    banner("7) VIDEO — frame-wise latent animation")
    frames = []
    for i in range(8):
        lat = model.generate_image(hidden, steps=8)
        fr = lat[0, :3].permute(1, 2, 0)
        fr = (fr - fr.min()) / (fr.max() - fr.min() + 1e-6)
        frames.append(Image.fromarray((fr.numpy() * 255).astype(np.uint8)).resize((128, 128), Image.NEAREST))
    frames[0].save(ROOT / "outputs" / "demo_gen_video.gif", save_all=True, append_images=frames[1:], duration=150, loop=0)
    print("saved outputs/demo_gen_video.gif")

    # 8. TOOLS
    banner("8) TOOLS — agent tool-calling loop")
    prompt_t = "Use the calc tool: [[tool:calc(17*23)]] then tell me the result."
    res = T.run_agent(model, tok, prompt_t, max_rounds=2, max_new=40)
    for kind, line in res["log"]:
        print(f"[{kind}] {line}")
    print("answer:", res["answer"][:200])

    # 9. QUANTIZE
    banner("9) QUANTIZE — int8 dynamic quantization on CPU")
    try:
        # Break weight-tying first (quantize_dynamic cannot share weights)
        model.text_head.weight = torch.nn.Parameter(model.text_head.weight.detach().clone())
        qmodel = torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)
        t0 = time.time()
        qout = qmodel.generate_text(torch.tensor([ids]), max_new=20, temp=0.8, top_k=50)
        qt = time.time() - t0
        t0 = time.time()
        model.generate_text(torch.tensor([ids]), max_new=20, temp=0.8, top_k=50)
        ft = time.time() - t0
        print(f"int8 dyn quant: {qt:.2f}s vs fp32 {ft:.2f}s for 20 tokens")
        print("quantized sample:", tok.decode(qout[0].tolist())[:120])
        print("PASS")
    except Exception as e:
        print(f"quantize skipped: {e}")

    print("\nALL DEMOS DONE. outputs/ holds artifacts.")


if __name__ == "__main__":
    main()
