"""
Tests for the Email Resume Bulk Sender backend.

Covers:
- Record CRUD (create, update, delete, list, clear)
- Single-record send + send-all (success, failure, partial)
- SMTP timeout enforcement
- Email validation endpoint
- Message preview (single template, custom override)
- Profile endpoint
- Compose message logic
- CC update endpoint
- Resume generation/download endpoints (mocked Neon)
- Role CRUD endpoints (mocked Neon)
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
os.environ.setdefault("YOUR_LOCATION", "Mumbai, India")
os.environ.setdefault("YOUR_EXPERIENCE_YEARS", "4+")
os.environ.setdefault("NEON_DATABASE_URL", "")

# ---------------------------------------------------------------------------
# In-memory test DB — patch database module BEFORE importing main
# ---------------------------------------------------------------------------
import database as _db_mod

TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)

_db_mod.engine = TEST_ENGINE
_db_mod.SessionLocal = TestSession
_db_mod.NeonSessionLocal = None

import main

main.SessionLocal = TestSession

from database import Base
from models import Record

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
        experience_years=4,
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
            assert mock_ssl.called
            _, kw = mock_ssl.call_args
            assert kw.get("timeout") == 30


# ---------------------------------------------------------------------------
# 2. skip_smtp at send time
# ---------------------------------------------------------------------------

class TestSkipSMTPAtSend:
    def test_send_single_record_uses_skip_smtp_true(self):
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
                with patch.object(main, "_get_resume_for_send", return_value=b"%PDF"):
                    with patch.object(main, "_get_role_title", return_value="Engineer"):
                        with patch.object(main, "_get_top_skills", return_value="Python"):
                            main._send_single_record(record, db)

        assert observed_skip_smtp
        assert all(observed_skip_smtp)
        db.close()


# ---------------------------------------------------------------------------
# 3. send_all
# ---------------------------------------------------------------------------

def _mock_compose():
    return patch.object(main, "_compose_message", return_value=("Subject", "Body"))


def _mock_smtp():
    """Mock SMTP_SSL so send_all doesn't try a real connection."""
    mock_server = MagicMock()
    mock_server.login = MagicMock()
    mock_server.send_message = MagicMock()
    mock_server.quit = MagicMock()
    return patch("smtplib.SMTP_SSL", return_value=mock_server)


class TestSendAll:
    def test_deletes_sent_records(self, client):
        _seed(3)
        with patch.object(main, "validate_email_full",
                          return_value={"valid": True, "checks": [], "reason": "ok"}):
            with patch.object(main, "_get_resume_for_send", return_value=b"%PDF"):
                with _mock_compose():
                    with _mock_smtp():
                        with patch.object(main, "_get_role_title", return_value="Engineer"):
                            resp = client.post("/send-all")

        assert resp.status_code == 200
        data = resp.json()
        assert data["sent"] == 3
        assert data["failed"] == 0

        db = TestSession()
        assert db.query(Record).count() == 0
        db.close()

    def test_preserves_failed_records(self, client):
        _seed(2)
        mock_server = MagicMock()
        mock_server.login = MagicMock()
        mock_server.send_message = MagicMock(side_effect=smtplib.SMTPException("refused"))
        mock_server.quit = MagicMock()

        with patch.object(main, "validate_email_full",
                          return_value={"valid": True, "checks": [], "reason": "ok"}):
            with patch.object(main, "_get_resume_for_send", return_value=b"%PDF"):
                with _mock_compose():
                    with patch("smtplib.SMTP_SSL", return_value=mock_server):
                        with patch.object(main, "_get_role_title", return_value="Engineer"):
                            resp = client.post("/send-all")

        assert resp.status_code == 200
        data = resp.json()
        assert data["failed"] == 2
        assert data["sent"] == 0

        db = TestSession()
        assert db.query(Record).count() == 2
        db.close()

    def test_partial_success(self, client):
        _seed(4)

        def selective_validate(email, from_email="", skip_smtp=False):
            if "hr0" in email or "hr2" in email:
                return {"valid": False, "checks": [], "reason": "invalid"}
            return {"valid": True, "checks": [], "reason": "ok"}

        with patch.object(main, "validate_email_full", side_effect=selective_validate):
            with patch.object(main, "_get_resume_for_send", return_value=b"%PDF"):
                with _mock_compose():
                    with _mock_smtp():
                        with patch.object(main, "_get_role_title", return_value="Engineer"):
                            resp = client.post("/send-all")

        assert resp.status_code == 200
        data = resp.json()
        assert data["sent"] == 2
        assert data["failed"] == 2

        db = TestSession()
        assert db.query(Record).count() == 2
        db.close()

    def test_empty_queue_returns_400(self, client):
        resp = client.post("/send-all")
        assert resp.status_code == 400
        assert "No records" in resp.json()["detail"]


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
                with patch.object(main, "_get_resume_for_send", return_value=b"%PDF"):
                    with _mock_compose():
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
                with patch.object(main, "_get_resume_for_send", return_value=b"%PDF"):
                    with _mock_compose():
                        resp = client.post(f"/records/{rid}/send")

        assert resp.status_code == 200
        assert resp.json()["failed"] == 1

        db = TestSession()
        assert db.query(Record).filter(Record.id == rid).first() is not None
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
        with patch("email_checker.validate_syntax", return_value=(True, "ok")):
            with patch("email_checker.check_typo", return_value=(False, "hr@co.com", "ok")):
                with patch("email_checker.check_disposable", return_value=(True, "ok")):
                    with patch("email_checker.check_mx",
                               return_value=(True, "ok", ["mx.co.com"])):
                        resp = client.post("/records", json=_make_record())

        assert resp.status_code == 200
        data = resp.json()
        assert data["to_email"] == "hr@company.com"
        assert data["role_key"] == "software_engineer"
        assert data["custom_subject"] == ""
        assert len(client.get("/records").json()) == 1

    def test_create_with_custom_subject_body(self, client):
        with patch("email_checker.validate_syntax", return_value=(True, "ok")):
            with patch("email_checker.check_typo", return_value=(False, "hr@co.com", "ok")):
                with patch("email_checker.check_disposable", return_value=(True, "ok")):
                    with patch("email_checker.check_mx",
                               return_value=(True, "ok", ["mx.co.com"])):
                        resp = client.post("/records", json=_make_record(
                            custom_subject="My Subject",
                            custom_body="My Body",
                        ))

        assert resp.status_code == 200
        data = resp.json()
        assert data["custom_subject"] == "My Subject"
        assert data["custom_body"] == "My Body"

    def test_create_invalid_syntax_rejected(self, client):
        with patch("email_checker.validate_syntax", return_value=(False, "invalid format")):
            resp = client.post("/records", json=_make_record(to_email="notanemail"))
        assert resp.status_code == 422

    def test_create_disposable_rejected(self, client):
        with patch("email_checker.validate_syntax", return_value=(True, "ok")):
            with patch("email_checker.check_typo", return_value=(False, "", "ok")):
                with patch("email_checker.check_disposable",
                           return_value=(False, "Disposable domain")):
                    resp = client.post("/records", json=_make_record(
                        to_email="test@mailinator.com"
                    ))
        assert resp.status_code == 422
        assert "Blocked" in resp.json()["detail"]

    def test_create_typo_rejected(self, client):
        with patch("email_checker.validate_syntax", return_value=(True, "ok")):
            with patch("email_checker.check_typo",
                       return_value=(True, "hr@gmail.com", "Did you mean gmail.com?")):
                resp = client.post("/records", json=_make_record(
                    to_email="hr@gmial.com"
                ))
        assert resp.status_code == 422
        assert "typo" in resp.json()["detail"].lower()

    def test_update_record(self, client):
        ids = _seed(1)
        rid = ids[0]
        updated = _make_record(hr_name="Jane Doe", company_name="NewCo")
        resp = client.put(f"/records/{rid}", json=updated)
        assert resp.status_code == 200
        assert resp.json()["hr_name"] == "Jane Doe"
        assert resp.json()["company_name"] == "NewCo"

    def test_update_nonexistent(self, client):
        resp = client.put("/records/99999", json=_make_record())
        assert resp.status_code == 404

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
# 6. Email validation endpoint
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
                   return_value={"valid": False, "checks": [], "reason": "bad format"}):
            resp = client.post("/validate-email", json={"email": "bad@"})
        assert resp.status_code == 200
        assert resp.json()["valid"] is False

    def test_skip_smtp_flag(self, client):
        with patch("main.validate_email_full",
                   return_value={"valid": True, "checks": [], "reason": "ok"}) as mock_fn:
            client.post("/validate-email",
                        json={"email": "hr@co.com", "skip_smtp": True})
            mock_fn.assert_called_once()
            assert mock_fn.call_args[1].get("skip_smtp") is True or \
                   (len(mock_fn.call_args[0]) > 2 and mock_fn.call_args[0][2] is True)


# ---------------------------------------------------------------------------
# 7. Message compose logic
# ---------------------------------------------------------------------------

class TestComposeMessage:
    def test_default_template_uses_profile(self):
        with patch.object(main, "_get_role_title", return_value="Data Engineer"):
            with patch.object(main, "_get_top_skills", return_value="Python, SQL"):
                subject, body = main._compose_message(
                    "Alice", "TechCo", "data_engineer"
                )
        assert "Data Engineer" in subject
        assert "Alice" in body
        assert "TechCo" in body

    def test_custom_overrides_both(self):
        subject, body = main._compose_message(
            "Bob", "Corp", "swe",
            custom_subject="My Subj", custom_body="My Body"
        )
        assert subject == "My Subj"
        assert body == "My Body"

    def test_custom_subject_only(self):
        with patch.object(main, "_get_role_title", return_value="Engineer"):
            with patch.object(main, "_get_top_skills", return_value="Python"):
                subject, body = main._compose_message(
                    "HR", "Co", "swe", custom_subject="Custom Subj"
                )
        assert subject == "Custom Subj"
        assert "HR" in body

    def test_custom_body_only(self):
        with patch.object(main, "_get_role_title", return_value="Engineer"):
            with patch.object(main, "_get_top_skills", return_value="Python"):
                subject, body = main._compose_message(
                    "HR", "Co", "swe", custom_body="Custom Body"
                )
        assert "Engineer" in subject
        assert body == "Custom Body"

    def test_empty_hr_name_uses_casual_greeting(self):
        with patch.object(main, "_get_role_title", return_value="Engineer"):
            with patch.object(main, "_get_top_skills", return_value="Python"):
                _, body = main._compose_message("", "Co", "swe")
        assert "Hey there," in body

    def test_empty_company_omits_at_company(self):
        with patch.object(main, "_get_role_title", return_value="Engineer"):
            with patch.object(main, "_get_top_skills", return_value="Python"):
                _, body = main._compose_message("Alice", "", "swe")
        assert "position at " not in body


# ---------------------------------------------------------------------------
# 8. Message preview endpoint
# ---------------------------------------------------------------------------

class TestMessagePreview:
    def test_message_preview_basic(self, client):
        resp = client.post("/message-preview", json={
            "role_key": "",
            "role_title": "Software Engineer",
            "hr_name": "Jane",
            "company_name": "Acme Corp",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "subject" in data
        assert "body" in data
        assert "Software Engineer" in data["subject"]
        assert "Jane" in data["body"]
        assert "Acme Corp" in data["body"]

    def test_message_preview_defaults(self, client):
        resp = client.post("/message-preview", json={
            "role_key": "",
            "role_title": "",
            "hr_name": "",
            "company_name": "",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "Hey there," in data["body"]
        assert "Professional" in data["subject"]


# ---------------------------------------------------------------------------
# 9. Profile endpoint
# ---------------------------------------------------------------------------

class TestProfile:
    def test_get_profile_returns_env_values(self, client):
        resp = client.get("/profile")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Test User"
        assert data["email"] == "test@example.com"
        assert data["phone"] == "+91 9999999999"

    def test_profile_has_experience_years(self, client):
        resp = client.get("/profile")
        assert "experience_years" in resp.json()


# ---------------------------------------------------------------------------
# 10. CC update endpoint
# ---------------------------------------------------------------------------

class TestCCUpdate:
    def test_update_cc(self, client):
        ids = _seed(1)
        rid = ids[0]
        resp = client.patch(f"/records/{rid}/cc",
                            json={"cc_emails": "cc1@co.com, cc2@co.com"})
        assert resp.status_code == 200
        assert resp.json()["cc_emails"] == "cc1@co.com, cc2@co.com"

    def test_update_cc_nonexistent(self, client):
        resp = client.patch("/records/99999/cc", json={"cc_emails": "a@b.com"})
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 11. Resume endpoints (Neon required — test 500 when unavailable)
# ---------------------------------------------------------------------------

class TestResumeEndpoints:
    def test_roles_returns_empty_when_no_neon(self, client):
        resp = client.get("/roles")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_role_detail_requires_neon(self, client):
        resp = client.get("/roles/data_engineer")
        assert resp.status_code == 500

    def test_role_skills_requires_neon(self, client):
        resp = client.get("/roles/data_engineer/skills")
        assert resp.status_code == 500

    def test_resume_pdf_requires_neon(self, client):
        resp = client.get("/resume/data_engineer/pdf")
        assert resp.status_code == 500

    def test_resume_latex_requires_neon(self, client):
        resp = client.get("/resume/data_engineer/latex")
        assert resp.status_code == 500

    def test_profile_update_requires_neon(self, client):
        resp = client.put("/profile", json={"name": "New Name"})
        assert resp.status_code == 500


# ---------------------------------------------------------------------------
# 12. Resumes generate and status
# ---------------------------------------------------------------------------

class TestResumesGenerate:
    def test_regenerate(self, client):
        with patch.object(main, "_generate_all_resumes", return_value=5):
            resp = client.post("/resumes/generate")
        assert resp.status_code == 200
        assert "5" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# 13. Helpers
# ---------------------------------------------------------------------------

class TestHelpers:
    def test_parse_cc_emails_empty(self):
        assert main._parse_cc_emails("") == []
        assert main._parse_cc_emails(None) == []
        assert main._parse_cc_emails("   ") == []

    def test_parse_cc_emails_multiple(self):
        result = main._parse_cc_emails("A@b.com, C@d.com, E@F.COM")
        assert result == ["a@b.com", "c@d.com", "e@f.com"]

    def test_parse_cc_emails_strips_whitespace(self):
        result = main._parse_cc_emails("  x@y.com , z@w.com  ")
        assert result == ["x@y.com", "z@w.com"]

    def test_validate_and_filter_cc(self):
        with patch("main.validate_email_full") as mock_fn:
            mock_fn.side_effect = [
                {"valid": True, "reason": "ok"},
                {"valid": False, "reason": "bad"},
            ]
            valid, skipped = main._validate_and_filter_cc(
                ["good@co.com", "bad@co.com"], "from@co.com"
            )
        assert valid == ["good@co.com"]
        assert len(skipped) == 1
        assert skipped[0]["email"] == "bad@co.com"


# ---------------------------------------------------------------------------
# 14. Resume templates module
# ---------------------------------------------------------------------------

class TestResumeTemplates:
    def test_sanitize(self):
        from resume_templates import _sanitize
        assert _sanitize("Hello — world") == "Hello -- world"
        assert _sanitize("It's 'fine'") == "It's 'fine'"
        assert _sanitize("«test»") == "«test»"  # unchanged chars pass through

    def test_resume_pdf_class(self):
        from resume_templates import _ResumePDF
        pdf = _ResumePDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(w=0, h=5, text="Hello World")
        result = bytes(pdf.output())
        assert result[:4] == b"%PDF"

    def test_list_templates_requires_db(self):
        from resume_templates import list_templates
        with pytest.raises(Exception):
            list_templates(db=None)

    def test_get_template_requires_db(self):
        from resume_templates import get_template
        with pytest.raises(Exception):
            get_template("test", db=None)


# ---------------------------------------------------------------------------
# 15. Email checker module
# ---------------------------------------------------------------------------

class TestEmailChecker:
    def test_validate_syntax_valid(self):
        from email_checker import validate_syntax
        ok, reason = validate_syntax("user@example.com")
        assert ok is True

    def test_validate_syntax_invalid(self):
        from email_checker import validate_syntax
        ok, reason = validate_syntax("notanemail")
        assert ok is False

    def test_validate_syntax_empty(self):
        from email_checker import validate_syntax
        ok, reason = validate_syntax("")
        assert ok is False

    def test_check_disposable_clean(self):
        from email_checker import check_disposable
        ok, reason = check_disposable("user@gmail.com")
        assert ok is True

    def test_check_disposable_blocked(self):
        from email_checker import check_disposable
        ok, reason = check_disposable("user@mailinator.com")
        assert ok is False

    def test_check_typo_clean(self):
        from email_checker import check_typo
        has_typo, suggestion, detail = check_typo("user@gmail.com")
        assert has_typo is False

    def test_check_typo_gmial(self):
        from email_checker import check_typo
        has_typo, suggestion, detail = check_typo("user@gmial.com")
        assert has_typo is True
        assert "gmail.com" in suggestion


# ---------------------------------------------------------------------------
# 16. Neon models structure
# ---------------------------------------------------------------------------

class TestNeonModels:
    def test_profile_model_fields(self):
        from neon_models import Profile
        p = Profile()
        assert hasattr(p, "name")
        assert hasattr(p, "email")
        assert hasattr(p, "experience_years")
        assert hasattr(p, "company_1_name")
        assert hasattr(p, "company_2_duration")

    def test_role_model_fields(self):
        from neon_models import Role
        r = Role()
        assert hasattr(r, "key")
        assert hasattr(r, "title")
        assert hasattr(r, "summary")
        assert hasattr(r, "is_active")
        assert hasattr(r, "sort_order")

    def test_role_relationships(self):
        from neon_models import Role
        r = Role()
        assert hasattr(r, "skills")
        assert hasattr(r, "experiences")
        assert hasattr(r, "achievements")
        assert hasattr(r, "focus_areas")

    def test_role_skill_model(self):
        from neon_models import RoleSkill
        s = RoleSkill()
        assert hasattr(s, "category")
        assert hasattr(s, "skills")
        assert hasattr(s, "sort_order")

    def test_role_experience_model(self):
        from neon_models import RoleExperience
        e = RoleExperience()
        assert hasattr(e, "position_index")
        assert hasattr(e, "bullets")
        assert hasattr(e, "client_name")
        assert hasattr(e, "client_location")
        assert hasattr(e, "min_years")

    def test_role_achievement_model(self):
        from neon_models import RoleAchievement
        a = RoleAchievement()
        assert hasattr(a, "text")
        assert hasattr(a, "sort_order")

    def test_role_focus_area_model(self):
        from neon_models import RoleFocusArea
        f = RoleFocusArea()
        assert hasattr(f, "area")
        assert hasattr(f, "sort_order")


# ---------------------------------------------------------------------------
# 17. Pydantic schema validation
# ---------------------------------------------------------------------------

class TestSchemas:
    def test_record_create_no_message_type(self):
        schema = main.RecordCreate(to_email="hr@co.com")
        assert not hasattr(schema, "message_type")
        assert schema.custom_subject == ""
        assert schema.custom_body == ""
        assert schema.role_key == ""

    def test_record_create_all_fields(self):
        schema = main.RecordCreate(
            to_email="hr@co.com",
            cc_emails="cc@co.com",
            hr_name="Alice",
            company_name="Corp",
            role_key="swe",
            experience_years=6,
            custom_subject="Subj",
            custom_body="Body",
        )
        assert schema.to_email == "hr@co.com"
        assert schema.cc_emails == "cc@co.com"
        assert schema.hr_name == "Alice"
        assert schema.experience_years == 6

    def test_record_create_default_experience(self):
        schema = main.RecordCreate(to_email="hr@co.com")
        assert schema.experience_years == 4

    def test_record_out_no_message_type(self):
        fields = set(main.RecordOut.model_fields.keys())
        assert "message_type" not in fields
        assert "to_email" in fields
        assert "role_key" in fields
        assert "custom_subject" in fields
        assert "experience_years" in fields

    def test_record_create_rejects_invalid_email(self):
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            main.RecordCreate(to_email="not-an-email")


# ---------------------------------------------------------------------------
# 18. SQLite Record model
# ---------------------------------------------------------------------------

class TestRecordModel:
    def test_record_has_no_message_type_column(self):
        columns = {c.name for c in Record.__table__.columns}
        assert "message_type" not in columns
        assert "to_email" in columns
        assert "role_key" in columns
        assert "custom_subject" in columns
        assert "custom_body" in columns

    def test_record_columns_exist(self):
        columns = {c.name for c in Record.__table__.columns}
        for col in ("to_email", "cc_emails", "hr_name", "company_name",
                     "role_key", "experience_years", "custom_subject",
                     "custom_body", "created_at"):
            assert col in columns, f"Missing column: {col}"


# ---------------------------------------------------------------------------
# 19. Experience years flow
# ---------------------------------------------------------------------------

def _mock_email_checks():
    """Context manager that patches all email validation checks for record creation."""
    from contextlib import contextmanager
    @contextmanager
    def _ctx():
        with patch("email_checker.validate_syntax", return_value=(True, "ok")):
            with patch("email_checker.check_typo", return_value=(False, "", "ok")):
                with patch("email_checker.check_disposable", return_value=(True, "ok")):
                    with patch("email_checker.check_mx", return_value=(True, "ok", ["mx.co.com"])):
                        yield
    return _ctx()


class TestExperienceYears:
    def test_create_record_with_experience_years(self, client):
        data = _make_record(experience_years=7)
        with _mock_email_checks():
            resp = client.post("/records", json=data)
        assert resp.status_code == 200
        assert resp.json()["experience_years"] == 7

    def test_create_record_default_experience_years(self, client):
        data = _make_record()
        del data["experience_years"]
        with _mock_email_checks():
            resp = client.post("/records", json=data)
        assert resp.status_code == 200
        assert resp.json()["experience_years"] == 4

    def test_update_record_experience_years(self, client):
        ids = _seed(1)
        data = _make_record(experience_years=9)
        resp = client.put(f"/records/{ids[0]}", json=data)
        assert resp.status_code == 200
        assert resp.json()["experience_years"] == 9

    def test_message_preview_with_experience_years(self, client):
        resp = client.post("/message-preview", json={
            "role_title": "Software Engineer",
            "hr_name": "Test",
            "company_name": "Corp",
            "experience_years": 7,
        })
        assert resp.status_code == 200
        body = resp.json()
        assert "7" in body["subject"]
        assert "7" in body["body"]

    def test_compose_message_uses_experience_years(self):
        subj, body = main._compose_message(
            "HR", "Corp", "", experience_years=5
        )
        assert "5" in subj
        assert "5" in body

    def test_latex_resume_filters_clients(self):
        from resume_templates import make_latex_resume
        template = {
            "title": "Test Dev",
            "summary": "Developer with 4+ years experience.",
            "skills": {"Languages": ["Python"]},
            "clients": [
                {"client_name": "Alpha", "client_location": "US",
                 "min_years": 1, "position_index": 0, "bullets": ["Bullet A"]},
                {"client_name": "Beta", "client_location": "UK",
                 "min_years": 5, "position_index": 1, "bullets": ["Bullet B"]},
                {"client_name": "Gamma", "client_location": "DE",
                 "min_years": 9, "position_index": 2, "bullets": ["Bullet C"]},
            ],
            "focus": [],
            "achievements": ["Award"],
            "coursework": "CS",
        }
        basics = {"name": "Test User"}

        latex_3 = make_latex_resume(template, basics, experience_years=3)
        assert "Alpha" in latex_3
        assert "Beta" not in latex_3
        assert "Gamma" not in latex_3

        latex_6 = make_latex_resume(template, basics, experience_years=6)
        assert "Alpha" in latex_6
        assert "Beta" in latex_6
        assert "Gamma" not in latex_6

        latex_10 = make_latex_resume(template, basics, experience_years=10)
        assert "Alpha" in latex_10
        assert "Beta" in latex_10
        assert "Gamma" in latex_10

    def test_latex_resume_updates_experience_in_summary(self):
        from resume_templates import make_latex_resume
        template = {
            "title": "Dev",
            "summary": "Developer with 4+ years experience.",
            "skills": {},
            "clients": [],
            "focus": [],
            "achievements": [],
            "coursework": "",
        }
        basics = {"name": "Test"}
        latex = make_latex_resume(template, basics, experience_years=7)
        assert "7 years" in latex.lower() or "7" in latex


# ---------------------------------------------------------------------------
# 20. _get_role_title / _get_top_skills guards (no Neon)
# ---------------------------------------------------------------------------

class TestRoleTitleSkillsGuards:
    def test_get_role_title_no_neon(self):
        with patch.object(main, "_neon_db_session", return_value=None):
            title = main._get_role_title("data_engineer")
        assert title == "Data Engineer"

    def test_get_role_title_empty_key(self):
        assert main._get_role_title("") == "Professional"

    def test_get_role_title_with_template(self):
        mock_db = MagicMock()
        with patch.object(main, "_neon_db_session", return_value=mock_db):
            with patch("main.get_template", return_value={"title": "AI Engineer"}):
                title = main._get_role_title("ai_ml_engineer")
        assert title == "AI Engineer"

    def test_get_role_title_template_not_found(self):
        mock_db = MagicMock()
        with patch.object(main, "_neon_db_session", return_value=mock_db):
            with patch("main.get_template", return_value=None):
                title = main._get_role_title("unknown_role")
        assert title == "Unknown Role"

    def test_get_top_skills_no_neon(self):
        with patch.object(main, "_neon_db_session", return_value=None):
            skills = main._get_top_skills("data_engineer")
        assert skills == "modern technologies and tools"

    def test_get_top_skills_empty_key(self):
        assert main._get_top_skills("") == "modern technologies and tools"

    def test_get_top_skills_with_template(self):
        mock_db = MagicMock()
        tmpl = {"skills": {"Languages": ["Python", "SQL"], "Tools": ["Docker", "Git", "AWS"]}}
        with patch.object(main, "_neon_db_session", return_value=mock_db):
            with patch("main.get_template", return_value=tmpl):
                skills = main._get_top_skills("swe", count=3)
        assert skills == "Python, SQL, Docker"


# ---------------------------------------------------------------------------
# 21. _neon_db_session helper
# ---------------------------------------------------------------------------

class TestNeonDbSession:
    def test_returns_none_when_no_neon(self):
        orig = main.NeonSessionLocal
        main.NeonSessionLocal = None
        try:
            assert main._neon_db_session() is None
        finally:
            main.NeonSessionLocal = orig

    def test_returns_session_when_configured(self):
        mock_session = MagicMock()
        orig = main.NeonSessionLocal
        main.NeonSessionLocal = mock_session
        try:
            result = main._neon_db_session()
            mock_session.assert_called_once()
        finally:
            main.NeonSessionLocal = orig


# ---------------------------------------------------------------------------
# 22. _get_resume_for_send
# ---------------------------------------------------------------------------

class TestGetResumeForSend:
    def test_returns_custom_resume_if_set(self, tmp_path):
        custom_pdf = tmp_path / "custom.pdf"
        custom_pdf.write_bytes(b"%PDF-custom")
        with patch.dict(os.environ, {"CUSTOM_RESUME_PATH": str(custom_pdf)}):
            result = main._get_resume_for_send("swe", 4)
        assert result == b"%PDF-custom"

    def test_returns_generated_pdf(self):
        with patch.dict(os.environ, {"CUSTOM_RESUME_PATH": ""}):
            with patch.object(main, "_neon_db_session", return_value=MagicMock()):
                with patch("main.generate_pdf_resume", return_value=b"%PDF-gen"):
                    result = main._get_resume_for_send("swe", 4)
        assert result == b"%PDF-gen"

    def test_closes_neon_db(self):
        mock_db = MagicMock()
        with patch.dict(os.environ, {"CUSTOM_RESUME_PATH": ""}):
            with patch.object(main, "_neon_db_session", return_value=mock_db):
                with patch("main.generate_pdf_resume", return_value=b"%PDF"):
                    main._get_resume_for_send("swe", 4)
        mock_db.close.assert_called_once()


# ---------------------------------------------------------------------------
# 23. _generate_all_resumes
# ---------------------------------------------------------------------------

class TestGenerateAllResumes:
    def test_returns_zero_when_no_neon(self):
        orig = main.NeonSessionLocal
        main.NeonSessionLocal = None
        try:
            result = main._generate_all_resumes()
        finally:
            main.NeonSessionLocal = orig
        assert result == 0

    def test_generates_resumes(self, tmp_path):
        mock_db = MagicMock()
        mock_tmpl = [{"key": "swe", "title": "SWE"}]
        with patch.object(main, "_neon_db_session", return_value=mock_db):
            with patch("main.list_templates", return_value=mock_tmpl):
                with patch("main.generate_pdf_resume", return_value=b"%PDF"):
                    main.RESUME_DIR = tmp_path
                    result = main._generate_all_resumes()
        assert result == 1
        assert (tmp_path / "swe.pdf").exists()


# ---------------------------------------------------------------------------
# 24. compile-latex endpoint
# ---------------------------------------------------------------------------

class TestCompileLatex:
    def test_compiler_not_found(self, client):
        with patch.object(main, "_find_latex_compiler",
                          side_effect=RuntimeError("No compiler")):
            resp = client.post("/resume/compile-latex",
                               json={"latex": "\\doc", "filename": "test.pdf"})
        assert resp.status_code == 500
        assert "No compiler" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# 25. _compute_client_dates
# ---------------------------------------------------------------------------

class TestComputeClientDates:
    def test_empty_clients(self):
        from resume_templates import _compute_client_dates
        assert _compute_client_dates([], 5) == []

    def test_single_client(self):
        from resume_templates import _compute_client_dates
        clients = [{"client_name": "A", "min_years": 1}]
        result = _compute_client_dates(clients, 3)
        assert len(result) == 1
        assert "Present" in result[0]["end"]

    def test_multiple_clients(self):
        from resume_templates import _compute_client_dates
        clients = [
            {"client_name": "A", "min_years": 1},
            {"client_name": "B", "min_years": 1},
            {"client_name": "C", "min_years": 1},
        ]
        result = _compute_client_dates(clients, 6)
        assert len(result) == 3
        assert "Present" in result[0]["end"]
        assert "Present" not in result[2]["end"]
        for r in result:
            assert "--" in r["dur"]


# ---------------------------------------------------------------------------
# 26. LaTeX helpers
# ---------------------------------------------------------------------------

class TestLatexHelpers:
    def test_latex_escape(self):
        from resume_templates import _latex_escape
        assert _latex_escape("A & B") == r"A \& B"
        assert _latex_escape("100%") == r"100\%"
        assert _latex_escape("$50") == r"\$50"
        assert _latex_escape("C# lang") == r"C\# lang"
        assert _latex_escape("under_score") == r"under\_score"

    def test_normalize_link(self):
        from resume_templates import _normalize_link
        assert _normalize_link("https://github.com/user", "") == "github.com/user"
        assert _normalize_link("http://example.com/", "") == "example.com"
        assert _normalize_link("", "fallback.com") == "fallback.com"

    def test_tex_resume_items(self):
        from resume_templates import _tex_resume_items
        result = _tex_resume_items(["Built API", "Deployed"])
        assert "\\resumeItem{Built API}" in result
        assert "\\resumeItem{Deployed}" in result

    def test_tex_skill_items(self):
        from resume_templates import _tex_skill_items
        result = _tex_skill_items({"Languages": ["Python", "Go"]})
        assert "\\textbf{Languages}" in result
        assert "Python, Go" in result


# ---------------------------------------------------------------------------
# 27. make_latex_resume full output validation
# ---------------------------------------------------------------------------

class TestMakeLatexResumeFull:
    @pytest.fixture()
    def sample_template(self):
        return {
            "title": "Software Engineer",
            "summary": "Engineer with 4+ years of experience.",
            "skills": {"Languages": ["Python", "SQL"], "Tools": ["Docker"]},
            "clients": [
                {"client_name": "Spreetail", "client_location": "US",
                 "min_years": 1, "position_index": 0,
                 "bullets": ["Built REST APIs", "Optimized queries"]},
                {"client_name": "Meridian", "client_location": "UK",
                 "min_years": 3, "position_index": 1,
                 "bullets": ["Led migrations"]},
            ],
            "focus": ["Backend development"],
            "achievements": ["Reduced latency by 40%"],
            "coursework": "Data Structures, Algorithms",
        }

    @pytest.fixture()
    def sample_basics(self):
        return {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1 555-0100",
            "linkedin": "https://linkedin.com/in/johndoe",
            "github": "https://github.com/johndoe",
            "portfolio": "https://johndoe.dev",
            "education": "B.Tech, MIT",
            "graduation_year": "2022 -- 2026",
            "location": "Cambridge, MA",
            "company_1_name": "CubexO",
            "company_1_location": "Indore, India",
            "company_1_role": "Software Engineer",
        }

    def test_latex_has_required_sections(self, sample_template, sample_basics):
        from resume_templates import make_latex_resume
        latex = make_latex_resume(sample_template, sample_basics, experience_years=5)
        assert "\\section*{Professional Summary}" in latex
        assert "\\section{Technical Skills}" in latex
        assert "\\section{Experience}" in latex
        assert "\\section{Education}" in latex

    def test_latex_contains_name_and_contact(self, sample_template, sample_basics):
        from resume_templates import make_latex_resume
        latex = make_latex_resume(sample_template, sample_basics, experience_years=4)
        assert "JOHN DOE" in latex
        assert "john@example.com" in latex
        assert "+1 555-0100" in latex

    def test_latex_contains_skills(self, sample_template, sample_basics):
        from resume_templates import make_latex_resume
        latex = make_latex_resume(sample_template, sample_basics, experience_years=4)
        assert "Python" in latex
        assert "Docker" in latex

    def test_latex_defaults_for_missing_profile(self, sample_template):
        from resume_templates import make_latex_resume
        latex = make_latex_resume(sample_template, {}, experience_years=4)
        assert "YOUR NAME" in latex
        assert "email@example.com" in latex

    def test_latex_experience_years_clamped(self, sample_template, sample_basics):
        from resume_templates import make_latex_resume
        latex_low = make_latex_resume(sample_template, sample_basics, experience_years=0)
        assert "1" in latex_low or "Spreetail" in latex_low
        latex_high = make_latex_resume(sample_template, sample_basics, experience_years=15)
        assert "Spreetail" in latex_high
        assert "Meridian" in latex_high


# ---------------------------------------------------------------------------
# 28. generate_pdf_resume produces valid PDF
# ---------------------------------------------------------------------------

class TestGeneratePdfResume:
    def test_produces_pdf_bytes(self):
        from resume_templates import generate_pdf_resume
        mock_role = MagicMock()
        mock_role.key = "swe"
        mock_role.title = "Software Engineer"
        mock_role.previous_title = ""
        mock_role.summary = "Test engineer"
        mock_role.coursework = "CS"
        mock_role.skills = []
        mock_role.experiences = []
        mock_role.achievements = []
        mock_role.focus_areas = []

        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = mock_role

        profile = {"name": "Test", "email": "t@t.com"}
        result = generate_pdf_resume("swe", profile, db=mock_db, experience_years=4)
        assert result[:4] == b"%PDF"

    def test_unknown_role_raises(self):
        from resume_templates import generate_pdf_resume
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ValueError, match="Unknown role"):
            generate_pdf_resume("nonexistent", {}, db=mock_db)


# ---------------------------------------------------------------------------
# 29. _sanitize edge cases
# ---------------------------------------------------------------------------

class TestSanitizeEdgeCases:
    def test_all_replacements(self):
        from resume_templates import _sanitize
        assert _sanitize("—") == "--"
        assert _sanitize("–") == "-"
        assert _sanitize("‘") == "'"
        assert _sanitize("’") == "'"
        assert _sanitize("“") == '"'
        assert _sanitize("”") == '"'
        assert _sanitize("…") == "..."
        assert _sanitize("•") == "-"

    def test_plain_text_unchanged(self):
        from resume_templates import _sanitize
        assert _sanitize("Hello World 123") == "Hello World 123"


# ---------------------------------------------------------------------------
# 30. _ResumePDF methods
# ---------------------------------------------------------------------------

class TestResumePDFMethods:
    def test_section_header(self):
        from resume_templates import _ResumePDF
        pdf = _ResumePDF()
        pdf.add_page()
        pdf.section_header("Test Section")
        result = bytes(pdf.output())
        assert result[:4] == b"%PDF"

    def test_bullet(self):
        from resume_templates import _ResumePDF
        pdf = _ResumePDF()
        pdf.add_page()
        pdf.bullet("A test bullet point")
        result = bytes(pdf.output())
        assert result[:4] == b"%PDF"


# ---------------------------------------------------------------------------
# 31. Neon model structure (no RoleProject)
# ---------------------------------------------------------------------------

class TestNeonModelsClean:
    def test_no_role_project_model(self):
        import neon_models
        assert not hasattr(neon_models, "RoleProject")

    def test_role_has_no_projects_relationship(self):
        from neon_models import Role
        r = Role()
        assert not hasattr(r, "projects")


# ---------------------------------------------------------------------------
# 32. Send email constructs proper message
# ---------------------------------------------------------------------------

class TestSendEmailMessage:
    def test_send_email_with_cc(self):
        mock_server = MagicMock()
        mock_server.__enter__ = lambda s: s
        mock_server.__exit__ = MagicMock(return_value=False)

        with patch("smtplib.SMTP_SSL", return_value=mock_server):
            main._send_email(
                "to@co.com", "Subj", "Body", b"%PDF", "resume.pdf",
                cc_emails=["cc1@co.com", "cc2@co.com"]
            )
        mock_server.send_message.assert_called_once()
        args, kwargs = mock_server.send_message.call_args
        msg = args[0]
        assert msg["Cc"] == "cc1@co.com, cc2@co.com"
        recipients = kwargs.get("to_addrs") or args[1] if len(args) > 1 else None
        if recipients:
            assert "to@co.com" in recipients
            assert "cc1@co.com" in recipients

    def test_send_email_no_cc(self):
        mock_server = MagicMock()
        mock_server.__enter__ = lambda s: s
        mock_server.__exit__ = MagicMock(return_value=False)

        with patch("smtplib.SMTP_SSL", return_value=mock_server):
            main._send_email(
                "to@co.com", "Subj", "Body", b"%PDF", "resume.pdf"
            )
        mock_server.send_message.assert_called_once()


# ---------------------------------------------------------------------------
# 33. Role CRUD with mocked Neon
# ---------------------------------------------------------------------------

class TestRoleCRUDMocked:
    @pytest.fixture()
    def neon_client(self):
        mock_db = MagicMock()

        def override():
            try:
                yield mock_db
            finally:
                pass

        main.app.dependency_overrides[main._get_db] = _override_get_db
        main.app.dependency_overrides[main._get_neon_db] = override
        with TestClient(main.app) as c:
            yield c, mock_db
        main.app.dependency_overrides.clear()

    def test_create_role_missing_key(self, neon_client):
        c, mock_db = neon_client
        resp = c.post("/roles", json={"key": "", "title": "New"})
        assert resp.status_code == 422
        assert "key is required" in resp.json()["detail"].lower()

    def test_delete_role_not_found(self, neon_client):
        c, mock_db = neon_client
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = c.delete("/roles/nonexistent")
        assert resp.status_code == 404

    def test_update_role_not_found(self, neon_client):
        c, mock_db = neon_client
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = c.put("/roles/nonexistent", json={"title": "New Title"})
        assert resp.status_code == 404

    def test_get_role_detail_not_found(self, neon_client):
        c, mock_db = neon_client
        with patch("main.get_template", return_value=None):
            resp = c.get("/roles/nonexistent")
        assert resp.status_code == 404

    def test_update_skills_role_not_found(self, neon_client):
        c, mock_db = neon_client
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = c.put("/roles/nonexistent/skills", json=[])
        assert resp.status_code == 404

    def test_update_experience_role_not_found(self, neon_client):
        c, mock_db = neon_client
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = c.put("/roles/nonexistent/experience", json=[])
        assert resp.status_code == 404

    def test_update_achievements_role_not_found(self, neon_client):
        c, mock_db = neon_client
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = c.put("/roles/nonexistent/achievements", json=[])
        assert resp.status_code == 404

    def test_update_focus_role_not_found(self, neon_client):
        c, mock_db = neon_client
        mock_db.query.return_value.filter.return_value.first.return_value = None
        resp = c.put("/roles/nonexistent/focus", json=[])
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 34. Profile update with mocked Neon
# ---------------------------------------------------------------------------

class TestProfileUpdate:
    def test_update_profile_creates_new(self):
        mock_db = MagicMock()
        mock_db.query.return_value.first.return_value = None

        def override():
            try:
                yield mock_db
            finally:
                pass

        main.app.dependency_overrides[main._get_db] = _override_get_db
        main.app.dependency_overrides[main._get_neon_db] = override
        with TestClient(main.app) as c:
            with patch.object(main, "_get_profile", return_value={"name": "New"}):
                resp = c.put("/profile", json={"name": "New Name"})
        main.app.dependency_overrides.clear()
        assert resp.status_code == 200
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()


# ---------------------------------------------------------------------------
# 35. _send_single_record edge cases
# ---------------------------------------------------------------------------

class TestSendSingleRecordEdgeCases:
    def test_invalid_to_email_returns_failed(self):
        db = TestSession()
        record = Record(**_make_record())
        db.add(record)
        db.commit()
        db.refresh(record)

        with patch.object(main, "validate_email_full",
                          return_value={"valid": False, "checks": ["syntax"], "reason": "bad"}):
            result = main._send_single_record(record, db)
        assert result["status"] == "failed"
        assert "TO validation" in result["error"]
        db.close()

    def test_fallback_resume_on_generation_error(self):
        db = TestSession()
        record = Record(**_make_record(role_key="broken_role"))
        db.add(record)
        db.commit()
        db.refresh(record)

        call_count = [0]
        def mock_resume(role_key, exp_years):
            call_count[0] += 1
            if role_key == "broken_role":
                raise Exception("generation failed")
            return b"%PDF-fallback"

        with patch.object(main, "validate_email_full",
                          return_value={"valid": True, "checks": [], "reason": "ok"}):
            with patch.object(main, "_get_resume_for_send", side_effect=mock_resume):
                with patch.object(main, "_send_email"):
                    with patch.object(main, "_get_role_title", return_value="Engineer"):
                        with patch.object(main, "_get_top_skills", return_value="Python"):
                            result = main._send_single_record(record, db)
        assert result["status"] == "sent"
        assert call_count[0] == 2
        db.close()


# ---------------------------------------------------------------------------
# 36. Message preview edge cases
# ---------------------------------------------------------------------------

class TestMessagePreviewEdgeCases:
    def test_preview_with_role_key_no_title(self, client):
        with patch.object(main, "_get_role_title", return_value="Data Scientist"):
            with patch.object(main, "_get_top_skills", return_value="Python, R"):
                resp = client.post("/message-preview", json={
                    "role_key": "data_scientist",
                    "role_title": "",
                    "hr_name": "Bob",
                    "company_name": "Corp",
                })
        assert resp.status_code == 200
        assert "Data Scientist" in resp.json()["subject"]

    def test_preview_with_experience_years(self, client):
        resp = client.post("/message-preview", json={
            "role_key": "",
            "role_title": "Engineer",
            "hr_name": "Test",
            "company_name": "Co",
            "experience_years": 9,
        })
        assert resp.status_code == 200
        assert "9" in resp.json()["subject"]


# ---------------------------------------------------------------------------
# 20. Client date computation
# ---------------------------------------------------------------------------

class TestClientDateComputation:
    def test_empty_clients_returns_empty(self):
        from resume_templates import _compute_client_dates
        assert _compute_client_dates([], 5) == []

    def test_single_client_ends_with_present(self):
        from resume_templates import _compute_client_dates
        clients = [{"client_name": "A", "min_years": 1, "position_index": 0}]
        dates = _compute_client_dates(clients, 3)
        assert len(dates) == 1
        assert dates[0]["end"] == "Present"

    def test_multiple_clients_last_is_present(self):
        from resume_templates import _compute_client_dates
        clients = [
            {"client_name": "A", "min_years": 1, "position_index": 0},
            {"client_name": "B", "min_years": 3, "position_index": 1},
        ]
        dates = _compute_client_dates(clients, 5)
        assert len(dates) == 2
        assert dates[0]["end"] == "Present"
        assert "Present" not in dates[1]["end"]

    def test_dates_have_dur_field(self):
        from resume_templates import _compute_client_dates
        clients = [{"client_name": "A", "min_years": 1, "position_index": 0}]
        dates = _compute_client_dates(clients, 2)
        assert "dur" in dates[0]
        assert "--" in dates[0]["dur"]


# ---------------------------------------------------------------------------
# 21. PDF resume generation
# ---------------------------------------------------------------------------

class TestPDFGeneration:
    def test_generate_pdf_produces_valid_pdf(self):
        from resume_templates import generate_pdf_resume
        mock_db = MagicMock()
        mock_role = MagicMock()
        mock_role.key = "test_role"
        mock_role.title = "Test Developer"
        mock_role.previous_title = ""
        mock_role.summary = "Test summary with 4+ years."
        mock_role.coursework = "CS"

        mock_skill = MagicMock()
        mock_skill.category = "Languages"
        mock_skill.skills = ["Python", "SQL"]
        mock_role.skills = [mock_skill]

        mock_exp = MagicMock()
        mock_exp.client_name = "TestClient"
        mock_exp.client_location = "US"
        mock_exp.min_years = 1
        mock_exp.position_index = 0
        mock_exp.bullets = ["Built APIs", "Deployed services"]
        mock_role.experiences = [mock_exp]

        mock_role.focus_areas = []
        mock_role.achievements = [MagicMock(text="Won award")]

        mock_db.query.return_value.filter.return_value.first.return_value = mock_role

        profile = {"name": "Test User", "email": "test@test.com"}
        pdf_bytes = generate_pdf_resume("test_role", profile, db=mock_db)
        assert pdf_bytes[:4] == b"%PDF"

    def test_generate_pdf_with_experience_filter(self):
        from resume_templates import generate_pdf_resume
        mock_db = MagicMock()
        mock_role = MagicMock()
        mock_role.key = "test"
        mock_role.title = "Dev"
        mock_role.previous_title = ""
        mock_role.summary = "Dev with 4+ years."
        mock_role.coursework = "CS"
        mock_role.skills = []

        exp1 = MagicMock()
        exp1.client_name = "Alpha"
        exp1.client_location = "US"
        exp1.min_years = 1
        exp1.position_index = 0
        exp1.bullets = ["Bullet A"]

        exp2 = MagicMock()
        exp2.client_name = "Beta"
        exp2.client_location = "UK"
        exp2.min_years = 5
        exp2.position_index = 1
        exp2.bullets = ["Bullet B"]

        mock_role.experiences = [exp1, exp2]
        mock_role.focus_areas = []
        mock_role.achievements = []

        mock_db.query.return_value.filter.return_value.first.return_value = mock_role

        profile = {"name": "Test"}
        pdf_2yr = generate_pdf_resume("test", profile, db=mock_db, experience_years=2)
        assert pdf_2yr[:4] == b"%PDF"

    def test_generate_pdf_unknown_role_raises(self):
        from resume_templates import generate_pdf_resume
        mock_db = MagicMock()
        mock_db.query.return_value.filter.return_value.first.return_value = None
        with pytest.raises(ValueError, match="Unknown role key"):
            generate_pdf_resume("nonexistent", {}, db=mock_db)


# ---------------------------------------------------------------------------
# 22. LaTeX resume generation
# ---------------------------------------------------------------------------

class TestLatexGeneration:
    def test_latex_escape_special_chars(self):
        from resume_templates import _latex_escape
        assert r"\&" in _latex_escape("AT&T")
        assert r"\%" in _latex_escape("100%")
        assert r"\$" in _latex_escape("$100")
        assert r"\#" in _latex_escape("#1")

    def test_normalize_link_strips_protocol(self):
        from resume_templates import _normalize_link
        assert _normalize_link("https://github.com/user", "") == "github.com/user"
        assert _normalize_link("http://example.com/", "") == "example.com"

    def test_normalize_link_uses_fallback(self):
        from resume_templates import _normalize_link
        result = _normalize_link("", "github.com/default")
        assert result == "github.com/default"

    def test_latex_resume_contains_all_sections(self):
        from resume_templates import make_latex_resume
        template = {
            "title": "Software Developer",
            "summary": "Summary text with 4+ years.",
            "skills": {"Languages": ["Python", "SQL"]},
            "clients": [
                {"client_name": "ClientA", "client_location": "US",
                 "min_years": 1, "position_index": 0,
                 "bullets": ["Built APIs"]},
            ],
            "focus": ["Backend"],
            "achievements": ["Best developer"],
            "coursework": "Data Structures",
        }
        basics = {"name": "Test User", "email": "test@test.com"}
        latex = make_latex_resume(template, basics, experience_years=4)

        assert "Professional Summary" in latex
        assert "Technical Skills" in latex
        assert "Experience" in latex
        assert "Education" in latex
        assert "ClientA" in latex
        assert "Python" in latex


# ---------------------------------------------------------------------------
# 23. _get_resume_for_send
# ---------------------------------------------------------------------------

class TestGetResumeForSend:
    def test_uses_custom_resume_path(self, tmp_path):
        custom_pdf = tmp_path / "custom.pdf"
        custom_pdf.write_bytes(b"%PDF-custom")
        with patch.dict(os.environ, {"CUSTOM_RESUME_PATH": str(custom_pdf)}):
            result = main._get_resume_for_send("any_role", 4)
        assert result == b"%PDF-custom"

    def test_generates_fresh_pdf(self):
        with patch.dict(os.environ, {"CUSTOM_RESUME_PATH": ""}):
            with patch.object(main, "generate_pdf_resume", return_value=b"%PDF-fresh") as mock_gen:
                with patch.object(main, "_neon_db_session", return_value=None):
                    result = main._get_resume_for_send("sw_eng", 6)
        assert result == b"%PDF-fresh"
        mock_gen.assert_called_once()
        assert mock_gen.call_args[1]["experience_years"] == 6


# ---------------------------------------------------------------------------
# 24. Send single record with experience_years
# ---------------------------------------------------------------------------

class TestSendSingleWithExperience:
    def test_send_passes_experience_years_to_resume(self):
        db = TestSession()
        record = Record(**_make_record(experience_years=8))
        db.add(record)
        db.commit()
        db.refresh(record)

        resume_exp = []

        def capture_resume(role_key, exp_years=4):
            resume_exp.append(exp_years)
            return b"%PDF"

        with patch.object(main, "validate_email_full",
                          return_value={"valid": True, "checks": [], "reason": "ok"}):
            with patch.object(main, "_send_email"):
                with patch.object(main, "_get_resume_for_send", side_effect=capture_resume):
                    with patch.object(main, "_get_role_title", return_value="Engineer"):
                        with patch.object(main, "_get_top_skills", return_value="Python"):
                            main._send_single_record(record, db)

        assert resume_exp == [8]
        db.close()


# ---------------------------------------------------------------------------
# 25. Record CRUD edge cases
# ---------------------------------------------------------------------------

class TestRecordEdgeCases:
    def test_create_with_all_experience_values(self, client):
        with _mock_email_checks():
            for exp in [1, 5, 10]:
                data = _make_record(to_email=f"hr{exp}@company.com", experience_years=exp)
                resp = client.post("/records", json=data)
                assert resp.status_code == 200
                assert resp.json()["experience_years"] == exp

    def test_update_preserves_all_fields(self, client):
        ids = _seed(1)
        updated = _make_record(
            to_email="new@co.com",
            cc_emails="cc@co.com",
            hr_name="Alice",
            company_name="NewCo",
            role_key="data_engineer",
            experience_years=7,
            custom_subject="Custom Sub",
            custom_body="Custom Body",
        )
        resp = client.put(f"/records/{ids[0]}", json=updated)
        assert resp.status_code == 200
        data = resp.json()
        assert data["to_email"] == "new@co.com"
        assert data["cc_emails"] == "cc@co.com"
        assert data["hr_name"] == "Alice"
        assert data["company_name"] == "NewCo"
        assert data["role_key"] == "data_engineer"
        assert data["experience_years"] == 7
        assert data["custom_subject"] == "Custom Sub"
        assert data["custom_body"] == "Custom Body"


# ---------------------------------------------------------------------------
# 26. Profile endpoint edge cases
# ---------------------------------------------------------------------------

class TestProfileEdgeCases:
    def test_profile_contains_company_fields(self, client):
        resp = client.get("/profile")
        assert resp.status_code == 200
        data = resp.json()
        assert "company_1_name" in data
        assert "company_1_role" in data
        assert "company_1_location" in data
        assert "company_1_duration" in data

    def test_profile_contains_all_personal_fields(self, client):
        resp = client.get("/profile")
        data = resp.json()
        for field in ["name", "email", "phone", "location",
                      "linkedin", "github", "portfolio",
                      "education", "graduation_year"]:
            assert field in data


# ---------------------------------------------------------------------------
# 27. Compose message edge cases
# ---------------------------------------------------------------------------

class TestComposeEdgeCases:
    def test_compose_with_zero_experience(self):
        subj, body = main._compose_message(
            "HR", "Corp", "", experience_years=0
        )
        assert "0" in subj

    def test_compose_with_large_experience(self):
        subj, body = main._compose_message(
            "HR", "Corp", "", experience_years=10
        )
        assert "10" in subj
        assert "10" in body

    def test_compose_all_empty_strings(self):
        subj, body = main._compose_message("", "", "")
        assert "Hey there," in body
        assert "Professional" in subj

    def test_compose_custom_subject_default_body(self):
        with patch.object(main, "_get_role_title", return_value="Dev"):
            with patch.object(main, "_get_top_skills", return_value="Python"):
                subj, body = main._compose_message(
                    "HR", "Co", "swe",
                    custom_subject="My Subject",
                    custom_body="",
                )
        assert subj == "My Subject"
        assert "HR" in body

    def test_compose_default_subject_custom_body(self):
        with patch.object(main, "_get_role_title", return_value="Dev"):
            with patch.object(main, "_get_top_skills", return_value="Python"):
                subj, body = main._compose_message(
                    "HR", "Co", "swe",
                    custom_subject="",
                    custom_body="My body text",
                )
        assert "Dev" in subj
        assert body == "My body text"


# ---------------------------------------------------------------------------
# 28. Database model edge cases
# ---------------------------------------------------------------------------

class TestDatabaseEdgeCases:
    def test_record_default_experience_years_in_db(self):
        db = TestSession()
        r = Record(to_email="test@co.com")
        db.add(r)
        db.commit()
        db.refresh(r)
        assert r.experience_years == 4
        db.close()

    def test_record_stores_experience_years(self):
        db = TestSession()
        r = Record(to_email="test@co.com", experience_years=9)
        db.add(r)
        db.commit()
        db.refresh(r)
        assert r.experience_years == 9
        db.close()


# ---------------------------------------------------------------------------
# 29. Resume template helpers
# ---------------------------------------------------------------------------

class TestResumeTemplateHelpers:
    def test_tex_resume_items(self):
        from resume_templates import _tex_resume_items
        result = _tex_resume_items(["Built APIs", "Deployed services"])
        assert "\\resumeItem{Built APIs}" in result
        assert "\\resumeItem{Deployed services}" in result

    def test_tex_skill_items(self):
        from resume_templates import _tex_skill_items
        result = _tex_skill_items({"Languages": ["Python", "SQL"]})
        assert "Languages" in result
        assert "Python, SQL" in result

    def test_sanitize_all_replacements(self):
        from resume_templates import _sanitize
        assert _sanitize("—") == "--"
        assert _sanitize("–") == "-"
        assert _sanitize("‘") == "'"
        assert _sanitize("’") == "'"
        assert _sanitize("“") == '"'
        assert _sanitize("”") == '"'
        assert _sanitize("…") == "..."
        assert _sanitize("•") == "-"


# ---------------------------------------------------------------------------
# 30. Message preview edge cases
# ---------------------------------------------------------------------------

class TestMessagePreviewEdgeCases:
    def test_preview_with_experience_years(self, client):
        resp = client.post("/message-preview", json={
            "role_key": "",
            "role_title": "Engineer",
            "hr_name": "Test",
            "company_name": "Corp",
            "experience_years": 9,
        })
        assert resp.status_code == 200
        assert "9" in resp.json()["subject"]

    def test_preview_with_role_key_no_title(self, client):
        resp = client.post("/message-preview", json={
            "role_key": "software_engineer",
            "role_title": "",
            "hr_name": "",
            "company_name": "",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "subject" in data
        assert "body" in data

    def test_preview_no_role_key_no_title(self, client):
        resp = client.post("/message-preview", json={
            "role_key": "",
            "role_title": "",
            "hr_name": "Alice",
            "company_name": "BigCo",
        })
        assert resp.status_code == 200
        assert "Professional" in resp.json()["subject"]
        assert "Alice" in resp.json()["body"]
        assert "BigCo" in resp.json()["body"]


# ---------------------------------------------------------------------------
# 31. Send all edge cases
# ---------------------------------------------------------------------------

class TestSendAllEdgeCases:
    def test_send_all_with_mixed_experience_years(self, client):
        db = TestSession()
        for exp in [2, 5, 8]:
            r = Record(**_make_record(to_email=f"hr{exp}@company.com", experience_years=exp))
            db.add(r)
        db.commit()
        db.close()

        with patch.object(main, "validate_email_full",
                          return_value={"valid": True, "checks": [], "reason": "ok"}):
            with patch.object(main, "_get_resume_for_send", return_value=b"%PDF"):
                with _mock_compose():
                    with _mock_smtp():
                        with patch.object(main, "_get_role_title", return_value="Engineer"):
                            resp = client.post("/send-all")

        assert resp.status_code == 200
        assert resp.json()["sent"] == 3
