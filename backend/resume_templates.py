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


ROLE_PROJECTS = {
    "python_developer": [
        {
            "name": "AI Resume Builder & Email Automation Tool",
            "tech": "Python, FastAPI, React, Next.js, PostgreSQL, SMTP",
            "bullets": [
                "Full-stack app that generates role-specific ATS-optimized resumes as PDF, composes personalized cover emails with template variations, and sends them directly via SMTP with resume attachment.",
                "Built React frontend with dynamic form, role-based template auto-loading, and resume preview. FastAPI backend handles PDF generation, email composition, and direct SMTP delivery.",
            ],
        },
        {
            "name": "Real-Time E-Commerce Analytics Dashboard",
            "tech": "PySpark, Snowflake, Apache Airflow, React, D3.js",
            "bullets": [
                "ETL pipeline processing 500K+ daily sales records from multiple marketplaces, transforming raw data into analytics-ready tables in Snowflake with automated quality checks.",
                "Interactive React dashboard with D3.js visualizations showing revenue trends, conversion funnels, and inventory health metrics used by the operations team daily.",
            ],
        },
        {
            "name": "Infrastructure Automation Toolkit",
            "tech": "Ansible, Terraform, Docker, AWS, Python",
            "bullets": [
                "Automated provisioning and configuration of multi-environment AWS infrastructure (VPC, EC2, RDS, S3) with Terraform modules and Ansible playbooks.",
                "Reduced deployment time from 2 days to 30 minutes with reusable IaC templates and automated compliance validation.",
            ],
        },
        {
            "name": "Distributed Task Queue System",
            "tech": "FastAPI, Celery, Redis, PostgreSQL, WebSocket",
            "bullets": [
                "Priority-based distributed task execution system with retry logic, dead-letter queues, and real-time progress tracking via WebSocket connections.",
                "Handles 10K+ tasks per hour with configurable concurrency, rate limiting, and automatic failure recovery.",
            ],
        },
    ],
    "software_engineer": [
        {
            "name": "AI Resume Builder & Email Automation Tool",
            "tech": "Python, FastAPI, React, PostgreSQL, SMTP",
            "bullets": [
                "Full-stack application that generates role-specific resumes as PDF and sends personalized job application emails directly via SMTP with resume attachment.",
                "FastAPI backend with SQLAlchemy ORM, template engine for email/resume generation, and React frontend with dynamic forms.",
            ],
        },
        {
            "name": "REST API Scaffolding CLI",
            "tech": "Python, Click, Jinja2, Docker",
            "bullets": [
                "CLI tool that generates production-ready FastAPI project scaffolds with database models, CRUD endpoints, test suites, and Docker configuration.",
                "Supports multiple database backends (PostgreSQL, SQLite, MongoDB) with automatic migration setup and OpenAPI documentation.",
            ],
        },
        {
            "name": "Automated Deployment Pipeline",
            "tech": "GitHub Actions, Docker, AWS ECS, Terraform",
            "bullets": [
                "End-to-end CI/CD pipeline with automated testing, container builds, security scanning, and zero-downtime blue-green deployments to AWS ECS.",
                "Reduced release cycle from 2 days to 30 minutes with automated rollback on health check failures.",
            ],
        },
    ],
    "ai_ml_engineer": [
        {
            "name": "RAG-Powered Document Q&A System",
            "tech": "LangChain, FAISS, FastAPI, React, OpenAI",
            "bullets": [
                "Retrieval-augmented generation system that indexes 10K+ documents and answers natural language queries with source citations and confidence scores.",
                "Built chunking pipeline with semantic splitting, vector embeddings via OpenAI, and hybrid search combining dense retrieval with BM25.",
            ],
        },
        {
            "name": "Real-Time Sentiment Analysis API",
            "tech": "HuggingFace Transformers, FastAPI, Docker, Redis",
            "bullets": [
                "Production sentiment classification service fine-tuned on domain-specific data achieving 94% accuracy with batch and streaming inference modes.",
                "Handles 5K+ requests per minute with Redis caching, model versioning, and A/B testing support for model comparison.",
            ],
        },
        {
            "name": "Automated ML Pipeline Framework",
            "tech": "MLflow, PyTorch, Airflow, AWS SageMaker",
            "bullets": [
                "End-to-end ML pipeline for training, evaluating, and deploying models with automated hyperparameter tuning and experiment tracking.",
                "Supports scheduled retraining, data drift detection, and model performance monitoring with automated rollback.",
            ],
        },
    ],
    "data_engineer": [
        {
            "name": "Streaming Data Pipeline Platform",
            "tech": "Kafka, PySpark, Delta Lake, Airflow, AWS",
            "bullets": [
                "Real-time data ingestion and transformation pipeline processing 1M+ events daily with exactly-once semantics and schema evolution support.",
                "Built monitoring dashboards tracking pipeline health, data freshness, and processing lag with automated alerting.",
            ],
        },
        {
            "name": "Data Quality Framework",
            "tech": "Great Expectations, Python, PostgreSQL, Slack API",
            "bullets": [
                "Automated data validation framework with schema enforcement, statistical anomaly detection, and Slack alerting for pipeline failures.",
                "Reduced data quality incidents by 80% with pre-commit validation hooks and automated reconciliation jobs.",
            ],
        },
        {
            "name": "ETL Orchestration Platform",
            "tech": "Airflow, dbt, Snowflake, Docker, Terraform",
            "bullets": [
                "Modular ETL framework with dependency management, incremental loads, and automated data quality checks across 50+ data sources.",
                "Self-service data pipeline provisioning for analysts with templated DAGs and configuration-driven transformations.",
            ],
        },
    ],
    "data_scientist": [
        {
            "name": "Predictive Customer Churn Platform",
            "tech": "XGBoost, Scikit-learn, FastAPI, React, MLflow",
            "bullets": [
                "End-to-end churn prediction system with feature engineering, model training, and real-time scoring API serving predictions for 50K+ users.",
                "Built interactive dashboard showing risk segments, feature importance, and intervention recommendations for the customer success team.",
            ],
        },
        {
            "name": "Time Series Forecasting Service",
            "tech": "Prophet, LightGBM, FastAPI, PostgreSQL, Plotly",
            "bullets": [
                "Multi-variate time series forecasting API supporting demand forecasting, revenue prediction, and anomaly detection with configurable horizons.",
                "Achieved 8% MAPE on 12-month revenue forecasts with automated model selection and ensemble methods.",
            ],
        },
        {
            "name": "A/B Testing & Experimentation Framework",
            "tech": "Python, Bayesian Statistics, PostgreSQL, React",
            "bullets": [
                "Statistical experimentation platform with Bayesian A/B testing, sequential analysis, and early stopping for product experiments.",
                "Self-service UI for designing experiments, monitoring results, and generating statistical reports with automated significance detection.",
            ],
        },
    ],
    "data_analyst_bi": [
        {
            "name": "Automated KPI Reporting Platform",
            "tech": "Python, Power BI, PostgreSQL, Airflow",
            "bullets": [
                "Automated reporting system that pulls data from 8+ sources, computes business KPIs, and publishes Power BI dashboards on schedule.",
                "Replaced 70% of manual reporting effort with Python automation scripts and scheduled data refresh pipelines.",
            ],
        },
        {
            "name": "Customer Cohort Analysis Tool",
            "tech": "SQL, Python, Tableau, Snowflake",
            "bullets": [
                "Self-service cohort analysis platform with retention curves, LTV estimation, and segmentation by acquisition channel and behavior.",
                "Built SQL-based attribution models tracking revenue per cohort and feature-level usage-to-revenue correlations.",
            ],
        },
        {
            "name": "Revenue Attribution Dashboard",
            "tech": "GA4, Python, BigQuery, Looker",
            "bullets": [
                "Multi-touch attribution model connecting marketing spend across channels to actual revenue conversions using data-driven attribution.",
                "Automated daily data pulls from GA4, ad platforms, and CRM into BigQuery for unified cross-channel performance analysis.",
            ],
        },
    ],
    "business_analyst": [
        {
            "name": "Requirements Management System",
            "tech": "Django, React, PostgreSQL, Jira API",
            "bullets": [
                "Web-based platform for managing BRDs, user stories, and acceptance criteria with traceability to Jira tickets and test cases.",
                "Automated requirements-to-test coverage reporting that reduced development rework by 40%.",
            ],
        },
        {
            "name": "Process Mapping & Optimization Tool",
            "tech": "Python, React, D3.js, PostgreSQL",
            "bullets": [
                "Interactive process mapping application with drag-and-drop workflow design, bottleneck identification, and optimization recommendations.",
                "Used for 15+ process improvement projects, identifying average 30% efficiency gains in mapped workflows.",
            ],
        },
        {
            "name": "Stakeholder Communication Dashboard",
            "tech": "Power BI, Python, Confluence API, Jira API",
            "bullets": [
                "Automated project status dashboard pulling sprint data from Jira, requirements status from Confluence, and KPIs from databases.",
                "Replaced weekly manual status reports with real-time visibility for 20+ stakeholders across 5 project streams.",
            ],
        },
    ],
    "full_stack_developer": [
        {
            "name": "AI Resume Builder & Email Automation Tool",
            "tech": "FastAPI, React, Next.js, PostgreSQL, SMTP",
            "bullets": [
                "Full-stack app generating role-specific ATS-optimized resumes and sending personalized job application emails with resume attachments.",
                "React frontend with dynamic forms, real-time preview, and role-based template switching. FastAPI backend with PDF generation and SMTP integration.",
            ],
        },
        {
            "name": "Real-Time Collaboration Platform",
            "tech": "Django Channels, React, WebSocket, Redis, PostgreSQL",
            "bullets": [
                "Multi-user collaborative workspace with real-time document editing, chat, and task management using WebSocket connections.",
                "Supports 500+ concurrent users with Redis pub/sub for message broadcasting and PostgreSQL for persistence.",
            ],
        },
        {
            "name": "E-Commerce Marketplace",
            "tech": "Django, React, Stripe, AWS S3, PostgreSQL",
            "bullets": [
                "Multi-vendor marketplace with product listings, shopping cart, Stripe payment integration, and vendor management dashboard.",
                "Built responsive React frontend with Tailwind CSS and Django REST backend handling 10K+ products and 1K+ daily orders.",
            ],
        },
    ],
    "backend_engineer": [
        {
            "name": "API Gateway & Service Mesh",
            "tech": "FastAPI, Redis, PostgreSQL, Docker, Nginx",
            "bullets": [
                "Centralized API gateway handling JWT authentication, rate limiting, circuit breakers, and request routing for 15+ microservices.",
                "Processes 50K+ requests per minute with sub-10ms routing overhead, Prometheus metrics, and OpenAPI documentation aggregation.",
            ],
        },
        {
            "name": "Event-Driven Notification Service",
            "tech": "FastAPI, RabbitMQ, Celery, Redis, PostgreSQL",
            "bullets": [
                "Multi-channel notification system supporting email, SMS, push, and webhook delivery with template management and delivery tracking.",
                "Handles 100K+ notifications daily with priority queuing, retry logic, and per-channel rate limiting.",
            ],
        },
        {
            "name": "Distributed Job Scheduler",
            "tech": "Python, Celery, Redis, FastAPI, PostgreSQL",
            "bullets": [
                "Horizontally scalable job scheduling system with cron-like scheduling, dependency chains, and real-time progress monitoring.",
                "Supports 10K+ scheduled jobs with automatic failover, dead-letter queues, and WebSocket-based status updates.",
            ],
        },
    ],
    "cloud_devops_engineer": [
        {
            "name": "Multi-Cloud Infrastructure Platform",
            "tech": "Terraform, Ansible, AWS, Docker, Python",
            "bullets": [
                "Reusable Terraform modules for provisioning AWS infrastructure (VPC, ECS, RDS, S3) with automated compliance validation.",
                "Reduced environment provisioning from 2 days to 30 minutes with self-service infrastructure templates.",
            ],
        },
        {
            "name": "GitOps Deployment Pipeline",
            "tech": "ArgoCD, Kubernetes, Helm, GitHub Actions, Prometheus",
            "bullets": [
                "GitOps-based deployment system with automated canary releases, progressive traffic shifting, and auto-rollback on SLO violations.",
                "Manages 20+ microservice deployments with Slack approval gates and full audit trail of all production changes.",
            ],
        },
        {
            "name": "Observability & Monitoring Stack",
            "tech": "Prometheus, Grafana, ELK Stack, PagerDuty, Python",
            "bullets": [
                "Centralized monitoring platform with custom Prometheus exporters, Grafana dashboards, and log aggregation via ELK Stack.",
                "Automated incident detection and PagerDuty alerting with runbooks that reduced MTTR from 45 minutes to 12 minutes.",
            ],
        },
    ],
    "software_tester_qa": [
        {
            "name": "Automated Test Framework",
            "tech": "pytest, Selenium, Playwright, GitHub Actions",
            "bullets": [
                "Modular test automation framework with page object model, data-driven tests, and parallel execution across browsers.",
                "Integrated into CI/CD pipeline with automatic test selection based on changed files, reducing test suite runtime by 60%.",
            ],
        },
        {
            "name": "API Contract Testing Platform",
            "tech": "Python, pytest, Pact, Docker, PostgreSQL",
            "bullets": [
                "Consumer-driven contract testing system for 50+ API endpoints across 15 microservices with automated compatibility checks.",
                "Catches breaking API changes before deployment, preventing 30+ integration failures per quarter.",
            ],
        },
        {
            "name": "Load Testing & Performance Benchmarking",
            "tech": "Locust, Python, Grafana, InfluxDB, Docker",
            "bullets": [
                "Automated load testing framework simulating 10K+ concurrent users with realistic traffic patterns and performance regression detection.",
                "Generates performance reports comparing against baselines with automated alerting when response times exceed SLA thresholds.",
            ],
        },
    ],
}


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

    projects = ROLE_PROJECTS.get(role_key, [])
    if projects:
        pdf.section_header("Projects")
        for proj in projects:
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(30, 30, 30)
            pdf.cell(w=0, h=5, text=proj["name"])
            pdf.set_font("Helvetica", "I", 8)
            pdf.set_text_color(100, 100, 100)
            pdf.cell(w=0, h=5, text=proj["tech"],
                     align="R", new_x="LMARGIN", new_y="NEXT")
            for b in proj["bullets"]:
                pdf.bullet(b)
            pdf.ln(0.3)
        pdf.ln(0.5)

    if template["achievements"]:
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


def _tex_projects_section(role_key: str) -> str:
    """Render a LaTeX Projects section if the role has projects."""
    projects = ROLE_PROJECTS.get(role_key, [])
    if not projects:
        return ""
    blocks = []
    for proj in projects:
        bullets = "\n".join(
            f"          \\resumeItem{{{_latex_escape(b)}}}"
            for b in proj["bullets"]
        )
        block = (
            "  \\resumeSubheading\n"
            "      {" + _latex_escape(proj["name"]) + "}{}\n"
            "      {" + _latex_escape(proj["tech"]) + "}{}\n"
            "      \\resumeItemListStart\n"
            + bullets + "\n"
            "      \\resumeItemListEnd"
        )
        blocks.append(block)
    return (
        "\\section{Projects}\n"
        "\\resumeSubHeadingList\n"
        + "\n".join(blocks) + "\n"
        "\\resumeSubHeadingListEnd"
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

{_tex_projects_section(template.get("key", ""))}
\\end{{document}}"""
