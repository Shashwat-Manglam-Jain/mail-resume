"""
seed_roles.py — Seed the Neon PostgreSQL database with Python-related roles and profile.

Reads 10 Python roles from the hardcoded resume_templates.py and inserts them
into the new dynamic resume tables. Also seeds the profile from .env.

Idempotent: skips roles/profile that already exist.

Usage:
    python seed_roles.py
"""

import os

from dotenv import load_dotenv

load_dotenv()

from database import NeonSessionLocal
from neon_models import (
    Profile, Role, RoleSkill,
    RoleExperience, RoleAchievement, RoleFocusArea,
)
from resume_templates import get_template

PYTHON_ROLE_KEYS = [
    "python_developer",
    "ai_ml_engineer",
    "data_engineer",
    "data_scientist",
    "data_analyst_bi",
    "business_analyst",
    "software_engineer",
    "full_stack_developer",
    "backend_engineer",
    "cloud_devops_engineer",
    "software_tester_qa",
    "seo_digital_marketing",
]


def seed_profile(db):
    existing = db.query(Profile).first()
    if existing:
        print("Profile already exists — skipping")
        return

    profile = Profile(
        name=os.getenv("YOUR_NAME", ""),
        email=os.getenv("YOUR_EMAIL", ""),
        phone=os.getenv("YOUR_PHONE", ""),
        location=os.getenv("YOUR_LOCATION", ""),
        linkedin=os.getenv("YOUR_LINKEDIN", ""),
        github=os.getenv("YOUR_GITHUB", ""),
        portfolio=os.getenv("YOUR_PORTFOLIO", ""),
        education=os.getenv("YOUR_EDUCATION", ""),
        graduation_year=os.getenv("YOUR_GRADUATION_YEAR", ""),
        experience_years=os.getenv("YOUR_EXPERIENCE_YEARS", ""),
        company_1_name=os.getenv("COMPANY_1_NAME", ""),
        company_1_role=os.getenv("COMPANY_1_ROLE", ""),
        company_1_location=os.getenv("COMPANY_1_LOCATION", ""),
        company_1_duration=os.getenv("COMPANY_1_DURATION", ""),
        company_2_name=os.getenv("COMPANY_2_NAME", ""),
        company_2_role=os.getenv("COMPANY_2_ROLE", ""),
        company_2_location=os.getenv("COMPANY_2_LOCATION", ""),
        company_2_duration=os.getenv("COMPANY_2_DURATION", ""),
    )
    db.add(profile)
    db.commit()
    print("Profile seeded from .env")


def seed_role(db, role_key, sort_order):
    existing = db.query(Role).filter(Role.key == role_key).first()
    if existing:
        print(f"  {role_key} — already exists, skipping")
        return

    tpl = get_template(role_key)
    if not tpl:
        print(f"  {role_key} — template not found in resume_templates.py, skipping")
        return

    role = Role(
        key=tpl["key"],
        title=tpl["title"],
        previous_title=tpl.get("previous_title", ""),
        summary=tpl.get("summary", ""),
        coursework=tpl.get("coursework", ""),
        sort_order=sort_order,
    )
    db.add(role)
    db.flush()

    for i, (category, skill_list) in enumerate(tpl.get("skills", {}).items()):
        db.add(RoleSkill(
            role_id=role.id,
            category=category,
            skills=skill_list,
            sort_order=i,
        ))

    for i, exp in enumerate(tpl.get("experience", [])):
        db.add(RoleExperience(
            role_id=role.id,
            position_index=i,
            bullets=exp.get("bullets", []),
        ))

    for i, ach in enumerate(tpl.get("achievements", [])):
        db.add(RoleAchievement(
            role_id=role.id,
            text=ach,
            sort_order=i,
        ))

    for i, area in enumerate(tpl.get("focus", [])):
        db.add(RoleFocusArea(
            role_id=role.id,
            area=area,
            sort_order=i,
        ))

    db.commit()
    skills_count = len(tpl.get("skills", {}))
    exp_count = len(tpl.get("experience", []))
    print(f"  {role_key} — seeded ({skills_count} skill categories, {exp_count} experience entries)")


def main():
    if not NeonSessionLocal:
        print("ERROR: NEON_DATABASE_URL not set. Cannot seed.")
        return

    db = NeonSessionLocal()
    try:
        print("=== Seeding Profile ===")
        seed_profile(db)

        print(f"\n=== Seeding {len(PYTHON_ROLE_KEYS)} Python Roles ===")
        for i, key in enumerate(PYTHON_ROLE_KEYS):
            seed_role(db, key, sort_order=i)

        total = db.query(Role).count()
        print(f"\nDone. {total} roles in database.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
