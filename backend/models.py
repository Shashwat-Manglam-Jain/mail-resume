"""
models.py — SQLAlchemy ORM model for the mail queue.

Each row represents one email to send. Records are auto-deleted after
successful delivery. Failed records stay for retry.
"""

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from database import Base


class Record(Base):
    """
    A single queued email record.

    Fields:
        to_email      — recipient HR email address
        hr_name       — name used in greeting (defaults to 'Hiring Manager')
        company_name  — target company (used in subject and body)
        role_key      — key matching a role template (e.g. 'data_scientist')
        message_type  — which email template to use (e.g. 'job_apply')
        created_at    — auto-set timestamp when row is inserted

    Lifecycle:
        Created → Send attempted → Deleted on success / Stays on failure
    """
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    to_email = Column(String, nullable=False)
    hr_name = Column(String, nullable=False, default="Hiring Manager")
    company_name = Column(String, nullable=False, default="")
    role_key = Column(String, nullable=False, default="")
    message_type = Column(String, nullable=False, default="job_apply")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
