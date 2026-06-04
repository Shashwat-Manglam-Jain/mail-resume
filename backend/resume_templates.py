"""
resume_templates.py — Role-specific resume data and generators.

This module holds every role template (skills, projects, experience,
certifications, achievements) and exposes two generators:

    generate_pdf_resume(role_key, profile) -> bytes   (ATS-friendly PDF)
    make_latex_resume(template, basics)    -> str      (LaTeX source)

Profile dict (loaded from .env by main.py):
    name, email, phone, location, linkedin, github, portfolio,
    education, graduation_year

Public helpers:
    list_templates()          -> summary list of all roles
    get_template(role_key)    -> full template dict or None
"""

from textwrap import dedent

from fpdf import FPDF


# ============================================================================
# SECTION 1 — Role template builder
# ============================================================================

def _role(key, title, summary, skills, projects, experience,
          focus, certifications, achievements):
    """Build a structured role-template dict."""
    return {
        "key": key,
        "title": title,
        "summary": summary,
        "skills": skills,           # dict[category -> list[str]]
        "projects": projects,       # list[dict(name, stack, bullets)]
        "experience": experience,   # list[str]  (bullet points)
        "focus": focus,             # list[str]  (interview focus areas)
        "certifications": certifications,  # list[str]
        "achievements": achievements,      # list[str]
    }


# ============================================================================
# SECTION 2 — Detailed role templates (top 5 — hand-tuned for 2025-2026)
# ============================================================================

ROLE_TEMPLATES = [

    # ── AI / ML Engineer ────────────────────────────────────────────────
    _role(
        "ai_ml_engineer",
        "AI/ML Engineer",
        "AI/ML Engineer with hands-on experience building production-grade "
        "machine learning systems, LLM-powered applications, RAG pipelines, "
        "and cloud-deployed inference APIs delivering measurable business impact.",
        {
            "Languages": [
                "Python", "SQL", "Bash", "C++",
            ],
            "ML & Deep Learning": [
                "PyTorch", "TensorFlow", "Scikit-learn", "XGBoost",
                "Transformers", "HuggingFace",
            ],
            "GenAI & LLM": [
                "LangChain", "LlamaIndex", "RAG", "FAISS",
                "Fine-tuning (LoRA/QLoRA)", "Prompt Engineering",
                "OpenAI API", "Claude API",
            ],
            "MLOps & Cloud": [
                "MLflow", "Docker", "Kubernetes", "FastAPI",
                "AWS SageMaker", "CI/CD", "Weights & Biases",
            ],
            "Tools": [
                "Git", "Linux", "Jupyter", "Pandas", "NumPy",
                "Postman", "VS Code",
            ],
        },
        [
            {
                "name": "LLM-Powered Document Intelligence Platform",
                "stack": "LangChain, RAG, FAISS, FastAPI, React",
                "bullets": [
                    "Built a retrieval-augmented generation system that answers "
                    "questions over 10k+ internal documents with citation "
                    "tracking and confidence scoring.",
                    "Implemented chunking strategies, metadata filters, and "
                    "re-ranking to achieve 92% answer relevance on evaluation "
                    "benchmarks.",
                ],
            },
            {
                "name": "Production ML Pipeline — Customer Churn Prediction",
                "stack": "PyTorch, Scikit-learn, MLflow, Docker, AWS",
                "bullets": [
                    "Designed end-to-end pipeline covering feature engineering, "
                    "model training, hyperparameter tuning, and automated "
                    "deployment with 0.91 F1 score.",
                    "Reduced monthly churn by 18% through SHAP-based "
                    "explainability reports consumed by retention teams.",
                ],
            },
            {
                "name": "Real-Time Object Detection API",
                "stack": "YOLOv8, FastAPI, Redis, Docker, Prometheus",
                "bullets": [
                    "Deployed a low-latency (<50ms) inference API for "
                    "manufacturing defect detection processing 500+ images "
                    "per minute.",
                    "Added model versioning, A/B rollout, and Prometheus "
                    "monitoring for drift detection in production.",
                ],
            },
        ],
        [
            "Built ML pipelines covering data preprocessing, training, "
            "validation, deployment, and inference monitoring.",
            "Converted business problems into measurable ML tasks with "
            "clear metrics (F1, recall, latency, drift).",
            "Collaborated with product and engineering teams to integrate "
            "models into production APIs and dashboards.",
        ],
        [
            "Python ML stack", "LLM/RAG systems", "model evaluation",
            "deployment APIs", "MLOps", "business metric impact",
        ],
        [
            "AWS Machine Learning Specialty",
            "Deep Learning Specialization — Andrew Ng",
            "LangChain for LLM Application Development",
        ],
        [
            "Delivered 3 end-to-end AI projects with production-ready APIs.",
            "Solved 300+ DSA and Python problems for coding interviews.",
        ],
    ),

    # ── Data Engineer ───────────────────────────────────────────────────
    _role(
        "data_engineer",
        "Data Engineer",
        "Data Engineer experienced in designing scalable ETL/ELT pipelines, "
        "lakehouse architectures, real-time streaming, data quality frameworks, "
        "and analytics-ready datasets serving business intelligence teams.",
        {
            "Languages": [
                "Python", "SQL", "Scala", "Bash",
            ],
            "Data Processing": [
                "Apache Spark", "Apache Kafka", "Apache Airflow",
                "dbt", "Apache Flink",
            ],
            "Cloud & Warehouses": [
                "AWS (S3, Glue, Redshift)", "GCP (BigQuery, Dataflow)",
                "Snowflake", "Databricks", "Delta Lake",
            ],
            "Infrastructure": [
                "Docker", "Terraform", "Kubernetes",
                "GitHub Actions", "CI/CD",
            ],
            "Tools": [
                "Git", "Linux", "Great Expectations",
                "Power BI", "Tableau", "PostgreSQL",
            ],
        },
        [
            {
                "name": "Real-Time Data Lakehouse Platform",
                "stack": "Spark, Kafka, Delta Lake, Airflow, AWS S3",
                "bullets": [
                    "Designed a streaming-plus-batch lakehouse ingesting "
                    "2M+ events/day from CRM, payments, and product telemetry "
                    "into curated dimensional marts.",
                    "Implemented schema evolution, data quality gates, and "
                    "SLA alerting that reduced dashboard data issues by 75%.",
                ],
            },
            {
                "name": "Cloud Data Warehouse Migration",
                "stack": "dbt, Snowflake, Terraform, GitHub Actions",
                "bullets": [
                    "Migrated 200+ legacy SQL scripts to dbt models with "
                    "staging, intermediate, and mart layers, achieving full "
                    "lineage documentation.",
                    "Automated CI/CD with model tests, freshness checks, "
                    "and incremental builds cutting warehouse costs by 40%.",
                ],
            },
            {
                "name": "Event-Driven ETL Pipeline",
                "stack": "Kafka, Python, PostgreSQL, Docker",
                "bullets": [
                    "Built streaming ingestion for order and payment events "
                    "with retry handling, dead-letter queues, and real-time "
                    "monitoring dashboards.",
                    "Reduced manual reporting effort by 60% by making "
                    "near-real-time sales KPIs available to BI consumers.",
                ],
            },
        ],
        [
            "Developed ETL workflows with orchestration, partitioning, "
            "incremental loads, and warehouse optimization.",
            "Translated reporting requirements into source-to-target "
            "mappings and reusable data models.",
            "Partnered with analysts to improve KPI definitions, dashboard "
            "reliability, and data availability.",
        ],
        [
            "SQL depth", "Spark/Kafka", "Airflow orchestration",
            "warehouse modeling", "data quality", "dbt",
        ],
        [
            "Databricks Lakehouse Fundamentals",
            "dbt Analytics Engineering Certification",
            "AWS Data Analytics Specialty",
        ],
        [
            "Built reusable SQL models and data quality checks for "
            "analytics workflows.",
            "Documented data lineage and ownership for 50+ critical "
            "reporting tables.",
        ],
    ),

    # ── Data Scientist ──────────────────────────────────────────────────
    _role(
        "data_scientist",
        "Data Scientist",
        "Data Scientist skilled in statistical modeling, predictive analytics, "
        "experimentation design, and translating complex datasets into "
        "actionable business recommendations with measurable ROI.",
        {
            "Languages": [
                "Python", "R", "SQL",
            ],
            "Machine Learning": [
                "Scikit-learn", "XGBoost", "LightGBM",
                "Feature Engineering", "Model Selection",
            ],
            "Statistics": [
                "Hypothesis Testing", "A/B Testing",
                "Bayesian Methods", "Time Series",
                "Causal Inference", "Regression",
            ],
            "GenAI & NLP": [
                "LLMs", "Prompt Engineering", "RAG",
                "Text Analytics", "Sentiment Analysis",
            ],
            "Visualization": [
                "Tableau", "Power BI", "Plotly",
                "Matplotlib", "Seaborn",
            ],
            "Tools": [
                "Jupyter", "Git", "BigQuery", "Snowflake",
                "Pandas", "NumPy", "MLflow",
            ],
        },
        [
            {
                "name": "Customer Lifetime Value Prediction Engine",
                "stack": "XGBoost, SHAP, Streamlit, PostgreSQL",
                "bullets": [
                    "Built a CLV prediction model segmenting 500k+ "
                    "customers into value tiers with 0.88 AUC, enabling "
                    "targeted retention campaigns.",
                    "Created an interactive Streamlit dashboard with SHAP "
                    "explanations consumed by marketing leadership.",
                ],
            },
            {
                "name": "A/B Testing Analytics Platform",
                "stack": "Python, Statsmodels, SQL, Power BI",
                "bullets": [
                    "Designed experiment framework with sample-size "
                    "calculators, sequential testing, and guardrail metrics "
                    "for pricing experiments.",
                    "Delivered lift analysis dashboards showing confidence "
                    "intervals, segment effects, and revenue impact "
                    "projections.",
                ],
            },
            {
                "name": "Demand Forecasting System",
                "stack": "Prophet, LightGBM, Pandas, Airflow",
                "bullets": [
                    "Forecasted weekly product demand across 120 SKUs with "
                    "seasonality, holiday effects, and promotional overlays.",
                    "Improved inventory planning accuracy by 25% over "
                    "baseline moving-average approach.",
                ],
            },
        ],
        [
            "Performed exploratory analysis, feature engineering, model "
            "training, validation, and stakeholder storytelling.",
            "Defined success metrics and evaluated models against business "
            "outcomes, not only technical scores.",
            "Created dashboards and notebooks that made insights accessible "
            "to non-technical teams.",
        ],
        [
            "statistics", "SQL depth", "business impact",
            "experimentation", "model interpretation",
            "dashboard storytelling",
        ],
        [
            "Google Advanced Data Analytics Professional Certificate",
            "Applied Data Science with Python — University of Michigan",
            "Statistics for Data Science and Business Analysis",
        ],
        [
            "Delivered end-to-end analysis projects covering data cleaning, "
            "modeling, and recommendations.",
            "Built reusable notebooks for EDA, model comparison, and "
            "executive reporting.",
        ],
    ),

    # ── Data Analyst / BI Analyst ───────────────────────────────────────
    _role(
        "data_analyst_bi",
        "Data Analyst / BI Analyst",
        "Data Analyst and BI professional focused on SQL-driven analysis, "
        "KPI reporting, dashboard design, and translating raw data into "
        "actionable insights for cross-functional business teams.",
        {
            "Analytics": [
                "SQL", "Excel", "Power BI", "Tableau", "Looker",
            ],
            "BI Engineering": [
                "DAX", "Power Query", "Data Modeling",
                "KPI Design", "Dashboard UX",
            ],
            "Data Skills": [
                "Data Cleaning", "Joins", "Window Functions",
                "CTEs", "Cohort Analysis", "Funnel Analysis",
            ],
            "Business": [
                "Stakeholder Reporting", "Root Cause Analysis",
                "Revenue Analytics", "Presentation Design",
            ],
            "Tools": [
                "Python", "Pandas", "Google Sheets",
                "GA4", "Jira", "Confluence",
            ],
        },
        [
            {
                "name": "Executive Revenue Dashboard",
                "stack": "Power BI, SQL, DAX, Azure SQL",
                "bullets": [
                    "Created a leadership dashboard tracking revenue, churn, "
                    "renewal, pipeline, and region-wise performance used by "
                    "C-suite for weekly reviews.",
                    "Built DAX measures with drill-through views enabling "
                    "teams to diagnose metric changes in under 2 minutes.",
                ],
            },
            {
                "name": "Sales Funnel Conversion Analysis",
                "stack": "SQL, Tableau, Excel",
                "bullets": [
                    "Analyzed lead source, stage conversion, sales cycle "
                    "length, and win-rate trends using SQL window functions "
                    "and Tableau visual reports.",
                    "Recommended lead-quality scoring changes that improved "
                    "sales follow-up prioritization by 30%.",
                ],
            },
            {
                "name": "Customer Support SLA Reporting System",
                "stack": "SQL, Power Query, Power BI",
                "bullets": [
                    "Built weekly SLA, backlog, aging, and agent productivity "
                    "reports with automated refresh reducing manual prep "
                    "by 4 hours/week.",
                    "Standardized ticket-level data transformations across "
                    "3 support teams for consistent executive reporting.",
                ],
            },
        ],
        [
            "Built dashboards, recurring reports, and ad-hoc analyses for "
            "business stakeholders.",
            "Used SQL to clean, join, and aggregate datasets from product, "
            "sales, and operations systems.",
            "Translated ambiguous business questions into measurable KPIs "
            "and clear recommendations.",
        ],
        [
            "advanced SQL", "Power BI / Tableau", "KPI definitions",
            "business storytelling", "Excel", "dashboard quality",
        ],
        [
            "Microsoft Power BI Data Analyst Associate",
            "Google Data Analytics Professional Certificate",
            "Advanced SQL for Data Analysis",
        ],
        [
            "Created dashboards with automated refresh and stakeholder-"
            "ready summaries.",
            "Improved reporting consistency by documenting KPI definitions "
            "across departments.",
        ],
    ),

    # ── Business Analyst ────────────────────────────────────────────────
    _role(
        "business_analyst",
        "Business Analyst",
        "Business Analyst experienced in requirement gathering, process mapping, "
        "user story creation, UAT coordination, and delivering KPI-backed "
        "recommendations that drive operational improvements.",
        {
            "Analysis": [
                "Requirement Gathering", "Process Mapping",
                "Gap Analysis", "Root Cause Analysis",
                "Impact Assessment",
            ],
            "Documentation": [
                "BRD", "FRD", "User Stories",
                "Acceptance Criteria", "SOPs", "Wireframes",
            ],
            "Data": [
                "SQL", "Excel", "Power BI", "KPI Reporting",
            ],
            "Delivery": [
                "Jira", "Agile/Scrum", "UAT",
                "Stakeholder Management", "Sprint Planning",
            ],
            "Tools": [
                "Figma", "Miro", "Confluence",
                "Lucidchart", "Postman",
            ],
        },
        [
            {
                "name": "Loan Origination Workflow Optimization",
                "stack": "BPMN, Jira, SQL, Power BI",
                "bullets": [
                    "Mapped current-state and future-state workflows for "
                    "application intake, verification, approval, and "
                    "disbursal reducing cycle time by 35%.",
                    "Defined 40+ user stories with acceptance criteria that "
                    "reduced rework during development handoff by 50%.",
                ],
            },
            {
                "name": "Customer Support Process Analytics",
                "stack": "SQL, Excel, Power BI, Jira",
                "bullets": [
                    "Analyzed ticket aging, escalation reasons, and SLA "
                    "breaches to identify process bottlenecks across "
                    "3 support regions.",
                    "Built KPI dashboards and recommended queue-routing "
                    "changes that improved first-response time by 25%.",
                ],
            },
            {
                "name": "E-commerce Checkout Requirement Pack",
                "stack": "Figma, Jira, Confluence, Miro",
                "bullets": [
                    "Documented checkout, payment, coupon, refund, and "
                    "order-status requirements covering 60+ edge cases.",
                    "Coordinated UAT across 3 teams and tracked defects "
                    "through closure before production release.",
                ],
            },
        ],
        [
            "Converted stakeholder needs into clear requirements, user "
            "stories, workflows, and acceptance criteria.",
            "Supported UAT, release readiness, defect triage, and "
            "business impact reporting.",
            "Used data analysis to validate process improvements and "
            "prioritize product changes.",
        ],
        [
            "BRD/FRD", "user stories", "UAT coordination",
            "SQL reporting", "process mapping", "communication",
        ],
        [
            "IIBA Entry Certificate in Business Analysis (ECBA)",
            "Agile Business Analysis — ICAgile",
            "Microsoft Power BI for Business Users",
        ],
        [
            "Created complete requirement packs with workflow diagrams "
            "and test scenarios.",
            "Improved stakeholder alignment through structured meeting "
            "notes and decision logs.",
        ],
    ),
]


# ============================================================================
# SECTION 3 — Extra roles (auto-generated from compact specs)
# ============================================================================

_EXTRA_ROLE_SPECS = [
    # (key, title, skills_csv, project_name, stack, project_desc)
    ("full_stack_developer", "Full-Stack Developer",
     "React, Next.js, TypeScript, Node.js, Express, PostgreSQL, MongoDB, "
     "Prisma, Tailwind CSS, Docker, AWS, Redis, JWT, REST APIs, GraphQL",
     "Professional Networking Platform",
     "Next.js, TypeScript, PostgreSQL, Prisma, Tailwind CSS",
     "multi-role platform with auth, profiles, job posts, search, saved "
     "jobs, and admin moderation"),

    ("backend_engineer", "Back-End Developer",
     "Python, FastAPI, Django, Node.js, PostgreSQL, Redis, REST, GraphQL, "
     "Docker, System Design, Celery, RabbitMQ, Nginx, Linux, Kubernetes",
     "Scalable Notification Service",
     "FastAPI, Redis Queue, PostgreSQL, Docker, Prometheus",
     "queue-backed email/SMS service with retries, templates, delivery "
     "logs, and rate limiting"),

    ("frontend_engineer", "Front-End Developer",
     "React, Next.js, TypeScript, JavaScript, HTML, CSS, Redux, Zustand, "
     "Tailwind CSS, Accessibility, Testing Library, Playwright, Figma, Vite",
     "Analytics Workspace UI",
     "React, Next.js, TypeScript, Recharts, Tailwind CSS",
     "responsive dashboard with filters, saved views, accessible tables, "
     "and loading/error states"),

    ("cloud_devops_engineer", "Cloud & DevOps Engineer",
     "AWS, Docker, Kubernetes, Terraform, GitHub Actions, Jenkins, Linux, "
     "Prometheus, Grafana, Nginx, Ansible, Helm, ArgoCD, Vault, CI/CD",
     "Kubernetes Microservices Platform",
     "AWS EKS, Terraform, Docker, GitHub Actions, Helm",
     "containerized app platform with autoscaling, secrets, ingress, "
     "monitoring, and rollback workflows"),

    ("cybersecurity_analyst", "Cybersecurity Analyst",
     "SIEM, Splunk, Network Security, Vulnerability Assessment, Incident "
     "Response, Linux, Python, OWASP, IAM, MITRE ATT&CK, Nessus, Wireshark",
     "SOC Alert Triage Playbook",
     "Splunk, Python, MITRE ATT&CK, SOAR",
     "incident triage workflows for phishing, brute force, malware, and "
     "suspicious login alerts"),

    ("mobile_app_developer", "Mobile App Developer",
     "Flutter, React Native, Kotlin, Swift, Dart, Firebase, REST APIs, "
     "State Management, Push Notifications, SQLite, CI/CD, Fastlane",
     "Field Service Mobile App",
     "Flutter, Firebase, REST APIs, SQLite",
     "cross-platform app for job assignment, GPS check-ins, image upload, "
     "offline sync, and push notifications"),

    ("software_engineer", "Software Engineer",
     "Java, Python, JavaScript, TypeScript, SQL, Data Structures, "
     "REST APIs, Spring Boot, React, PostgreSQL, Git, System Design, Agile",
     "Task Management Platform",
     "Java, Spring Boot, React, PostgreSQL, Docker",
     "task assignment, comments, notifications, audit history, and "
     "role-based access control"),

    ("software_tester_qa", "Software Tester (QA)",
     "Manual Testing, Selenium, Playwright, Postman, API Testing, Jira, "
     "Test Cases, Regression Testing, SQL, CI/CD, Performance Testing",
     "E-commerce Regression Automation",
     "Playwright, Postman, SQL, Jira, GitHub Actions",
     "test suite covering login, search, cart, checkout, payments, "
     "refunds, and order tracking"),

    ("ui_ux_engineer", "UI/UX Engineer",
     "Figma, React, HTML, CSS, Design Systems, Wireframing, Prototyping, "
     "Usability Testing, Accessibility, Storybook, Framer Motion",
     "Checkout Experience Redesign",
     "Figma, React, Usability Testing, Design Tokens",
     "mobile-first checkout flow with prototypes, design tokens, and "
     "implemented UI components"),

    ("product_designer", "Product Designer",
     "Product Strategy, Figma, User Research, Wireframing, Prototyping, "
     "Design Systems, Analytics, A/B Testing, Information Architecture",
     "Subscription Upgrade Flow",
     "Figma, Analytics, A/B Testing, FigJam",
     "plan comparison, upgrade prompts, payment flow, and experiment-"
     "ready design variants"),

    ("web_developer", "Web Developer",
     "HTML, CSS, JavaScript, React, WordPress, PHP, SEO, Responsive "
     "Design, Git, Web Performance, Tailwind CSS, Bootstrap, GA4",
     "Local Business Website Suite",
     "React, WordPress, GA4, Search Console, Tailwind CSS",
     "responsive service website with landing pages, forms, schema "
     "markup, and optimized Core Web Vitals"),

    ("seo_specialist", "SEO Specialist",
     "Keyword Research, Google Search Console, GA4, Ahrefs, SEMrush, "
     "Technical SEO, On-page SEO, Schema Markup, Content Strategy, "
     "Link Building, Core Web Vitals",
     "Technical SEO Growth Audit",
     "Screaming Frog, GA4, Search Console, Ahrefs",
     "crawl audit, metadata fixes, schema recommendations, internal "
     "linking, and keyword opportunity map"),

    ("graphic_designer", "Graphic Designer",
     "Photoshop, Illustrator, InDesign, Figma, Branding, Typography, "
     "Social Media Design, Print Design, Layout, Motion Graphics",
     "Startup Brand Identity Kit",
     "Illustrator, Photoshop, Figma, After Effects",
     "logo system, typography, color palette, pitch deck graphics, "
     "and social media templates"),

    ("video_editor", "Video Editor",
     "Premiere Pro, After Effects, DaVinci Resolve, Color Grading, "
     "Audio Cleanup, Motion Graphics, Storyboarding, Captions, YouTube",
     "Product Demo Video Series",
     "Premiere Pro, After Effects, Audition",
     "short-form and long-form demo videos with captions, motion "
     "callouts, and clean audio"),

    ("account_manager", "Account Manager",
     "Client Management, CRM, Renewals, Upselling, Presentation, "
     "Negotiation, Account Planning, Reporting, HubSpot, Salesforce",
     "Renewal Risk Program",
     "HubSpot, Excel, Power BI, Salesforce",
     "account health model with usage, support, renewal date, and "
     "expansion opportunity tracking"),

    ("sales_representative", "Sales Representative",
     "Prospecting, CRM, Cold Calling, Product Demos, Negotiation, "
     "Follow-ups, Lead Qualification, Objection Handling, HubSpot",
     "Demo Conversion Improvement Plan",
     "CRM, Excel, Email Sequencing, HubSpot",
     "follow-up cadence, objection script, demo notes, and opportunity "
     "tracking dashboard"),
]


def _build_extra_role(key, title, skill_text, project_name, stack,
                      project_description):
    """Generate a full role template from a compact spec tuple."""
    skills = [s.strip() for s in skill_text.split(",")]
    return _role(
        key,
        title,
        f"{title} with practical experience building job-ready projects, "
        f"collaborating with stakeholders, and delivering measurable "
        f"improvements using modern industry tools.",
        {
            "Core": skills[:5],
            "Technical": skills[5:10],
            "Delivery": skills[10:15] if len(skills) > 10 else [
                "Agile", "Documentation", "Stakeholder Communication",
                "Problem Solving", "Quality Review",
            ],
            "Tools": ["Git", "Jira", "Postman", "VS Code", "Linux"],
        },
        [
            {
                "name": project_name,
                "stack": stack,
                "bullets": [
                    f"Built a portfolio-grade {project_description} aligned "
                    f"with common {title} job requirements.",
                    "Added measurable outcomes, documentation, test evidence, "
                    "and user-focused improvements for interview readiness.",
                ],
            },
            {
                "name": f"{title} Operations Dashboard",
                "stack": "SQL, Excel, Power BI, Documentation",
                "bullets": [
                    "Created KPI tracking for task progress, quality issues, "
                    "delivery timelines, and stakeholder requests.",
                    "Used reporting insights to prioritize improvements and "
                    "explain project impact clearly during interviews.",
                ],
            },
            {
                "name": f"{title} Automation Toolkit",
                "stack": "Python, APIs, Git, CI/CD",
                "bullets": [
                    "Automated repetitive checks, exports, and status updates "
                    "to reduce manual effort and improve consistency.",
                    "Documented setup steps, edge cases, and results so "
                    "reviewers can quickly understand ownership quality.",
                ],
            },
        ],
        [
            f"Delivered practical {title.lower()} tasks using modern tools, "
            f"structured documentation, and measurable quality checks.",
            "Worked with cross-functional stakeholders to clarify "
            "requirements, review feedback, and improve deliverables.",
            "Prepared demos, reports, and project notes showing business "
            "value and technical understanding.",
        ],
        skills[:8],
        [
            f"{title} Professional Certificate",
            "Agile Project Delivery",
            "Communication and Stakeholder Management",
        ],
        [
            "Created portfolio projects mapped directly to job-description "
            "keywords.",
            "Prepared interview-ready case studies explaining problem, "
            "action, tools, and impact.",
        ],
    )


# Build extra roles and merge into main list
ROLE_TEMPLATES.extend(_build_extra_role(*spec) for spec in _EXTRA_ROLE_SPECS)


# ============================================================================
# SECTION 4 — Public API helpers
# ============================================================================

def list_templates():
    """Return a summary list of all roles (key, title, summary, skills, focus)."""
    return [
        {
            "key": t["key"],
            "title": t["title"],
            "summary": t["summary"],
            "skills": [s for vals in t["skills"].values() for s in vals],
            "focus": t["focus"],
        }
        for t in ROLE_TEMPLATES
    ]


def get_template(key: str):
    """Return the full template dict for a role key, or None."""
    return next((t for t in ROLE_TEMPLATES if t["key"] == key), None)


# ============================================================================
# SECTION 5 — PDF Resume Generator (ATS-friendly, single page)
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

    # ── Auto-sanitize all text for Latin-1 fonts ─────────────────────
    def cell(self, *args, text="", **kwargs):
        """Override cell() to sanitize Unicode before rendering."""
        return super().cell(*args, text=_sanitize(str(text)), **kwargs)

    def multi_cell(self, *args, text="", **kwargs):
        """Override multi_cell() to sanitize Unicode before rendering."""
        return super().multi_cell(*args, text=_sanitize(str(text)), **kwargs)

    # ── Section divider ─────────────────────────────────────────────
    def section_header(self, title: str):
        """Draw a bold section title with a thin horizontal rule below."""
        self.set_font("Helvetica", "B", 10.5)
        self.set_text_color(30, 30, 30)
        self.cell(w=0, h=6, text=title.upper(), new_x="LMARGIN", new_y="NEXT")
        y = self.get_y()
        self.set_draw_color(80, 80, 80)
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(1.5)

    # ── Bullet point ────────────────────────────────────────────────
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


def generate_pdf_resume(role_key: str, profile: dict) -> bytes:
    """
    Generate a single-page ATS-friendly PDF resume for the given role.

    Args:
        role_key: template key (e.g. 'data_scientist')
        profile:  dict with name, email, phone, location, linkedin,
                  github, portfolio, education, graduation_year

    Returns:
        PDF file content as bytes, ready to attach to an email.
    """
    template = get_template(role_key)
    if not template:
        raise ValueError(f"Unknown role key: {role_key}")

    # Extract profile fields with fallbacks
    name = (profile.get("name") or "YOUR NAME").upper()
    email = profile.get("email") or "email@example.com"
    phone = profile.get("phone") or "+91 00000 00000"
    location = profile.get("location") or "City, India"
    linkedin = (profile.get("linkedin") or "").replace("https://", "").rstrip("/")
    github = (profile.get("github") or "").replace("https://", "").rstrip("/")
    portfolio = (profile.get("portfolio") or "").replace("https://", "").rstrip("/")
    education = profile.get("education") or "B.Tech / B.Sc, Your College"
    grad_year = profile.get("graduation_year") or "2026"

    pdf = _ResumePDF()
    pdf.add_page()

    # ── Name ────────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(w=0, h=9, text=name, align="C", new_x="LMARGIN", new_y="NEXT")

    # ── Contact line ────────────────────────────────────────────────
    contact_parts = [p for p in [email, phone, location] if p]
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(
        w=0, h=4.5,
        text="  |  ".join(contact_parts),
        align="C", new_x="LMARGIN", new_y="NEXT",
    )

    # ── Links line ──────────────────────────────────────────────────
    link_parts = [p for p in [linkedin, github, portfolio] if p]
    if link_parts:
        pdf.cell(
            w=0, h=4.5,
            text="  |  ".join(link_parts),
            align="C", new_x="LMARGIN", new_y="NEXT",
        )
    pdf.ln(2)

    # ── Professional Summary ────────────────────────────────────────
    pdf.section_header("Professional Summary")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(50, 50, 50)
    summary = (
        template["summary"]
        + " Strong foundation in communication, ownership, "
        "documentation, and interview-ready project storytelling."
    )
    pdf.multi_cell(w=0, h=4, text=summary)
    pdf.ln(1.5)

    # ── Technical Skills ────────────────────────────────────────────
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

    # ── Experience ──────────────────────────────────────────────────
    pdf.section_header("Professional Experience")
    # Title and company on same line
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(w=0, h=5, text=f"Intern — {template['title']}")
    # Date right-aligned
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(w=0, h=5, text="Jan 2025 — Present",
             align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(w=0, h=4, text="SkillBridge Labs, Remote",
             new_x="LMARGIN", new_y="NEXT")
    for exp_bullet in template["experience"]:
        pdf.bullet(exp_bullet)
    pdf.ln(1)

    # ── Key Projects ────────────────────────────────────────────────
    pdf.section_header("Key Projects")
    for project in template["projects"]:
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(w=0, h=5, text=project["name"])
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(w=0, h=5, text=project["stack"],
                 align="R", new_x="LMARGIN", new_y="NEXT")
        for b in project["bullets"]:
            pdf.bullet(b)
        pdf.ln(0.5)
    pdf.ln(0.5)

    # ── Education ───────────────────────────────────────────────────
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
    pdf.cell(
        w=0, h=4,
        text="Relevant coursework: Data Structures, Databases, "
             "Statistics, Software Engineering",
        new_x="LMARGIN", new_y="NEXT",
    )
    pdf.ln(1)

    # ── Certifications ──────────────────────────────────────────────
    pdf.section_header("Certifications")
    for cert in template["certifications"]:
        pdf.bullet(cert, indent=2)
    pdf.ln(0.5)

    # ── Achievements ────────────────────────────────────────────────
    pdf.section_header("Achievements")
    for ach in template["achievements"]:
        pdf.bullet(ach, indent=2)

    return bytes(pdf.output())


# ============================================================================
# SECTION 6 — LaTeX Resume Generator (alternative download format)
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


def _tex_items(items):
    """Render a list of strings as LaTeX itemize bullets."""
    return "\n".join(rf"  \item {_latex_escape(item)}" for item in items)


def _tex_skill_rows(skills):
    """Render skill categories as LaTeX tabularx rows."""
    return "\n".join(
        rf"{_latex_escape(cat)}: & {_latex_escape(', '.join(vals))} \\"
        for cat, vals in skills.items()
    )


def _tex_projects(projects):
    """Render project list as LaTeX blocks."""
    blocks = []
    for p in projects:
        bullets = _tex_items(p["bullets"])
        blocks.append(
            rf"""\textbf{{{_latex_escape(p["name"])}}} | """
            rf"""\textit{{{_latex_escape(p["stack"])}}}
\begin{{itemize}}
{bullets}
\end{{itemize}}"""
        )
    return "\n\n".join(blocks)


def make_latex_resume(template: dict, basics: dict) -> str:
    """
    Generate a full LaTeX resume document for the given template and basics.

    Args:
        template: full role template dict from get_template()
        basics:   dict with name, email, phone, location, linkedin,
                  github, portfolio, education, graduation_year

    Returns:
        Complete LaTeX document as a string.
    """
    name = _latex_escape((basics.get("name") or "YOUR NAME").upper())
    email = _latex_escape(basics.get("email") or "email@example.com")
    phone = _latex_escape(basics.get("phone") or "+91 00000 00000")
    location = _latex_escape(basics.get("location") or "City, India")
    linkedin = _normalize_link(basics.get("linkedin"), "linkedin.com/in/profile")
    github = _normalize_link(basics.get("github"), "github.com/username")
    portfolio = _normalize_link(basics.get("portfolio"), "yourportfolio.com")
    education = _latex_escape(
        basics.get("education") or "B.Tech / B.Sc / BCA, Your College"
    )
    grad_year = _latex_escape(basics.get("graduation_year") or "2026")
    title = _latex_escape(template["title"])
    summary = _latex_escape(template["summary"])

    return dedent(
        rf"""
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % {name} — {title} Resume
        % ATS-friendly one-page template. Edit personal details in .env.
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

        \documentclass[10pt,a4paper]{{article}}
        \usepackage[left=0.4in,top=0.3in,right=0.4in,bottom=0.3in]{{geometry}}
        \usepackage{{times}}
        \usepackage[hidelinks]{{hyperref}}
        \usepackage{{enumitem}}
        \usepackage{{tabularx}}
        \usepackage{{titlesec}}

        \pagenumbering{{gobble}}
        \setlength{{\parindent}}{{0pt}}
        \setlist[itemize]{{leftmargin=*, itemsep=1pt, topsep=2pt}}
        \titleformat{{\section}}{{\large\bfseries}}{{}}{{0em}}{{}}[\titlerule]
        \titlespacing*{{\section}}{{0pt}}{{6pt}}{{4pt}}
        \newenvironment{{rSection}}[1]{{\section*{{#1}}}}{{}}
        \newcommand{{\name}}[1]{{\begin{{center}}{{\LARGE\bfseries #1}}\end{{center}}\vspace{{-6pt}}}}
        \newcommand{{\address}}[1]{{\begin{{center}}#1\end{{center}}\vspace{{-8pt}}}}

        \begin{{document}}

        \name{{{name}}}
        \address{{GitHub: \href{{https://{github}}}{{{_latex_escape(github)}}} \quad | \quad Portfolio: \href{{https://{portfolio}}}{{{_latex_escape(portfolio)}}}}}
        \address{{LinkedIn: \href{{https://{linkedin}}}{{{_latex_escape(linkedin)}}} \quad | \quad Email: \href{{mailto:{email}}}{{{email}}}}}
        \address{{Location: {location} \quad | \quad Phone: {phone}}}

        \begin{{rSection}}{{Professional Summary}}
        {summary} Strong foundation in communication, ownership, documentation, and interview-ready project storytelling.
        \end{{rSection}}

        \begin{{rSection}}{{Core Skills}}
        \begin{{tabularx}}{{\textwidth}}{{@{{}} >{{\bfseries}}l @{{\hspace{{2ex}}}} X @{{}}}}
        {_tex_skill_rows(template["skills"])}
        \end{{tabularx}}
        \end{{rSection}}

        \begin{{rSection}}{{Experience}}
        \textbf{{Intern — {title}}} \hfill {{\em Jan 2025 — Present}}\\
        SkillBridge Labs, Remote
        \begin{{itemize}}
        {_tex_items(template["experience"])}
        \end{{itemize}}
        \end{{rSection}}

        \begin{{rSection}}{{Key Projects}}
        {_tex_projects(template["projects"])}
        \end{{rSection}}

        \begin{{rSection}}{{Education}}
        \textbf{{{education}}} \hfill {grad_year}\\
        Relevant coursework: Data Structures, Databases, Statistics, Software Engineering, Business Communication
        \end{{rSection}}

        \begin{{rSection}}{{Certifications}}
        \begin{{itemize}}
        {_tex_items(template["certifications"])}
        \end{{itemize}}
        \end{{rSection}}

        \begin{{rSection}}{{Achievements}}
        \begin{{itemize}}
        {_tex_items(template["achievements"])}
        \end{{itemize}}
        \end{{rSection}}

        \end{{document}}
        """
    ).strip()


def generate_all_resumes(output_dir, basics=None):
    """Generate LaTeX resumes for every role and write to output_dir."""
    from pathlib import Path
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    basics = basics or {}
    generated = []
    for t in ROLE_TEMPLATES:
        p = output_path / f"{t['key']}_resume.tex"
        p.write_text(make_latex_resume(t, basics), encoding="utf-8")
        generated.append(p)
    return generated
