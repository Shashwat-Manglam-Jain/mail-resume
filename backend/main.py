"""
main.py — FastAPI application for the Email Resume Bulk Sender.

Profile:
    GET  /profile                       — user profile from DB / .env
    PUT  /profile                       — update user profile

Roles (Resume Builder):
    GET  /roles                         — list all active roles
    GET  /roles/{key}                   — full role detail
    POST /roles                         — create a new role
    PUT  /roles/{key}                   — update role fields
    DELETE /roles/{key}                 — delete a role
    GET  /roles/{key}/skills            — categorized skills
    PUT  /roles/{key}/skills            — replace skill categories
    PUT  /roles/{key}/experience        — replace client experience
    PUT  /roles/{key}/achievements      — replace achievements
    PUT  /roles/{key}/focus             — replace focus areas

Mail Queue:
    GET  /records                       — list all queued records
    POST /records                       — add a record (validates email)
    PUT  /records/{id}                  — update a record
    DELETE /records/{id}                — delete a record
    DELETE /records                     — clear all records
    PATCH /records/{id}/cc              — update CC emails
    POST /records/{id}/send             — send one email
    POST /send-all                      — send all queued emails
    POST /message-preview               — preview email subject + body
    POST /validate-email                — validate an email address

Resumes:
    GET  /resume/{key}/pdf              — download PDF resume
    GET  /resume/{key}/latex            — download LaTeX source
    POST /resume/compile-latex          — compile raw LaTeX to PDF
    GET  /resumes/download-all          — download all resumes as ZIP
    POST /resumes/generate              — regenerate all cached PDFs
    GET  /resumes/status                — check resume cache status
"""

import os
import ssl
import smtplib
import logging
from io import BytesIO
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Body, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, StreamingResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from email.message import EmailMessage

from database import Base, SessionLocal, engine, NeonSessionLocal
from models import Record
from neon_models import (
    Profile as ProfileModel, Role, RoleSkill,
    RoleExperience, RoleAchievement, RoleFocusArea,
)
from email_checker import validate_email_full
from resume_templates import (
    get_template,
    list_templates,
    generate_pdf_resume,
    make_latex_resume,
)

logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

IS_VERCEL = os.environ.get("VERCEL") == "1"

if IS_VERCEL:
    RESUME_DIR = Path("/tmp/generated_resumes")
else:
    RESUME_DIR = Path(__file__).parent / "generated_resumes"
RESUME_DIR.mkdir(parents=True, exist_ok=True)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(application):
    if not IS_VERCEL:
        import threading
        threading.Thread(target=_generate_all_resumes, daemon=True).start()
    yield

app = FastAPI(
    title="Email Resume Bulk Sender",
    description="Queue HR emails, auto-generate role-specific resumes, "
                "and bulk-send with one click.",
    lifespan=lifespan,
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


EMAIL_SUBJECT_TEMPLATE = (
    "{role_title} -- {your_name} ({experience_years} yrs exp)"
)

EMAIL_BODY_TEMPLATE = (
    "{greeting}\n\n"
    "I came across the {role_title} opening{at_company} and wanted "
    "to reach out. I've been working with {top_skills} for about "
    "{experience_years} years now, mostly building backend systems "
    "and shipping production code for clients across the US and Europe.\n\n"
    "I've attached my resume -- it covers the specifics better than "
    "I can in an email, but the short version is that I've spent most "
    "of my career solving real operational problems: automating manual "
    "workflows, building data pipelines, and getting things into "
    "production reliably.\n\n"
    "Would love to chat if you think there's a fit. Happy to jump "
    "on a quick call whenever works for you.\n\n"
    "Thanks,\n"
    "{your_name}\n"
    "{your_email} | {your_phone}"
)


# ── Pydantic schemas ──────────────────────────────────────────────────────

class RecordCreate(BaseModel):
    to_email: EmailStr
    cc_emails: str = ""
    hr_name: str = ""
    company_name: str = ""
    role_key: str = ""
    experience_years: int = 4
    custom_subject: str = ""
    custom_body: str = ""


class RecordOut(BaseModel):
    id: int
    to_email: str
    cc_emails: str
    hr_name: str
    company_name: str
    role_key: str
    experience_years: int = 4
    custom_subject: str
    custom_body: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class SendResult(BaseModel):
    sent: int
    failed: int
    errors: list[dict]


class ValidateEmailRequest(BaseModel):
    email: str
    skip_smtp: bool = False


class CompileLatexRequest(BaseModel):
    latex: str
    filename: str = "resume.pdf"


class UpdateCCRequest(BaseModel):
    cc_emails: str = ""


# ── Helpers ───────────────────────────────────────────────────────────────

def _get_profile() -> dict:
    env_profile = {
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
        "experience_years": os.getenv("YOUR_EXPERIENCE_YEARS", "4+"),
    }
    if NeonSessionLocal:
        try:
            ndb = NeonSessionLocal()
            row = ndb.query(ProfileModel).first()
            ndb.close()
            if row:
                db_profile = {}
                for field in env_profile:
                    val = getattr(row, field, "")
                    db_profile[field] = val if val else env_profile[field]
                return db_profile
        except Exception:
            pass
    return env_profile


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


def _neon_db_session():
    if NeonSessionLocal:
        return NeonSessionLocal()
    return None


def _get_role_title(role_key: str) -> str:
    if not role_key:
        return "Professional"
    ndb = _neon_db_session()
    if not ndb:
        return role_key.replace("_", " ").title()
    try:
        template = get_template(role_key, db=ndb)
    finally:
        ndb.close()
    if template:
        return template["title"]
    return role_key.replace("_", " ").title()


def _get_top_skills(role_key: str, count: int = 5) -> str:
    if not role_key:
        return "modern technologies and tools"
    ndb = _neon_db_session()
    if not ndb:
        return "modern technologies and tools"
    try:
        template = get_template(role_key, db=ndb)
    finally:
        ndb.close()
    if template:
        all_skills = [s for vals in template["skills"].values() for s in vals]
        return ", ".join(all_skills[:count])
    return "modern technologies and tools"


def _compose_message(hr_name: str, company_name: str,
                     role_key: str, custom_subject: str = "",
                     custom_body: str = "",
                     experience_years: int = 4) -> tuple[str, str]:
    if custom_subject and custom_body:
        return custom_subject, custom_body

    profile = _get_profile()
    at_company = f" at {company_name}" if company_name.strip() else ""
    hr_clean = hr_name.strip()
    greeting = f"Hi {hr_clean}," if hr_clean else "Hey there,"

    replacements = {
        "greeting": greeting,
        "at_company": at_company,
        "role_title": _get_role_title(role_key),
        "top_skills": _get_top_skills(role_key),
        "your_name": profile["name"] or "Applicant",
        "your_email": profile["email"] or "",
        "your_phone": profile["phone"] or "",
        "experience_years": str(experience_years),
    }

    subject = custom_subject if custom_subject else EMAIL_SUBJECT_TEMPLATE.format(**replacements)
    body = custom_body if custom_body else EMAIL_BODY_TEMPLATE.format(**replacements)
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
    ndb = _neon_db_session()
    if not ndb:
        logger.warning("Neon DB not configured — skipping resume generation")
        return 0
    try:
        roles = list_templates(db=ndb)
        count = 0
        for t in roles:
            key = t["key"]
            pdf_path = RESUME_DIR / f"{key}.pdf"
            try:
                pdf_bytes = generate_pdf_resume(key, profile, db=ndb)
                pdf_path.write_bytes(pdf_bytes)
                count += 1
            except Exception as exc:
                logger.warning("Failed to generate resume for %s: %s", key, exc)
    finally:
        ndb.close()
    logger.info("Generated %d resume PDFs in %s", count, RESUME_DIR)
    return count


def _get_resume_for_send(role_key: str, experience_years: int = 4) -> bytes:
    """Generate a fresh PDF with the given experience_years (no caching)."""
    custom_path = os.getenv("CUSTOM_RESUME_PATH", "").strip()
    if custom_path:
        p = Path(custom_path)
        if p.exists():
            return p.read_bytes()
    profile = _get_profile()
    ndb = _neon_db_session()
    try:
        return generate_pdf_resume(role_key, profile, db=ndb,
                                   experience_years=experience_years)
    finally:
        if ndb:
            ndb.close()




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
    with smtplib.SMTP_SSL(host, port, context=context, timeout=30) as server:
        server.login(user, password)
        all_recipients = [to_email] + (cc_emails or [])
        server.send_message(msg, to_addrs=all_recipients)



def _send_single_record(record: Record, db: Session) -> dict:
    profile = _get_profile()
    from_email = os.getenv("SMTP_FROM", os.getenv("SMTP_USER", ""))

    to_result = validate_email_full(record.to_email, from_email, skip_smtp=True)
    if not to_result["valid"]:
        return {
            "id": record.id,
            "status": "failed",
            "error": f"TO validation failed: {to_result['reason']}",
            "checks": to_result["checks"],
        }

    cc_list = _parse_cc_emails(record.cc_emails)
    valid_cc, skipped_cc = _validate_and_filter_cc(cc_list, from_email)

    exp_years = getattr(record, "experience_years", 4) or 4

    subject, body = _compose_message(
        record.hr_name,
        record.company_name,
        record.role_key,
        record.custom_subject,
        record.custom_body,
        experience_years=exp_years,
    )

    try:
        pdf_bytes = _get_resume_for_send(record.role_key, exp_years)
    except Exception:
        pdf_bytes = _get_resume_for_send("ai_ml_engineer", exp_years)

    name_slug = (profile.get("name") or "Resume").replace(" ", "_")
    custom_resume_path = os.getenv("CUSTOM_RESUME_PATH", "").strip()
    if custom_resume_path and Path(custom_resume_path).exists():
        pdf_filename = f"{name_slug}_Resume.pdf"
    else:
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


def _get_neon_db():
    if not NeonSessionLocal:
        raise HTTPException(status_code=500, detail="Neon DB not configured")
    db = NeonSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── API Endpoints ─────────────────────────────────────────────────────────

@app.get("/profile")
def get_profile():
    return _get_profile()


@app.put("/profile")
def update_profile(data: dict = Body(...), neon_db: Session = Depends(_get_neon_db)):
    row = neon_db.query(ProfileModel).first()
    if not row:
        row = ProfileModel()
        neon_db.add(row)
    allowed = {
        "name", "email", "phone", "location", "linkedin", "github",
        "portfolio", "education", "graduation_year", "experience_years",
        "company_1_name", "company_1_role", "company_1_location", "company_1_duration",
        "company_2_name", "company_2_role", "company_2_location", "company_2_duration",
    }
    for k, v in data.items():
        if k in allowed:
            setattr(row, k, v or "")
    neon_db.commit()
    neon_db.refresh(row)
    return _get_profile()


@app.get("/roles")
def get_roles():
    if not NeonSessionLocal:
        return []
    db = NeonSessionLocal()
    try:
        return list_templates(db=db)
    finally:
        db.close()


@app.post("/message-preview")
def message_preview(data: dict = Body(...)):
    role_key = data.get("role_key", "")
    hr_name = data.get("hr_name", "")
    company_name = data.get("company_name", "")
    role_title = data.get("role_title", "")
    experience_years = data.get("experience_years", 4)

    profile = _get_profile()
    at_company = f" at {company_name}" if company_name.strip() else ""

    if role_title:
        title = role_title
    elif role_key:
        title = _get_role_title(role_key)
    else:
        title = "Professional"

    hr_clean = hr_name.strip()
    greeting = f"Hi {hr_clean}," if hr_clean else "Hey there,"

    replacements = {
        "greeting": greeting,
        "at_company": at_company,
        "role_title": title,
        "top_skills": _get_top_skills(role_key) if role_key else "modern technologies and tools",
        "your_name": profile["name"] or "Applicant",
        "your_email": profile["email"] or "",
        "your_phone": profile["phone"] or "",
        "experience_years": str(experience_years),
    }

    return {
        "subject": EMAIL_SUBJECT_TEMPLATE.format(**replacements),
        "body": EMAIL_BODY_TEMPLATE.format(**replacements),
    }


@app.get("/roles/{role_key}")
def get_role_detail(role_key: str, neon_db: Session = Depends(_get_neon_db)):
    template = get_template(role_key, db=neon_db)
    if not template:
        raise HTTPException(status_code=404, detail="Role not found")
    return template


@app.post("/roles")
def create_role(data: dict = Body(...), neon_db: Session = Depends(_get_neon_db)):
    key = data.get("key", "").strip().lower().replace(" ", "_").replace("-", "_")
    if not key:
        raise HTTPException(status_code=422, detail="Role key is required")
    existing = neon_db.query(Role).filter(Role.key == key).first()
    if existing:
        raise HTTPException(status_code=409, detail="Role key already exists")
    max_order = neon_db.query(Role.sort_order).order_by(Role.sort_order.desc()).first()
    role = Role(
        key=key,
        title=data.get("title", key.replace("_", " ").title()),
        previous_title=data.get("previous_title", ""),
        summary=data.get("summary", ""),
        coursework=data.get("coursework", ""),
        sort_order=(max_order[0] + 1) if max_order else 0,
    )
    neon_db.add(role)
    neon_db.commit()
    return get_template(key, db=neon_db)


@app.put("/roles/{role_key}")
def update_role(role_key: str, data: dict = Body(...), neon_db: Session = Depends(_get_neon_db)):
    role = neon_db.query(Role).filter(Role.key == role_key).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    for field in ("title", "previous_title", "summary", "coursework"):
        if field in data:
            setattr(role, field, data[field])
    neon_db.commit()
    return get_template(role_key, db=neon_db)


@app.delete("/roles/{role_key}")
def delete_role(role_key: str, neon_db: Session = Depends(_get_neon_db)):
    role = neon_db.query(Role).filter(Role.key == role_key).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    neon_db.delete(role)
    neon_db.commit()
    return {"detail": f"Role '{role_key}' deleted"}


@app.get("/roles/{role_key}/skills")
def get_role_skills(role_key: str, neon_db: Session = Depends(_get_neon_db)):
    template = get_template(role_key, db=neon_db)
    if not template:
        raise HTTPException(status_code=404, detail="Role not found")
    return [
        {"category": cat, "skills": skills}
        for cat, skills in template["skills"].items()
    ]


@app.put("/roles/{role_key}/skills")
def update_role_skills(role_key: str, data: list = Body(...), neon_db: Session = Depends(_get_neon_db)):
    role = neon_db.query(Role).filter(Role.key == role_key).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    neon_db.query(RoleSkill).filter(RoleSkill.role_id == role.id).delete()
    for i, item in enumerate(data):
        neon_db.add(RoleSkill(
            role_id=role.id,
            category=item.get("category", ""),
            skills=item.get("skills", []),
            sort_order=i,
        ))
    neon_db.commit()
    return get_template(role_key, db=neon_db)["skills"]



@app.put("/roles/{role_key}/experience")
def update_role_experience(role_key: str, data: list = Body(...),
                           neon_db: Session = Depends(_get_neon_db)):
    role = neon_db.query(Role).filter(Role.key == role_key).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    neon_db.query(RoleExperience).filter(RoleExperience.role_id == role.id).delete()
    for i, item in enumerate(data):
        neon_db.add(RoleExperience(
            role_id=role.id,
            position_index=item.get("position_index", i),
            bullets=item.get("bullets", []),
            client_name=item.get("client_name", ""),
            client_location=item.get("client_location", ""),
            min_years=item.get("min_years", 1),
        ))
    neon_db.commit()
    return get_template(role_key, db=neon_db)["clients"]


@app.put("/roles/{role_key}/achievements")
def update_role_achievements(role_key: str, data: list = Body(...),
                             neon_db: Session = Depends(_get_neon_db)):
    role = neon_db.query(Role).filter(Role.key == role_key).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    neon_db.query(RoleAchievement).filter(RoleAchievement.role_id == role.id).delete()
    for i, item in enumerate(data):
        text = item if isinstance(item, str) else item.get("text", "")
        neon_db.add(RoleAchievement(role_id=role.id, text=text, sort_order=i))
    neon_db.commit()
    return get_template(role_key, db=neon_db)["achievements"]


@app.put("/roles/{role_key}/focus")
def update_role_focus(role_key: str, data: list = Body(...),
                      neon_db: Session = Depends(_get_neon_db)):
    role = neon_db.query(Role).filter(Role.key == role_key).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    neon_db.query(RoleFocusArea).filter(RoleFocusArea.role_id == role.id).delete()
    for i, item in enumerate(data):
        area = item if isinstance(item, str) else item.get("area", "")
        neon_db.add(RoleFocusArea(role_id=role.id, area=area, sort_order=i))
    neon_db.commit()
    return get_template(role_key, db=neon_db)["focus"]


@app.post("/validate-email")
def validate_email_endpoint(req: ValidateEmailRequest):
    from_email = os.getenv("SMTP_FROM", os.getenv("SMTP_USER", ""))
    result = validate_email_full(req.email, from_email, skip_smtp=req.skip_smtp)
    return result


@app.get("/resume/{role_key}/pdf")
def download_resume_pdf(role_key: str, experience_years: int = 4,
                        neon_db: Session = Depends(_get_neon_db)):
    template = get_template(role_key, db=neon_db)
    if not template:
        raise HTTPException(status_code=404, detail="Role not found")
    profile = _get_profile()
    pdf_bytes = generate_pdf_resume(role_key, profile, db=neon_db,
                                    experience_years=experience_years)
    name_slug = (profile.get("name") or "Resume").replace(" ", "_")
    filename = f"{name_slug}_{template['title'].replace(' ', '_')}_Resume.pdf"
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/resume/{role_key}/latex", response_class=PlainTextResponse)
def download_resume_latex(role_key: str, experience_years: int = 4,
                          neon_db: Session = Depends(_get_neon_db)):
    template = get_template(role_key, db=neon_db)
    if not template:
        raise HTTPException(status_code=404, detail="Role not found")
    profile = _get_profile()
    return make_latex_resume(template, profile, experience_years=experience_years)



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


@app.get("/resumes/download-all")
def download_all_resumes(neon_db: Session = Depends(_get_neon_db)):
    """Download all generated resumes as a single ZIP file."""
    import zipfile

    profile = _get_profile()
    name_slug = (profile.get("name") or "Resume").replace(" ", "_")
    roles = list_templates(db=neon_db)

    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for t in roles:
            key = t["key"]
            try:
                pdf_bytes = generate_pdf_resume(key, profile, db=neon_db)
                role_slug = t["title"].replace(" ", "_")
                filename = f"{name_slug}_{role_slug}_Resume.pdf"
                zf.writestr(filename, pdf_bytes)
            except Exception:
                pass
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{name_slug}_All_Resumes.zip"'},
    )


@app.post("/resumes/generate")
def regenerate_resumes():
    load_dotenv(override=True)
    count = _generate_all_resumes()
    return {"detail": f"Regenerated {count} resume PDFs."}


@app.get("/resumes/status")
def resume_cache_status(neon_db: Session = Depends(_get_neon_db)):
    roles = list_templates(db=neon_db)
    total = len(roles)
    cached = sum(1 for t in roles if (RESUME_DIR / f"{t['key']}.pdf").exists())
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
        experience_years=data.experience_years,
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
    record.experience_years = data.experience_years
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

    from_email = os.getenv("SMTP_FROM", os.getenv("SMTP_USER", ""))
    profile = _get_profile()
    host, port, user, password, sender = _get_smtp_settings()

    sent = 0
    failed = 0
    errors = []

    ctx = ssl.create_default_context()
    try:
        smtp_server = smtplib.SMTP_SSL(host, port, context=ctx, timeout=30)
        smtp_server.login(user, password)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Cannot connect to mail server: {exc}",
        )

    try:
        for record in records:
            to_result = validate_email_full(record.to_email, from_email,
                                            skip_smtp=True)
            if not to_result["valid"]:
                failed += 1
                errors.append({
                    "id": record.id, "status": "failed",
                    "error": f"TO validation failed: {to_result['reason']}",
                })
                continue

            cc_list = _parse_cc_emails(record.cc_emails)
            valid_cc, skipped_cc = _validate_and_filter_cc(cc_list, from_email)

            exp_years = getattr(record, "experience_years", 4) or 4

            subject, body = _compose_message(
                record.hr_name, record.company_name,
                record.role_key, record.custom_subject, record.custom_body,
                experience_years=exp_years,
            )

            try:
                pdf_bytes = _get_resume_for_send(record.role_key, exp_years)
            except Exception:
                pdf_bytes = _get_resume_for_send("ai_ml_engineer", exp_years)

            name_slug = (profile.get("name") or "Resume").replace(" ", "_")
            custom_resume_path = os.getenv("CUSTOM_RESUME_PATH", "").strip()
            if custom_resume_path and Path(custom_resume_path).exists():
                pdf_filename = f"{name_slug}_Resume.pdf"
            else:
                role_slug = _get_role_title(record.role_key).replace(" ", "_")
                pdf_filename = f"{name_slug}_{role_slug}_Resume.pdf"

            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = record.to_email
            if valid_cc:
                msg["Cc"] = ", ".join(valid_cc)
            msg.set_content(body)
            msg.add_attachment(
                pdf_bytes,
                maintype="application",
                subtype="pdf",
                filename=pdf_filename,
            )
            all_recipients = [record.to_email] + valid_cc

            try:
                try:
                    smtp_server.send_message(msg, to_addrs=all_recipients)
                except (smtplib.SMTPServerDisconnected, OSError):
                    smtp_server = smtplib.SMTP_SSL(
                        host, port, context=ctx, timeout=30)
                    smtp_server.login(user, password)
                    smtp_server.send_message(msg, to_addrs=all_recipients)
            except Exception as exc:
                failed += 1
                errors.append({
                    "id": record.id, "status": "failed",
                    "error": str(exc), "skipped_cc": skipped_cc,
                })
                continue

            db.delete(record)
            sent += 1
    finally:
        try:
            smtp_server.quit()
        except Exception:
            pass

    db.commit()
    return SendResult(sent=sent, failed=failed, errors=errors)


