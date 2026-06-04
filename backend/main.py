import os
import shutil
import ssl
import smtplib
import mimetypes
from pathlib import Path
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from email.message import EmailMessage

from database import Base, SessionLocal, engine
from models import Record
from resume_templates import get_template, list_templates, make_latex_resume

load_dotenv()

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Email Resume Bulk Sender")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MESSAGE_TEMPLATES = {
    "initial": "Hello,\n\nI hope you are doing well. Please find the attached resume for your review.\n\nBest regards,\nTeam",
    "followup": "Hello,\n\nFollowing up on my previous message. I have attached the resume again for your convenience.\n\nThanks,\nTeam",
    "interview": "Hello,\n\nThank you for reviewing the profile. Please find the attached resume for the upcoming interview.\n\nRegards,\nTeam",
}


class RecordOut(BaseModel):
    id: int
    to_email: EmailStr
    message_type: str
    original_filename: str

    class Config:
        from_attributes = True


class ExecuteResult(BaseModel):
    sent: int
    failed: int
    details: list[dict]


class ResumeDetails(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""
    education: str = ""
    graduation_year: str = ""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_smtp_settings():
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "465"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("SMTP_FROM", user)
    if not host or not user or not password:
        raise HTTPException(status_code=500, detail="SMTP configuration is missing. Set SMTP_HOST, SMTP_USER, and SMTP_PASSWORD.")
    return host, port, user, password, sender


def build_message_body(message_type: str) -> str:
    return MESSAGE_TEMPLATES.get(
        message_type,
        MESSAGE_TEMPLATES["initial"],
    )


def send_email(to_email: str, subject: str, body: str, attachment_path: Path, attachment_name: str):
    host, port, user, password, sender = get_smtp_settings()
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = to_email
    message.set_content(body)

    with open(attachment_path, "rb") as attachment_file:
        data = attachment_file.read()

    ctype, encoding = mimetypes.guess_type(attachment_name)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"
    maintype, subtype = ctype.split("/", 1)
    message.add_attachment(data, maintype=maintype, subtype=subtype, filename=attachment_name)

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(host, port, context=context) as server:
        server.login(user, password)
        server.send_message(message)


@app.get("/message-types")
def message_types():
    return [{"key": key, "label": key.replace("_", " ").title()} for key in MESSAGE_TEMPLATES.keys()]


@app.get("/resume-templates")
def resume_templates():
    return list_templates()


@app.post("/resume-templates/{template_key}/latex", response_class=PlainTextResponse)
def generate_latex_resume(template_key: str, details: ResumeDetails):
    template = get_template(template_key)
    if not template:
        raise HTTPException(status_code=404, detail="Resume template not found")
    return make_latex_resume(template, details.dict())


@app.get("/records", response_model=list[RecordOut])
def read_records(db: Session = Depends(get_db)):
    return db.query(Record).order_by(Record.created_at).all()


@app.post("/records", response_model=RecordOut)
def create_record(
    to_email: EmailStr = Form(...),
    message_type: str = Form(...),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    stored_filename = f"{uuid4().hex}_{Path(resume.filename).name}"
    stored_path = UPLOAD_DIR / stored_filename
    with stored_path.open("wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)

    record = Record(
        to_email=to_email,
        message_type=message_type,
        original_filename=resume.filename,
        stored_filename=stored_filename,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@app.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(Record).filter(Record.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    file_path = UPLOAD_DIR / record.stored_filename
    if file_path.exists():
        file_path.unlink()
    db.delete(record)
    db.commit()
    return {"detail": "Record removed"}


@app.post("/records/clear")
def clear_records(db: Session = Depends(get_db)):
    records = db.query(Record).all()
    for record in records:
        file_path = UPLOAD_DIR / record.stored_filename
        if file_path.exists():
            file_path.unlink()
        db.delete(record)
    db.commit()
    return {"detail": "All records cleared"}


@app.post("/execute", response_model=ExecuteResult)
def execute_all(db: Session = Depends(get_db)):
    records = db.query(Record).all()
    if not records:
        raise HTTPException(status_code=400, detail="No pending records to execute.")

    sent = 0
    failed = 0
    details = []

    for record in records:
        attachment_path = UPLOAD_DIR / record.stored_filename
        body = build_message_body(record.message_type)
        subject = f"Resume: {record.original_filename}"
        try:
            send_email(record.to_email, subject, body, attachment_path, record.original_filename)
            sent += 1
            details.append({"id": record.id, "status": "sent"})
        except Exception as exc:
            failed += 1
            details.append({"id": record.id, "status": "failed", "error": str(exc)})
        finally:
            if attachment_path.exists():
                attachment_path.unlink()
            db.delete(record)

    db.commit()
    return ExecuteResult(sent=sent, failed=failed, details=details)
