"""
generate_all_resumes.py — CLI tool to batch-generate all role resumes.

Usage:
    python generate_all_resumes.py --output ../generated_resumes

Reads personal details from .env (or override with --name, --email, etc.).
Generates one LaTeX .tex file and one PDF per role template.
"""

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv
import os

from resume_templates import (
    ROLE_TEMPLATES,
    generate_pdf_resume,
    make_latex_resume,
)


def _load_profile_from_env() -> dict:
    """Load personal details from .env file."""
    load_dotenv()
    return {
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


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate all role-based ATS resumes (PDF + LaTeX).",
    )
    parser.add_argument(
        "--output", default="../generated_resumes",
        help="Output folder for generated files.",
    )
    parser.add_argument("--name", default="", help="Override name from .env.")
    parser.add_argument("--email", default="", help="Override email from .env.")
    parser.add_argument("--phone", default="", help="Override phone from .env.")
    parser.add_argument("--location", default="", help="Override location.")
    parser.add_argument("--linkedin", default="", help="Override LinkedIn URL.")
    parser.add_argument("--github", default="", help="Override GitHub URL.")
    parser.add_argument("--portfolio", default="", help="Override portfolio URL.")
    parser.add_argument("--education", default="", help="Override education.")
    parser.add_argument("--graduation-year", default="", help="Override year.")
    parser.add_argument(
        "--details-json", default="",
        help="JSON file with personal details (overrides .env).",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    # Start with .env profile, then overlay CLI args
    profile = _load_profile_from_env()
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

    # Overlay JSON file if provided
    if args.details_json:
        details_path = Path(args.details_json)
        profile.update(json.loads(details_path.read_text(encoding="utf-8")))

    # Generate resumes
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)

    generated = []
    for template in ROLE_TEMPLATES:
        key = template["key"]

        # LaTeX
        tex_path = output_path / f"{key}_resume.tex"
        tex_path.write_text(
            make_latex_resume(template, profile), encoding="utf-8",
        )
        generated.append(tex_path)

        # PDF
        pdf_path = output_path / f"{key}_resume.pdf"
        pdf_bytes = generate_pdf_resume(key, profile)
        pdf_path.write_bytes(pdf_bytes)
        generated.append(pdf_path)

    print(f"Generated {len(generated)} files in {output_path.resolve()}")
    for path in generated:
        print(f"  {path}")


if __name__ == "__main__":
    main()
