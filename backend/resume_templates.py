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
          focus, certifications, achievements, previous_title=None,
          coursework=None):
    """Build a structured role-template dict."""
    return {
        "key": key,
        "title": title,
        "previous_title": previous_title or f"Junior {title}",
        "summary": summary,
        "skills": skills,           # dict[category -> list[str]]
        "projects": projects,       # list[dict(name, stack, bullets)]
        "experience": experience,   # list[dict(bullets=list[str])]
        "focus": focus,             # list[str]  (interview focus areas)
        "certifications": certifications,  # list[str]
        "achievements": achievements,      # list[str]
        "coursework": coursework or "Data Structures, Algorithms, Databases, Statistics, Software Engineering",
    }


# ============================================================================
# SECTION 2 — Detailed role templates (top 5 — hand-tuned for 2025-2026)
# ============================================================================

ROLE_TEMPLATES = [

    # ── AI / ML Engineer ────────────────────────────────────────────────
    _role(
        "ai_ml_engineer",
        "AI/ML Engineer",
        "Results-driven AI/ML Engineer with 4+ years of experience building "
        "production-grade machine learning systems, LLM-powered applications, "
        "RAG pipelines, and cloud-deployed inference APIs. Proven track record "
        "of reducing operational costs by 35% and improving model accuracy "
        "through end-to-end ML lifecycle management across cross-functional teams.",
        {
            "Languages": [
                "Python", "SQL", "Bash", "C++",
            ],
            "ML & Deep Learning": [
                "PyTorch", "TensorFlow", "Scikit-learn", "XGBoost",
                "Transformers", "HuggingFace", "OpenCV",
            ],
            "GenAI & LLM": [
                "LangChain", "LlamaIndex", "RAG", "FAISS",
                "Fine-tuning (LoRA/QLoRA)", "Prompt Engineering",
                "OpenAI API", "Claude API", "Vector Databases",
            ],
            "MLOps & Cloud": [
                "MLflow", "Docker", "Kubernetes", "FastAPI",
                "AWS SageMaker", "CI/CD", "Weights & Biases",
                "GitHub Actions",
            ],
            "Tools": [
                "Git", "Linux", "Jupyter", "Pandas", "NumPy",
                "Postman", "VS Code", "Agile/Scrum",
            ],
        },
        [
            {
                "name": "AI SaaS Platform -- LLM Chat & RAG Document Intelligence",
                "stack": "FastAPI, LangChain, OpenAI GPT-4, ChromaDB, Next.js 14, PostgreSQL, Stripe, AWS, Docker",
                "bullets": [
                    "Built multi-tenant SaaS platform where businesses upload "
                    "documents and query them via a streaming AI chatbot -- RAG "
                    "pipeline using ChromaDB for vector search and GPT-4 for "
                    "context-aware answers with <2s response time.",
                    "Implemented Stripe subscription tiers, RBAC, usage metering, "
                    "and real-time token streaming -- onboarded 500+ paying users "
                    "at 98% satisfaction rate with zero infrastructure incidents "
                    "in 3 months of production.",
                ],
            },
            {
                "name": "Real-Time Collaborative Developer Platform",
                "stack": "Node.js, React, WebSockets, Redis Pub/Sub, PostgreSQL, Docker, GitHub Actions",
                "bullets": [
                    "Engineered browser-based collaborative environment with "
                    "real-time code sync, live cursors, and session management "
                    "using WebSockets + Redis pub/sub -- supporting 2,000+ "
                    "concurrent users at sub-50ms latency.",
                    "Implemented project versioning, diff tracking, and team "
                    "permission system backed by PostgreSQL -- 88% automated "
                    "test coverage with GitHub Actions CI running on every PR.",
                ],
            },
            {
                "name": "Multi-Vendor E-Commerce SaaS Marketplace",
                "stack": "Django, Next.js, PostgreSQL, Celery, Redis, AWS S3, Stripe, Docker",
                "bullets": [
                    "Delivered full multi-vendor marketplace -- product catalog, "
                    "order management, vendor dashboard, Stripe payment processing, "
                    "and admin moderation -- serving 5,000+ daily active users.",
                    "Optimized PostgreSQL with selective indexing and prefetch "
                    "strategies, reducing average API response time by 60% and "
                    "database CPU by 40%; Celery handled async order processing "
                    "at 99.8% success rate.",
                ],
            },
        ],
        [
            {
                "bullets": [
                    "Led design and deployment of LLM-powered RAG pipelines "
                    "serving 10K+ daily queries, reducing support ticket volume "
                    "by 35% and saving 200+ engineering hours monthly.",
                    "Built end-to-end ML inference APIs using FastAPI and Docker "
                    "with sub-50ms latency, serving 5 production models across "
                    "3 business verticals.",
                    "Established model evaluation frameworks using MLflow and "
                    "Weights & Biases, improving model iteration speed by 40% "
                    "across the ML team.",
                ],
            },
            {
                "bullets": [
                    "Developed customer churn and demand prediction models using "
                    "PyTorch and Scikit-learn, achieving 0.91 F1 score and "
                    "reducing monthly churn by 18%.",
                    "Implemented automated feature engineering pipelines "
                    "processing 2M+ records daily with comprehensive data "
                    "validation, monitoring, and alerting.",
                ],
            },
        ],
        [
            "Python ML stack", "LLM/RAG systems", "model evaluation",
            "deployment APIs", "MLOps", "business metric impact",
        ],
        [],
        [
            "Delivered 5 end-to-end AI projects from ideation to production "
            "deployment serving 50K+ users.",
            "Solved 400+ DSA problems on LeetCode and HackerRank.",
            "Mentored 3 junior engineers on ML best practices and code review.",
        ],
        previous_title="Machine Learning Developer",
        coursework="Machine Learning, Deep Learning, Data Structures, "
                   "Algorithms, Statistics, Linear Algebra",
    ),

    # ── Data Engineer ───────────────────────────────────────────────────
    _role(
        "data_engineer",
        "Data Engineer",
        "Data Engineer with 4+ years of experience designing scalable "
        "ETL/ELT pipelines, lakehouse architectures, real-time streaming "
        "systems, and data quality frameworks. Expertise in processing 5M+ "
        "events/day and delivering analytics-ready datasets that drive "
        "data-informed business decisions across organizations.",
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
                "Power BI", "Tableau", "PostgreSQL", "Agile/Scrum",
            ],
        },
        [
            {
                "name": "AI SaaS Platform -- Data Pipeline & Vector Indexing",
                "stack": "FastAPI, ChromaDB, PostgreSQL, AWS S3, Docker, LangChain",
                "bullets": [
                    "Built ingestion and vector indexing pipeline for 50,000+ "
                    "documents with chunking, embedding, and metadata indexing "
                    "into ChromaDB -- serving 500+ users with <2s query latency "
                    "and zero data loss across 3 months of production.",
                    "Implemented automated data validation, versioning, and "
                    "monitoring pipeline processing 10,000+ daily document "
                    "updates with drift detection and SLA alerting.",
                ],
            },
            {
                "name": "Multi-Vendor E-Commerce Data Platform",
                "stack": "Django, PostgreSQL, Celery, Redis, AWS S3, Docker",
                "bullets": [
                    "Engineered data infrastructure for 5,000+ daily active "
                    "user marketplace -- optimized PostgreSQL with selective "
                    "indexing and prefetch strategies reducing query times by "
                    "60% and database CPU by 40%.",
                    "Built Celery-powered async processing pipeline at 99.8% "
                    "success rate handling order, payment, and notification "
                    "workflows at scale.",
                ],
            },
            {
                "name": "DevOps Automation & Observability Suite",
                "stack": "Python, Docker, AWS, GitHub Actions, Nginx, Grafana, Bash",
                "bullets": [
                    "Built internal toolkit automating deployment health checks, "
                    "log aggregation, and Grafana dashboards monitoring 10+ "
                    "microservices -- reduced manual ops effort by 50% and "
                    "MTTR by 35%.",
                    "Wrote infrastructure runbooks enabling 5 new engineers to "
                    "self-serve incident response and deploy independently "
                    "within their first week.",
                ],
            },
        ],
        [
            {
                "bullets": [
                    "Architected streaming data lakehouse ingesting 5M+ "
                    "events/day from CRM, payments, and product telemetry "
                    "using Spark, Kafka, and Delta Lake.",
                    "Designed and maintained 200+ dbt models with full lineage "
                    "documentation, achieving 40% warehouse cost reduction "
                    "through incremental builds and partitioning.",
                    "Implemented data quality gates with SLA alerting that "
                    "reduced dashboard data issues by 75% across the org.",
                ],
            },
            {
                "bullets": [
                    "Built batch and real-time ETL pipelines using Python, SQL, "
                    "and Airflow, processing data from 15+ source systems into "
                    "analytics-ready datasets.",
                    "Developed monitoring dashboards and automated alerting for "
                    "pipeline health, reducing data incidents by 60%.",
                ],
            },
        ],
        [
            "SQL depth", "Spark/Kafka", "Airflow orchestration",
            "warehouse modeling", "data quality", "dbt",
        ],
        [],
        [
            "Built reusable SQL models and data quality checks adopted "
            "by 3 engineering teams.",
            "Documented data lineage and ownership for 80+ critical "
            "reporting tables across the data warehouse.",
            "Reduced pipeline failure rate from 12% to under 2% through "
            "proactive monitoring and alerting.",
        ],
        previous_title="ETL Developer",
        coursework="Database Systems, Data Warehousing, Distributed Systems, "
                   "Data Structures, Cloud Computing",
    ),

    # ── Data Scientist ──────────────────────────────────────────────────
    _role(
        "data_scientist",
        "Data Scientist",
        "Data Scientist with 4+ years of experience in statistical modeling, "
        "predictive analytics, A/B experimentation, and translating complex "
        "datasets into actionable business recommendations. Delivered $500K+ "
        "measurable ROI through customer segmentation, demand forecasting, "
        "and experiment-driven product optimization.",
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
                "Pandas", "NumPy", "MLflow", "Agile/Scrum",
            ],
        },
        [
            {
                "name": "AI SaaS Platform -- LLM Analytics & Intelligent Search",
                "stack": "FastAPI, LangChain, OpenAI GPT-4, ChromaDB, PostgreSQL, AWS",
                "bullets": [
                    "Designed RAG pipeline with semantic search, response quality "
                    "scoring, and user interaction analytics -- achieving <2s "
                    "response time and 98% user satisfaction across 500+ paying "
                    "users.",
                    "Implemented usage metering, prompt A/B testing, and "
                    "conversion analytics that informed product decisions driving "
                    "3-month growth milestones with zero infrastructure incidents.",
                ],
            },
            {
                "name": "Multi-Vendor E-Commerce Analytics Engine",
                "stack": "Django, PostgreSQL, Celery, Redis, Python",
                "bullets": [
                    "Analyzed product, order, and user behavior data across "
                    "5,000+ daily active users -- built reporting views and KPI "
                    "dashboards consumed by vendor and admin stakeholders.",
                    "Identified query bottlenecks and optimized PostgreSQL "
                    "indexes, reducing average API response time by 60% and "
                    "enabling real-time analytics dashboards.",
                ],
            },
            {
                "name": "Professional Networking & Hiring Platform -- Data Insights",
                "stack": "Next.js 14, TypeScript, PostgreSQL, Prisma, CI/CD",
                "bullets": [
                    "Architected multi-role platform (candidates, recruiters, "
                    "admins) with smart job-match scoring, activity tracking, "
                    "and admin moderation analytics -- 1,000+ active users at "
                    "99.5% uptime.",
                    "Built CI/CD pipeline cutting deployment time by 60%; "
                    "automated tests with 88%+ coverage reduced post-release "
                    "defects by 40%.",
                ],
            },
        ],
        [
            {
                "bullets": [
                    "Led end-to-end data science projects from problem framing "
                    "to production deployment, delivering $500K+ measurable "
                    "business impact across 4 key initiatives.",
                    "Designed A/B testing framework with sequential testing and "
                    "guardrail metrics, standardizing experimentation across "
                    "3 product teams.",
                    "Created executive dashboards with SHAP-based model "
                    "explanations, translating complex ML outputs into "
                    "actionable business recommendations.",
                ],
            },
            {
                "bullets": [
                    "Performed exploratory data analysis and built predictive "
                    "models for demand forecasting across 120 SKUs, improving "
                    "inventory planning accuracy by 25%.",
                    "Developed automated reporting pipelines using SQL and "
                    "Python, reducing manual reporting effort by 60% for "
                    "the analytics team.",
                ],
            },
        ],
        [
            "statistics", "SQL depth", "business impact",
            "experimentation", "model interpretation",
            "dashboard storytelling",
        ],
        [],
        [
            "Delivered 6 end-to-end analysis projects covering data cleaning, "
            "modeling, and production recommendations.",
            "Built reusable experiment analysis templates adopted by 3 teams.",
            "Presented quarterly insights to C-suite leadership driving "
            "strategic product decisions.",
        ],
        previous_title="Data Analyst",
        coursework="Statistics, Probability, Machine Learning, Data Mining, "
                   "Linear Algebra, Research Methods",
    ),

    # ── Data Analyst / BI Analyst ───────────────────────────────────────
    _role(
        "data_analyst_bi",
        "Data Analyst / BI Analyst",
        "Data Analyst and BI professional with 4+ years of experience in "
        "SQL-driven analysis, KPI reporting, dashboard design, and translating "
        "raw data into actionable insights. Built 30+ executive dashboards "
        "used by C-suite leadership, reducing reporting turnaround by 70% "
        "and driving data-informed decisions across cross-functional teams.",
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
                "GA4", "Jira", "Confluence", "Agile/Scrum",
            ],
        },
        [
            {
                "name": "Multi-Vendor E-Commerce Analytics Dashboard",
                "stack": "Django, PostgreSQL, Python, Power BI, SQL",
                "bullets": [
                    "Built reporting layer for 5,000+ daily active user "
                    "marketplace covering order volume, vendor revenue, refund "
                    "rates, and conversion funnels -- consumed by 20+ "
                    "stakeholders for weekly business reviews.",
                    "Identified PostgreSQL query bottlenecks and optimized "
                    "indexes, reducing average reporting query times by 60% "
                    "and enabling real-time dashboards.",
                ],
            },
            {
                "name": "Professional Networking Platform -- KPI Reporting",
                "stack": "Next.js 14, PostgreSQL, Prisma, TypeScript, SQL",
                "bullets": [
                    "Designed user acquisition, job-match success, recruiter "
                    "engagement, and retention KPIs for 1,000+ active user "
                    "platform -- delivered automated stakeholder reports with "
                    "drill-through views.",
                    "Automated CI/CD-driven data pipeline tests achieving 88%+ "
                    "coverage and reducing post-release data incidents by 40%.",
                ],
            },
            {
                "name": "DevOps Observability & Operations Dashboard",
                "stack": "Python, Grafana, Docker, AWS CloudWatch, Bash",
                "bullets": [
                    "Built Grafana dashboards monitoring 10+ microservices "
                    "across deployment health, log aggregation, and SLA metrics "
                    "-- reduced manual ops effort by 50% and MTTR by 35%.",
                    "Documented monitoring runbooks and alert definitions "
                    "enabling 5 new engineers to self-serve incident response "
                    "within their first week.",
                ],
            },
        ],
        [
            {
                "bullets": [
                    "Built 30+ dashboards and recurring reports for business "
                    "stakeholders, reducing reporting turnaround from 3 days "
                    "to same-day delivery.",
                    "Led root cause analysis initiatives identifying $200K+ "
                    "in revenue leakage across sales and operations teams.",
                    "Translated ambiguous business questions into measurable "
                    "KPIs and clear recommendations for senior leadership.",
                ],
            },
            {
                "bullets": [
                    "Used SQL to clean, join, and aggregate datasets from "
                    "product, sales, and operations systems, creating "
                    "standardized reporting tables for 5 departments.",
                    "Built automated Excel and Power BI reports reducing "
                    "manual data preparation effort by 15 hours/week.",
                ],
            },
        ],
        [
            "advanced SQL", "Power BI / Tableau", "KPI definitions",
            "business storytelling", "Excel", "dashboard quality",
        ],
        [],
        [
            "Created 30+ dashboards with automated refresh and "
            "stakeholder-ready summaries adopted company-wide.",
            "Improved reporting consistency by documenting KPI definitions "
            "and data dictionaries across 5 departments.",
            "Received 'Analyst of the Quarter' recognition for revenue "
            "leakage analysis saving $200K+.",
        ],
        previous_title="Junior Data Analyst",
        coursework="Business Statistics, Database Management, Data "
                   "Visualization, Business Intelligence, Excel Analytics",
    ),

    # ── Business Analyst ────────────────────────────────────────────────
    _role(
        "business_analyst",
        "Business Analyst",
        "Business Analyst with 4+ years of experience in requirement "
        "gathering, process mapping, user story creation, UAT coordination, "
        "and delivering KPI-backed recommendations. Successfully managed "
        "requirements for 10+ product releases, reducing development rework "
        "by 50% and driving operational improvements across organizations.",
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
                "name": "Multi-Vendor E-Commerce SaaS -- Requirements & UAT",
                "stack": "Jira, Confluence, SQL, Power BI, Figma",
                "bullets": [
                    "Documented product catalog, order management, vendor "
                    "dashboard, payment processing, and admin moderation "
                    "requirements covering 50+ user stories with detailed "
                    "acceptance criteria and edge cases.",
                    "Coordinated UAT across 3 teams for 5,000+ daily active "
                    "user platform -- tracked defects through closure achieving "
                    "zero critical bugs at production release.",
                ],
            },
            {
                "name": "Professional Networking & Hiring Platform -- Product Analysis",
                "stack": "Jira, Figma, Miro, SQL, Confluence",
                "bullets": [
                    "Gathered and structured requirements for multi-role "
                    "platform (candidates, recruiters, admins) with OAuth, "
                    "smart job search, saved listings, and admin moderation "
                    "for 1,000+ active users.",
                    "Defined sprint-by-sprint delivery plan; CI/CD pipeline "
                    "cut deployment time by 60% and automated tests reduced "
                    "post-release defects by 40%.",
                ],
            },
            {
                "name": "AI SaaS Platform -- Business Requirements & Go-to-Market",
                "stack": "Jira, Confluence, SQL, Figma, Stripe",
                "bullets": [
                    "Documented subscription tier logic, RBAC, usage metering, "
                    "and onboarding requirements for multi-tenant SaaS -- "
                    "enabling 500+ paying user onboarding at 98% satisfaction "
                    "rate.",
                    "Mapped Stripe payment integration workflows, refund edge "
                    "cases, and compliance requirements, achieving zero critical "
                    "billing incidents in 3 months of production.",
                ],
            },
        ],
        [
            {
                "bullets": [
                    "Led requirement gathering for 10+ product releases, "
                    "converting stakeholder needs into structured BRDs, user "
                    "stories, and acceptance criteria.",
                    "Managed end-to-end UAT coordination across 3 product "
                    "teams, reducing post-release defects by 60% through "
                    "comprehensive test scenario design.",
                    "Used SQL and Power BI to validate process improvements "
                    "and deliver KPI-backed recommendations to leadership.",
                ],
            },
            {
                "bullets": [
                    "Supported requirement documentation, process mapping, "
                    "and sprint planning for Agile development teams across "
                    "2 product lines.",
                    "Created workflow diagrams, meeting notes, and decision "
                    "logs improving stakeholder alignment and reducing "
                    "requirement ambiguity by 40%.",
                ],
            },
        ],
        [
            "BRD/FRD", "user stories", "UAT coordination",
            "SQL reporting", "process mapping", "communication",
        ],
        [],
        [
            "Created complete requirement packs for 10+ releases with "
            "workflow diagrams and 500+ test scenarios.",
            "Improved stakeholder alignment score by 30% through "
            "structured communication frameworks.",
            "Recognized as top BA contributor for reducing development "
            "rework by 50% across the product org.",
        ],
        previous_title="Associate Business Analyst",
        coursework="Business Analysis, Project Management, Database Systems, "
                   "Software Engineering, Communication Skills",
    ),

    # ── Software Engineer ──────────────────────────────────────────────
    _role(
        "software_engineer",
        "Software Engineer",
        "Software Engineer with 4+ years of experience designing and building "
        "scalable web applications, RESTful APIs, and microservices using "
        "Python (FastAPI, Django) and Node.js (Express). Proven ability to "
        "deliver high-performance backend systems handling 10K+ RPM, implement "
        "CI/CD pipelines, and collaborate effectively in Agile teams to ship "
        "production-grade features on schedule.",
        {
            "Languages": [
                "Python", "JavaScript", "TypeScript", "SQL", "Bash",
            ],
            "Backend Frameworks": [
                "FastAPI", "Django", "Django REST Framework",
                "Node.js", "Express.js",
            ],
            "Frontend": [
                "React", "Next.js", "HTML", "CSS", "Tailwind CSS",
            ],
            "Databases & Caching": [
                "PostgreSQL", "MongoDB", "Redis", "SQLite",
            ],
            "DevOps & Cloud": [
                "Docker", "AWS (EC2, S3, Lambda)", "Nginx",
                "GitHub Actions", "CI/CD", "Linux",
            ],
            "Concepts & Tools": [
                "REST APIs", "GraphQL", "System Design",
                "Data Structures", "Algorithms", "Git",
                "Agile/Scrum", "OOP", "Design Patterns",
            ],
        },
        [
            {
                "name": "AI SaaS Platform -- LLM Chat & RAG Document Intelligence",
                "stack": "FastAPI, LangChain, OpenAI GPT-4, ChromaDB, Next.js 14, PostgreSQL, Stripe, AWS, Docker",
                "bullets": [
                    "Built multi-tenant SaaS platform where businesses upload "
                    "documents and query them via a streaming AI chatbot -- RAG "
                    "pipeline using ChromaDB for vector search and GPT-4 for "
                    "context-aware answers with <2s response time.",
                    "Implemented Stripe subscription tiers, RBAC, usage metering, "
                    "and real-time token streaming -- onboarded 500+ paying users "
                    "at 98% satisfaction rate with zero infrastructure incidents "
                    "in 3 months of production.",
                ],
            },
            {
                "name": "Multi-Vendor E-Commerce SaaS Marketplace",
                "stack": "Django, Next.js, PostgreSQL, Celery, Redis, AWS S3, Stripe, Docker",
                "bullets": [
                    "Delivered full multi-vendor marketplace -- product catalog, "
                    "order management, vendor dashboard, Stripe payment processing, "
                    "and admin moderation -- serving 5,000+ daily active users.",
                    "Optimized PostgreSQL with selective indexing and prefetch "
                    "strategies, reducing average API response time by 60% and "
                    "database CPU by 40%; Celery handled async order processing "
                    "at 99.8% success rate.",
                ],
            },
            {
                "name": "High-Scale Microservices Notification Engine",
                "stack": "Node.js, Express, MongoDB, RabbitMQ, Docker, Swagger",
                "bullets": [
                    "Designed multi-channel notification service (email, SMS, push) "
                    "with template engine, exponential retry logic, and real-time "
                    "delivery tracking -- processing 50,000+ notifications/day at "
                    "99.7% delivery rate.",
                    "90%+ test coverage, full Swagger API docs, and Docker dev "
                    "environment -- reduced engineer onboarding time by 50%.",
                ],
            },
        ],
        [
            {
                "bullets": [
                    "Designed and built RESTful APIs and microservices using "
                    "FastAPI, Django, and Node.js, serving 10K+ RPM across "
                    "3 production applications with 99.5% uptime.",
                    "Led migration of monolithic Django application to FastAPI "
                    "microservices, improving response times by 55% and enabling "
                    "independent deployment of 6 services.",
                    "Established CI/CD pipelines with GitHub Actions, Docker "
                    "containerization, and automated testing, reducing deployment "
                    "time from 2 hours to 15 minutes.",
                ],
            },
            {
                "bullets": [
                    "Developed backend features using Django and Express.js "
                    "including user authentication, payment flows, and CRUD APIs "
                    "across 2 product lines.",
                    "Wrote unit and integration tests achieving 85%+ code coverage, "
                    "performed code reviews, and contributed to technical "
                    "documentation improving team onboarding efficiency by 30%.",
                ],
            },
        ],
        [
            "Python backend (FastAPI, Django)", "Node.js/Express",
            "REST API design", "database optimization",
            "system design", "Docker & deployment",
            "data structures & algorithms", "testing",
        ],
        [],
        [
            "Delivered 8+ production backend services from design to deployment "
            "serving 50K+ users across FastAPI, Django, and Node.js stacks.",
            "Solved 500+ DSA problems on LeetCode and HackerRank.",
            "Mentored 4 junior developers on API design patterns, code review "
            "best practices, and backend architecture.",
        ],
        previous_title="Junior Software Engineer",
        coursework="Data Structures, Algorithms, Operating Systems, "
                   "Database Systems, Computer Networks, Software Engineering",
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
        f"{title} with 4+ years of hands-on experience building production "
        f"systems, collaborating with cross-functional teams, and delivering "
        f"measurable improvements using modern industry tools and Agile "
        f"methodology.",
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
                    f"Architected and delivered a production-grade "
                    f"{project_description}, serving 1,000+ active users "
                    f"with 99.5% uptime and comprehensive test coverage.",
                    f"Implemented CI/CD pipelines, automated testing, and "
                    f"monitoring, reducing deployment time by 60% and "
                    f"post-release defects by 40%.",
                ],
            },
            {
                "name": "AI SaaS Platform -- LLM Chat & RAG Document Intelligence",
                "stack": "FastAPI, LangChain, OpenAI GPT-4, ChromaDB, Next.js 14, PostgreSQL, Stripe, AWS, Docker",
                "bullets": [
                    "Built multi-tenant SaaS with AI chatbot and RAG document "
                    "search -- onboarded 500+ paying users at 98% satisfaction "
                    "rate with <2s response time.",
                    "Implemented Stripe subscriptions, RBAC, and real-time "
                    "token streaming with zero infrastructure incidents in "
                    "3 months of production.",
                ],
            },
            {
                "name": "Multi-Vendor E-Commerce SaaS Marketplace",
                "stack": "Django, Next.js, PostgreSQL, Celery, Redis, AWS S3, Stripe, Docker",
                "bullets": [
                    "Delivered full multi-vendor marketplace serving 5,000+ "
                    "daily active users -- product catalog, order management, "
                    "vendor dashboard, and Stripe payment processing.",
                    "Optimized PostgreSQL reducing API response time by 60%; "
                    "Celery pipeline handled async processing at 99.8% "
                    "success rate.",
                ],
            },
        ],
        [
            {
                "bullets": [
                    f"Led end-to-end {title.lower()} projects using modern "
                    f"tools, delivering measurable quality improvements and "
                    f"30%+ efficiency gains across key workflows.",
                    "Collaborated with cross-functional stakeholders to gather "
                    "requirements, define deliverables, and execute projects "
                    "following Agile/Scrum methodology.",
                    "Mentored junior team members on best practices, code "
                    "reviews, and technical documentation standards.",
                ],
            },
            {
                "bullets": [
                    f"Supported {title.lower()} workflows including task "
                    f"execution, quality assurance, reporting, and client "
                    f"deliverable preparation.",
                    "Built reusable templates and automated repetitive "
                    "processes, reducing manual effort by 30% and improving "
                    "team productivity.",
                ],
            },
        ],
        skills[:8],
        [],
        [
            f"Delivered 5+ production projects with documented business "
            f"impact and stakeholder sign-off.",
            "Received team recognition for process improvements saving "
            "10+ hours/week in manual effort.",
        ],
        previous_title=f"Junior {title}",
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
    pdf.multi_cell(w=0, h=4, text=template["summary"])
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

    company_1_name = profile.get("company_1_name") or "Current Company"
    company_1_loc = profile.get("company_1_location") or ""
    company_1_dur = profile.get("company_1_duration") or "Jan 2024 -- Present"
    company_2_name = profile.get("company_2_name") or "Previous Company"
    company_2_loc = profile.get("company_2_location") or ""
    company_2_dur = profile.get("company_2_duration") or "Jan 2022 -- Dec 2022"

    exp_entries = template["experience"]

    # Current company
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(w=0, h=5, text=template["title"])
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(w=0, h=5, text=company_1_dur,
             align="R", new_x="LMARGIN", new_y="NEXT")
    company_1_line = ", ".join(p for p in [company_1_name, company_1_loc] if p)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(w=0, h=4, text=company_1_line,
             new_x="LMARGIN", new_y="NEXT")
    if len(exp_entries) > 0:
        for b in exp_entries[0].get("bullets", []):
            pdf.bullet(b)
    pdf.ln(1)

    # Previous company
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(30, 30, 30)
    prev_title = template.get("previous_title", f"Junior {template['title']}")
    pdf.cell(w=0, h=5, text=prev_title)
    pdf.set_font("Helvetica", "I", 8.5)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(w=0, h=5, text=company_2_dur,
             align="R", new_x="LMARGIN", new_y="NEXT")
    company_2_line = ", ".join(p for p in [company_2_name, company_2_loc] if p)
    pdf.set_font("Helvetica", "", 8.5)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(w=0, h=4, text=company_2_line,
             new_x="LMARGIN", new_y="NEXT")
    if len(exp_entries) > 1:
        for b in exp_entries[1].get("bullets", []):
            pdf.bullet(b)
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
    cw = template.get("coursework",
                      "Data Structures, Algorithms, Databases, "
                      "Statistics, Software Engineering")
    pdf.cell(
        w=0, h=4,
        text=f"Relevant coursework: {cw}",
        new_x="LMARGIN", new_y="NEXT",
    )
    pdf.ln(1)

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

    # Company details from profile
    c1_name = _latex_escape(basics.get("company_1_name") or "Current Company")
    c1_loc = _latex_escape(basics.get("company_1_location") or "")
    c1_dur = _latex_escape(basics.get("company_1_duration") or "Jan 2024 -- Present")
    c2_name = _latex_escape(basics.get("company_2_name") or "Previous Company")
    c2_loc = _latex_escape(basics.get("company_2_location") or "")
    c2_dur = _latex_escape(basics.get("company_2_duration") or "Jan 2022 -- Dec 2022")
    prev_title = _latex_escape(
        template.get("previous_title", f"Junior {template['title']}")
    )
    coursework_text = _latex_escape(
        template.get("coursework",
                     "Data Structures, Algorithms, Databases, "
                     "Statistics, Software Engineering")
    )

    c1_line = f"{c1_name}, {c1_loc}" if c1_loc else c1_name
    c2_line = f"{c2_name}, {c2_loc}" if c2_loc else c2_name

    exp_entries = template["experience"]
    exp1_bullets = _tex_items(exp_entries[0]["bullets"]) if exp_entries else ""
    exp2_bullets = (_tex_items(exp_entries[1]["bullets"])
                    if len(exp_entries) > 1 else "")

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
        {summary}
        \end{{rSection}}

        \begin{{rSection}}{{Core Skills}}
        \begin{{tabularx}}{{\textwidth}}{{@{{}} >{{\bfseries}}l @{{\hspace{{2ex}}}} X @{{}}}}
        {_tex_skill_rows(template["skills"])}
        \end{{tabularx}}
        \end{{rSection}}

        \begin{{rSection}}{{Professional Experience}}
        \textbf{{{title}}} \hfill {{\em {c1_dur}}}\\
        {c1_line}
        \begin{{itemize}}
        {exp1_bullets}
        \end{{itemize}}

        \vspace{{4pt}}
        \textbf{{{prev_title}}} \hfill {{\em {c2_dur}}}\\
        {c2_line}
        \begin{{itemize}}
        {exp2_bullets}
        \end{{itemize}}
        \end{{rSection}}

        \begin{{rSection}}{{Key Projects}}
        {_tex_projects(template["projects"])}
        \end{{rSection}}

        \begin{{rSection}}{{Education}}
        \textbf{{{education}}} \hfill {grad_year}\\
        Relevant coursework: {coursework_text}
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
