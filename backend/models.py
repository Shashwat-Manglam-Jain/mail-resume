from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from database import Base


class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    to_email = Column(String, nullable=False)
    message_type = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
