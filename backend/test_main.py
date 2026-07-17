"""
Tests for the Email Resume Bulk Sender backend.

Covers:
- SMTP timeout is enforced (no hanging connections)
- Bulk send skips slow SMTP probe on TO address
- Parallel send_all: records committed per-thread, not in one final batch
- Partial sends survive a mid-batch failure
- Single-record send endpoint
- Record CRUD (create, update, delete)
- Email validation endpoint
- Message preview endpoint
"""

import os
import smtplib
import threading
import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ---------------------------------------------------------------------------
# Minimal env so main.py imports without errors
# ---------------------------------------------------------------------------
os.environ.setdefault("SMTP_HOST", "smtp.example.com")
os.environ.setdefault("SMTP_PORT", "465")
os.environ.setdefault("SMTP_USER", "test@example.com")
os.environ.setdefault("SMTP_PASSWORD", "secret")
os.environ.setdefault("SMTP_FROM", "test@example.com")
os.environ.setdefault("YOUR_NAME", "Test User")
os.environ.setdefault("YOUR_EMAIL", "test@example.com")
os.environ.setdefault("YOUR_PHONE", "+91 9999999999")
os.environ.setdefault("NEON_DATABASE_URL", "")

# ---------------------------------------------------------------------------
# In-memory test DB — patch database module BEFORE importing main
# ---------------------------------------------------------------------------
import database as _db_mod  # noqa: E402

TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # share the single in-memory DB across all connections
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

_db_mod.engine = TEST_ENGINE
_db_mod.SessionLocal = TestSession
_db_mod.NeonSessionLocal = None  # disable Neon entirely

import main  # noqa: E402 — must come after patching database

main.SessionLocal = TestSession  # used directly by _send_by_id worker threads

from database import Base  # noqa: E402
from models import Record  # noqa: E402

# Create all tables once
Base.metadata.create_all(bind=TEST_ENGINE)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    main.app.dependency_overrides[main._get_db] = _override_get_db
    with TestClient(main.app) as c:
        yield c
    main.app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def clean_db():
    """Wipe records table before every test."""
    db = TestSession()
    db.query(Record).delete()
    db.commit()
    db.close()


def _make_record(**kwargs) -> dict:
    defaults = dict(
        to_email="hr@company.com",
        cc_emails="",
        hr_name="HR Manager",
        company_name="Acme Corp",
        role_key="software_engineer",
        message_type="job_apply",
        custom_subject="",
        custom_body="",
    )
    defaults.update(kwargs)
    return defaults


def _seed(n: int) -> list[int]:
    db = TestSession()
    ids = []
    for i in range(n):
        r = Record(**_make_record(to_email=f"hr{i}@company.com"))
        db.add(r)
        db.commit()
        db.refresh(r)
        ids.append(r.id)
    db.close()
    return ids


# ---------------------------------------------------------------------------
# 1. SMTP timeout
# ---------------------------------------------------------------------------

class TestSMTPTimeout:
    def test_send_email_passes_timeout_30(self):
        """smtplib.SMTP_SSL must be called with timeout=30."""
        mock_server = MagicMock()
        mock_server.__enter__ = lambda s: s
        mock_server.__exit__ = MagicMock(return_value=False)

        with patch("smtplib.SMTP_SSL", return_value=mock_server) as mock_ssl:
            try:
                main._send_email(
                    "hr@company.com", "Subject", "Body", b"%PDF-1.4", "resume.pdf"
                )
            except Exception:
                pass
            assert mock_ssl.called, "smtplib.SMTP_SSL was never called"
            _, kw = mock_ssl.call_args
            assert kw.get("timeout") == 30, (
                f"Expected timeout=30 in SMTP_SSL kwargs, got: {kw}"
            )


# ---------------------------------------------------------------------------
# 2. skip_smtp at send time
# ---------------------------------------------------------------------------

class TestSkipSMTPAtSend:
    def test_send_single_record_uses_skip_smtp_true(self):
        """
        _send_single_record must pass skip_smtp=True to validate_email_full.
        Without this, each email triggers a 30-60 s SMTP probe — causing 502s.
        """
        db = TestSession()
        record = Record(**_make_record())
        db.add(record)
        db.commit()
        db.refresh(record)

        observed_skip_smtp = []

        def spy(email, from_email="", skip_smtp=False):
            observed_skip_smtp.append(skip_smtp)
            return {"valid": True, "checks": [], "reason": "ok"}

        with patch.object(main, "validate_email_full", side_effect=spy):
            with patch.object(main, "_send_email"):
                with patch.object(main, "_get_cached_resume", return_value=b"%PDF"):
                    main._send_single_record(record, db)

        assert observed_skip_smtp, "validate_email_full was never called"
        assert all(observed_skip_smtp), (
            "validate_email_full must be called with skip_smtp=True for every address"
        )
        db.close()


# ---------------------------------------------------------------------------
# 3. send_all
# ---------------------------------------------------------------------------

class TestSendAll:
    def test_deletes_sent_records(self, client):
        _seed(3)
        with patch.object(main, "validate_email_full",
                          return_value={"valid": True, "checks": [], "reason": "ok"}):
            with patch.object(main, "_send_email"):
                with patch.object(main, "_get_cached_resume", return_value=b"%PDF"):
                    resp = client.post("/send-all")

        assert resp.status_code == 200
        data = resp.json()
        assert data["sent"] == 3
        assert data["failed"] == 0

        db = TestSession()
        assert db.query(Record).count() == 0, "Sent records must be removed from DB"
        db.close()

    def test_preserves_failed_records(self, client):
        _seed(2)
        with patch.object(main, "validate_email_full",
                          return_value={"valid": True, "checks": [], "reason": "ok"}):
            with patch.object(main, "_send_email",
                              side_effect=smtplib.SMTPException("refused")):
                with patch.object(main, "_get_cached_resume", return_value=b"%PDF"):
                    resp = client.post("/send-all")

        assert resp.status_code == 200
        data = resp.json()
        assert data["failed"] == 2
        assert data["sent"] == 0

        db = TestSession()
        assert db.query(Record).count() == 2, "Failed records must stay in DB"
        db.close()

    def test_partial_success(self, client):
        _seed(4)  # seeds hr0@, hr1@, hr2@, hr3@company.com

        # Deterministic failure based on email content — thread-safe, no shared counter
        def flaky(to_email, *a, **kw):
            if "hr0" in to_email or "hr2" in to_email:
                raise smtplib.SMTPException("flaky")

        with patch.object(main, "validate_email_full",
                          return_value={"valid": True, "checks": [], "reason": "ok"}):
            with patch.object(main, "_send_email", side_effect=flaky):
                with patch.object(main, "_get_cached_resume", return_value=b"%PDF"):
                    resp = client.post("/send-all")

        assert resp.status_code == 200
        data = resp.json()
        assert data["sent"] == 2
        assert data["failed"] == 2

        db = TestSession()
        remaining = db.query(Record).count()
        db.close()
        assert remaining == 2, "DB must contain exactly the 2 failed records"

    def test_empty_queue_returns_400(self, client):
        resp = client.post("/send-all")
        assert resp.status_code == 400
        assert "No records" in resp.json()["detail"]

    def test_uses_parallel_workers(self, client):
        """Multiple emails are sent concurrently, not sequentially."""
        _seed(6)

        active: set = set()
        lock = threading.Lock()
        peak = {"n": 0}

        def slow_send(*a, **kw):
            tid = threading.current_thread().ident
            with lock:
                active.add(tid)
                if len(active) > peak["n"]:
                    peak["n"] = len(active)
            time.sleep(0.05)
            with lock:
                active.discard(tid)

        with patch.object(main, "validate_email_full",
                          return_value={"valid": True, "checks": [], "reason": "ok"}):
            with patch.object(main, "_send_email", side_effect=slow_send):
                with patch.object(main, "_get_cached_resume", return_value=b"%PDF"):
                    resp = client.post("/send-all")

        assert resp.status_code == 200
        assert peak["n"] > 1, (
            f"Expected parallel execution (peak concurrent = {peak['n']}), "
            "but all sends ran sequentially"
        )


# ---------------------------------------------------------------------------
# 4. send one
# ---------------------------------------------------------------------------

class TestSendOne:
    def test_success_removes_record(self, client):
        ids = _seed(1)
        rid = ids[0]

        with patch.object(main, "validate_email_full",
                          return_value={"valid": True, "checks": [], "reason": "ok"}):
            with patch.object(main, "_send_email"):
                with patch.object(main, "_get_cached_resume", return_value=b"%PDF"):
                    resp = client.post(f"/records/{rid}/send")

        assert resp.status_code == 200
        assert resp.json()["sent"] == 1

        db = TestSession()
        assert db.query(Record).filter(Record.id == rid).first() is None
        db.close()

    def test_smtp_failure_keeps_record(self, client):
        ids = _seed(1)
        rid = ids[0]

        with patch.object(main, "validate_email_full",
                          return_value={"valid": True, "checks": [], "reason": "ok"}):
            with patch.object(main, "_send_email",
                              side_effect=smtplib.SMTPException("auth error")):
                with patch.object(main, "_get_cached_resume", return_value=b"%PDF"):
                    resp = client.post(f"/records/{rid}/send")

        assert resp.status_code == 200
        assert resp.json()["failed"] == 1

        db = TestSession()
        assert db.query(Record).filter(Record.id == rid).first() is not None, (
            "Record must survive a send failure"
        )
        db.close()

    def test_not_found(self, client):
        resp = client.post("/records/99999/send")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 5. Record CRUD
# ---------------------------------------------------------------------------

class TestRecordCRUD:
    def test_list_empty(self, client):
        resp = client.get("/records")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_create_and_list(self, client):
        # patch at source module — create_record imports them locally from email_checker
        with patch("email_checker.validate_syntax", return_value=(True, "ok")):
            with patch("email_checker.check_typo", return_value=(False, "hr@co.com", "ok")):
                with patch("email_checker.check_disposable", return_value=(True, "ok")):
                    with patch("email_checker.check_mx",
                               return_value=(True, "ok", ["mx.co.com"])):
                        resp = client.post("/records", json=_make_record())

        assert resp.status_code == 200
        assert resp.json()["to_email"] == "hr@company.com"
        assert len(client.get("/records").json()) == 1

    def test_create_invalid_syntax_rejected(self, client):
        with patch("email_checker.validate_syntax", return_value=(False, "invalid format")):
            resp = client.post("/records", json=_make_record(to_email="notanemail"))
        assert resp.status_code == 422

    def test_update_record(self, client):
        ids = _seed(1)
        rid = ids[0]
        updated = _make_record(hr_name="Jane Doe")
        resp = client.put(f"/records/{rid}", json=updated)
        assert resp.status_code == 200
        assert resp.json()["hr_name"] == "Jane Doe"

    def test_delete_record(self, client):
        ids = _seed(1)
        rid = ids[0]
        resp = client.delete(f"/records/{rid}")
        assert resp.status_code == 200

        db = TestSession()
        assert db.query(Record).filter(Record.id == rid).first() is None
        db.close()

    def test_delete_nonexistent(self, client):
        resp = client.delete("/records/99999")
        assert resp.status_code == 404

    def test_clear_all_records(self, client):
        _seed(3)
        resp = client.delete("/records")
        assert resp.status_code == 200

        db = TestSession()
        assert db.query(Record).count() == 0
        db.close()


# ---------------------------------------------------------------------------
# 6. Validation endpoint
# ---------------------------------------------------------------------------

class TestValidateEmail:
    def test_valid_email(self, client):
        with patch("main.validate_email_full",
                   return_value={"valid": True, "checks": [], "reason": "ok"}):
            resp = client.post("/validate-email",
                               json={"email": "hr@company.com"})
        assert resp.status_code == 200
        assert resp.json()["valid"] is True

    def test_invalid_email(self, client):
        with patch("main.validate_email_full",
                   return_value={"valid": False, "checks": [], "reason": "invalid format"}):
            resp = client.post("/validate-email", json={"email": "bad@"})
        assert resp.status_code == 200
        assert resp.json()["valid"] is False


# ---------------------------------------------------------------------------
# 7. Message preview
# ---------------------------------------------------------------------------

class TestMessagePreview:
    def test_job_apply_template(self, client):
        resp = client.post("/message-preview", json={
            "message_type": "job_apply",
            "hr_name": "Alice",
            "company_name": "Acme",
            "role_key": "software_engineer",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "subject" in data and "body" in data
        assert "Alice" in data["body"]

    def test_custom_message_passes_through(self, client):
        resp = client.post("/message-preview", json={
            "message_type": "custom",
            "hr_name": "",
            "company_name": "",
            "role_key": "",
            "custom_subject": "My Subject",
            "custom_body": "My Body",
        })
        assert resp.status_code == 200
        assert resp.json()["subject"] == "My Subject"
        assert resp.json()["body"] == "My Body"

    def test_all_template_types_render(self, client):
        for key in ("job_apply", "interview_schedule", "follow_up",
                    "thank_you", "referral", "cold_outreach"):
            resp = client.post("/message-preview", json={
                "message_type": key,
                "hr_name": "Bob",
                "company_name": "Corp",
                "role_key": "software_engineer",
            })
            assert resp.status_code == 200, f"Template {key} failed"
            assert resp.json()["subject"], f"Empty subject for {key}"


# ---------------------------------------------------------------------------
# 8. Profile & roles meta
# ---------------------------------------------------------------------------

class TestMeta:
    def test_get_profile(self, client):
        resp = client.get("/profile")
        assert resp.status_code == 200
        assert "name" in resp.json()

    def test_get_roles_non_empty(self, client):
        resp = client.get("/roles")
        assert resp.status_code == 200
        roles = resp.json()
        assert isinstance(roles, list) and len(roles) > 0
        assert "key" in roles[0] and "title" in roles[0]

    def test_get_message_templates(self, client):
        resp = client.get("/message-templates")
        assert resp.status_code == 200
        keys = {t["key"] for t in resp.json()}
        assert "job_apply" in keys
        assert "custom" in keys

    def test_role_skills(self, client):
        resp = client.get("/roles/software_engineer/skills")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_role_not_found(self, client):
        resp = client.get("/roles/nonexistent_role_xyz/skills")
        assert resp.status_code == 404
