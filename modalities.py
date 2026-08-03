"""Audio DSP in pure numpy: wav I/O, mel spectrogram, Griffin-Lim, synthesis.
No torchaudio dependency — the from-scratch core stays self-contained.
"""
import math
import wave

import numpy as np

SR = 16000
N_FFT = 512
HOP = 160
N_MELS = 64


def read_wav(path: str):
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        frames = w.readframes(w.getnframes())
        n_ch = w.getnchannels()
        sampwidth = w.getsampwidth()
    dtype = np.int16 if sampwidth == 2 else np.int32 if sampwidth == 4 else np.uint8
    x = np.frombuffer(frames, dtype=dtype).astype(np.float32)
    if n_ch > 1:
        x = x.reshape(-1, n_ch).mean(axis=1)
    if sampwidth == 2:
        x = x / 32768.0
    return x, sr


def write_wav(path, x: np.ndarray, sr: int = SR):
    x = np.clip(x, -1, 1)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


def _hz_to_mel(f):
    return 2595.0 * np.log10(1.0 + f / 700.0)


def _mel_to_hz(m):
    return 700.0 * (10.0 ** (m / 2595.0) - 1.0)


def mel_filterbank(n_fft: int = N_FFT, sr: int = SR, n_mels: int = N_MELS, fmin: float = 0.0, fmax: float = None):
    fmax = fmax or sr / 2
    bins = np.fft.rfftfreq(n_fft, 1 / sr)
    mels = np.linspace(_hz_to_mel(fmin), _hz_to_mel(fmax), n_mels + 2)
    hz = _mel_to_hz(mels)
    fbin = np.floor((n_fft + 1) * hz / sr).astype(int)
    fb = np.zeros((n_mels, len(bins)))
    for m in range(1, n_mels + 1):
        left, ctr, right = fbin[m - 1], fbin[m], fbin[m + 1]
        if ctr > left:
            fb[m - 1, left:ctr] = (np.arange(left, ctr) - left) / (ctr - left)
        if right > ctr:
            fb[m - 1, ctr:right] = (right - np.arange(ctr, right)) / (right - ctr)
    return fb


def mel_spectrogram(x: np.ndarray, sr: int = SR, n_fft: int = N_FFT, hop: int = HOP, n_mels: int = N_MELS):
    if len(x) < n_fft:
        x = np.pad(x, (0, n_fft - len(x)))
    pad = n_fft // 2
    xp = np.pad(x, (pad, pad), mode="reflect")
    n_frames = 1 + (len(xp) - n_fft) // hop
    win = np.hanning(n_fft)
    spec = np.empty((n_frames, n_fft // 2 + 1), dtype=np.float32)
    for i in range(n_frames):
        seg = xp[i * hop: i * hop + n_fft] * win
        spec[i] = np.abs(np.fft.rfft(seg))
    fb = mel_filterbank(n_fft, sr, n_mels)
    mel = spec @ fb.T
    return np.log1p(mel).astype(np.float32)


def griffin_lim(mel: np.ndarray, n_mels: int = N_MELS, sr: int = SR, n_fft: int = N_FFT, hop: int = HOP, iters: int = 30):
    """Invert log-mel to waveform with a simplified Griffin-Lim (pseudo-inverse filterbank)."""
    mel = np.expm1(np.clip(mel, 0, 20))  # undo log1p
    fb = mel_filterbank(n_fft, sr, n_mels)
    # Solve fb @ mag ~ mel.T : fb (n_mels, n_bins), mel.T (n_mels, n_frames) -> mag (n_bins, n_frames)
    mag = np.linalg.lstsq(fb, mel.T, rcond=None)[0].T  # (frames, bins) magnitude estimate
    mag = np.clip(mag, 0, None)
    n_frames, n_bins = mag.shape
    win = np.hanning(n_fft)
    phase = np.random.rand(n_frames, n_bins) * 2 * np.pi
    x = np.zeros((n_frames - 1) * hop + n_fft)
    for _ in range(iters):
        x[:] = 0
        for i in range(n_frames):
            comp = mag[i] * np.exp(1j * phase[i])
            seg = np.fft.irfft(comp, n_fft) * win
            x[i * hop: i * hop + n_fft] += seg
        xp = np.pad(x, (n_fft // 2, n_fft // 2), mode="reflect")
        for i in range(n_frames):
            seg = xp[i * hop: i * hop + n_fft] * win
            phase[i] = np.angle(np.fft.rfft(seg))
    return x.astype(np.float32)


def to_mel_tensor(x: np.ndarray, sr: int = SR, n_mels: int = N_MELS, target_frames: int = 128):
    import torch
    mel = mel_spectrogram(x, sr=sr, n_mels=n_mels)
    if mel.shape[0] > target_frames:
        mel = mel[:target_frames]
    else:
        mel = np.pad(mel, ((0, target_frames - mel.shape[0]), (0, 0)))
    return torch.from_numpy(mel).unsqueeze(0).unsqueeze(0)  # (1, 1, n_mels, T)


def save_mel_wav(path, x: np.ndarray, sr: int = SR):
    write_wav(path, x, sr)


def synthesize_music(seconds: float = 2.0, notes_hz=(261.63, 329.63, 392.00), sr: int = SR):
    """Simple chord synth — creates the 'music SIA listens to' demo file."""
    n = int(seconds * sr)
    t = np.arange(n) / sr
    x = np.zeros(n)
    for f in notes_hz:
        x += 0.22 * np.sin(2 * np.pi * f * t) * np.exp(-t / (seconds / 3))
    return x.astype(np.float32)


def freq_to_note(f: float) -> str:
    if f <= 0:
        return "silence"
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    midi = 69 + 12 * math.log2(f / 440.0)
    idx = int(round(midi)) % 12
    return names[idx] + str(int(round(midi)) // 12 - 1)


def analyze_audio(x: np.ndarray, sr: int = SR) -> dict:
    """Deterministic DSP 'listening': dominant pitch, energy, rough tempo."""
    mel = mel_spectrogram(x, sr=sr)
    frame_energy = mel.mean(axis=1)
    peak_frame = int(np.argmax(frame_energy))
    fb = mel_filterbank(N_FFT, sr, N_MELS)
    fbin = np.fft.rfftfreq(N_FFT, 1 / sr)
    mags = np.expm1(mel[peak_frame]) @ fb
    dom_bin = int(np.argmax(mags))
    freq = float(fbin[dom_bin]) if dom_bin < len(fbin) else 0.0
    note = freq_to_note(freq)
    d = np.diff(frame_energy)
    onsets = int(np.sum(d > d.mean() + 2 * d.std()))
    dur = len(x) / sr
    return {
        "duration_s": round(dur, 2),
        "dominant_hz": round(freq, 1),
        "note": note,
        "onsets": onsets,
        "tempo_bpm": round(onsets / dur * 60) if dur > 0 else 0,
    }
