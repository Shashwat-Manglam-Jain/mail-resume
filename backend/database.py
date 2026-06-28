import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

IS_VERCEL = os.environ.get("VERCEL") == "1"

# --- SQLite for the local email queue (existing) ---
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

# --- Neon PostgreSQL for shared job data ---
NEON_DATABASE_URL = os.environ.get("NEON_DATABASE_URL", "")
neon_engine = None
NeonSessionLocal = None
NeonBase = declarative_base()

if NEON_DATABASE_URL:
    neon_engine = create_engine(NEON_DATABASE_URL)
    NeonSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=neon_engine)
