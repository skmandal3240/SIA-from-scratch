"""Local web PoC for SIA's India company-registration readiness workflow.

This server is intentionally local-demo oriented. It does not authenticate users,
submit forms, sign documents, process payments, or upload identity documents.
"""

from __future__ import annotations

import json
import os
import tempfile
from copy import deepcopy
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, redirect, render_template, request, url_for

from poc_data import DEFAULT_DRAFT, VERIFIED_ON, checklist, default_draft, programs, sources
from poc_rules import gpu_plan, match_programs, readiness, review_payload

ROOT = Path(__file__).resolve().parent
STATE_DIR = ROOT / ".poc_state"
STATE_FILE = STATE_DIR / "draft.json"

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    return response


def _load_draft() -> dict[str, Any]:
    draft = default_draft()
    try:
        saved = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        if isinstance(saved, dict):
            draft.update(saved)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return draft


def _save_draft(draft: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(draft, indent=2, ensure_ascii=False)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=STATE_DIR, delete=False) as handle:
        handle.write(payload)
        temp_name = handle.name
    os.replace(temp_name, STATE_FILE)


def _checked(form: Any, key: str) -> bool:
    return form.get(key) in {"1", "true", "on", "yes"}


def _draft_from_form(form: Any, previous: dict[str, Any]) -> dict[str, Any]:
    draft = deepcopy(previous)
    text_fields = [
        "company_name", "alternate_name", "state", "district", "city", "address_line", "postal_code",
        "founder_name", "founder_email", "founder_phone", "founder_age", "founder_status", "social_category",
        "university", "second_member_name", "second_director_name", "ai_product", "target_users", "data_type",
        "company_object", "authorised_capital", "paid_up_capital", "shareholding_notes", "dsc_status",
        "dpiit_status", "incorporation_stage",
    ]
    for field in text_fields:
        if field in form:
            draft[field] = form.get(field, "").strip()
    for field in ["has_second_member", "has_second_director", "office_proof_uploaded", "director_proofs_uploaded"]:
        if field in form:
            draft[field] = _checked(form, field)
    return draft


def _context(draft: dict[str, Any], gpu: dict[str, Any] | None = None) -> dict[str, Any]:
    report = readiness(draft)
    matches = match_programs(draft)
    return {
        "draft": draft,
        "readiness": report,
        "matches": matches,
        "checklist": checklist(),
        "sources": sources(),
        "verified_on": VERIFIED_ON,
        "gpu": gpu or gpu_plan({}),
    }


@app.get("/healthz")
def healthz():
    return jsonify({"ok": True, "service": "sia-india-registration-poc", "rules_version": "2026.08.21.1"})


@app.get("/")
def dashboard():
    draft = _load_draft()
    return render_template("dashboard.html", **_context(draft))


@app.route("/company", methods=["GET", "POST"])
def company():
    draft = _load_draft()
    saved = False
    if request.method == "POST":
        draft = _draft_from_form(request.form, draft)
        _save_draft(draft)
        saved = True
    return render_template("company.html", **_context(draft), saved=saved)


@app.route("/documents", methods=["GET", "POST"])
def documents():
    draft = _load_draft()
    saved = False
    if request.method == "POST":
        # Deliberately store only review flags and metadata in this first PoC.
        draft["office_proof_uploaded"] = _checked(request.form, "office_proof_uploaded")
        draft["director_proofs_uploaded"] = _checked(request.form, "director_proofs_uploaded")
        _save_draft(draft)
        saved = True
    return render_template("documents.html", **_context(draft), saved=saved)


@app.get("/support")
def support():
    draft = _load_draft()
    return render_template("support.html", **_context(draft))


@app.route("/gpu", methods=["GET", "POST"])
def gpu():
    draft = _load_draft()
    inputs = request.form.to_dict() if request.method == "POST" else {}
    plan = gpu_plan(inputs)
    return render_template("gpu.html", **_context(draft, plan), gpu_inputs=inputs)


@app.get("/review")
def review():
    draft = _load_draft()
    context = _context(draft)
    payload = review_payload(draft, context["readiness"], context["matches"], context["gpu"])
    return render_template("review.html", **context, payload=payload)


@app.get("/export.json")
def export_json():
    draft = _load_draft()
    context = _context(draft)
    payload = review_payload(draft, context["readiness"], context["matches"], context["gpu"])
    response = jsonify(payload)
    response.headers["Content-Disposition"] = "attachment; filename=sia-registration-review.json"
    return response


@app.post("/reset")
def reset():
    _save_draft(default_draft())
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(host=os.getenv("POC_HOST", "127.0.0.1"), port=int(os.getenv("POC_PORT", "5000")), debug=False)
