"""Deterministic rules for the India registration and funding PoC."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from poc_data import checklist, programs

RULES_VERSION = "2026.08.21.1"


def _text(value: Any) -> str:
    return str(value or "").strip()


def _bool(value: Any) -> bool:
    return value is True or value == "true" or value == "on" or value == 1


def _age(value: Any) -> int | None:
    try:
        age = int(str(value).strip())
    except (TypeError, ValueError):
        return None
    return age if 0 < age < 130 else None


def _email_valid(value: Any) -> bool:
    text = _text(value)
    return "@" in text and "." in text.rsplit("@", 1)[-1] and " " not in text


def _postal_valid(value: Any) -> bool:
    text = _text(value)
    return len(text) == 6 and text.isdigit()


def _base_item(item_id: str, status: str, detail: str) -> dict[str, str]:
    return {"id": item_id, "status": status, "detail": detail}


def readiness(draft: dict[str, Any]) -> dict[str, Any]:
    """Return an explainable readiness report without certifying legal readiness."""

    issues: list[str] = []
    warnings: list[str] = []
    items: list[dict[str, str]] = []

    company_name = _text(draft.get("company_name"))
    alternate_name = _text(draft.get("alternate_name"))
    ai_product = _text(draft.get("ai_product"))
    target_users = _text(draft.get("target_users"))
    founder_name = _text(draft.get("founder_name"))
    founder_email = _text(draft.get("founder_email"))
    age = _age(draft.get("founder_age"))

    if company_name and alternate_name:
        items.append(_base_item("company-name", "complete", "Preferred and alternate names are present for professional review."))
    else:
        items.append(_base_item("company-name", "needs_information", "Add both a preferred and alternate name."))
        issues.append("Add a preferred and alternate company name.")

    if ai_product and target_users:
        items.append(_base_item("ai-description", "complete", "AI product and target users are described."))
    else:
        items.append(_base_item("ai-description", "needs_information", "Add the AI product and target users before scheme matching can be specific."))
        issues.append("Describe the AI product and target users.")

    if _text(draft.get("state")).lower() == "bihar" and _text(draft.get("district")).lower() == "madhubani":
        items.append(_base_item("registered-office", "conditional", "Madhubani, Bihar is selected; office evidence is still required."))
    else:
        items.append(_base_item("registered-office", "needs_information", "Use the genuine operating state and district; the current PoC is configured for Madhubani, Bihar."))
        issues.append("Confirm the genuine Bihar operating base.")

    if _bool(draft.get("has_second_member")) and _text(draft.get("second_member_name")):
        items.append(_base_item("second-member", "complete", "Second member/subscriber is identified."))
    else:
        items.append(_base_item("second-member", "blocked", "A second member/subscriber is not identified; do not call this Private Limited Company profile complete."))
        issues.append("Identify the second member/subscriber and obtain professional review.")

    if _bool(draft.get("has_second_director")) and _text(draft.get("second_director_name")):
        items.append(_base_item("second-director", "complete", "Second director is identified."))
    else:
        items.append(_base_item("second-director", "blocked", "A second director is not identified; do not proceed as if the structure is filing-ready."))
        issues.append("Identify the second director and obtain professional review.")

    if founder_name and _email_valid(founder_email):
        items.append(_base_item("founder-proof", "needs_document", "Founder contact is present; safe proof metadata still needs to be recorded."))
    else:
        items.append(_base_item("founder-proof", "needs_information", "Add founder name and a valid contact email; never paste PAN/Aadhaar numbers into the PoC."))
        issues.append("Add founder name and a valid email.")

    if _bool(draft.get("director_proofs_uploaded")):
        items.append(_base_item("director-proofs", "complete", "Director/member proof metadata is marked as reviewed."))
    else:
        items.append(_base_item("director-proofs", "needs_document", "Record safe metadata for director/member proofs."))
        issues.append("Record director/member proof metadata.")

    address_ok = bool(_text(draft.get("address_line")) and _postal_valid(draft.get("postal_code")))
    if address_ok and _bool(draft.get("office_proof_uploaded")):
        items.append(_base_item("registered-office", "complete", "Address fields and office-proof metadata are present."))
    elif address_ok:
        items.append(_base_item("registered-office", "needs_document", "Address is entered; add owner consent/NOC and office-proof metadata."))
        issues.append("Add registered-office proof metadata and owner consent/NOC where applicable.")
    else:
        issues.append("Add a genuine Madhubani address and six-digit postal code.")

    if _text(draft.get("dsc_status")) in {"planned", "obtained", "reviewed"}:
        items.append(_base_item("dsc", "complete", "DSC status is recorded for follow-up."))
    else:
        items.append(_base_item("dsc", "needs_information", "Record whether a DSC plan exists; confirm the exact route with a professional."))
        issues.append("Record a DSC plan or status.")

    if _text(draft.get("authorised_capital")) and _text(draft.get("paid_up_capital")) and _text(draft.get("shareholding_notes")):
        items.append(_base_item("capital", "complete", "Capital and shareholding notes are present for professional review."))
    else:
        items.append(_base_item("capital", "needs_information", "Add capital and shareholding notes without assuming a default amount."))
        issues.append("Add a professional-reviewed capital and shareholding plan.")

    items.append(_base_item("spice", "professional_review", "The PoC can map inputs to SPICe+ concepts but cannot file or sign MCA forms."))
    items.append(_base_item("post-incorporation", "conditional", "Post-incorporation tasks become actionable after incorporation."))

    if age is None:
        warnings.append("Founder age is missing or not valid; the majority/eligibility gate cannot be resolved.")
        issues.append("Add founder age or obtain professional advice before director decisions.")
    elif age < 18:
        issues.append("Founder is below 18 in the profile; do not present the founder as a director without professional advice.")
        warnings.append("Founder is below 18; the minor-founder structure requires professional review and is blocked in this PoC.")
    elif age < 21:
        warnings.append("Student/young-founder details may require additional professional and institutional review.")

    if _text(draft.get("social_category")).upper() == "OBC":
        warnings.append("OBC status is stored as a filter input; it is not treated as a universal startup-grant entitlement.")

    blocker_count = sum(1 for issue in issues if issue.startswith(("Identify", "Founder is", "Add a genuine")))
    if age is not None and age < 18:
        overall = "blocked"
    elif blocker_count or issues:
        overall = "incomplete"
    else:
        overall = "professional_review_required"

    completed = sum(1 for item in items if item["status"] == "complete")
    return {
        "rules_version": RULES_VERSION,
        "overall": overall,
        "completion_percent": round((completed / max(len(items), 1)) * 100),
        "items": items,
        "issues": issues,
        "warnings": warnings,
        "disclaimer": "This report is a draft decision-support result, not legal advice or an MCA filing certification.",
    }


def match_programs(draft: dict[str, Any]) -> list[dict[str, Any]]:
    """Return explainable, conservative support matches for the draft profile."""

    result: list[dict[str, Any]] = []
    incorporated = _text(draft.get("incorporation_stage")) in {"incorporated", "post_incorporation"}
    product_ready = bool(_text(draft.get("ai_product")) and _text(draft.get("target_users")))
    bihar = _text(draft.get("state")).lower() == "bihar" and _text(draft.get("district")).lower() == "madhubani"
    structure_ready = _bool(draft.get("has_second_member")) and _bool(draft.get("has_second_director"))

    for source_program in programs():
        program = dict(source_program)
        missing: list[str] = []
        reasons: list[str] = []
        status = source_program["status"]

        if source_program["id"] == "dpiit-recognition":
            if not incorporated:
                status = "not_yet_available"
                missing.append("incorporation")
                reasons.append("Apply after incorporation if the current recognition criteria fit.")
            elif not product_ready:
                status = "conditional"
                missing.append("AI product narrative")
                reasons.append("Add the product and innovation narrative before applying.")
            else:
                status = "conditional"
                reasons.append("Post-incorporation recognition route appears relevant; verify the current form.")
        elif source_program["id"] == "sisfs":
            if not structure_ready:
                missing.append("second member/director structure")
            if not product_ready:
                missing.append("product and target-user narrative")
            if not incorporated:
                missing.append("incorporation and current scheme checks")
            status = "conditional" if not missing else "requires_verification"
            reasons.append("Prototype support is potentially relevant through approved incubators, subject to current rules and selection.")
        elif source_program["id"] == "bihar-policy":
            if not bihar:
                missing.append("genuine Bihar/Madhubani operating evidence")
            if not incorporated:
                missing.append("current entity-stage requirement")
            status = "conditional" if not missing else "requires_verification"
            reasons.append("The stated Madhubani base makes Bihar the primary route to verify.")
        elif source_program["id"] == "indiaai-compute":
            if not product_ready:
                missing.append("technical workload description")
            if not incorporated:
                missing.append("portal/entity eligibility check")
            status = "conditional" if not missing else "requires_verification"
            reasons.append("Prepare a benchmark and workload plan; allocation and pricing must be checked at application time.")
        elif source_program["id"] in {"tide-2", "nidhi-incubator"}:
            if not product_ready:
                missing.append("prototype narrative")
            missing.append("participating incubator/current call")
            status = "conditional" if product_ready else "requires_verification"
            reasons.append("Incubator-linked support may fit a technology prototype, but the exact call controls eligibility.")
        elif source_program["id"] == "samridh":
            status = "not_yet_stage_fit"
            missing.append("validated product and current accelerator cohort")
            reasons.append("Reassess after a demonstrable PoC and user evidence.")
        elif source_program["id"] == "airawat":
            status = "requires_verification"
            missing.append("current outreach route and capacity")
            reasons.append("Compute access is program- and capacity-dependent, not a cash award.")

        program.update({"status": status, "missing": missing, "reasons": reasons})
        result.append(program)
    return result


def gpu_plan(inputs: dict[str, Any]) -> dict[str, Any]:
    """Create a transparent estimate; it intentionally avoids price promises."""

    def number(key: str, default: float) -> float:
        try:
            value = float(inputs.get(key, default))
            return value if value >= 0 else default
        except (TypeError, ValueError):
            return default

    params = number("model_params_b", 1.0)
    hours = number("gpu_hours", 50.0)
    storage = number("storage_gb", 50.0)
    mode = _text(inputs.get("workload_type")) or "parameter-efficient fine-tuning"
    budget = number("budget_inr", 0.0)

    memory_gb = max(8.0, params * (2.0 if mode == "inference" else 5.0))
    if mode == "full_pretraining":
        memory_gb = max(memory_gb, params * 12.0)
    elif mode == "full_finetuning":
        memory_gb = max(memory_gb, params * 10.0)

    routes = [
        {"name": "IndiaAI Compute", "fit": "conditional", "why": "Potential public or discounted compute route; verify current eligibility, allocation, and pricing."},
        {"name": "C-DAC AIRAWAT / outreach", "fit": "conditional", "why": "Potential research or challenge-linked access; verify current program and capacity."},
        {"name": "Incubator or university infrastructure", "fit": "recommended_first", "why": "Often the most realistic first route for a student founder with a small reproducible benchmark."},
        {"name": "Commercial cloud comparison", "fit": "fallback", "why": "Use only after comparing the actual workload, storage, egress, and idle-time assumptions."},
    ]
    recommendations = [
        "Start with a small reproducible benchmark and parameter-efficient fine-tuning or inference before considering full pretraining.",
        "Record the model license, dataset permissions, privacy safeguards, and expected evaluation metric in the technical dossier.",
        "Apply for public or incubator access with an hours estimate; access is not guaranteed and no price is promised here.",
    ]
    if budget == 0:
        recommendations.insert(0, "No cash budget was entered; prioritize incubator, university, IndiaAI, or C-DAC routes before commercial rental.")

    return {
        "inputs": {"model_params_b": params, "gpu_hours": hours, "storage_gb": storage, "workload_type": mode, "budget_inr": budget},
        "estimated_memory_gb": round(memory_gb, 1),
        "estimated_compute_hours": round(hours, 1),
        "storage_gb": round(storage, 1),
        "routes": routes,
        "recommendations": recommendations,
        "disclaimer": "This is a planning estimate, not a GPU allocation, quote, or approval.",
    }


def review_payload(draft: dict[str, Any], readiness_report: dict[str, Any], matches: list[dict[str, Any]], gpu: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rules_version": RULES_VERSION,
        "company_profile": {
            key: draft.get(key, "")
            for key in [
                "company_name", "alternate_name", "state", "district", "city", "address_line", "postal_code",
                "founder_name", "founder_email", "founder_status", "social_category", "university", "second_member_name",
                "second_director_name", "ai_product", "target_users", "data_type", "company_object", "authorised_capital",
                "paid_up_capital", "shareholding_notes", "incorporation_stage", "dpiit_status",
            ]
        },
        "readiness": readiness_report,
        "support_matches": matches,
        "gpu_plan": gpu,
        "review_gate": "Draft for CA/CS/lawyer review before any MCA filing, signing, payment, or grant submission.",
    }
