from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from database import NeonBase


class Company(NeonBase):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    domain = Column(String(255))
    url = Column(String(500))
    created_at = Column(DateTime, server_default=func.now())

    jobs = relationship("Job", back_populates="company")
    contacts = relationship("Contact", back_populates="company")


class Job(NeonBase):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    source = Column(String(50), nullable=False)
    source_id = Column(String(255))
    title = Column(String(500), nullable=False)
    url = Column(String(1000))
    description = Column(Text)
    tags = Column(Text)
    location = Column(String(255))
    salary_min = Column(Integer)
    salary_max = Column(Integer)
    role_key = Column(String(50))
    match_confidence = Column(Float)
    posted_at = Column(String(100))
    scraped_at = Column(DateTime, server_default=func.now())
    needs_manual_apply = Column(Boolean, default=False)

    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job")


class Contact(NeonBase):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"))
    email = Column(String(255), nullable=False)
    name = Column(String(255), default="")
    title = Column(String(255), default="")
    confidence = Column(Float, default=0)
    source = Column(String(100), default="")
    verified = Column(Boolean, default=False)
    discovered_at = Column(DateTime, server_default=func.now())

    company = relationship("Company", back_populates="contacts")
    applications = relationship("Application", back_populates="contact")


class Application(NeonBase):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"))
    contact_id = Column(Integer, ForeignKey("contacts.id", ondelete="SET NULL"))
    status = Column(String(50), default="pending")
    sent_at = Column(DateTime)
    sent_via = Column(String(255))
    error = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    job = relationship("Job", back_populates="applications")
    contact = relationship("Contact", back_populates="applications")


class SentCompany(NeonBase):
    __tablename__ = "sent_companies"

    id = Column(Integer, primary_key=True)
    company_name = Column(String(255), nullable=False)
    email_used = Column(String(255), nullable=False)
    sent_at = Column(DateTime, server_default=func.now())
    sent_via = Column(String(255), default="")
    month_key = Column(String(7), default="")


class CareerApplication(NeonBase):
    __tablename__ = "career_applications"

    id = Column(Integer, primary_key=True)
    company_name = Column(String(255), nullable=False)
    job_title = Column(String(500), default="")
    job_url = Column(String(1000), nullable=False)
    ats_type = Column(String(50), default="generic")
    status = Column(String(50), default="pending")
    fields_filled = Column(Integer, default=0)
    error = Column(Text, default="")
    applied_at = Column(DateTime, server_default=func.now())
