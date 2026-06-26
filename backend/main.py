"""
main.py — FastAPI application for the Email Resume Bulk Sender.

Endpoints:
    GET  /profile              — user profile from .env
    GET  /roles                — list all available role templates
    GET  /roles/{key}/skills   — categorized skills for a role
    GET  /message-templates    — list message template options
    POST /message-preview      — preview composed subject + body
    GET  /records              — list all queued records
    POST /records              — create a new record
    PUT  /records/{id}         — update a record
    DELETE /records/{id}       — delete a single record
    POST /records/{id}/send    — send one record, delete on success
    POST /send-all             — send all records, delete successful ones
    POST /validate-email       — validate an email address (syntax + MX + SMTP)
    GET  /resume/{key}/pdf     — download cached PDF resume
    GET  /resume/{key}/latex   — download auto-generated LaTeX resume
    POST /resumes/generate     — regenerate all cached PDFs
    GET  /resumes/status       — check if resume cache is ready
    POST /resume/compile-latex — compile raw LaTeX to PDF (auto-downloads tectonic)
"""

import os
import ssl
import smtplib
import logging
from io import BytesIO
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from email.message import EmailMessage

from database import Base, SessionLocal, engine
from models import Record
from email_checker import validate_email_full
from resume_templates import (
    get_template,
    list_templates,
    generate_pdf_resume,
    make_latex_resume,
    ROLE_TEMPLATES,
)

logger = logging.getLogger(__name__)

load_dotenv()

Base.metadata.create_all(bind=engine)

IS_VERCEL = os.environ.get("VERCEL") == "1"

if IS_VERCEL:
    RESUME_DIR = Path("/tmp/generated_resumes")
else:
    RESUME_DIR = Path(__file__).parent / "generated_resumes"
RESUME_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title="Email Resume Bulk Sender",
    description="Queue HR emails, auto-generate role-specific resumes, "
                "and bulk-send with one click.",
)

_origins = ["http://localhost:3000"]
_frontend_urls = os.getenv("FRONTEND_URL", "")
for _url in _frontend_urls.split(","):
    _url = _url.strip()
    if _url:
        _origins.append(_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if IS_VERCEL and len(_origins) == 1 else _origins,
    allow_credentials=not IS_VERCEL or len(_origins) > 1,
    allow_methods=["*"],
    allow_headers=["*"],
)


MESSAGE_TEMPLATES = {

    "job_apply": {
        "label": "Job Application",
        "subject": "Application for {role_title} -- {your_name} | Ready for Immediate Joining",
        "body": (
            "Dear {hr_name},\n\n"
            "I am writing to apply for the {role_title} position"
            "{at_company}. I have strong hands-on experience in "
            "{top_skills}, and I am confident I can deliver results "
            "from day one.\n\n"
            "Here is what I bring to your team:\n\n"
            "  - Proven expertise in {top_skills} with real project outcomes\n"
            "  - A track record of solving complex problems and delivering on tight deadlines\n"
            "  - Strong collaboration skills and a passion for building quality solutions\n\n"
            "I have attached my resume which details my projects, technical skills, "
            "and measurable achievements that directly align with this role.\n\n"
            "I am available for an interview at your earliest convenience and "
            "can join immediately. A quick 15-minute call would be a great start "
            "-- I would love to show you how I can add value to your team.\n\n"
            "Looking forward to hearing from you.\n\n"
            "Best regards,\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },

    "interview_schedule": {
        "label": "Interview Scheduling",
        "subject": "Re: Interview Scheduling -- {role_title} | {your_name} (Available This Week)",
        "body": (
            "Dear {hr_name},\n\n"
            "Thank you for shortlisting me for the {role_title} role"
            "{at_company} -- I am thrilled about this opportunity and "
            "eager to discuss how my skills in {top_skills} can directly "
            "contribute to your team's goals.\n\n"
            "I am flexible and available at the following times:\n\n"
            "    Weekdays:   10:00 AM -- 12:00 PM IST\n"
            "                 2:00 PM --  5:00 PM IST\n"
            "    Saturdays:  10:00 AM --  1:00 PM IST\n\n"
            "I am happy to work around your schedule -- please suggest any "
            "other time slot and I will confirm right away.\n\n"
            "My updated resume is attached for your reference. I am excited "
            "to walk you through my projects and demonstrate how my experience "
            "aligns with what you are looking for.\n\n"
            "Looking forward to connecting soon.\n\n"
            "Best regards,\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },

    "follow_up": {
        "label": "Follow Up",
        "subject": "Following Up: {role_title} Application -- {your_name} | Still Very Interested",
        "body": (
            "Dear {hr_name},\n\n"
            "I hope you are doing well. I recently applied for the "
            "{role_title} position{at_company} and wanted to follow up "
            "as I am genuinely excited about this opportunity.\n\n"
            "To quickly recap what I bring:\n\n"
            "  - Strong hands-on experience in {top_skills}\n"
            "  - Real project outcomes with measurable business impact\n"
            "  - Immediate availability and readiness to contribute from day one\n\n"
            "I understand the hiring process takes time, but I wanted to "
            "reaffirm my strong interest in this role. I am confident that "
            "even a brief conversation would demonstrate why I am a strong "
            "fit for your team.\n\n"
            "I have re-attached my resume for your convenience. Would it be "
            "possible to schedule a quick call this week?\n\n"
            "Thank you for your time.\n\n"
            "Best regards,\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },

    "thank_you": {
        "label": "Thank You (Post-Interview)",
        "subject": "Thank You for the {role_title} Interview -- {your_name} | Excited to Join",
        "body": (
            "Dear {hr_name},\n\n"
            "Thank you for taking the time to interview me for the "
            "{role_title} position{at_company}. I really enjoyed our "
            "conversation and learning more about the team and the "
            "exciting challenges ahead.\n\n"
            "After our discussion, I am even more enthusiastic about this "
            "role. A few things I want to highlight:\n\n"
            "  - My experience in {top_skills} maps directly to the problems "
            "your team is solving\n"
            "  - I am ready to hit the ground running and deliver results quickly\n"
            "  - I am genuinely passionate about the work your organization is doing\n\n"
            "I am very excited about the possibility of joining your team and "
            "contributing to its success. Please do not hesitate to reach out "
            "if you need any additional information from my side.\n\n"
            "Looking forward to the next steps.\n\n"
            "Warm regards,\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },

    "referral": {
        "label": "Referral Request",
        "subject": "Would You Refer Me? {role_title} Role{at_company} -- {your_name}",
        "body": (
            "Dear {hr_name},\n\n"
            "I hope you are doing well. I came across the {role_title} "
            "opening{at_company} and I believe it is a great match for "
            "my background.\n\n"
            "Here is a quick snapshot of what I bring:\n\n"
            "  - Strong expertise in {top_skills}\n"
            "  - Hands-on project experience with proven, measurable results\n"
            "  - Ready to contribute immediately and make an impact\n\n"
            "I would be truly grateful if you could refer me for this role "
            "or connect me with the right person on the hiring team. Even a "
            "brief introduction would mean a lot.\n\n"
            "I have attached my resume for your review -- it covers my "
            "projects, skills, and achievements in detail.\n\n"
            "Thank you so much for your time and support.\n\n"
            "Warm regards,\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },

    "cold_outreach": {
        "label": "Cold Outreach",
        "subject": "Experienced {role_title} -- Actively Seeking Opportunities{at_company} | {your_name}",
        "body": (
            "Dear {hr_name},\n\n"
            "I am a {role_title} with strong hands-on experience in "
            "{top_skills}, and I am actively looking for my next opportunity "
            "where I can create real impact.\n\n"
            "Here is what I can bring to your organization:\n\n"
            "  - Proven skills in {top_skills} backed by real project outcomes\n"
            "  - Ability to quickly adapt, learn, and deliver in fast-paced environments\n"
            "  - A problem-solving mindset focused on driving measurable results\n\n"
            "I have attached my resume which covers my projects, achievements, "
            "and technical expertise in detail. I would love the chance to have "
            "a quick 10-15 minute conversation to explore if there is a fit "
            "within your team.\n\n"
            "Even if there are no current openings, I would appreciate being "
            "kept in mind for future roles. I am available for a call at your "
            "convenience.\n\n"
            "Thank you for your time.\n\n"
            "Best regards,\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },

    "custom": {
        "label": "Custom Message",
        "subject": "",
        "body": "",
    },
}


# ── Pydantic schemas ──────────────────────────────────────────────────────

class RecordCreate(BaseModel):
    to_email: EmailStr
    cc_emails: str = ""
    hr_name: str = ""
    company_name: str = ""
    role_key: str = ""
    message_type: str = "job_apply"
    custom_subject: str = ""
    custom_body: str = ""


class RecordOut(BaseModel):
    id: int
    to_email: str
    cc_emails: str
    hr_name: str
    company_name: str
    role_key: str
    message_type: str
    custom_subject: str
    custom_body: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class SendResult(BaseModel):
    sent: int
    failed: int
    errors: list[dict]


class PreviewRequest(BaseModel):
    message_type: str = "job_apply"
    hr_name: str = ""
    company_name: str = ""
    role_key: str = ""
    custom_subject: str = ""
    custom_body: str = ""


class ValidateEmailRequest(BaseModel):
    email: str
    skip_smtp: bool = False


class CustomResumeRequest(BaseModel):
    role_key: str = ""
    custom_name: str = ""
    custom_email: str = ""
    custom_phone: str = ""
    custom_location: str = ""
    custom_linkedin: str = ""
    custom_github: str = ""
    custom_portfolio: str = ""
    custom_education: str = ""
    custom_graduation_year: str = ""
    custom_summary: str = ""
    custom_skills: dict = {}
    custom_company_1_name: str = ""
    custom_company_1_role: str = ""
    custom_company_1_location: str = ""
    custom_company_1_duration: str = ""
    custom_company_2_name: str = ""
    custom_company_2_role: str = ""
    custom_company_2_location: str = ""
    custom_company_2_duration: str = ""


class CompileLatexRequest(BaseModel):
    latex: str
    filename: str = "resume.pdf"


class UpdateCCRequest(BaseModel):
    cc_emails: str = ""


# ── Helpers ───────────────────────────────────────────────────────────────

def _get_profile() -> dict:
    return {
        "name": os.getenv("YOUR_NAME", ""),
        "email": os.getenv("YOUR_EMAIL", ""),
        "phone": os.getenv("YOUR_PHONE", ""),
        "location": os.getenv("YOUR_LOCATION", ""),
        "linkedin": os.getenv("YOUR_LINKEDIN", ""),
        "github": os.getenv("YOUR_GITHUB", ""),
        "portfolio": os.getenv("YOUR_PORTFOLIO", ""),
        "education": os.getenv("YOUR_EDUCATION", ""),
        "graduation_year": os.getenv("YOUR_GRADUATION_YEAR", ""),
        "company_1_name": os.getenv("COMPANY_1_NAME", ""),
        "company_1_role": os.getenv("COMPANY_1_ROLE", ""),
        "company_1_location": os.getenv("COMPANY_1_LOCATION", ""),
        "company_1_duration": os.getenv("COMPANY_1_DURATION", ""),
        "company_2_name": os.getenv("COMPANY_2_NAME", ""),
        "company_2_role": os.getenv("COMPANY_2_ROLE", ""),
        "company_2_location": os.getenv("COMPANY_2_LOCATION", ""),
        "company_2_duration": os.getenv("COMPANY_2_DURATION", ""),
    }


def _get_smtp_settings() -> tuple:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "465"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM", user)
    if not host or not user or not password:
        raise HTTPException(
            status_code=500,
            detail="SMTP not configured. Set SMTP_HOST, SMTP_USER, "
                   "SMTP_PASSWORD in .env",
        )
    return host, port, user, password, sender


def _get_role_title(role_key: str) -> str:
    template = get_template(role_key)
    if template:
        return template["title"]
    return role_key.replace("_", " ").title() if role_key else "Professional"


def _get_top_skills(role_key: str, count: int = 5) -> str:
    template = get_template(role_key)
    if template:
        all_skills = [s for vals in template["skills"].values() for s in vals]
        return ", ".join(all_skills[:count])
    return "modern technologies and tools"


def _compose_message(message_type: str, hr_name: str, company_name: str,
                     role_key: str, custom_subject: str = "",
                     custom_body: str = "") -> tuple[str, str]:
    if message_type == "custom" and custom_subject and custom_body:
        return custom_subject, custom_body

    if custom_subject and custom_body:
        return custom_subject, custom_body

    profile = _get_profile()
    tmpl = MESSAGE_TEMPLATES.get(message_type, MESSAGE_TEMPLATES["job_apply"])

    at_company = f" at {company_name}" if company_name.strip() else ""

    replacements = {
        "hr_name": hr_name.strip() if hr_name.strip() else "Sir/Madam",
        "at_company": at_company,
        "role_title": _get_role_title(role_key),
        "top_skills": _get_top_skills(role_key),
        "your_name": profile["name"] or "Applicant",
        "your_email": profile["email"] or "",
        "your_phone": profile["phone"] or "",
    }

    subject = custom_subject if custom_subject else tmpl["subject"].format(**replacements)
    body = custom_body if custom_body else tmpl["body"].format(**replacements)
    return subject, body


def _parse_cc_emails(cc_string: str) -> list[str]:
    if not cc_string or not cc_string.strip():
        return []
    return [e.strip().lower() for e in cc_string.split(",") if e.strip()]


def _validate_and_filter_cc(cc_list: list[str], from_email: str) -> tuple[list[str], list[dict]]:
    valid = []
    skipped = []
    for cc in cc_list:
        result = validate_email_full(cc, from_email, skip_smtp=True)
        if result["valid"]:
            valid.append(cc)
        else:
            skipped.append({"email": cc, "reason": result["reason"]})
    return valid, skipped


def _generate_all_resumes():
    profile = _get_profile()
    count = 0
    for template in ROLE_TEMPLATES:
        key = template["key"]
        pdf_path = RESUME_DIR / f"{key}.pdf"
        try:
            pdf_bytes = generate_pdf_resume(key, profile)
            pdf_path.write_bytes(pdf_bytes)
            count += 1
        except Exception as exc:
            logger.warning("Failed to generate resume for %s: %s", key, exc)
    logger.info("Generated %d resume PDFs in %s", count, RESUME_DIR)
    return count


def _get_cached_resume(role_key: str) -> bytes:
    pdf_path = RESUME_DIR / f"{role_key}.pdf"
    if pdf_path.exists():
        return pdf_path.read_bytes()
    profile = _get_profile()
    pdf_bytes = generate_pdf_resume(role_key, profile)
    pdf_path.write_bytes(pdf_bytes)
    return pdf_bytes


if not IS_VERCEL:
    _generate_all_resumes()


def _send_email(to_email: str, subject: str, body: str,
                pdf_bytes: bytes, pdf_filename: str,
                cc_emails: list[str] | None = None):
    host, port, user, password, sender = _get_smtp_settings()

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email
    if cc_emails:
        msg["Cc"] = ", ".join(cc_emails)
    msg.set_content(body)

    msg.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=pdf_filename,
    )

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(user, password)
        all_recipients = [to_email] + (cc_emails or [])
        server.send_message(msg, to_addrs=all_recipients)


def _send_single_record(record: Record, db: Session) -> dict:
    profile = _get_profile()
    from_email = os.getenv("SMTP_FROM", os.getenv("SMTP_USER", ""))

    to_result = validate_email_full(record.to_email, from_email)
    if not to_result["valid"]:
        return {
            "id": record.id,
            "status": "failed",
            "error": f"TO validation failed: {to_result['reason']}",
            "checks": to_result["checks"],
        }

    cc_list = _parse_cc_emails(record.cc_emails)
    valid_cc, skipped_cc = _validate_and_filter_cc(cc_list, from_email)

    subject, body = _compose_message(
        record.message_type,
        record.hr_name,
        record.company_name,
        record.role_key,
        record.custom_subject,
        record.custom_body,
    )

    try:
        pdf_bytes = _get_cached_resume(record.role_key)
    except Exception:
        pdf_bytes = _get_cached_resume("ai_ml_engineer")

    name_slug = (profile.get("name") or "Resume").replace(" ", "_")
    role_slug = _get_role_title(record.role_key).replace(" ", "_")
    pdf_filename = f"{name_slug}_{role_slug}_Resume.pdf"

    try:
        _send_email(record.to_email, subject, body, pdf_bytes, pdf_filename,
                    cc_emails=valid_cc)
    except Exception as exc:
        return {
            "id": record.id,
            "status": "failed",
            "error": str(exc),
            "skipped_cc": skipped_cc,
        }

    db.delete(record)
    return {
        "id": record.id,
        "status": "sent",
        "cc_sent": valid_cc,
        "skipped_cc": skipped_cc,
    }


def _get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── API Endpoints ─────────────────────────────────────────────────────────

@app.get("/profile")
def get_profile():
    return _get_profile()


@app.get("/roles")
def get_roles():
    return list_templates()


@app.get("/roles/{role_key}/skills")
def get_role_skills(role_key: str):
    template = get_template(role_key)
    if not template:
        raise HTTPException(status_code=404, detail="Role not found")
    return [
        {"category": cat, "skills": skills}
        for cat, skills in template["skills"].items()
    ]


@app.get("/message-templates")
def get_message_templates():
    return [
        {"key": key, "label": tmpl["label"]}
        for key, tmpl in MESSAGE_TEMPLATES.items()
    ]


@app.post("/message-preview")
def preview_message(req: PreviewRequest):
    subject, body = _compose_message(
        req.message_type, req.hr_name, req.company_name, req.role_key,
        req.custom_subject, req.custom_body,
    )
    return {"subject": subject, "body": body}


@app.post("/validate-email")
def validate_email_endpoint(req: ValidateEmailRequest):
    from_email = os.getenv("SMTP_FROM", os.getenv("SMTP_USER", ""))
    result = validate_email_full(req.email, from_email, skip_smtp=req.skip_smtp)
    return result


@app.get("/resume/{role_key}/pdf")
def download_resume_pdf(role_key: str):
    template = get_template(role_key)
    if not template:
        raise HTTPException(status_code=404, detail="Role not found")
    pdf_bytes = _get_cached_resume(role_key)
    profile = _get_profile()
    name_slug = (profile.get("name") or "Resume").replace(" ", "_")
    filename = f"{name_slug}_{template['title'].replace(' ', '_')}_Resume.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/resume/{role_key}/latex", response_class=PlainTextResponse)
def download_resume_latex(role_key: str):
    template = get_template(role_key)
    if not template:
        raise HTTPException(status_code=404, detail="Role not found")
    profile = _get_profile()
    return make_latex_resume(template, profile)


@app.post("/resume/custom")
def generate_custom_resume(req: CustomResumeRequest):
    """Generate a custom PDF resume with user-provided overrides."""
    from resume_templates import generate_pdf_resume, get_template
    import copy

    base_profile = _get_profile()
    profile = {
        "name": req.custom_name or base_profile["name"],
        "email": req.custom_email or base_profile["email"],
        "phone": req.custom_phone or base_profile["phone"],
        "location": req.custom_location or base_profile["location"],
        "linkedin": req.custom_linkedin or base_profile["linkedin"],
        "github": req.custom_github or base_profile["github"],
        "portfolio": req.custom_portfolio or base_profile["portfolio"],
        "education": req.custom_education or base_profile["education"],
        "graduation_year": req.custom_graduation_year or base_profile["graduation_year"],
        "company_1_name": req.custom_company_1_name or base_profile["company_1_name"],
        "company_1_role": req.custom_company_1_role or base_profile.get("company_1_role", ""),
        "company_1_location": req.custom_company_1_location or base_profile["company_1_location"],
        "company_1_duration": req.custom_company_1_duration or base_profile["company_1_duration"],
        "company_2_name": req.custom_company_2_name or base_profile["company_2_name"],
        "company_2_role": req.custom_company_2_role or base_profile.get("company_2_role", ""),
        "company_2_location": req.custom_company_2_location or base_profile["company_2_location"],
        "company_2_duration": req.custom_company_2_duration or base_profile["company_2_duration"],
    }

    role_key = req.role_key or "software_engineer"
    template = get_template(role_key)
    if not template:
        raise HTTPException(status_code=404, detail="Role not found")

    if req.custom_summary or req.custom_skills:
        from resume_templates import ROLE_TEMPLATES, _ResumePDF
        tmpl = copy.deepcopy(template)
        if req.custom_summary:
            tmpl["summary"] = req.custom_summary
        if req.custom_skills:
            tmpl["skills"] = req.custom_skills
        pdf_bytes = _generate_from_template(tmpl, profile)
    else:
        pdf_bytes = generate_pdf_resume(role_key, profile)

    name_slug = (profile.get("name") or "Resume").replace(" ", "_")
    role_slug = template["title"].replace(" ", "_")
    filename = f"{name_slug}_{role_slug}_Resume.pdf"

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


_TECTONIC_DIR = Path(__file__).parent / "bin"


def _find_latex_compiler() -> tuple[str, str]:
    """Find a LaTeX compiler. Auto-downloads tectonic if none found."""
    import shutil as _shutil

    for cmd in ("tectonic", "pdflatex", "xelatex", "lualatex"):
        path = _shutil.which(cmd)
        if path:
            return path, cmd

    local = _TECTONIC_DIR / "tectonic"
    if local.exists() and os.access(str(local), os.X_OK):
        return str(local), "tectonic"

    return _download_tectonic(), "tectonic"


def _download_tectonic() -> str:
    """Download tectonic binary from GitHub releases (no sudo needed)."""
    import platform
    import urllib.request
    import tarfile
    import zipfile
    import json

    _TECTONIC_DIR.mkdir(parents=True, exist_ok=True)
    target = _TECTONIC_DIR / "tectonic"

    machine = platform.machine().lower()
    system = platform.system().lower()

    if machine in ("x86_64", "amd64"):
        arch = "x86_64"
    elif machine in ("aarch64", "arm64"):
        arch = "aarch64"
    else:
        raise RuntimeError(f"Unsupported architecture: {machine}")

    logger.info("Downloading tectonic binary (arch=%s, os=%s)...", arch, system)

    api_url = "https://api.github.com/repos/tectonic-typesetting/tectonic/releases/latest"
    req = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github+json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        release = json.loads(resp.read())

    asset_url = None
    for asset in release.get("assets", []):
        name = asset["name"].lower()
        if arch in name and system in name and (name.endswith(".tar.gz") or name.endswith(".zip")):
            asset_url = asset["browser_download_url"]
            break

    if not asset_url:
        names = [a["name"] for a in release.get("assets", [])]
        raise RuntimeError(
            f"Could not find tectonic binary for {system}/{arch}. "
            f"Available: {names}"
        )

    logger.info("Downloading %s", asset_url)
    dl_path = _TECTONIC_DIR / "tectonic_download"
    urllib.request.urlretrieve(asset_url, str(dl_path))

    if asset_url.endswith(".tar.gz"):
        with tarfile.open(str(dl_path), "r:gz") as tf:
            for member in tf.getmembers():
                if member.name.endswith("tectonic") or member.name == "tectonic":
                    member.name = "tectonic"
                    tf.extract(member, path=str(_TECTONIC_DIR))
                    break
    elif asset_url.endswith(".zip"):
        with zipfile.ZipFile(str(dl_path)) as zf:
            for name in zf.namelist():
                if name.endswith("tectonic") or name == "tectonic":
                    data = zf.read(name)
                    target.write_bytes(data)
                    break

    dl_path.unlink(missing_ok=True)

    if not target.exists():
        raise RuntimeError("Failed to extract tectonic binary from download")

    target.chmod(0o755)
    logger.info("Tectonic installed to %s", target)
    return str(target)


@app.post("/resume/compile-latex")
def compile_latex_to_pdf(req: CompileLatexRequest):
    """Compile raw LaTeX source to PDF using tectonic or pdflatex."""
    import subprocess
    import tempfile

    try:
        compiler_path, compiler_name = _find_latex_compiler()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = Path(tmpdir) / "resume.tex"
        tex_path.write_text(req.latex, encoding="utf-8")

        if compiler_name == "tectonic":
            cmd = [compiler_path, "--outdir", tmpdir, str(tex_path)]
        else:
            cmd = [compiler_path, "-interaction=nonstopmode", "-halt-on-error",
                   "-output-directory", tmpdir, str(tex_path)]
            # Run twice for cross-references
            subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        pdf_path = Path(tmpdir) / "resume.pdf"
        if not pdf_path.exists():
            log_path = Path(tmpdir) / "resume.log"
            log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.exists() else ""
            error_lines = [l for l in log_text.splitlines() if l.startswith("!")]
            stderr = result.stderr or ""
            stdout = result.stdout or ""
            if error_lines:
                detail = "\n".join(error_lines[:10])
            elif stderr:
                detail = stderr[-2000:]
            elif stdout:
                detail = stdout[-2000:]
            else:
                detail = "Compilation failed with no output"
            raise HTTPException(status_code=422, detail=detail)

        pdf_bytes = pdf_path.read_bytes()

    filename = req.filename if req.filename.endswith(".pdf") else req.filename + ".pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _generate_from_template(template: dict, profile: dict) -> bytes:
    """Generate PDF from a modified template dict."""
    from resume_templates import _ResumePDF, _sanitize

    name = (profile.get("name") or "YOUR NAME").upper()
    email = profile.get("email") or ""
    phone = profile.get("phone") or ""
    location = profile.get("location") or ""
    linkedin = (profile.get("linkedin") or "").replace("https://", "").rstrip("/")
    github = (profile.get("github") or "").replace("https://", "").rstrip("/")
    portfolio = (profile.get("portfolio") or "").replace("https://", "").rstrip("/")
    education = profile.get("education") or ""
    grad_year = profile.get("graduation_year") or ""

    pdf = _ResumePDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(w=0, h=9, text=name, align="C", new_x="LMARGIN", new_y="NEXT")

    contact_parts = [p for p in [email, phone, location] if p]
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(w=0, h=4.5, text="  |  ".join(contact_parts),
             align="C", new_x="LMARGIN", new_y="NEXT")

    link_parts = [p for p in [linkedin, github, portfolio] if p]
    if link_parts:
        pdf.cell(w=0, h=4.5, text="  |  ".join(link_parts),
                 align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.section_header("Professional Summary")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(w=0, h=4, text=template["summary"])
    pdf.ln(1.5)

    pdf.section_header("Technical Skills")
    for category, skill_list in template["skills"].items():
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(w=38, h=4.5, text=f"{category}:")
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(w=0, h=4.5, text=", ".join(skill_list))
        pdf.ln(0.2)
    pdf.ln(1)

    pdf.section_header("Professional Experience")
    c1_name = profile.get("company_1_name") or "Current Company"
    c1_loc = profile.get("company_1_location") or ""
    c1_dur = profile.get("company_1_duration") or "Jan 2024 -- Present"
    c2_name = profile.get("company_2_name") or "Previous Company"
    c2_loc = profile.get("company_2_location") or ""
    c2_dur = profile.get("company_2_duration") or "Jul 2022 -- Dec 2023"

    exp = template["experience"]
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(w=0, h=5, text=template["title"])
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(w=0, h=5, text=c1_dur, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(w=0, h=4, text=", ".join(p for p in [c1_name, c1_loc] if p),
             new_x="LMARGIN", new_y="NEXT")
    if len(exp) > 0:
        for b in exp[0].get("bullets", []):
            pdf.bullet(b)
    pdf.ln(1)

    prev_title = template.get("previous_title", f"Junior {template['title']}")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(w=0, h=5, text=prev_title)
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(w=0, h=5, text=c2_dur, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(w=0, h=4, text=", ".join(p for p in [c2_name, c2_loc] if p),
             new_x="LMARGIN", new_y="NEXT")
    if len(exp) > 1:
        for b in exp[1].get("bullets", []):
            pdf.bullet(b)
    pdf.ln(1)

    pdf.section_header("Key Projects")
    for project in template["projects"]:
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(w=0, h=5, text=project["name"])
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(w=0, h=5, text=project["stack"], align="R", new_x="LMARGIN", new_y="NEXT")
        for b in project["bullets"]:
            pdf.bullet(b)
        pdf.ln(0.5)
    pdf.ln(0.5)

    pdf.section_header("Education")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(w=0, h=5, text=education)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(w=0, h=5, text=grad_year, align="R", new_x="LMARGIN", new_y="NEXT")
    cw = template.get("coursework", "Data Structures, Algorithms, Databases, Statistics, Software Engineering")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(w=0, h=4, text=f"Relevant coursework: {cw}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    pdf.section_header("Certifications")
    for cert in template["certifications"]:
        pdf.bullet(cert, indent=2)
    pdf.ln(0.5)

    pdf.section_header("Achievements")
    for ach in template["achievements"]:
        pdf.bullet(ach, indent=2)

    return bytes(pdf.output())


@app.patch("/records/{record_id}/cc")
def update_record_cc(record_id: int, data: UpdateCCRequest, db: Session = Depends(_get_db)):
    """Update just the CC emails on a record."""
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    record.cc_emails = data.cc_emails
    db.commit()
    db.refresh(record)
    return {"id": record.id, "cc_emails": record.cc_emails}


@app.post("/resumes/generate")
def regenerate_resumes():
    load_dotenv(override=True)
    count = _generate_all_resumes()
    return {"detail": f"Regenerated {count} resume PDFs."}


@app.get("/resumes/status")
def resume_cache_status():
    total = len(ROLE_TEMPLATES)
    cached = sum(1 for t in ROLE_TEMPLATES if (RESUME_DIR / f"{t['key']}.pdf").exists())
    return {"total": total, "cached": cached, "ready": cached == total}


@app.get("/records", response_model=list[RecordOut])
def list_records(db: Session = Depends(_get_db)):
    return db.query(Record).order_by(Record.created_at.desc()).all()


@app.post("/records", response_model=RecordOut)
def create_record(data: RecordCreate, db: Session = Depends(_get_db)):
    from email_checker import validate_syntax, check_typo, check_mx, check_disposable
    to = data.to_email.strip().lower()

    ok, reason = validate_syntax(to)
    if not ok:
        raise HTTPException(status_code=422, detail=f"Invalid email: {reason}")

    has_typo, suggestion, typo_detail = check_typo(to)
    if has_typo:
        raise HTTPException(
            status_code=422,
            detail=f"Possible typo in email domain: {typo_detail}. Did you mean {suggestion}?"
        )

    ok, reason = check_disposable(to)
    if not ok:
        raise HTTPException(status_code=422, detail=f"Blocked: {reason}")

    domain = to.rsplit("@", 1)[-1]
    mx_ok, mx_reason, _ = check_mx(domain)
    if not mx_ok:
        raise HTTPException(status_code=422, detail=f"Email domain invalid: {mx_reason}")

    record = Record(
        to_email=to,
        cc_emails=data.cc_emails,
        hr_name=data.hr_name,
        company_name=data.company_name,
        role_key=data.role_key,
        message_type=data.message_type,
        custom_subject=data.custom_subject,
        custom_body=data.custom_body,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.put("/records/{record_id}", response_model=RecordOut)
def update_record(record_id: int, data: RecordCreate, db: Session = Depends(_get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    record.to_email = data.to_email
    record.cc_emails = data.cc_emails
    record.hr_name = data.hr_name
    record.company_name = data.company_name
    record.role_key = data.role_key
    record.message_type = data.message_type
    record.custom_subject = data.custom_subject
    record.custom_body = data.custom_body
    db.commit()
    db.refresh(record)
    return record


@app.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(_get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"detail": "Record removed"}


@app.delete("/records")
def clear_all_records(db: Session = Depends(_get_db)):
    count = db.query(Record).delete()
    db.commit()
    return {"detail": f"Cleared {count} record(s)"}


@app.post("/records/{record_id}/send", response_model=SendResult)
def send_one(record_id: int, db: Session = Depends(_get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    result = _send_single_record(record, db)
    db.commit()

    sent = 1 if result["status"] == "sent" else 0
    failed = 1 - sent
    errors = [result] if result["status"] == "failed" else []
    return SendResult(sent=sent, failed=failed, errors=errors)


@app.post("/send-all", response_model=SendResult)
def send_all(db: Session = Depends(_get_db)):
    records = db.query(Record).all()
    if not records:
        raise HTTPException(
            status_code=400,
            detail="No records in the queue to send.",
        )

    sent = 0
    failed = 0
    errors = []

    for record in records:
        result = _send_single_record(record, db)
        if result["status"] == "sent":
            sent += 1
        else:
            failed += 1
            errors.append(result)

    db.commit()

    return SendResult(sent=sent, failed=failed, errors=errors)
