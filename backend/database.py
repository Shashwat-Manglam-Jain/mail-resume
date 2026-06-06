import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

IS_VERCEL = os.environ.get("VERCEL") == "1"

if IS_VERCEL:
    SQLALCHEMY_DATABASE_URL = "sqlite:////tmp/records.db"
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./records.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
