#!/usr/bin/env python3
"""Generate Project TRINITY architecture diagrams (dark-themed SVG HTML) per architecture-diagram skill."""
from pathlib import Path

OUT_DIR = Path("/root/SIA-from-scratch/outputs/goc/diagrams")
OUT_DIR.mkdir(parents=True, exist_ok=True)

HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
  body {{ background:#020617; color:#e2e8f0; font-family:'JetBrains Mono',monospace; padding:24px; }}
  .card {{ background:#0f172a; border:1px solid #1e293b; border-radius:12px; padding:20px; margin-bottom:20px; }}
  .title {{ font-size:22px; font-weight:600; }}
  .pulse {{ display:inline-block; width:10px; height:10px; background:#22d3ee; border-radius:50%; margin-right:8px; animation:pulse 2s infinite; }}
  @keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.3}} }}
  .sub {{ color:#94a3b8; font-size:12px; margin:6px 0 16px; }}
  .legend {{ font-size:11px; color:#94a3b8; margin-top:12px; }}
  .legend span {{ margin-right:16px; }}
  .dot {{ display:inline-block; width:8px; height:8px; border-radius:50%; margin-right:4px; vertical-align:middle; }}
  .cards {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-top:16px; }}
  .card {{ background:#0f172a; border:1px solid #1e293b; border-radius:10px; padding:14px; }}
  .card h3 {{ font-size:13px; margin:0 0 8px; color:#94a3b8; }}
  .card li {{ font-size:11px; margin:4px 0; color:#cbd5e1; }}
  ul {{ margin:0; padding-left:16px; }}
</style>
</head>
<body>
<div class="wrap">
<span class="pulse"></span><span class="title">{title}</span>
<div class="sub">{subtitle}</div>
<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;">
<defs>
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.5"/>
  </pattern>
  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8"/>
  </marker>
  <marker id="arrowSec" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M 0 0 L 10 5 L 0 10 z" fill="#fb7185"/>
  </marker>
</defs>
<rect width="100%" height="100%" fill="url(#grid)"/>
"""

FOOTER = """
</svg>
<div class="legend">
  <span><span class="dot" style="background:#22d3ee"></span>Frontend/App</span>
  <span><span class="dot" style="background:#34d399"></span>Backend/Agent</span>
  <span><span class="dot" style="background:#a78bfa"></span>Data/Model</span>
  <span><span class="dot" style="background:#fbbf24"></span>Cloud/Infra</span>
  <span><span class="dot" style="background:#fb7185"></span>Security/Sovereign</span>
</div>
</div>
"""

CARDS_TPL = """
<div class="cards">
  <div class="card"><h3>C1</h3><ul>BULLETS</ul></div>
  <div class="card"><h3>C2</h3><ul>BULLETS2</ul></div>
  <div class="card"><h3>C3</h3><ul>BULLETS3</ul></div>
</div>
"""

def comp(x, y, w, h, label, sub, fill, stroke):
    """Double-rect component: opaque base + styled top."""
    return f"""
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="#0f172a" stroke="#0f172a"/>
  <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>
  <text x="{x+w/2}" y="{y+h/2-6}" text-anchor="middle" fill="#e2e8f0" font-size="12" font-weight="600">{label}</text>
  <text x="{x+w/2}" y="{y+h/2+10}" text-anchor="middle" fill="#94a3b8" font-size="9">{sub}</text>"""

def arrow(x1, y1, x2, y2, color="#94a3b8", dashed=False, marker="arrow"):
    dash = ' stroke-dasharray="4,4"' if dashed else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.5"{dash} marker-end="url(#{marker})"/>'


def save(name, title, subtitle, svg_body, w=900, h=620, cards=None):
    html = HEADER.format(title=title, subtitle=subtitle, w=w, h=h) + svg_body + FOOTER
    if cards:
        c = cards
        html += CARDS_TPL.replace("BULLETS", c[0]).replace("BULLETS2", c[1]).replace("BULLETS3", c[2])
    html += "</body></html>"
    (OUT_DIR / name).write_text(html, encoding="utf-8")
    print(f"SAVED {OUT_DIR}/{name}")

# ============ DIAGRAM 1: 5-LAYER AI STACK ============
svg_body = "".join([
    comp(40, 40, 460, 90, "L1 · CODING AGENTS", "Claude Code / Codex · A-code", "rgba(8,51,68,0.4)", "#22d3ee"),
    comp(40, 160, 460, 90, "L2 · APPLICATIONS", "all verticals · health · edu · agri · gov", "rgba(8,51,68,0.4)", "#22d3ee"),
    comp(40, 280, 460, 90, "L3 · MODELS", "SIA family · multimodal", "rgba(76,29,149,0.4)", "#a78bfa"),
    comp(40, 400, 460, 90, "L4 · INFRASTRUCTURE", "data centers · rent→cluster", "rgba(120,53,15,0.3)", "#fbbf24"),
    comp(40, 520, 460, 80, "L5 · CHIP + ENERGY", "GPU/TPU/NPU/photonic · nuclear", "rgba(120,53,15,0.3)", "#fbbf24"),
    comp(560, 170, 500, 150, "SIA EVERYWHERE", "AI OS · every device", "rgba(6,78,59,0.4)", "#34d399"),
    comp(560, 430, 500, 140, "ROOT INDIA · BUILD INDIA", "IP · jobs · chips · energy in India", "rgba(136,19,55,0.4)", "#fb7185"),
    arrow(500, 245, 560, 245, "#34d399"),
    arrow(500, 500, 560, 500, "#fb7185"),
    arrow(270, 130, 270, 160, "#94a3b8"),
    arrow(270, 250, 270, 280, "#94a3b8"),
    arrow(270, 370, 270, 400, "#94a3b8"),
    arrow(270, 490, 270, 520, "#94a3b8"),
])
save("01_5layer_ai_stack.html", "TRINITY — 5-Layer AI Stack",
     "Claude Code/Codex → applications → models → infra → chip+energy; outcomes: SIA Everywhere · Root India",
     svg_body, cards=[
        "<li>L1 coding agents at the top of the pyramid</li><li>L5 anchored by chips + nuclear energy</li>",
        "<li>SIA Everywhere: same OS on every device</li><li>Nano→Cloud family shared runtime</li>",
        "<li>Root India / Build India = sovereign outcome</li><li>5 layers, one company, India as root</li>",
     ])

# ============ DIAGRAM 2: SIA MODEL FAMILY ============
svg2 = "".join([
    comp(60, 40, 420, 90, "SIA NANO · 0.5–1B", "wearables · IoT · MCUs", "rgba(76,29,149,0.4)", "#a78bfa"),
    comp(60, 180, 420, 90, "SIA EDGE · 2–4B", "phones · PCs · laptops", "rgba(76,29,149,0.4)", "#a78bfa"),
    comp(60, 320, 420, 90, "SIA PRO · 8–14B", "workstations · local GPUs", "rgba(76,29,149,0.4)", "#a78bfa"),
    comp(60, 460, 420, 90, "SIA CLOUD · 70B+", "data centers · advanced reasoning", "rgba(120,53,15,0.3)", "#fbbf24"),
    # Shared stack box
    comp(560, 180, 480, 300, "SHARED ACROSS ALL TIERS", "one tokenizer · one architecture", "rgba(6,78,59,0.4)", "#34d399"),
    arrow(480, 85, 560, 200, "#a78bfa"),
    arrow(480, 225, 560, 260, "#a78bfa"),
    arrow(480, 365, 560, 340, "#a78bfa"),
    arrow(480, 505, 560, 420, "#fbbf24"),
])
svg2 += """
  <text x="560" y="230" fill="#94a3b8" font-size="11">same tool-calling interface</text>
  <text x="560" y="254" fill="#94a3b8" font-size="11">same memory formats</text>
  <text x="560" y="278" fill="#94a3b8" font-size="11">compatible memory across devices</text>
  <text x="560" y="302" fill="#94a3b8" font-size="11">common runtime — synced knowledge</text>
"""
save("02_sia_model_family.svg", "TRINITY — SIA Model Family",
     "one AI OS · four hardware tiers · one shared stack", svg2, w=1100, h=620,
     cards=["<li>Nano for wearables/IoT</li><li>Edge for phones/PCs</li>",
            "<li>Pro for workstations + local GPUs</li><li>Cloud for data-center reasoning</li>",
            "<li>All share tokenizer, architecture, tools, memory</li><li>One runtime syncs knowledge</li>"])

# ============ DIAGRAM 3: DATA FLOW / MEMORY / AGENT LOOP ============
svg3 = "".join([
    comp(40, 40, 300, 110, "USER", "voice · text · image · cross-device", "rgba(8,51,68,0.4)", "#22d3ee"),
    comp(40, 260, 300, 140, "SIA AGENT", "autonomous task execution · tools", "rgba(6,78,59,0.4)", "#34d399"),
    comp(40, 500, 300, 100, "TOOLS", "calc · files · web · device actions", "rgba(251,146,60,0.3)", "#fb923c"),
    comp(420, 260, 300, 140, "SIA CORE", "orchestration + synchronization", "rgba(6,78,59,0.4)", "#34d399"),
    comp(780, 40, 300, 110, "SIA MEMORY", "consistent · personalized · cross-device", "rgba(76,29,149,0.4)", "#a78bfa"),
    comp(780, 260, 300, 140, "MODEL FAMILY", "nano → edge → pro → cloud", "rgba(76,29,149,0.4)", "#a78bfa"),
    comp(780, 500, 300, 100, "PRIVACY / DPDP", "everything on-device unless cloud needed", "rgba(136,19,55,0.4)", "#fb7185"),
    arrow(320, 90, 780, 90, "#22d3ee"),
    arrow(170, 150, 170, 260, "#34d399"),
    arrow(190, 340, 340, 340, "#34d399"),
    arrow(420, 340, 720, 340, "#a78bfa"),
    arrow(190, 400, 190, 500, "#fb923c"),
    arrow(930, 180, 930, 260, "#a78bfa"),
    arrow(170, 400, 170, 500 if False else 400, dashed=True, color="#fb7185"),
])
svg3 = svg3.replace('arrow(170, 400, 170, 500 if False else 400, dashed=True, color="#fb7185")',
                    'arrow(170, 400, 170, 460, dashed=True, color="#fb7185")')
save("03_memory-agents-loop.svg", "TRINITY — SIA Data / Memory / Tools Loop",
     "agent loop: intent → memory/context → model family → tool execution → result sync",
     svg3, w=1100, h=600,
     cards=["<li>Cross-device consistent memory</li><li>Compatible formats across tiers</li>",
            "<li>Agent splits to SIA Tools</li><li>Tool results sync through memory</li>",
            "<li>On-device by default (privacy)</li><li>Cloud fallback when needed (DPA)</li>"])

print("ALL DIAGRAMS DONE")