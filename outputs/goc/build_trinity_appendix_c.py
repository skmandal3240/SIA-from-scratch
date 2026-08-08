#!/usr/bin/env python3
"""Build standalone Appendix C — Remaining Work (30-page completion) DOCX for Project TRINITY.

Turns the 'what's left' list from the investor report into a tracked, owned
completion plan with owners, deliverables, and evidence required.
Run: python3 outputs/goc/build_trinity_appendix_c.py
"""
from pathlib import Path

from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "outputs" / "goc" / "TRINITY_Appendix_C_Remaining_Work.docx"

NAVY = RGBColor(0x0F, 0x1B, 0x2D)
GOLD = RGBColor(0xB8, 0x86, 0x0B)
GREY = RGBColor(0x55, 0x5F, 0x6E)

doc = Document()
style = doc.styles["Normal"]
style.font.name = "Calibri"
style.font.size = Pt(11)


def h1(text):
    p = doc.add_heading(text, level=1)
    for r in p.runs:
        r.font.color.rgb = NAVY
        r.font.size = Pt(18)


def h2(text):
    p = doc.add_heading(text, level=2)
    for r in p.runs:
        r.font.color.rgb = GOLD
        r.font.size = Pt(14)


def p(text):
    doc.add_paragraph(text)


def bullet(text):
    doc.add_paragraph(text, style="List Bullet")


def table(headers, rows):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Light Grid Accent 1"
    for i, h in enumerate(headers):
        t.rows[0].cells[i].text = str(h)
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            t.rows[r].cells[c].text = str(val)
    doc.add_paragraph()


# ============ COVER ============
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("Project TRINITY\n")
r.bold = True
r.font.size = Pt(30)
r.font.color.rgb = NAVY
r = doc.add_paragraph("Appendix C — Remaining Work (30-Page Completion)\n")
r.alignment = WD_ALIGN_PARAGRAPH.CENTER
r.runs[0].font.size = Pt(14)
r.runs[0].font.color.rgb = GOLD
r = doc.add_paragraph("Working draft | August 2026 | SIA / Mandal Holdings\n")
r.alignment = WD_ALIGN_PARAGRAPH.CENTER
r.runs[0].font.size = Pt(10)
r.runs[0].font.color.rgb = GREY
p("This appendix turns the master report from a foundation into the full 30-page investor-grade document. Each item lists the deliverable, the evidence required, and the preferred owner so the completion is trackable. Statuses: ⬜ not started | 🟡 drafting | ✅ done.")

# ============ 1. WHAT A 30-PAGE REPORT NEEDS ============
h1("1. The 30-Page Target (Master Structure)")
table(["Pages", "Section", "Status"],
[
    ("1", "Cover Page", "✅"),
    ("2", "Executive Summary", "✅ (foundation)"),
    ("3", "Vision, Mission & Why Now", "✅"),
    ("4", "India's AI Opportunity", "🟡 needs market data"),
    ("5", "Global AI Race (US, China, EU, India)", "⬜ research required"),
    ("6", "AI's Five Pillars Framework", "✅"),
    ("7", "Pillar 1 — Compute Infrastructure", "✅ foundation"),
    ("8", "Pillar 2 — Data Infrastructure", "🟡 needs dataset strategy"),
    ("9", "Pillar 3 — Foundation Models", "✅"),
    ("10", "Pillar 4 — AI Agents & OS", "✅"),
    ("11", "Pillar 5 — Applications & Ecosystem", "✅"),
    ("12", "Technology Architecture", "🟡 needs diagrams"),
    ("13", "Product Roadmap (2026–2035)", "✅"),
    ("14", "Competitive Landscape", "🟡 needs deep source docs"),
    ("15", "Why India Has an Advantage", "🟡 needs supporting data"),
    ("16", "Market Opportunity (TAM/SAM/SOM)", "⬜ not built"),
    ("17", "Business Model", "✅"),
    ("18", "Go-to-Market Strategy", "🟡 needs channel plan"),
    ("19", "Financial Model", "⬜ not built"),
    ("20", "Funding Strategy", "✅"),
    ("21", "Government Grants & Incentives", "✅ (04_TIDE2_DOSSIER)"),
    ("22", "Private Investors & Strategic Partners", "🟡 needs target list"),
    ("23", "Risk Analysis", "✅ foundation"),
    ("24", "AGI Roadmap & Scientific Position", "✅ evidence-based"),
    ("25", "Team & Hiring Plan", "🟡 needs costed plan"),
    ("26", "Company Valuation Strategy", "🟡 needs valuation model"),
    ("27", "Investor DD (Key Q&A) — Appendix A", "✅ re: Bengaluru ed"),
    ("28", "Government Evaluation — Appendix B", "✅ re: Bengaluru ed"),
    ("29", "Investment Ask & Use of Funds", "✅"),
    ("30", "Closing Vision & Call to Action", "✅"),
])

# ============ 2. THE GAP LIST ============
h1("2. Remaining Work by Category")

h2("2.1 Market & Sizing (pages 4, 16)")
bullet("TAM/SAM/SOM model with sources — India AI vs Global (expected final: SAM ~$25B by 2030, SOM 1% share by Y5, frame from research)  ⬜")
bullet("Datapoints: IndiaAI Mission GPU counts (34,000+), AI Kosh datasets, India GDP/IT spend, US-China-EU AI investment comparisons  ⬜")
bullet("Vertical sizing for healthcare/education/agriculture/defence/government  ⬜")

h2("2.2 Competitive Landscape (page 14)")
bullet("Feature matrix: SIA vs OpenAI/Anthropic/Google vs Indian labs  ⬜")
bullet("Positioning table: cloud-locked vs on-device vs sovereign  ⬜")
bullet("Evidence: benchmark reports, analyst notes, news clips  ⬜")

h2("2.3 Financial Model (page 19)")
bullet("3-statement model (Revenue, EBITDA, Cash Flow) 2026–2036  ⬜")
bullet("Unit economics transparency: CAC/LTV/churn/figures  ⬜")
bullet("Sensitivity scenarios: base/bull/bear  ⬜")

h2("2.4 Technical Architecture (page 12)")
bullet("5-Layer stack diagram (clean, investor-grade)  ⬜")
bullet("SIA model family diagram (Nano → Cloud)  ⬜")
bullet("Data flow / memory architecture / agent loop diagrams  ⬜")

h2("2.5 GTM & Channels (page 18)")
bullet("Channel plan: developer community, SDK, enterprise pilots, gov contracts  ⬜")
bullet("Pricing packaging per tier (SIA Edge/Pro/Cloud)  ⬜")
bullet("Pilot pipeline template: 5 target enterprises in Y1  ⬜")

h2("2.6 Team (page 25)")
bullet("Hiring plan with costs per year  ⬜")
bullet("Founder bio / past work (ASTRO, ALICE)  ⬜")
bullet("Advisory board candidates  ⬜")

h2("2.7 Valuation (page 26)")
bullet("DCF + comparables + VC-method valuation model  ⬜")
bullet("Cap-table & dilution timeline for each funding stage  ⬜")

h2("2.8 Governance, Legal & Tax (backend)")
bullet("Register provider: Bengaluru Pvt Ltd  ✅ (filing in progress)")
bullet("DPIIT/Startup India registration (gates IndiaAI/SAMRIDH/TIDE 2.0)  ⬜")
bullet("GST registration on first revenue  ⬜")

h2("2.9 Investor / Gov Attachments")
bullet("Appendix A — full due diligence Q&A  ✅ re: Bengaluru")
bullet("Appendix B — government evaluation  ✅ re: Bengaluru")
bullet("Government funding matrix (8+ programs)  ✅")
bullet("Pitch deck (10-slide SIA_AI_PITCH_DECK.pptx)  ✅")
bullet("TIDE 2.0 application dossier  ✅ (04_TIDE2_DOSSIER)")

# ============ 3. ONE-PAGE PRIORITISATION ============
h1("3. Prioritisation (What Unblocks What)")
table(["Priority", "Deliverable", "Why it matters"],
[
    ["1", "TAM/SAM/SOM + financial model", "Every investor asks; without it, valuation (page 26) is empty"),
    ["2", "Register + DPIIT numbers", "Gates government programs (TIDE 2.0/SAMRIDH/IndiaAI)"),
    ["3", "Architecture diagrams (5-layer + model family)", "Makes the technical story memorable"),
    ["4", "Competitive matrix + evidence", "Substantiates the moat claim"),
    ["5", "GTM channel plan + pricing", "Shows repeatability behind revenue"),
    ["6", "Hiring plan + advisory candidates", "Team credibility beyond founder"),
    ["7", "Valuation model + sensitivity", "Sets the round range"),
])

# ============ 4. PRODUCTION PROCESS ============
h1("4. How This Gets Done")
bullet("Owner: founder (AI scope) with Hermes agent support on research, financial modelling, diagrams, and drafting")
bullet("Inputs: research docs (DD PDF, TRINITY starter, 02_GRANTS_TRACKER), SIA repo (code + demos), market news (daily cron briefs)")
bullet("Deliverable: docs in outputs/goc/, generated by Python (python-docx), committed to GitHub on every completion")
bullet("Verification: each section lands in the master DOCX (build_trinity_report.py) with a rebuild; page count tracked")

# ============ 5. ACCEPTANCE ============
h1("5. Acceptance Criteria (30-page done)")
bullet("All 30 pages present with real content (no placeholders)")
bullet("TAM/SAM/SOM with named sources")
bullet("Financial model with 3 statements + unit economics")
bullet("Competitive landscape with evidence")
bullet("GTM plan + pricing")
bullet("Hiring plan + budget")
bullet("Valuation + cap-table scenarios")
bullet("Appendices A–C complete and Bengaluru-consistent")
bullet("Total pages 30 ± 2; readable as a strategy-consulting-style document")

doc.save(OUT)
print(f"SAVED {OUT} ({len(doc.paragraphs)} paragraphs)")