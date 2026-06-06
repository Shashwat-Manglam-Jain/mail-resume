"""
main.py — FastAPI application for the Email Resume Bulk Sender.

Architecture:
    .env holds personal details (name, email, phone, links) and SMTP config.
    The UI only collects: HR email, HR name, company, role, message type.
    Resumes are pre-generated into generated_resumes/ on startup.
    At send time, the cached PDF is attached — no generation delay.

Endpoints:
    GET  /profile              — user profile from .env
    GET  /roles                — list all available role templates
    GET  /roles/{key}/skills   — categorized skills for a role
    GET  /message-templates    — list message template options
    POST /message-preview      — preview composed subject + body
    GET  /records              — list all queued records
    POST /records              — create a new record (no file upload)
    DELETE /records/{id}       — delete a single record
    POST /records/{id}/send    — send one record, delete on success
    POST /send-all             — send all records, delete successful ones
    GET  /resume/{key}/pdf     — download cached PDF resume
    GET  /resume/{key}/latex   — download auto-generated LaTeX resume
    POST /resumes/generate     — regenerate all cached PDFs (after .env change)
    GET  /resumes/status       — check if resume cache is ready
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
from resume_templates import (
    get_template,
    list_templates,
    generate_pdf_resume,
    make_latex_resume,
    ROLE_TEMPLATES,
)

logger = logging.getLogger(__name__)

# ── Load environment variables ──────────────────────────────────────────────
load_dotenv()

# ── Create database tables on startup ───────────────────────────────────────
Base.metadata.create_all(bind=engine)

IS_VERCEL = os.environ.get("VERCEL") == "1"

# ── Resume cache directory ──────────────────────────────────────────────────
if IS_VERCEL:
    RESUME_DIR = Path("/tmp/generated_resumes")
else:
    RESUME_DIR = Path(__file__).parent / "generated_resumes"
RESUME_DIR.mkdir(parents=True, exist_ok=True)

# ── FastAPI application ─────────────────────────────────────────────────────
app = FastAPI(
    title="Email Resume Bulk Sender",
    description="Queue HR emails, auto-generate role-specific resumes, "
                "and bulk-send with one click.",
)

# ── CORS — allow frontend dev server ────────────────────────────────────────
_origins = ["http://localhost:3000"]
_frontend_url = os.getenv("FRONTEND_URL")
if _frontend_url:
    _origins.append(_frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if IS_VERCEL and not _frontend_url else _origins,
    allow_credentials=not IS_VERCEL or bool(_frontend_url),
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# MESSAGE TEMPLATES — Formal, professional emails for different scenarios
# ============================================================================
# Placeholders: {hr_name}, {company_name}, {role_title},
#               {top_skills}, {your_name}, {your_email}, {your_phone}
# ============================================================================

MESSAGE_TEMPLATES = {

    # ── Job Application — formal cover letter style ─────────────────
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

    # ── Interview Scheduling — with specific time availability ──────
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

    # ── Follow-up — polite check on application status ──────────────
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

    # ── Thank You — post-interview gratitude ────────────────────────
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

    # ── Referral Request — asking someone to refer you ──────────────
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

    # ── Cold Outreach — proactive introduction ──────────────────────
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
}


# ============================================================================
# Pydantic schemas — request/response models
# ============================================================================

class RecordCreate(BaseModel):
    """Schema for creating a new mail-queue record."""
    to_email: EmailStr
    hr_name: str = ""           # empty → "Sir/Madam" in email greeting
    company_name: str = ""      # empty → omitted from email body
    role_key: str = ""
    message_type: str = "job_apply"


class RecordOut(BaseModel):
    """Schema for returning a record to the frontend."""
    id: int
    to_email: str
    hr_name: str
    company_name: str
    role_key: str
    message_type: str
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class SendResult(BaseModel):
    """Result of a send-all or single-send operation."""
    sent: int
    failed: int
    errors: list[dict]


class PreviewRequest(BaseModel):
    """Schema for message preview."""
    message_type: str = "job_apply"
    hr_name: str = ""           # empty → "Sir/Madam"
    company_name: str = ""      # empty → omitted
    role_key: str = ""


# ============================================================================
# Helpers — profile, SMTP, message composition, email sending
# ============================================================================

def _get_profile() -> dict:
    """
    Load user profile from environment variables.
    These values are set once in .env and used everywhere:
    resume generation, email composition, and email signature.
    """
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
    """Load SMTP connection settings from environment variables."""
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
    """Resolve a role_key to its display title."""
    template = get_template(role_key)
    if template:
        return template["title"]
    return role_key.replace("_", " ").title() if role_key else "Professional"


def _get_top_skills(role_key: str, count: int = 5) -> str:
    """Get a comma-separated string of top skills for a role."""
    template = get_template(role_key)
    if template:
        all_skills = [s for vals in template["skills"].values() for s in vals]
        return ", ".join(all_skills[:count])
    return "modern technologies and tools"


def _compose_message(message_type: str, hr_name: str, company_name: str,
                     role_key: str) -> tuple[str, str]:
    """
    Build the email subject and body from a message template.

    Fallback logic:
        hr_name   → "Sir/Madam" when empty (safe formal greeting)
        company   → omitted from body when empty (no awkward placeholder)

    The {at_company} placeholder resolves to either " at CompanyName"
    or "" (empty string), so sentences read naturally either way:
        "the Data Scientist position at Google"   (company provided)
        "the Data Scientist position"             (company empty)

    Returns:
        (subject, body) tuple with all placeholders resolved.
    """
    profile = _get_profile()
    tmpl = MESSAGE_TEMPLATES.get(message_type, MESSAGE_TEMPLATES["job_apply"])

    # Build the conditional " at CompanyName" fragment
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

    subject = tmpl["subject"].format(**replacements)
    body = tmpl["body"].format(**replacements)
    return subject, body


def _generate_all_resumes():
    """
    Pre-generate PDF resumes for every role template into RESUME_DIR.

    Called once on server startup and again via POST /resumes/generate
    when the user updates their .env profile. Typically takes <1 second.
    """
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
    """
    Read a pre-generated PDF from the cache folder.

    Falls back to on-the-fly generation if the cache file is missing
    (e.g. new role added after last generation).
    """
    pdf_path = RESUME_DIR / f"{role_key}.pdf"
    if pdf_path.exists():
        return pdf_path.read_bytes()
    # Cache miss — generate on the fly and cache it
    profile = _get_profile()
    pdf_bytes = generate_pdf_resume(role_key, profile)
    pdf_path.write_bytes(pdf_bytes)
    return pdf_bytes


# Pre-generate all resumes on import (server startup) — skip on Vercel
# where cold starts should be fast; resumes are generated on-demand instead.
if not IS_VERCEL:
    _generate_all_resumes()


def _send_email(to_email: str, subject: str, body: str,
                pdf_bytes: bytes, pdf_filename: str):
    """
    Send an email with a PDF resume attachment via SMTP SSL.

    Args:
        to_email:     recipient address
        subject:      email subject line
        body:         plain-text email body
        pdf_bytes:    cached PDF resume bytes
        pdf_filename: attachment filename (e.g. 'John_Doe_Resume.pdf')
    """
    host, port, user, password, sender = _get_smtp_settings()

    # Build the email message
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(body)

    # Attach the cached PDF resume
    msg.add_attachment(
        pdf_bytes,
        maintype="application",
        subtype="pdf",
        filename=pdf_filename,
    )

    # Send via SMTP SSL
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(user, password)
        server.send_message(msg)


def _send_single_record(record: Record, db: Session) -> dict:
    """
    Send one record's email and delete it from the database on success.

    Steps:
        1. Compose subject + body from template and record data
        2. Read cached PDF resume for the record's role (no generation)
        3. Send the email with PDF attached
        4. On success → delete record from DB, return success
        5. On failure → keep record, return error details

    Returns:
        dict with 'id', 'status' ('sent'|'failed'), and optional 'error'
    """
    profile = _get_profile()

    # Step 1 — Compose the email
    subject, body = _compose_message(
        record.message_type,
        record.hr_name,
        record.company_name,
        record.role_key,
    )

    # Step 2 — Read cached PDF (fast disk read, no generation)
    try:
        pdf_bytes = _get_cached_resume(record.role_key)
    except Exception:
        pdf_bytes = _get_cached_resume("ai_ml_engineer")

    # Build attachment filename: "FirstName_LastName_RoleTitle_Resume.pdf"
    name_slug = (profile.get("name") or "Resume").replace(" ", "_")
    role_slug = _get_role_title(record.role_key).replace(" ", "_")
    pdf_filename = f"{name_slug}_{role_slug}_Resume.pdf"

    # Step 3 — Send the email
    try:
        _send_email(record.to_email, subject, body, pdf_bytes, pdf_filename)
    except Exception as exc:
        # Step 5 — Failed: keep record, return error
        return {"id": record.id, "status": "failed", "error": str(exc)}

    # Step 4 — Success: delete record from DB
    db.delete(record)
    return {"id": record.id, "status": "sent"}


# ── Database session dependency ─────────────────────────────────────────────

def _get_db():
    """Yield a database session and close it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# API Endpoints
# ============================================================================

# ── Profile ─────────────────────────────────────────────────────────────────

@app.get("/profile")
def get_profile():
    """Return user profile loaded from .env (name, email, phone, links)."""
    return _get_profile()


# ── Roles and Skills ────────────────────────────────────────────────────────

@app.get("/roles")
def get_roles():
    """Return summary list of all available role templates."""
    return list_templates()


@app.get("/roles/{role_key}/skills")
def get_role_skills(role_key: str):
    """
    Return categorized skills for a specific role.

    Response: list of {category: str, skills: list[str]}
    """
    template = get_template(role_key)
    if not template:
        raise HTTPException(status_code=404, detail="Role not found")
    return [
        {"category": cat, "skills": skills}
        for cat, skills in template["skills"].items()
    ]


# ── Message Templates ──────────────────────────────────────────────────────

@app.get("/message-templates")
def get_message_templates():
    """Return list of available message templates with key and label."""
    return [
        {"key": key, "label": tmpl["label"]}
        for key, tmpl in MESSAGE_TEMPLATES.items()
    ]


@app.post("/message-preview")
def preview_message(req: PreviewRequest):
    """
    Preview the composed email subject and body.

    Uses the selected message template + role + HR/company info
    to show exactly what will be sent.
    """
    subject, body = _compose_message(
        req.message_type, req.hr_name, req.company_name, req.role_key,
    )
    return {"subject": subject, "body": body}


# ── Resume Downloads (preview before sending) ──────────────────────────────

@app.get("/resume/{role_key}/pdf")
def download_resume_pdf(role_key: str):
    """
    Download cached PDF resume for a role.

    Reads from generated_resumes/ cache — no generation delay.
    """
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
    """Download LaTeX resume source for a role."""
    template = get_template(role_key)
    if not template:
        raise HTTPException(status_code=404, detail="Role not found")

    profile = _get_profile()
    return make_latex_resume(template, profile)


@app.post("/resumes/generate")
def regenerate_resumes():
    """
    Regenerate all cached PDF resumes.

    Call this after updating personal details in .env.
    Overwrites every PDF in generated_resumes/ with fresh data.
    """
    load_dotenv(override=True)
    count = _generate_all_resumes()
    return {"detail": f"Regenerated {count} resume PDFs."}


@app.get("/resumes/status")
def resume_cache_status():
    """
    Check how many resume PDFs are cached.

    Returns total role count and cached file count so the
    frontend can show whether resumes are ready.
    """
    total = len(ROLE_TEMPLATES)
    cached = sum(1 for t in ROLE_TEMPLATES if (RESUME_DIR / f"{t['key']}.pdf").exists())
    return {"total": total, "cached": cached, "ready": cached == total}


# ── Mail Queue (CRUD) ──────────────────────────────────────────────────────

@app.get("/records", response_model=list[RecordOut])
def list_records(db: Session = Depends(_get_db)):
    """Return all queued records, newest first."""
    return db.query(Record).order_by(Record.created_at.desc()).all()


@app.post("/records", response_model=RecordOut)
def create_record(data: RecordCreate, db: Session = Depends(_get_db)):
    """
    Add a new email record to the queue.

    No file upload needed — the resume PDF is auto-generated
    at send time based on the selected role.
    """
    record = Record(
        to_email=data.to_email,
        hr_name=data.hr_name,
        company_name=data.company_name,
        role_key=data.role_key,
        message_type=data.message_type,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.put("/records/{record_id}", response_model=RecordOut)
def update_record(record_id: int, data: RecordCreate, db: Session = Depends(_get_db)):
    """Update an existing record in the queue."""
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    record.to_email = data.to_email
    record.hr_name = data.hr_name
    record.company_name = data.company_name
    record.role_key = data.role_key
    record.message_type = data.message_type
    db.commit()
    db.refresh(record)
    return record


@app.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(_get_db)):
    """Delete a single record from the queue."""
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"detail": "Record removed"}


@app.delete("/records")
def clear_all_records(db: Session = Depends(_get_db)):
    """Delete all records from the queue."""
    count = db.query(Record).delete()
    db.commit()
    return {"detail": f"Cleared {count} record(s)"}


# ── Send Operations ────────────────────────────────────────────────────────

@app.post("/records/{record_id}/send", response_model=SendResult)
def send_one(record_id: int, db: Session = Depends(_get_db)):
    """
    Send a single record's email.

    On success: record is deleted from the queue.
    On failure: record stays for retry, error is returned.
    """
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
    """
    Send all queued records.

    For each record:
        1. Auto-generate PDF resume for the selected role
        2. Compose email using the selected message template
        3. Send via SMTP with PDF attached
        4. On success → delete that record from queue
        5. On failure → keep that record, include error in response

    After execution, only failed records remain in the queue.
    Successful records are permanently removed to prevent duplicates.
    """
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

    # Commit all changes (deletions of successful records)
    db.commit()

    return SendResult(sent=sent, failed=failed, errors=errors)
