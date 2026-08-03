#!/usr/bin/env python3
"""SIA daily 5-pillar digest. Reads the plan doc + grants tracker, prints a compact Telegram digest.
Usage: python3 cron_digest.py  (stdout is delivered verbatim by the cron job)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / "docs" / "AI_5_PILLARS_INDIA_PLAN.md"
TRACKER = ROOT / "outputs" / "goc" / "02_GRANTS_TRACKER.md"


def pillar_line(doc: str, pillar: str) -> str:
    """Find the '## PILLAR N — NAME' heading and return the first bolded line."""
    for m in re.finditer(r"## (PILLAR \d+ — [^\n]+)\n(.{0,600})", doc, re.S):
        if pillar.lower() in m.group(1).lower():
            body = m.group(2).splitlines()
            for line in body:
                line = line.strip()
                if line.startswith("**") and "**" in line[2:]:
                    return f"{m.group(1)}: {line.strip('*').strip()}"
    return f"{pillar}: (no summary found)"


def main() -> str:
    plan = PLAN.read_text(encoding="utf-8", errors="ignore")
    tracker = TRACKER.read_text(encoding="utf-8", errors="ignore") if TRACKER.exists() else ""
    lines = ["SIA 5-PILLAR DIGEST — daily", ""]
    for p in ["PILLAR 5", "PILLAR 4", "PILLAR 3", "PILLAR 2", "PILLAR 1"]:
        lines.append(pillar_line(plan, p))
    # Grants status line
    if tracker:
        statuses = re.findall(r"\|\s*([A-Za-z0-9 .()/-]+?)\s*\|\s*([A-Za-z /]+?)\s*\|\s*(?:[^|]*\|){2}\s*([✅🟢🟡🔴])", tracker)
        if statuses:
            lines.append("")
            lines.append("Grants: " + ", ".join(f"{n}: {s}" for n, _, s in statuses[:6]))
    lines.append("")
    lines.append("— SIA cron digest")
    return "\n".join(lines)


if __name__ == "__main__":
    print(main())
