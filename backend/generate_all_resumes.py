"""
generate_all_resumes.py — CLI tool to batch-generate all role resumes.

Usage:
    python generate_all_resumes.py --output ../generated_resumes

Reads roles from the Neon PostgreSQL database and personal details from
the DB profile (with .env fallback). Override with --name, --email, etc.
Generates one LaTeX .tex file and one PDF per active role.
"""

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv
import os

from resume_templates import (
    list_templates,
    get_template,
    generate_pdf_resume,
    make_latex_resume,
)


def _load_profile() -> dict:
    """Load personal details from DB first, then .env fallback."""
    load_dotenv()
    env_profile = {
        "name": os.getenv("YOUR_NAME", ""),
        "email": os.getenv("YOUR_EMAIL", ""),
        "phone": os.getenv("YOUR_PHONE", ""),
        "location": os.getenv("YOUR_LOCATION", ""),
        "linkedin": os.getenv("YOUR_LINKEDIN", ""),
        "github": os.getenv("YOUR_GITHUB", ""),
        "portfolio": os.getenv("YOUR_PORTFOLIO", ""),
        "education": os.getenv("YOUR_EDUCATION", ""),
        "graduation_year": os.getenv("YOUR_GRADUATION_YEAR", ""),
        "company_1_name": os.getenv("COMPANY_1_NAME", ""),
        "company_1_role": os.getenv("COMPANY_1_ROLE", ""),
        "company_1_location": os.getenv("COMPANY_1_LOCATION", ""),
        "company_1_duration": os.getenv("COMPANY_1_DURATION", ""),
        "company_2_name": os.getenv("COMPANY_2_NAME", ""),
        "company_2_role": os.getenv("COMPANY_2_ROLE", ""),
        "company_2_location": os.getenv("COMPANY_2_LOCATION", ""),
        "company_2_duration": os.getenv("COMPANY_2_DURATION", ""),
    }
    from database import NeonSessionLocal
    from neon_models import Profile
    if NeonSessionLocal:
        try:
            db = NeonSessionLocal()
            row = db.query(Profile).first()
            db.close()
            if row:
                for field in env_profile:
                    val = getattr(row, field, "")
                    if val:
                        env_profile[field] = val
        except Exception:
            pass
    return env_profile


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate all role-based ATS resumes (PDF + LaTeX).",
    )
    parser.add_argument(
        "--output", default="../generated_resumes",
        help="Output folder for generated files.",
    )
    parser.add_argument("--name", default="", help="Override name.")
    parser.add_argument("--email", default="", help="Override email.")
    parser.add_argument("--phone", default="", help="Override phone.")
    parser.add_argument("--location", default="", help="Override location.")
    parser.add_argument("--linkedin", default="", help="Override LinkedIn URL.")
    parser.add_argument("--github", default="", help="Override GitHub URL.")
    parser.add_argument("--portfolio", default="", help="Override portfolio URL.")
    parser.add_argument("--education", default="", help="Override education.")
    parser.add_argument("--graduation-year", default="", help="Override year.")
    parser.add_argument(
        "--details-json", default="",
        help="JSON file with personal details (overrides DB/env).",
    )
    parser.add_argument(
        "--experience-years", type=int, default=4,
        help="Experience years (1-10) for resume generation.",
    )
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()

    profile = _load_profile()
    cli_overrides = {
        "name": args.name,
        "email": args.email,
        "phone": args.phone,
        "location": args.location,
        "linkedin": args.linkedin,
        "github": args.github,
        "portfolio": args.portfolio,
        "education": args.education,
        "graduation_year": args.graduation_year,
    }
    for key, value in cli_overrides.items():
        if value:
            profile[key] = value

    if args.details_json:
        details_path = Path(args.details_json)
        profile.update(json.loads(details_path.read_text(encoding="utf-8")))

    from database import NeonSessionLocal
    db = NeonSessionLocal() if NeonSessionLocal else None

    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    roles = list_templates(db=db)
    generated = []
    for role_summary in roles:
        key = role_summary["key"]
        template = get_template(key, db=db)
        if not template:
            continue

        exp_years = args.experience_years

        tex_path = output_path / f"{key}_resume.tex"
        tex_path.write_text(make_latex_resume(template, profile, experience_years=exp_years), encoding="utf-8")
        generated.append(tex_path)

        pdf_path = output_path / f"{key}_resume.pdf"
        pdf_bytes = generate_pdf_resume(key, profile, db=db, experience_years=exp_years)
        pdf_path.write_bytes(pdf_bytes)
        generated.append(pdf_path)

    if db:
        db.close()

    print(f"Generated {len(generated)} files in {output_path.resolve()}")
    for path in generated:
        print(f"  {path}")


if __name__ == "__main__":
    main()
