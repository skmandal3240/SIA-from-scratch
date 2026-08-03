"""
SIA Unified Multimodal Transformer — core architecture.
One model: Text, Vision, Audio, Code, Tools.
Generation: Text, Code, Image, Video, Audio.
"""
import math
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

import torch
import torch.nn as nn
import torch.nn.functional as F
try:
    from einops import rearrange, repeat
except ImportError:
    # ponytail: fallback if einops not installed
    rearrange = lambda x, pattern, **kwargs: x
    repeat = lambda x, pattern, **kwargs: x


# ============================================================
# Config
# ============================================================
@dataclass
class SIAConfig:
    # Model scale
    dim: int = 768
    n_layers: int = 24
    n_heads: int = 12
    n_kv_heads: int = 4  # GQA
    mlp_mult: int = 4
    max_seq_len: int = 8192
    vocab_size: int = 128256  # LLaMA-3 tokenizer vocab
    eos_id: int = 1  # <|eos|> (matches tokenizer SPECIAL_TOKENS)

    # Vision
    img_size: int = 336
    patch_size: int = 14
    vision_layers: int = 24
    vision_dim: int = 1024
    vision_heads: int = 16

    # Audio
    audio_mel_bins: int = 128
    audio_target_len: int = 1024
    audio_layers: int = 12
    audio_dim: int = 768
    audio_heads: int = 12

    # Cross-attention (which layers have modality fusion)
    cross_attn_every: int = 3  # every N layers
    cross_attn_heads: int = 8

    # Diffusion heads
    diffusion_timesteps: int = 1000
    diffusion_cfg_scale: float = 7.5

    # System
    dtype: str = "bf16"
    rope_theta: float = 500000.0
    rope_scaling: Optional[Dict] = None

    # Agent swarm
    max_agents: int = 8
    agent_comm_layers: int = 2

    @classmethod
    def nano(cls):
        return cls(dim=256, n_layers=6, n_heads=4, n_kv_heads=2, max_seq_len=2048,
                   vision_layers=6, vision_dim=384, vision_heads=6,
                   audio_layers=4, audio_dim=256, audio_heads=4,
                   vocab_size=32000)

    @classmethod
    def small(cls):
        return cls(dim=512, n_layers=12, n_heads=8, n_kv_heads=2, max_seq_len=4096,
                   vision_layers=12, vision_dim=768, vision_heads=12,
                   audio_layers=8, audio_dim=512, audio_heads=8,
                   vocab_size=64000)

    @classmethod
    def base(cls):
        return cls()  # defaults above

    @classmethod
    def large(cls):
        return cls(dim=1024, n_layers=32, n_heads=16, n_kv_heads=4, max_seq_len=8192,
                   vision_layers=24, vision_dim=1024, vision_heads=16,
                   audio_layers=16, audio_dim=768, audio_heads=12)

    @classmethod
    def xl(cls):
        return cls(dim=1536, n_layers=40, n_heads=24, n_kv_heads=8, max_seq_len=16384,
                   vision_layers=32, vision_dim=1280, vision_heads=20,
                   audio_layers=24, audio_dim=1024, audio_heads=16)


# ============================================================
# Core Building Blocks
# ============================================================
class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        norm = x.norm(2, dim=-1, keepdim=True) * (x.size(-1) ** -0.5)
        return self.weight * x / (norm + self.eps)


class SwiGLU(nn.Module):
    def __init__(self, dim: int, hidden_dim: int):
        super().__init__()
        self.w1 = nn.Linear(dim, hidden_dim, bias=False)
        self.w2 = nn.Linear(dim, hidden_dim, bias=False)
        self.w3 = nn.Linear(hidden_dim, dim, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.w3(F.silu(self.w1(x)) * self.w2(x))


def precompute_freqs_cis(dim: int, end: int, theta: float = 500000.0) -> torch.Tensor:
    freqs = 1.0 / (theta ** (torch.arange(0, dim, 2)[: (dim // 2)].float() / dim))
    t = torch.arange(end, device=freqs.device)
    freqs = torch.outer(t, freqs).float()
    return torch.polar(torch.ones_like(freqs), freqs)  # complex64


def apply_rotary_emb(x: torch.Tensor, freqs_cis: torch.Tensor) -> torch.Tensor:
    # x: (bsz, n_heads, seqlen, head_dim) or (bsz, seqlen, n_heads, head_dim)
    # freqs_cis: (max_seqlen, head_dim//2) complex
    # Detect format and extract seqlen correctly
    if x.dim() == 4:
        # Assume (bsz, n_heads, seqlen, head_dim) - standard after transpose
        seqlen = x.shape[2]
    else:
        seqlen = x.shape[1]
    freqs_cis = freqs_cis[:seqlen]
    x_ = torch.view_as_complex(x.float().reshape(*x.shape[:-1], -1, 2))
    x_out = torch.view_as_real(x_ * freqs_cis).flatten(3)
    return x_out.type_as(x)


# ============================================================
# Attention
# ============================================================
class Attention(nn.Module):
    def __init__(self, config: SIAConfig):
        super().__init__()
        self.config = config
        self.n_heads = config.n_heads
        self.n_kv_heads = config.n_kv_heads
        self.head_dim = config.dim // config.n_heads
        self.scale = self.head_dim ** -0.5

        self.q_proj = nn.Linear(config.dim, config.n_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(config.dim, config.n_kv_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(config.dim, config.n_kv_heads * self.head_dim, bias=False)
        self.o_proj = nn.Linear(config.n_heads * self.head_dim, config.dim, bias=False)

        self.register_buffer("freqs_cis", precompute_freqs_cis(self.head_dim, config.max_seq_len, config.rope_theta), persistent=False)

    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None, start_pos: int = 0) -> torch.Tensor:
        bsz, seqlen, _ = x.shape
        q = self.q_proj(x).view(bsz, seqlen, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(bsz, seqlen, self.n_kv_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(bsz, seqlen, self.n_kv_heads, self.head_dim).transpose(1, 2)

        # RoPE on (bsz, nh, seqlen, hd); positions resume from start_pos
        q = apply_rotary_emb(q, self.freqs_cis[start_pos:start_pos + seqlen])
        k = apply_rotary_emb(k, self.freqs_cis[start_pos:start_pos + seqlen])

        # GQA: repeat k/v heads (dim=1 is the head axis)
        if self.n_kv_heads != self.n_heads:
            k = k.repeat_interleave(self.n_heads // self.n_kv_heads, dim=1)
            v = v.repeat_interleave(self.n_heads // self.n_kv_heads, dim=1)

        attn = F.scaled_dot_product_attention(q, k, v, attn_mask=mask, scale=self.scale, is_causal=mask is None)
        attn = attn.transpose(1, 2).contiguous().view(bsz, seqlen, -1)
        return self.o_proj(attn)


class CrossAttention(nn.Module):
    """Cross-attention: text queries attend to modality keys/values"""
    def __init__(self, config: SIAConfig, modality_dim: int):
        super().__init__()
        self.n_heads = config.cross_attn_heads
        self.head_dim = config.dim // config.cross_attn_heads
        self.scale = self.head_dim ** -0.5

        self.q_proj = nn.Linear(config.dim, config.cross_attn_heads * self.head_dim, bias=False)
        self.k_proj = nn.Linear(modality_dim, config.cross_attn_heads * self.head_dim, bias=False)
        self.v_proj = nn.Linear(modality_dim, config.cross_attn_heads * self.head_dim, bias=False)
        self.o_proj = nn.Linear(config.cross_attn_heads * self.head_dim, config.dim, bias=False)

    def forward(self, x: torch.Tensor, context: torch.Tensor, mask: Optional[torch.Tensor] = None) -> torch.Tensor:
        bsz, seqlen, _ = x.shape
        _, ctx_len, _ = context.shape

        q = self.q_proj(x).view(bsz, seqlen, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(context).view(bsz, ctx_len, self.n_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(context).view(bsz, ctx_len, self.n_heads, self.head_dim).transpose(1, 2)

        attn = F.scaled_dot_product_attention(q, k, v, attn_mask=mask, scale=self.scale)
        attn = attn.transpose(1, 2).contiguous().view(bsz, seqlen, -1)
        return self.o_proj(attn)


# ============================================================
# Transformer Block
# ============================================================
class TransformerBlock(nn.Module):
    def __init__(self, config: SIAConfig, layer_idx: int, modality_dims: Dict[str, int]):
        super().__init__()
        self.config = config
        self.layer_idx = layer_idx

        self.attn_norm = RMSNorm(config.dim)
        self.attn = Attention(config)

        self.mlp_norm = RMSNorm(config.dim)
        self.mlp = SwiGLU(config.dim, config.dim * config.mlp_mult)

        # Cross-attention for modality fusion
        self.has_cross = (layer_idx + 1) % config.cross_attn_every == 0
        if self.has_cross:
            self.cross_norms = nn.ModuleDict()
            self.cross_attns = nn.ModuleDict()
            for mod_name, mod_dim in modality_dims.items():
                self.cross_norms[mod_name] = RMSNorm(config.dim)
                self.cross_attns[mod_name] = CrossAttention(config, mod_dim)

    def forward(
        self,
        x: torch.Tensor,
        mask: Optional[torch.Tensor] = None,
        start_pos: int = 0,
        modalities: Optional[Dict[str, torch.Tensor]] = None,
    ) -> torch.Tensor:
        # Self-attention
        x = x + self.attn(self.attn_norm(x), mask, start_pos)

        # Cross-attention with modalities
        if self.has_cross and modalities:
            for mod_name, mod_tensor in modalities.items():
                if mod_tensor is not None and mod_name in self.cross_attns:
                    x = x + self.cross_attns[mod_name](self.cross_norms[mod_name](x), mod_tensor)

        # MLP
        x = x + self.mlp(self.mlp_norm(x))
        return x


# ============================================================
# Modality Encoders
# ============================================================
class PatchEmbed(nn.Module):
    def __init__(self, img_size: int, patch_size: int, in_chans: int, embed_dim: int):
        super().__init__()
        self.img_size = img_size
        self.patch_size = patch_size
        self.n_patches = (img_size // patch_size) ** 2
        self.proj = nn.Conv2d(in_chans, embed_dim, kernel_size=patch_size, stride=patch_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, 3, H, W) -> (B, N, D)
        x = self.proj(x).flatten(2).transpose(1, 2)
        return x


class VisionEncoder(nn.Module):
    """ViT encoder for images"""
    def __init__(self, config: SIAConfig):
        super().__init__()
        self.patch_embed = PatchEmbed(config.img_size, config.patch_size, 3, config.vision_dim)
        self.pos_embed = nn.Parameter(torch.zeros(1, self.patch_embed.n_patches + 1, config.vision_dim))
        self.cls_token = nn.Parameter(torch.zeros(1, 1, config.vision_dim))
        nn.init.trunc_normal_(self.pos_embed, std=0.02)
        nn.init.trunc_normal_(self.cls_token, std=0.02)

        self.blocks = nn.ModuleList([
            TransformerBlock(
                SIAConfig(dim=config.vision_dim, n_layers=1, n_heads=config.vision_heads,
                          n_kv_heads=config.vision_heads, max_seq_len=config.max_seq_len),
                i, {}
            ) for i in range(config.vision_layers)
        ])
        self.norm = RMSNorm(config.vision_dim)
        self.proj = nn.Linear(config.vision_dim, config.dim, bias=False)  # project to backbone dim

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, 3, H, W)
        b = x.shape[0]
        x = self.patch_embed(x)  # (B, N, D)
        cls = self.cls_token.expand(b, -1, -1)
        x = torch.cat([cls, x], dim=1)
        x = x + self.pos_embed

        for blk in self.blocks:
            x = blk(x)

        x = self.norm(x)
        x = self.proj(x)  # (B, N+1, backbone_dim)
        return x


class AudioEncoder(nn.Module):
    """Audio encoder (mel spectrogram -> tokens)"""
    def __init__(self, config: SIAConfig):
        super().__init__()
        self.patch_embed = nn.Conv2d(1, config.audio_dim, kernel_size=(16, 16), stride=(10, 10))
        # pos_embed will be created dynamically based on input size

        self.blocks = nn.ModuleList([
            TransformerBlock(
                SIAConfig(dim=config.audio_dim, n_layers=1, n_heads=config.audio_heads,
                          n_kv_heads=config.audio_heads, max_seq_len=config.max_seq_len),
                i, {}
            ) for i in range(config.audio_layers)
        ])
        self.norm = RMSNorm(config.audio_dim)
        self.proj = nn.Linear(config.audio_dim, config.dim, bias=False)
        # Fixed-size positional embedding (stride 10 on 1024-frame mel -> ~103 tokens)
        self.pos_embed = nn.Parameter(torch.zeros(1, (config.audio_target_len // 10) + 2, config.audio_dim))
        nn.init.trunc_normal_(self.pos_embed, std=0.02)

    def forward(self, mel: torch.Tensor) -> torch.Tensor:
        # mel: (B, 1, n_mels, time)
        x = self.patch_embed(mel).flatten(2).transpose(1, 2)  # (B, N, D)
        assert x.shape[1] <= self.pos_embed.shape[1], f"audio tokens {x.shape[1]} > pos_embed {self.pos_embed.shape[1]}"
        x = x + self.pos_embed[:, :x.shape[1]]

        for blk in self.blocks:
            x = blk(x)

        x = self.norm(x)
        x = self.proj(x)
        return x


class CodeEncoder(nn.Module):
    """Code encoder - shares backbone but with special tokens"""
    def __init__(self, config: SIAConfig):
        super().__init__()
        # Reuses text embeddings but adds code-specific tokens
        self.code_token_ids = {
            "<|code_start|>": config.vocab_size - 10,
            "<|code_end|>": config.vocab_size - 9,
            "<|cell|>": config.vocab_size - 8,
            "<|output|>": config.vocab_size - 7,
        }


# ============================================================
# Diffusion Heads (Generation)
# ============================================================
class TimestepEmbedding(nn.Module):
    def __init__(self, dim: int):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(dim, dim * 4),
            nn.SiLU(),
            nn.Linear(dim * 4, dim),
        )

    def forward(self, t: torch.Tensor) -> torch.Tensor:
        half_dim = self.mlp[0].in_features // 2  # match MLP input dim for any config
        emb = math.log(10000) / (half_dim - 1)
        emb = torch.exp(torch.arange(half_dim, device=t.device) * -emb)
        emb = t[:, None] * emb[None, :]
        emb = torch.cat([emb.sin(), emb.cos()], dim=-1)
        return self.mlp(emb)


class DiffusionHead(nn.Module):
    """Base diffusion head for image/video/audio generation"""
    def __init__(self, config: SIAConfig, out_channels: int, input_dim: int = None):
        super().__init__()
        self.config = config
        self.input_dim = input_dim or config.dim
        self.out_channels = out_channels

        self.time_embed = TimestepEmbedding(config.dim)
        self.cond_proj = nn.Linear(config.dim, config.dim)
        self.in_proj = nn.Conv2d(out_channels, config.dim, 3, padding=1) if out_channels > 0 else nn.Identity()

        # UNet-style blocks (simplified)
        self.down = nn.ModuleList([
            nn.Conv2d(config.dim, config.dim, 3, padding=1),
            nn.Conv2d(config.dim, config.dim * 2, 3, stride=2, padding=1),
            nn.Conv2d(config.dim * 2, config.dim * 2, 3, padding=1),
        ])
        self.mid = nn.Conv2d(config.dim * 2, config.dim * 2, 3, padding=1)
        self.up = nn.ModuleList([
            nn.ConvTranspose2d(config.dim * 2, config.dim, 4, stride=2, padding=1),
            nn.Conv2d(config.dim, config.dim, 3, padding=1),
        ])
        self.out_proj = nn.Conv2d(config.dim, out_channels, 3, padding=1)

    def forward(self, x: torch.Tensor, t: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        # x: (B, C, H, W) noisy input
        # t: (B,) timesteps
        # cond: (B, L, D) text conditioning

        t_emb = self.time_embed(t)  # (B, D)
        cond = self.cond_proj(cond.mean(dim=1))  # (B, D) - pool text tokens
        cond = cond + t_emb

        h = self.in_proj(x) + cond[:, :, None, None]
        skips = []
        for layer in self.down:
            h = layer(h)
            skips.append(h)
        h = self.mid(h)
        for layer, skip in zip(self.up, reversed(skips)):
            # ponytail: simplified UNet — only add the skip when resolutions align
            h = layer(h + skip if h.shape == skip.shape else h)
        return self.out_proj(h)


class ImageDiffusionHead(DiffusionHead):
    def __init__(self, config: SIAConfig):
        super().__init__(config, out_channels=4)  # latent channels (VAE)


class VideoDiffusionHead(DiffusionHead):
    def __init__(self, config: SIAConfig):
        super().__init__(config, out_channels=4)
        # Add temporal attention layers


class AudioDiffusionHead(DiffusionHead):
    def __init__(self, config: SIAConfig):
        super().__init__(config, out_channels=1)  # mel spectrogram


# ============================================================
# Tool Use Head
# ============================================================
class ToolHead(nn.Module):
    def __init__(self, config: SIAConfig, n_tools: int = 64):
        super().__init__()
        self.config = config
        self.tool_classifier = nn.Linear(config.dim, n_tools)
        self.arg_generator = nn.Linear(config.dim, config.dim)  # generates JSON-like args

    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        # x: (B, L, D) - last token or special tool token
        tool_logits = self.tool_classifier(x)  # (B, L, n_tools)
        args = self.arg_generator(x)
        return {"tool_logits": tool_logits, "args": args}


# ============================================================
# Agent Communication (Swarm)
# ============================================================
class AgentCommunication(nn.Module):
    """Inter-agent communication for swarm intelligence"""
    def __init__(self, config: SIAConfig):
        super().__init__()
        self.config = config
        self.comm_attn = nn.MultiheadAttention(
            config.dim, config.n_heads, batch_first=True
        )
        self.comm_mlp = SwiGLU(config.dim, config.dim * 2)
        self.norm = RMSNorm(config.dim)

    def forward(self, agent_states: torch.Tensor) -> torch.Tensor:
        # agent_states: (n_agents, B, L, D)
        n_agents, bsz, seqlen, dim = agent_states.shape
        agent_states = agent_states.view(n_agents * bsz, seqlen, dim)

        # Self-attention across agents
        attended, _ = self.comm_attn(agent_states, agent_states, agent_states)
        attended = attended + self.comm_mlp(self.norm(attended))
        return attended.view(n_agents, bsz, seqlen, dim)


# ============================================================
# Main SIA Model
# ============================================================
class SIA(nn.Module):
    def __init__(self, config: SIAConfig):
        super().__init__()
        self.config = config

        # Token embeddings
        self.tok_emb = nn.Embedding(config.vocab_size, config.dim)

        # Modality encoders
        self.vision = VisionEncoder(config)
        self.audio = AudioEncoder(config)
        self.code = CodeEncoder(config)

        # Modality dimensions for cross-attention
        modality_dims = {
            "vision": config.dim,
            "audio": config.dim,
            "code": config.dim,
        }

        # Shared transformer backbone
        self.blocks = nn.ModuleList([
            TransformerBlock(config, i, modality_dims) for i in range(config.n_layers)
        ])
        self.norm = RMSNorm(config.dim)

        # Output heads
        self.text_head = nn.Linear(config.dim, config.vocab_size, bias=False)
        self.text_head.weight = self.tok_emb.weight  # weight tying

        # Generation heads
        self.image_gen = ImageDiffusionHead(config)
        self.video_gen = VideoDiffusionHead(config)
        self.audio_gen = AudioDiffusionHead(config)

        # Tool use
        self.tool_head = ToolHead(config)

        # Agent swarm
        self.agent_comm = AgentCommunication(config)

        self.apply(self._init_weights)

    def _init_weights(self, module: nn.Module):
        if isinstance(module, nn.Linear):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            nn.init.normal_(module.weight, mean=0.0, std=0.02)
        elif isinstance(module, nn.Conv2d):
            nn.init.kaiming_normal_(module.weight, mode="fan_out")

    def encode_text(self, input_ids: torch.Tensor) -> torch.Tensor:
        return self.tok_emb(input_ids)

    def encode_vision(self, images: torch.Tensor) -> torch.Tensor:
        return self.vision(images)

    def encode_audio(self, mel: torch.Tensor) -> torch.Tensor:
        return self.audio(mel)

    def forward(
        self,
        input_ids: Optional[torch.Tensor] = None,
        images: Optional[torch.Tensor] = None,
        audio: Optional[torch.Tensor] = None,
        modality_masks: Optional[Dict[str, torch.Tensor]] = None,
        start_pos: int = 0,
    ) -> torch.Tensor:
        # Encode modalities
        modalities = {}
        if images is not None:
            modalities["vision"] = self.encode_vision(images)
        if audio is not None:
            modalities["audio"] = self.encode_audio(audio)

        # Text tokens
        x = self.encode_text(input_ids) if input_ids is not None else None

        # If multimodal, prepend modality tokens
        if x is not None and modalities:
            # Simple concatenation: [modality_tokens, text_tokens]
            # In practice, use special tokens and position offsets
            pass

        # Causal mask
        mask = None
        if x is not None and x.shape[1] > 1:
            mask = torch.tril(torch.ones(x.shape[1], x.shape[1], dtype=torch.bool, device=x.device)).view(1, 1, x.shape[1], x.shape[1])

        # Backbone
        if x is not None:
            for blk in self.blocks:
                x = blk(x, mask, start_pos, modalities)
            x = self.norm(x)

        return x

    # Generation methods
    @torch.no_grad()
    def generate_text(self, input_ids: torch.Tensor, max_new: int = 512, temp: float = 0.8, top_k: int = 50) -> torch.Tensor:
        for _ in range(max_new):
            logits = self.text_head(self.forward(input_ids)[:, -1]) / temp
            if top_k > 0:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = -float('inf')
            probs = F.softmax(logits, dim=-1)
            next_id = torch.multinomial(probs, 1)
            input_ids = torch.cat([input_ids, next_id], dim=1)
            # Stop if all sequences hit EOS
            if (next_id == self.config.eos_id).all():
                break
        return input_ids

    @torch.no_grad()
    def generate_image(self, prompt_embeds: torch.Tensor, steps: int = 50, cfg: float = 7.5) -> torch.Tensor:
        # Simplified DDPM sampling
        latents = torch.randn(1, 4, 32, 32, device=prompt_embeds.device)
        for t in reversed(range(steps)):
            t_tensor = torch.full((1,), t, device=prompt_embeds.device)
            noise_pred = self.image_gen(latents, t_tensor, prompt_embeds)
            # DDIM step (simplified)
            latents = latents - noise_pred * (1 / steps)
        return latents

    @torch.no_grad()
    def generate_audio(self, prompt_embeds: torch.Tensor, steps: int = 30, n_mels: int = 64, frames: int = 64) -> torch.Tensor:
        # Simplified DDPM sampling into a mel spectrogram; decode with modalities.griffin_lim
        latents = torch.randn(1, 1, n_mels, frames, device=prompt_embeds.device)
        for t in reversed(range(steps)):
            t_tensor = torch.full((1,), t, device=prompt_embeds.device)
            noise_pred = self.audio_gen(latents, t_tensor, prompt_embeds)
            latents = latents - noise_pred * (1 / steps)
        return latents

    @torch.no_grad()
    def call_tool(self, input_ids: torch.Tensor) -> Dict:
        x = self.forward(input_ids)
        return self.tool_head(x[:, -1:])

    def swarm_step(self, agent_inputs: List[torch.Tensor]) -> List[torch.Tensor]:
        """Run one step of multi-agent swarm"""
        # Stack agent states: (n_agents, B, L, D)
        states = torch.stack([self.forward(inp) for inp in agent_inputs])
        states = self.agent_comm(states)
        return [states[i] for i in range(len(agent_inputs))]


def count_params(model: nn.Module) -> int:
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


if __name__ == "__main__":
    # Test all configs
    for name, cfg_cls in [("nano", SIAConfig.nano), ("small", SIAConfig.small), ("base", SIAConfig.base), ("large", SIAConfig.large), ("xl", SIAConfig.xl)]:
        cfg = cfg_cls()
        model = SIA(cfg)
        print(f"SIA-{name}: {count_params(model):,} params")

    # Quick forward test
    model = SIA(SIAConfig.nano())
    text = torch.randint(0, 32000, (2, 128))
    img = torch.randn(2, 3, 336, 336)
    audio = torch.randn(2, 1, 128, 1024)

    out = model(text, img, audio)
    print(f"Forward: {out.shape}")

    gen = model.generate_text(text[:, :10], max_new=20)
    print(f"Generate: {gen.shape}")

    tools = model.call_tool(text[:, :10])
    print(f"Tools: {tools['tool_logits'].shape}")

    agents = model.swarm_step([text, text])
    print(f"Swarm: {len(agents)} agents")