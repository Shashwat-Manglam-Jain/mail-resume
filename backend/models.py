from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from database import Base


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    to_email = Column(String, nullable=False)
    cc_emails = Column(String, nullable=False, default="")
    hr_name = Column(String, nullable=False, default="Hiring Manager")
    company_name = Column(String, nullable=False, default="")
    role_key = Column(String, nullable=False, default="")
    experience_years = Column(Integer, nullable=False, default=4)
    custom_subject = Column(String, nullable=False, default="")
    custom_body = Column(Text, nullable=False, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
