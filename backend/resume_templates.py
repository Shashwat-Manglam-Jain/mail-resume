"""
resume_templates.py — Role-specific resume data and generators.

All role data lives in the Neon PostgreSQL database. This module exposes
two generators and lookup helpers:

    generate_pdf_resume(role_key, profile, db) -> bytes   (ATS-friendly PDF)
    make_latex_resume(template, basics)        -> str      (LaTeX source)

Profile dict (loaded from DB / .env by main.py):
    name, email, phone, location, linkedin, github, portfolio,
    education, graduation_year

Public helpers:
    list_templates(db)          -> summary list of all roles
    get_template(role_key, db)  -> full template dict or None
"""

from textwrap import dedent

from fpdf import FPDF


# ============================================================================
# ORM -> dict converter
# ============================================================================

def _role_to_dict(role) -> dict:
    """Convert a Role ORM object (with loaded relationships) to a template dict."""
    skills = {s.category: (s.skills or []) for s in role.skills}
    clients = []
    for e in role.experiences:
        clients.append({
            "client_name": getattr(e, "client_name", "") or "",
            "client_location": getattr(e, "client_location", "") or "",
            "min_years": getattr(e, "min_years", 1) or 1,
            "position_index": e.position_index,
            "bullets": e.bullets or [],
        })
    clients.sort(key=lambda c: c["position_index"])
    return {
        "key": role.key,
        "title": role.title,
        "previous_title": role.previous_title or "",
        "summary": role.summary or "",
        "skills": skills,
        "clients": clients,
        "focus": [f.area for f in role.focus_areas],
        "achievements": [a.text for a in role.achievements],
        "coursework": role.coursework or "",
    }


# ============================================================================
# Public API helpers
# ============================================================================

def list_templates(db):
    """Return a summary list of all roles (key, title, summary, skills, focus).

    Reads from the Neon database.  *db* is required.
    """
    from neon_models import Role
    roles = db.query(Role).filter(Role.is_active == True).order_by(Role.sort_order).all()
    results = []
    for r in roles:
        d = _role_to_dict(r)
        results.append({
            "key": d["key"],
            "title": d["title"],
            "summary": d["summary"],
            "skills": [s for vals in d["skills"].values() for s in vals],
            "focus": d["focus"],
        })
    return results


def get_template(key: str, db):
    """Return the full template dict for a role key, or None.

    Reads from the Neon database.  *db* is required.
    """
    from neon_models import Role
    role = db.query(Role).filter(Role.key == key, Role.is_active == True).first()
    if role:
        return _role_to_dict(role)
    return None


# ============================================================================
# PDF Resume Generator (ATS-friendly, single page)
# ============================================================================

def _sanitize(text: str) -> str:
    """Replace non-Latin-1 characters so built-in PDF fonts can render them."""
    return (
        text
        .replace("—", "--")   # em dash
        .replace("–", "-")    # en dash
        .replace("‘", "'")    # left single quote
        .replace("’", "'")    # right single quote
        .replace("“", '"')    # left double quote
        .replace("”", '"')    # right double quote
        .replace("…", "...")   # ellipsis
        .replace("•", "-")    # bullet
    )


class _ResumePDF(FPDF):
    """Custom FPDF subclass for clean, ATS-optimized resume layout."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_margins(left=12, top=8, right=12)
        self.set_auto_page_break(auto=True, margin=8)

    def cell(self, *args, text="", **kwargs):
        """Override cell() to sanitize Unicode before rendering."""
        return super().cell(*args, text=_sanitize(str(text)), **kwargs)

    def multi_cell(self, *args, text="", **kwargs):
        """Override multi_cell() to sanitize Unicode before rendering."""
        return super().multi_cell(*args, text=_sanitize(str(text)), **kwargs)

    def section_header(self, title: str):
        """Draw a bold section title with a thin horizontal rule below."""
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(30, 30, 30)
        self.cell(w=0, h=6, text=title.upper(), new_x="LMARGIN", new_y="NEXT")
        y = self.get_y()
        self.set_draw_color(80, 80, 80)
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(1.5)

    def bullet(self, text: str, indent: float = 4):
        """Render a bullet point with hanging indent."""
        self.set_font("Helvetica", "", 8.5)
        self.set_text_color(50, 50, 50)
        x = self.get_x() + indent
        bullet_w = self.w - self.r_margin - x
        self.set_x(x)
        self.cell(w=4, h=4, text="-")
        self.multi_cell(w=bullet_w - 4, h=4, text=text)
        self.ln(0.3)


def generate_pdf_resume(role_key: str, profile: dict, db, experience_years: int = 4) -> bytes:
    """
    Generate a single-page ATS-friendly PDF resume with multi-client CubexO format.

    Args:
        role_key:         template key (e.g. 'data_scientist')
        profile:          dict with name, email, phone, location, linkedin, etc.
        db:               Neon DB session (required)
        experience_years: 1-10, controls how many clients appear

    Returns:
        PDF file content as bytes.
    """
    template = get_template(role_key, db=db)
    if not template:
        raise ValueError(f"Unknown role key: {role_key}")

    exp_years = max(1, min(10, experience_years))

    name = (profile.get("name") or "YOUR NAME").upper()
    email = profile.get("email") or "email@example.com"
    phone = profile.get("phone") or "+91 00000 00000"
    location = profile.get("location") or "City, India"
    linkedin = (profile.get("linkedin") or "").replace("https://", "").rstrip("/")
    github = (profile.get("github") or "").replace("https://", "").rstrip("/")
    portfolio = (profile.get("portfolio") or "").replace("https://", "").rstrip("/")
    education = profile.get("education") or "B.Tech / B.Sc, Your College"
    grad_year = profile.get("graduation_year") or "2026"

    c1_name = profile.get("company_1_name") or "CubexO Software Solutions"
    c1_loc = profile.get("company_1_location") or "Indore, India"

    all_clients = template.get("clients", [])
    visible = [c for c in all_clients if c["min_years"] <= exp_years]
    visible.sort(key=lambda c: c["position_index"])
    dates = _compute_client_dates(visible, exp_years)

    summary = template["summary"].replace("4+", str(exp_years))

    pdf = _ResumePDF()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(w=0, h=9, text=name, align="C", new_x="LMARGIN", new_y="NEXT")

    contact_parts = [p for p in [email, phone, location] if p]
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(
        w=0, h=4.5,
        text="  |  ".join(contact_parts),
        align="C", new_x="LMARGIN", new_y="NEXT",
    )

    link_parts = [p for p in [linkedin, github, portfolio] if p]
    if link_parts:
        pdf.cell(
            w=0, h=4.5,
            text="  |  ".join(link_parts),
            align="C", new_x="LMARGIN", new_y="NEXT",
        )
    pdf.ln(2)

    pdf.section_header("Professional Summary")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(w=0, h=4, text=summary)
    pdf.ln(1.5)

    pdf.section_header("Technical Skills")
    for category, skill_list in template["skills"].items():
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(40, 40, 40)
        cat_w = 38
        pdf.cell(w=cat_w, h=4.5, text=f"{category}:")
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(60, 60, 60)
        skills_text = ", ".join(skill_list)
        pdf.multi_cell(w=0, h=4.5, text=skills_text)
        pdf.ln(0.2)
    pdf.ln(1)

    pdf.section_header("Professional Experience")

    cubexo_dur = dates[-1]["start"] + " -- Present" if dates else "Present"
    cubexo_line = ", ".join(p for p in [c1_name, c1_loc] if p)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(w=0, h=5, text=template["title"])
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(w=0, h=5, text=cubexo_dur,
             align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(w=0, h=4, text=cubexo_line,
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)

    for i, client in enumerate(visible):
        dur = dates[i]["dur"] if i < len(dates) else ""
        label = f"Client: {client['client_name']} ({client['client_location']})"
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(w=0, h=5, text=label)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(w=0, h=5, text=dur,
                 align="R", new_x="LMARGIN", new_y="NEXT")
        for b in client.get("bullets", []):
            pdf.bullet(b)
        pdf.ln(0.5)
    pdf.ln(0.5)

    pdf.section_header("Education")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(w=0, h=5, text=education)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(w=0, h=5, text=grad_year,
             align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(80, 80, 80)
    cw = template.get("coursework",
                      "Data Structures, Algorithms, Databases, "
                      "Statistics, Software Engineering")
    pdf.cell(
        w=0, h=4,
        text=f"Relevant coursework: {cw}",
        new_x="LMARGIN", new_y="NEXT",
    )
    pdf.ln(1)

    pdf.section_header("Achievements")
    for ach in template["achievements"]:
        pdf.bullet(ach, indent=2)

    return bytes(pdf.output())


# ============================================================================
# LaTeX Resume Generator (ATS-friendly format)
# ============================================================================

def _latex_escape(value: str) -> str:
    """Escape special LaTeX characters in a string."""
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{",
        "}": r"\}", "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(c, c) for c in str(value))


def _normalize_link(value: str, fallback: str) -> str:
    """Strip protocol prefix from a URL for display."""
    value = (value or fallback).strip()
    return value.replace("https://", "").replace("http://", "").rstrip("/")


def _tex_resume_items(items):
    """Render bullets using \\resumeItem macro."""
    return "\n".join(
        f"          \\resumeItem{{{_latex_escape(item)}}}"
        for item in items
    )


def _tex_skill_items(skills):
    """Render skill categories using \\resumeItem macro."""
    return "\n".join(
        f"  \\resumeItem{{\\textbf{{{_latex_escape(cat)}}}: {_latex_escape(', '.join(vals))}}}"
        for cat, vals in skills.items()
    )


def _compute_client_dates(clients, experience_years):
    """Compute realistic date ranges for each client working backwards from now."""
    from datetime import date, timedelta
    today = date.today()
    start = today - timedelta(days=experience_years * 365)
    total_months = experience_years * 12
    n = len(clients)
    if n == 0:
        return []

    months_per = max(total_months // n, 6)
    results = []
    cursor = start
    for i, c in enumerate(reversed(clients)):
        is_latest = (i == n - 1)
        if is_latest:
            end_str = "Present"
        else:
            end_date = cursor + timedelta(days=months_per * 30)
            end_str = end_date.strftime("%b %Y")
        start_str = cursor.strftime("%b %Y")
        results.append({"start": start_str, "end": end_str, "dur": f"{start_str} -- {end_str}"})
        cursor = cursor + timedelta(days=months_per * 30 + 15)
    results.reverse()
    return results


def make_latex_resume(template: dict, basics: dict, experience_years: int = 4) -> str:
    """Generate an ATS-friendly LaTeX resume with multi-client CubexO experience."""
    name = (basics.get("name") or "YOUR NAME").upper()
    email = basics.get("email") or "email@example.com"
    phone = basics.get("phone") or "+91 00000 00000"
    linkedin = _normalize_link(basics.get("linkedin"), "linkedin.com/in/profile")
    github = _normalize_link(basics.get("github"), "github.com/username")
    portfolio = _normalize_link(basics.get("portfolio"), "yourportfolio.com")

    edu_text = basics.get("education") or "B.Tech in Computer Science & Engineering"
    edu_parts = edu_text.split(",", 1)
    edu_degree = edu_parts[0].strip()
    edu_institution = edu_parts[1].strip() if len(edu_parts) > 1 else "University"
    edu_location = basics.get("location") or "India"
    grad_year = basics.get("graduation_year") or "2022 -- 2026"

    title = template["title"]
    exp_years = max(1, min(10, experience_years))

    summary = _latex_escape(template["summary"]).replace(
        _latex_escape("4+"), str(exp_years)
    ).replace("4+", str(exp_years))

    c1_name = basics.get("company_1_name") or "CubexO Software Solutions"
    c1_loc = basics.get("company_1_location") or "Indore, India"
    c1_role = basics.get("company_1_role") or title

    # Filter clients by experience
    all_clients = template.get("clients", [])
    visible = [c for c in all_clients if c["min_years"] <= exp_years]
    visible.sort(key=lambda c: c["position_index"])

    dates = _compute_client_dates(visible, exp_years)
    if dates:
        cubexo_dur = dates[-1]["start"] + " -- Present"
    else:
        cubexo_dur = basics.get("company_1_duration") or "Dec 2025 -- Present"

    # Build client sub-blocks inside CubexO
    client_blocks = []
    for i, client in enumerate(visible):
        cname = client["client_name"]
        cloc = client["client_location"]
        dur = dates[i]["dur"] if i < len(dates) else ""
        label = f"Client: {cname} ({cloc})"
        bullets = _tex_resume_items(client["bullets"])
        block = (
            "      \\vspace{2pt}\n"
            "      \\textbf{" + _latex_escape(label) + "} \\hfill \\textit{" + _latex_escape(dur) + "}\n"
            "      \\resumeItemListStart\n"
            + bullets + "\n"
            "      \\resumeItemListEnd"
        )
        client_blocks.append(block)

    exp_section = (
        "  \\resumeSubheading\n"
        "      {" + _latex_escape(c1_role) + "}{" + _latex_escape(cubexo_dur) + "}\n"
        "      {" + _latex_escape(c1_name) + "}{" + _latex_escape(c1_loc) + "}\n"
        + "\n".join(client_blocks)
    )

    skills_section = _tex_skill_items(template.get("skills", {}))

    esc_name = _latex_escape(name)
    esc_email = _latex_escape(email)
    esc_phone = _latex_escape(phone)
    esc_linkedin_display = _latex_escape(linkedin)
    esc_github_display = _latex_escape(github)
    esc_portfolio_display = _latex_escape(portfolio)
    esc_edu_degree = _latex_escape(edu_degree)
    esc_edu_institution = _latex_escape(edu_institution)
    esc_edu_location = _latex_escape(edu_location)
    esc_grad_year = _latex_escape(grad_year)

    return f"""\\documentclass[letterpaper,11pt]{{article}}

\\usepackage{{latexsym}}
\\usepackage[T1]{{fontenc}}
\\usepackage[left=0.8in, right=0.8in, top=0.8in, bottom=0.8in]{{geometry}}
\\usepackage{{titlesec}}
\\usepackage{{marvosym}}
\\usepackage[usenames,dvipsnames]{{color}}
\\usepackage{{verbatim}}
\\usepackage{{enumitem}}
\\usepackage[hidelinks]{{hyperref}}
\\usepackage{{fancyhdr}}
\\usepackage[english]{{babel}}
\\input{{glyphtounicode}}

\\usepackage[sfdefault]{{roboto}}

\\pagestyle{{fancy}}
\\fancyhf{{}}
\\fancyfoot{{}}
\\renewcommand{{\\headrulewidth}}{{0pt}}
\\renewcommand{{\\footrulewidth}}{{0pt}}

\\urlstyle{{same}}
\\raggedbottom
\\raggedright

\\titleformat{{\\section}}{{\\Large\\bfseries\\scshape\\raggedright}}{{}}{{0em}}{{}}[\\titlerule]
\\titlespacing*{{\\section}}{{0pt}}{{12pt}}{{8pt}}

\\pdfgentounicode=1

\\newcommand{{\\resumeItem}}[1]{{\\item\\small{{#1}}}}

\\newcommand{{\\resumeSubheading}}[4]{{
  \\item
    \\textbf{{#1}} \\hfill #2 \\\\
    \\textit{{#3}} \\hfill \\textit{{#4}} \\vspace{{4pt}}
}}

\\newcommand{{\\resumeSubHeadingList}}{{\\begin{{itemize}}[leftmargin=0in, label={{}}]}}
\\newcommand{{\\resumeSubHeadingListEnd}}{{\\end{{itemize}}}}

\\newcommand{{\\resumeItemListStart}}{{\\begin{{itemize}}[leftmargin=0.2in, itemsep=4pt]}}
\\newcommand{{\\resumeItemListEnd}}{{\\end{{itemize}}\\vspace{{4pt}}}}

\\begin{{document}}

\\begin{{center}}
  \\textbf{{\\Huge {esc_name}}} \\\\ \\vspace{{8pt}}
  \\small {esc_phone} \\textbar{{}} \\href{{mailto:{esc_email}}}{{{esc_email}}} \\\\ \\vspace{{4pt}}
  \\href{{https://{portfolio}}}{{{esc_portfolio_display}}} \\textbar{{}}
  \\href{{https://{linkedin}}}{{{esc_linkedin_display}}} \\textbar{{}}
  \\href{{https://{github}}}{{{esc_github_display}}}
\\end{{center}}

\\vspace{{10pt}}

\\section*{{Professional Summary}}
\\vspace{{4pt}}
{summary}

\\section{{Technical Skills}}
\\resumeSubHeadingList
{skills_section}
\\resumeSubHeadingListEnd

\\section{{Experience}}
\\resumeSubHeadingList
{exp_section}
\\resumeSubHeadingListEnd

\\section{{Education}}
\\resumeSubHeadingList
  \\resumeSubheading
      {{{esc_edu_institution}}}{{{esc_edu_location}}}
      {{{esc_edu_degree}}}{{{esc_grad_year}}}
\\resumeSubHeadingListEnd

\\end{{document}}"""
