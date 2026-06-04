import argparse
import json
from pathlib import Path

from resume_templates import generate_all_resumes


def parse_args():
    parser = argparse.ArgumentParser(description="Generate all role-based ATS LaTeX resumes.")
    parser.add_argument("--output", default="../generated_resumes", help="Folder where .tex resumes will be written.")
    parser.add_argument("--name", default="", help="Candidate full name.")
    parser.add_argument("--email", default="", help="Candidate email.")
    parser.add_argument("--phone", default="", help="Candidate phone number.")
    parser.add_argument("--location", default="", help="Candidate location.")
    parser.add_argument("--linkedin", default="", help="LinkedIn URL without or with https://.")
    parser.add_argument("--github", default="", help="GitHub URL without or with https://.")
    parser.add_argument("--portfolio", default="", help="Portfolio URL without or with https://.")
    parser.add_argument("--education", default="", help="Education line, for example B.Tech CSE, ABC College.")
    parser.add_argument("--graduation-year", default="", help="Graduation year.")
    parser.add_argument("--details-json", default="", help="Optional JSON file with the same basic detail keys.")
    return parser.parse_args()


def main():
    args = parse_args()
    basics = {
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

    if args.details_json:
        details_path = Path(args.details_json)
        basics.update(json.loads(details_path.read_text(encoding="utf-8")))

    generated = generate_all_resumes(args.output, basics)
    print(f"Generated {len(generated)} resumes in {Path(args.output).resolve()}")
    for resume_path in generated:
        print(resume_path)


if __name__ == "__main__":
    main()
