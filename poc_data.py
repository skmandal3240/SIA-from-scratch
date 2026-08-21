"""Static, source-backed data for the SIA India registration PoC.

This module intentionally contains no personal identifiers. Scheme facts are kept
as qualitative metadata with an as-of date so the UI cannot imply a grant award
or guarantee a current call.
"""

from copy import deepcopy

VERIFIED_ON = "2026-08-21"

DEFAULT_DRAFT = {
    "company_name": "SIA AI PRIVATE LIMITED",
    "alternate_name": "SIA PRIVATE LIMITED",
    "state": "Bihar",
    "district": "Madhubani",
    "city": "Madhubani",
    "address_line": "",
    "postal_code": "",
    "founder_name": "",
    "founder_email": "",
    "founder_phone": "",
    "founder_age": "",
    "founder_status": "student",
    "social_category": "OBC",
    "university": "",
    "has_second_member": False,
    "second_member_name": "",
    "has_second_director": False,
    "second_director_name": "",
    "ai_product": "",
    "target_users": "",
    "data_type": "",
    "company_object": "Build and commercialise privacy-preserving AI software and related research products.",
    "authorised_capital": "",
    "paid_up_capital": "",
    "shareholding_notes": "",
    "office_proof_uploaded": False,
    "director_proofs_uploaded": False,
    "dsc_status": "not_started",
    "dpiit_status": "not_incorporated",
    "incorporation_stage": "pre_incorporation",
    "last_saved": None,
}

CHECKLIST = [
    {"id": "company-name", "title": "Proposed company name and alternate", "section": "Company identity", "kind": "field", "hint": "Provide a preferred name and a fallback name for professional review."},
    {"id": "ai-description", "title": "AI product, users, and data description", "section": "Company identity", "kind": "field", "hint": "Explain the problem, product, target users, and data type in plain language."},
    {"id": "second-member", "title": "Second member/subscriber identified", "section": "People and ownership", "kind": "gate", "hint": "A Private Limited Company cannot be treated as complete until the required second member is addressed."},
    {"id": "second-director", "title": "Second director identified", "section": "People and ownership", "kind": "gate", "hint": "The PoC keeps this as an explicit professional-review gate."},
    {"id": "founder-proof", "title": "Founder identity and address proofs", "section": "Documents", "kind": "document", "hint": "Use safe demo metadata only; do not paste real PAN or Aadhaar values here."},
    {"id": "director-proofs", "title": "Director/member proof metadata", "section": "Documents", "kind": "document", "hint": "Collect document type and review status, not raw identity numbers."},
    {"id": "registered-office", "title": "Madhubani registered-office proof and owner consent", "section": "Documents", "kind": "document", "hint": "A Bihar operating address must be evidenced before marking the profile ready."},
    {"id": "dsc", "title": "Digital Signature Certificate plan", "section": "MCA preparation", "kind": "choice", "hint": "Confirm the DSC route with a professional before filing."},
    {"id": "capital", "title": "Authorised, paid-up capital, and shareholding plan", "section": "MCA preparation", "kind": "field", "hint": "Enter a professional-reviewed capital and ownership plan; do not assume a default amount."},
    {"id": "spice", "title": "SPICe+ and linked-form field map reviewed", "section": "MCA preparation", "kind": "review", "hint": "The PoC exports a field map; it does not submit or sign MCA forms."},
    {"id": "post-incorporation", "title": "Post-incorporation actions planned", "section": "After incorporation", "kind": "review", "hint": "Plan PAN/TAN, bank, auditor, commencement, GST/Udyam, and DPIIT decisions."},
]

SOURCES = {
    "mca": {"label": "Ministry of Corporate Affairs", "url": "https://www.mca.gov.in/"},
    "dpiit": {"label": "DPIIT Startup Recognition", "url": "https://www.startupindia.gov.in/content/sih/en/startupgov/startup_recognition_page.html"},
    "startup-scheme": {"label": "Startup India Scheme", "url": "https://www.startupindia.gov.in/content/sih/en/startup-scheme.html"},
    "sisfs": {"label": "Startup India Seed Fund Scheme", "url": "https://seedfund.startupindia.gov.in/"},
    "startup-schemes": {"label": "Startup India Government Schemes", "url": "https://www.startupindia.gov.in/content/sih/en/government-schemes.html"},
    "bihar": {"label": "Bihar Startup Portal", "url": "https://startup.bihar.gov.in/"},
    "tide": {"label": "MeitY Startup Hub: TIDE 2.0", "url": "https://msh.meity.gov.in/schemes/tide"},
    "samridh": {"label": "MeitY Startup Hub: SAMRIDH", "url": "https://msh.meity.gov.in/schemes/samridh"},
    "indiaai": {"label": "IndiaAI Compute Capacity", "url": "https://indiaai.gov.in/hub/indiaai-compute-capacity"},
    "airawat": {"label": "C-DAC AIRAWAT Outreach", "url": "https://airawat.cdac.in/airawat/outreachandeducation"},
}

PROGRAMS = [
    {
        "id": "dpiit-recognition",
        "name": "DPIIT Startup Recognition",
        "owner": "DPIIT / Startup India",
        "support_type": "enabling_status",
        "stage": "post_incorporation",
        "geography": "India",
        "sector": "technology / innovation",
        "founder_condition": "No OBC-specific entitlement assumed.",
        "requirements": ["Private Limited Company or another permitted entity", "innovation/technology narrative", "current recognition criteria"],
        "status": "conditional",
        "confidence": "official-source route; current criteria must be checked",
        "next_step": "Incorporate first, then verify the current Startup India recognition form and criteria.",
        "source": "dpiit",
        "note": "Recognition is not a grant and does not automatically award any other benefit.",
    },
    {
        "id": "sisfs",
        "name": "Startup India Seed Fund Scheme",
        "owner": "DPIIT / Startup India",
        "support_type": "direct_grant_or_seed_support",
        "stage": "prototype / early validation",
        "geography": "India through approved incubators",
        "sector": "technology / innovation",
        "founder_condition": "Student status may support the narrative but is not sufficient by itself.",
        "requirements": ["current scheme eligibility", "innovation/PoC evidence", "application through an approved incubator", "company-age and recognition checks"],
        "status": "conditional",
        "confidence": "official portal; call and incubator availability must be verified",
        "next_step": "Prepare a technical dossier and identify approved incubators accepting current applications.",
        "source": "sisfs",
        "note": "The PoC never treats selection as guaranteed and does not hardcode an award amount.",
    },
    {
        "id": "bihar-policy",
        "name": "Bihar Startup Policy support",
        "owner": "Government of Bihar",
        "support_type": "state_support_verify_grant_or_loan",
        "stage": "pre / post incorporation",
        "geography": "Bihar, subject to local-presence rules",
        "sector": "startup / innovation",
        "founder_condition": "Madhubani base is a relevant fact; OBC benefit is not assumed without a scheme rule.",
        "requirements": ["genuine Bihar operations", "current Bihar portal call", "entity and founder documents", "scheme-specific review"],
        "status": "conditional",
        "confidence": "official portal route; support type and current call must be verified",
        "next_step": "Confirm the current Bihar policy notification, application window, support type, and local evidence requirements.",
        "source": "bihar",
        "note": "The UI deliberately distinguishes repayable seed support from a non-repayable grant.",
    },
    {
        "id": "nidhi-incubator",
        "name": "NIDHI-linked prototype / incubator routes",
        "owner": "Department of Science & Technology / approved incubators",
        "support_type": "incubator_linked_support",
        "stage": "prototype",
        "geography": "India through participating institutions",
        "sector": "technology / innovation",
        "founder_condition": "Student and incubator affiliation may matter for a particular call.",
        "requirements": ["specific program call", "incubator or institutional route", "prototype plan", "current eligibility"],
        "status": "requires_verification",
        "confidence": "candidate route; verify the current program and incubator",
        "next_step": "Find an eligible incubator or university program and ask whether the current call accepts this profile.",
        "source": "startup-schemes",
        "note": "No amount or deadline is hardcoded because the exact NIDHI track is not yet selected.",
    },
    {
        "id": "tide-2",
        "name": "MeitY TIDE 2.0",
        "owner": "MeitY Startup Hub",
        "support_type": "incubator_linked_support",
        "stage": "technology prototype / early startup",
        "geography": "India through participating incubators",
        "sector": "emerging technology",
        "founder_condition": "OBC status is not a universal TIDE entitlement.",
        "requirements": ["participating incubator", "current call", "technology and prototype fit", "application documents"],
        "status": "conditional",
        "confidence": "official scheme page; current incubator call must be verified",
        "next_step": "Prepare the problem, product, technical novelty, milestones, and budget for a participating incubator.",
        "source": "tide",
        "note": "This is shown as incubator-linked support, not as an automatic direct grant.",
    },
    {
        "id": "samridh",
        "name": "MeitY SAMRIDH",
        "owner": "MeitY Startup Hub",
        "support_type": "accelerator_or_co_investment",
        "stage": "validation / scale",
        "geography": "India through selected accelerators",
        "sector": "technology startup",
        "founder_condition": "Student status alone does not establish later-stage fit.",
        "requirements": ["current accelerator cohort", "product traction or readiness", "technology fit", "program-specific terms"],
        "status": "not_yet_stage_fit",
        "confidence": "official scheme page; current cohort terms must be verified",
        "next_step": "Reassess after a demonstrable PoC, user evidence, and an accelerator-ready application.",
        "source": "samridh",
        "note": "Possible accelerator or co-investment support is not the same as a non-repayable grant.",
    },
    {
        "id": "indiaai-compute",
        "name": "IndiaAI Compute",
        "owner": "IndiaAI / MeitY",
        "support_type": "in_kind_compute_or_discount",
        "stage": "prototype / training / inference",
        "geography": "India through the current portal and allocation rules",
        "sector": "AI workloads",
        "founder_condition": "Company status, workload, allocation, and current portal rules must be checked.",
        "requirements": ["current portal eligibility", "technical workload description", "capacity/approval", "budget and usage plan"],
        "status": "conditional",
        "confidence": "official infrastructure page; allocation and price must be verified at application time",
        "next_step": "Prepare a small benchmark, GPU-memory requirement, hours estimate, and reproducible training plan.",
        "source": "indiaai",
        "note": "The planner never promises a specific GPU, quota, discount, or rental duration.",
    },
    {
        "id": "airawat",
        "name": "C-DAC AIRAWAT / outreach and education routes",
        "owner": "C-DAC",
        "support_type": "in_kind_compute_or_institutional_access",
        "stage": "research / prototype",
        "geography": "India through current outreach route",
        "sector": "AI / research",
        "founder_condition": "Startups, MSMEs, academia, or research institutions may be treated differently by a call.",
        "requirements": ["current outreach or challenge", "technical proposal", "institutional/program fit", "available capacity"],
        "status": "requires_verification",
        "confidence": "official outreach page; current route and access rules must be verified",
        "next_step": "Track current outreach calls and prepare a concise compute proposal with benchmarks and responsible-use safeguards.",
        "source": "airawat",
        "note": "This is infrastructure access, not a cash grant.",
    },
]


def default_draft():
    return deepcopy(DEFAULT_DRAFT)


def checklist():
    return deepcopy(CHECKLIST)


def programs():
    return deepcopy(PROGRAMS)


def sources():
    return deepcopy(SOURCES)
