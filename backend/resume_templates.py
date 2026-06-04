from pathlib import Path
from textwrap import dedent


def role(key, title, summary, skills, projects, experience, focus, certifications, achievements):
    return {
        "key": key,
        "title": title,
        "summary": summary,
        "skills": skills,
        "projects": projects,
        "experience": experience,
        "focus": focus,
        "certifications": certifications,
        "achievements": achievements,
    }


ROLE_TEMPLATES = [
    role(
        "ai_ml_engineer",
        "AI/ML Engineer",
        "AI/ML Engineer skilled in building production-ready machine learning systems, LLM applications, evaluation pipelines, and cloud-deployed inference APIs with measurable business impact.",
        {
            "Programming": ["Python", "SQL", "Bash", "OOP", "Data Structures"],
            "Machine Learning": ["PyTorch", "TensorFlow", "Scikit-learn", "XGBoost", "Feature Engineering", "Model Evaluation"],
            "AI/NLP": ["Transformers", "HuggingFace", "LangChain", "RAG", "FAISS", "Prompt Engineering"],
            "MLOps": ["MLflow", "Docker", "FastAPI", "AWS", "CI/CD", "Model Monitoring"],
            "Tools": ["Git", "Postman", "Jupyter", "Linux", "Pandas", "NumPy"],
        },
        [
            {
                "name": "AI Resume Screening & Job Match System",
                "stack": "Python, HuggingFace, FAISS, FastAPI, React",
                "bullets": [
                    "Built an ATS-style ranking engine that compares resumes with job descriptions using embeddings, keyword coverage, and experience scoring.",
                    "Added explainable match reports showing missing skills, project gaps, and role-specific improvement suggestions for candidates.",
                ],
            },
            {
                "name": "RAG Knowledge Assistant",
                "stack": "LangChain, OpenAI-compatible APIs, FAISS, Streamlit",
                "bullets": [
                    "Developed a document question-answering assistant with chunking, vector search, citation display, and guardrails for low-confidence answers.",
                    "Evaluated retrieval quality using precision-style checks and improved answer relevance through metadata filters.",
                ],
            },
            {
                "name": "Customer Churn Prediction API",
                "stack": "Scikit-learn, MLflow, FastAPI, Docker, AWS",
                "bullets": [
                    "Trained classification models with feature importance analysis, threshold tuning, and recall-focused evaluation for retention teams.",
                    "Packaged the model as a REST API with versioned artifacts and automated smoke tests for deployment readiness.",
                ],
            },
        ],
        [
            "Built ML pipelines covering data preprocessing, training, validation, deployment, and inference monitoring.",
            "Converted business problems into measurable ML tasks with clear metrics such as F1 score, recall, latency, and drift.",
            "Collaborated with product and engineering teams to integrate models into usable APIs and dashboards.",
        ],
        ["Python ML stack", "LLM/RAG projects", "model evaluation", "deployment API", "MLOps", "business metric impact"],
        ["Machine Learning Specialization", "Deep Learning with PyTorch", "AWS Cloud Practitioner"],
        ["Completed 3 end-to-end AI projects with deployment-ready APIs.", "Solved 300+ DSA and Python problems for interview readiness."],
    ),
    role(
        "data_engineer",
        "Data Engineer",
        "Data Engineer experienced in scalable ETL/ELT pipelines, warehouse modeling, orchestration, data quality checks, and analytics-ready datasets for business users.",
        {
            "Programming": ["Python", "SQL", "PySpark", "Bash"],
            "Data Engineering": ["ETL", "ELT", "Airflow", "dbt", "Kafka", "Data Modeling", "Data Quality"],
            "Warehouses": ["Snowflake", "BigQuery", "Redshift", "PostgreSQL"],
            "Cloud": ["AWS S3", "AWS Glue", "Lambda", "Docker", "CI/CD"],
            "Tools": ["Git", "Linux", "Great Expectations", "Power BI", "Tableau"],
        },
        [
            {
                "name": "Customer 360 Data Platform",
                "stack": "PySpark, Airflow, dbt, Snowflake, AWS S3",
                "bullets": [
                    "Designed batch pipelines to combine CRM, payments, product events, and support tickets into curated dimensional marts.",
                    "Added freshness, null, duplicate, and schema checks to improve trust in executive dashboards.",
                ],
            },
            {
                "name": "Real-Time Sales Event Pipeline",
                "stack": "Kafka, Python, PostgreSQL, Docker",
                "bullets": [
                    "Built streaming ingestion for order and payment events with retry handling, dead-letter logging, and monitoring metrics.",
                    "Reduced manual reporting effort by making near-real-time sales KPIs available to BI consumers.",
                ],
            },
            {
                "name": "Modern Data Warehouse with dbt",
                "stack": "dbt, BigQuery, SQL, GitHub Actions",
                "bullets": [
                    "Created staging, intermediate, and mart layers with tests, documentation, lineage, and reusable macros.",
                    "Automated dbt runs in CI/CD to catch broken models before production refreshes.",
                ],
            },
        ],
        [
            "Developed ETL workflows with orchestration, partitioning, incremental loads, and warehouse optimization.",
            "Translated reporting requirements into source-to-target mappings and reusable data models.",
            "Partnered with analysts to improve KPI definitions, dashboard reliability, and data availability.",
        ],
        ["SQL depth", "Airflow", "Spark", "warehouse modeling", "data quality", "cloud storage", "dbt"],
        ["Databricks Lakehouse Fundamentals", "dbt Fundamentals", "AWS Data Analytics Fundamentals"],
        ["Built reusable SQL models and data quality checks for analytics workflows.", "Documented lineage and ownership for critical reporting tables."],
    ),
    role(
        "data_scientist",
        "Data Scientist",
        "Data Scientist skilled in statistical analysis, predictive modeling, experimentation, and converting complex data into practical business recommendations.",
        {
            "Programming": ["Python", "R", "SQL"],
            "Data Science": ["Pandas", "NumPy", "Scikit-learn", "XGBoost", "Statsmodels", "Feature Engineering"],
            "Statistics": ["Hypothesis Testing", "A/B Testing", "Regression", "Classification", "Time Series"],
            "Visualization": ["Tableau", "Power BI", "Matplotlib", "Seaborn"],
            "Tools": ["Jupyter", "Git", "Excel", "MLflow", "BigQuery"],
        },
        [
            {
                "name": "Revenue Churn Prediction Model",
                "stack": "Python, Scikit-learn, XGBoost, SHAP",
                "bullets": [
                    "Built classification models to identify customers at churn risk using usage, payment, and support interaction features.",
                    "Explained model output using SHAP and recommended retention actions by customer segment.",
                ],
            },
            {
                "name": "A/B Testing Analytics Framework",
                "stack": "SQL, Python, Statsmodels, Power BI",
                "bullets": [
                    "Designed experiment metrics, sample-size assumptions, and statistical tests for pricing and onboarding changes.",
                    "Created dashboards showing lift, confidence intervals, segment performance, and decision recommendations.",
                ],
            },
            {
                "name": "Demand Forecasting System",
                "stack": "Python, Prophet, ARIMA, Pandas",
                "bullets": [
                    "Forecasted weekly product demand with seasonality, holiday effects, and error tracking across categories.",
                    "Improved planning decisions by comparing baseline, statistical, and ML forecasting approaches.",
                ],
            },
        ],
        [
            "Performed exploratory analysis, feature engineering, model training, validation, and stakeholder-ready storytelling.",
            "Defined success metrics and evaluated models against business outcomes, not only technical scores.",
            "Created dashboards and notebooks that made insights easy for non-technical teams to use.",
        ],
        ["statistics", "SQL", "business impact", "experimentation", "model interpretation", "dashboard storytelling"],
        ["Google Advanced Data Analytics", "Applied Data Science with Python", "Statistics for Data Science"],
        ["Delivered end-to-end analysis projects covering data cleaning, modeling, and recommendations.", "Built reusable notebooks for EDA, model comparison, and reporting."],
    ),
    role(
        "data_analyst_bi",
        "Data Analyst / BI Analyst",
        "Data Analyst and BI professional focused on SQL analysis, KPI reporting, dashboard design, and actionable insights for business teams.",
        {
            "Analytics": ["SQL", "Excel", "Power BI", "Tableau", "Looker"],
            "BI": ["DAX", "Power Query", "Data Modeling", "KPI Design", "Dashboard UX"],
            "Data": ["Data Cleaning", "Joins", "Window Functions", "CTEs", "Cohort Analysis"],
            "Business": ["Stakeholder Reporting", "Root Cause Analysis", "Funnel Analysis", "Presentation"],
            "Tools": ["Python", "Pandas", "Google Sheets", "GA4", "Jira"],
        },
        [
            {
                "name": "Executive Revenue Dashboard",
                "stack": "Power BI, SQL, DAX",
                "bullets": [
                    "Created a leadership dashboard tracking revenue, churn, renewal, pipeline, and region-wise performance metrics.",
                    "Built DAX measures and drill-through views to help teams diagnose metric changes quickly.",
                ],
            },
            {
                "name": "Sales Funnel Conversion Analysis",
                "stack": "SQL, Excel, Tableau",
                "bullets": [
                    "Analyzed lead source, stage conversion, sales cycle length, and win-rate trends using SQL and visual reports.",
                    "Recommended lead-quality changes that improved prioritization for sales follow-ups.",
                ],
            },
            {
                "name": "Customer Support SLA Report",
                "stack": "SQL, Power Query, Power BI",
                "bullets": [
                    "Built weekly SLA, backlog, aging, and agent productivity reporting with automated refreshes.",
                    "Reduced manual spreadsheet preparation by standardizing ticket-level data transformations.",
                ],
            },
        ],
        [
            "Built dashboards, recurring reports, and ad hoc analyses for business stakeholders.",
            "Used SQL to clean, join, and aggregate datasets from product, sales, and operations systems.",
            "Translated ambiguous questions into measurable KPIs and clear recommendations.",
        ],
        ["advanced SQL", "Power BI/Tableau", "KPI definitions", "business storytelling", "Excel", "dashboard quality"],
        ["Microsoft Power BI Data Analyst", "Google Data Analytics", "SQL for Data Analysis"],
        ["Created dashboards with automated refresh and stakeholder-ready summaries.", "Improved reporting consistency by documenting KPI definitions."],
    ),
    role(
        "business_analyst",
        "Business Analyst",
        "Business Analyst experienced in requirement gathering, process mapping, user stories, UAT coordination, and KPI-backed recommendations.",
        {
            "Analysis": ["Requirement Gathering", "Process Mapping", "Gap Analysis", "Root Cause Analysis"],
            "Documentation": ["BRD", "FRD", "User Stories", "Acceptance Criteria", "SOPs"],
            "Data": ["SQL", "Excel", "Power BI", "KPI Reporting"],
            "Delivery": ["Jira", "Agile", "Scrum", "UAT", "Stakeholder Management"],
            "Tools": ["Figma", "Miro", "Confluence", "Lucidchart", "Postman"],
        },
        [
            {
                "name": "Loan Origination Workflow Optimization",
                "stack": "BPMN, Jira, SQL, Power BI",
                "bullets": [
                    "Mapped current-state and future-state workflows for application intake, verification, approval, and disbursal.",
                    "Defined user stories and acceptance criteria that reduced rework during development handoff.",
                ],
            },
            {
                "name": "Customer Support Process Analytics",
                "stack": "SQL, Excel, Power BI",
                "bullets": [
                    "Analyzed ticket aging, escalation reasons, and SLA breaches to identify process bottlenecks.",
                    "Built KPI dashboards and recommended queue-routing changes for faster resolution.",
                ],
            },
            {
                "name": "E-commerce Checkout Requirement Pack",
                "stack": "Figma, Jira, Confluence",
                "bullets": [
                    "Documented checkout, payment, coupon, refund, and order-status requirements with edge cases.",
                    "Coordinated UAT scenarios and tracked defects through closure before release.",
                ],
            },
        ],
        [
            "Converted stakeholder needs into clear requirements, user stories, workflows, and acceptance criteria.",
            "Supported UAT, release readiness, defect triage, and business impact reporting.",
            "Used data analysis to validate process improvements and prioritize product changes.",
        ],
        ["BRD/FRD", "user stories", "UAT", "SQL reporting", "process mapping", "communication"],
        ["IIBA ECBA Preparation", "Agile Business Analysis", "Power BI for Business Users"],
        ["Created complete requirement packs with workflow diagrams and test scenarios.", "Improved stakeholder alignment through structured meeting notes and decision logs."],
    ),
]


EXTRA_ROLE_SPECS = [
    ("full_stack_developer", "Full-Stack Software Developer", "React, Next.js, Node.js, Express, PostgreSQL, MongoDB, TypeScript, REST APIs, JWT, Docker", "JobConnect Professional Networking Platform", "MERN Stack, Cloudinary, JWT, Tailwind CSS", "multi-role job portal with auth, profiles, job posts, search, saved jobs, and admin moderation"),
    ("backend_engineer", "Back-end Developer", "Python, FastAPI, Django, Node.js, PostgreSQL, Redis, REST, GraphQL, Docker, System Design", "Scalable Notification Service", "FastAPI, Redis Queue, PostgreSQL, Docker", "queue-backed email and SMS service with retries, templates, delivery logs, and rate limiting"),
    ("frontend_engineer", "Front-end Developer", "React, Next.js, TypeScript, JavaScript, HTML, CSS, Redux, Accessibility, Testing Library, Figma", "Analytics Workspace UI", "React, Next.js, TypeScript, Chart.js", "responsive dashboard with filters, saved views, accessible tables, and loading/error states"),
    ("ui_ux_engineer", "UI/UX Engineer", "Figma, React, HTML, CSS, Design Systems, Wireframing, Prototyping, Usability Testing, Accessibility", "Checkout Experience Redesign", "Figma, React, Usability Testing", "mobile-first checkout flow with prototypes, design tokens, and implemented UI components"),
    ("cloud_devops_engineer", "Cloud & DevOps Engineer", "AWS, Docker, Kubernetes, Terraform, Jenkins, GitHub Actions, Linux, Prometheus, Grafana, Nginx", "Kubernetes Microservices Deployment", "AWS EKS, Terraform, Docker, GitHub Actions", "containerized app platform with autoscaling, secrets, ingress, monitoring, and rollback workflows"),
    ("cybersecurity_analyst", "Cybersecurity Analyst", "SIEM, Splunk, Network Security, Vulnerability Assessment, Incident Response, Linux, Python, OWASP, IAM", "SOC Alert Triage Playbook", "Splunk, Python, MITRE ATT&CK", "incident triage workflows for phishing, brute force, malware, and suspicious login alerts"),
    ("mobile_app_developer", "Mobile App Developer", "Flutter, React Native, Kotlin, Swift, Dart, Firebase, REST APIs, State Management, Push Notifications", "Field Service Mobile App", "Flutter, Firebase, REST APIs", "cross-platform app for job assignment, GPS check-ins, image upload, offline sync, and notifications"),
    ("web_developer", "Web Developer", "HTML, CSS, JavaScript, React, WordPress, PHP, SEO Basics, Responsive Design, Git, Web Performance", "Local Business Website Suite", "React, WordPress, GA4, Search Console", "responsive service website with landing pages, forms, schema markup, and optimized Core Web Vitals"),
    ("software_tester_qa", "Software Tester (QA)", "Manual Testing, Selenium, Playwright, Postman, API Testing, Jira, Test Cases, Regression Testing, SQL", "E-commerce Regression Automation", "Playwright, Postman, SQL, Jira", "test suite covering login, search, cart, checkout, payments, refunds, and order tracking"),
    ("graphic_designer", "Graphic Designer", "Photoshop, Illustrator, InDesign, Figma, Branding, Typography, Social Media Design, Print Design, Layout", "Startup Brand Identity Kit", "Illustrator, Photoshop, Figma", "logo system, typography, color palette, pitch deck graphics, and social media templates"),
    ("video_editor", "Video Editor", "Premiere Pro, After Effects, DaVinci Resolve, Color Grading, Audio Cleanup, Motion Graphics, Storyboarding", "Product Demo Video Series", "Premiere Pro, After Effects, Audition", "short-form and long-form demo videos with captions, motion callouts, and clean audio"),
    ("seo_specialist", "SEO Specialist", "Keyword Research, Google Search Console, GA4, Ahrefs, SEMrush, Technical SEO, On-page SEO, Schema", "Technical SEO Growth Audit", "Screaming Frog, GA4, Search Console, Ahrefs", "crawl audit, metadata fixes, schema recommendations, internal linking, and keyword opportunity map"),
    ("applications_engineer", "Applications Engineer", "SQL, Python, APIs, Troubleshooting, SaaS Configuration, Linux, Documentation, UAT, Integration Testing", "Client API Integration Rollout", "REST APIs, SQL, Postman, Python", "configured customer integrations, validated mappings, and supported go-live troubleshooting"),
    ("systems_developer", "Systems Developer", "Python, C++, Linux, Shell Scripting, Networking, Databases, APIs, Automation, Git, Debugging", "Log Processing & Health Check Utility", "Python, Bash, Linux, PostgreSQL", "CLI automation for log parsing, error detection, environment checks, and report export"),
    ("software_engineer", "Software Engineer", "Java, Python, JavaScript, SQL, Data Structures, REST APIs, Testing, Git, System Design, Agile", "Task Management Platform", "Java, Spring Boot, React, PostgreSQL", "task assignment, comments, notifications, audit history, and role-based access control"),
    ("ux_writer", "UX Writer", "UX Writing, Microcopy, Content Design, Figma, User Research, Information Architecture, A/B Testing, Accessibility", "Onboarding Copy System", "Figma, Maze, Content Guidelines", "clear sign-up, setup, empty state, error, and success messages for SaaS onboarding"),
    ("ux_researcher", "UX Researcher", "User Interviews, Usability Testing, Survey Design, Journey Mapping, Research Synthesis, Analytics, Persona Creation", "Checkout Usability Research Study", "User Interviews, Maze, FigJam", "moderated research, journey map, pain-point synthesis, and prioritized recommendations"),
    ("ui_designer", "User Interface (UI) Designer", "Figma, Visual Design, Typography, Color Systems, Component Design, Prototyping, Design QA, Accessibility", "SaaS Dashboard UI Redesign", "Figma, Design Tokens, Auto Layout", "high-density dashboard screens, table states, filter patterns, and component specifications"),
    ("ux_designer", "UX Designer", "Figma, Wireframing, Prototyping, User Flows, Journey Mapping, Usability Testing, Information Architecture", "Self-Service Support Portal", "Figma, FigJam, Usability Testing", "knowledge search, ticket creation, status tracking, and feedback flow redesign"),
    ("product_designer", "Product Designer", "Product Strategy, Figma, User Research, Wireframing, Prototyping, Design Systems, Analytics, A/B Testing", "Subscription Upgrade Flow", "Figma, Analytics, A/B Testing", "plan comparison, upgrade prompts, payment flow, and experiment-ready design variants"),
    ("account_manager", "Account Manager", "Client Management, CRM, Renewals, Upselling, Presentation, Negotiation, Account Planning, Reporting", "Renewal Risk Program", "HubSpot, Excel, Power BI", "account health model with usage, support, renewal date, and expansion opportunity tracking"),
    ("business_development_associate", "Business Development Associate", "Lead Generation, Cold Outreach, CRM, LinkedIn Sales Navigator, Email Campaigns, Discovery Calls", "Outbound Prospecting Campaign", "HubSpot, LinkedIn Sales Navigator, Apollo", "target account list, outreach sequences, qualification notes, and sales handoff process"),
    ("business_development_manager", "Business Development Manager", "Partnerships, Enterprise Sales, Pipeline Management, CRM, Negotiation, Market Expansion, Forecasting", "Channel Partner Growth Program", "CRM, Excel, Proposal Decks", "partner tiers, onboarding process, sales collateral, and co-selling pipeline structure"),
    ("sales_representative", "Sales Representative", "Prospecting, CRM, Cold Calling, Product Demos, Negotiation, Follow-ups, Lead Qualification, Objection Handling", "Demo Conversion Improvement Plan", "CRM, Excel, Email Sequencing", "follow-up cadence, objection script, demo notes, and opportunity tracking dashboard"),
]


def build_extra_role(key, title, skill_text, project_name, stack, project_description):
    skills = [item.strip() for item in skill_text.split(",")]
    return role(
        key,
        title,
        f"{title} with practical experience in building job-ready projects, collaborating with stakeholders, and delivering measurable improvements using modern industry tools.",
        {
            "Core": skills[:5],
            "Technical": skills[5:10],
            "Delivery": ["Agile", "Documentation", "Stakeholder Communication", "Problem Solving", "Quality Review"],
            "Tools": ["Git", "Jira", "Postman", "Excel", "Analytics"],
        },
        [
            {
                "name": project_name,
                "stack": stack,
                "bullets": [
                    f"Built a portfolio-grade {project_description} aligned with common {title} job requirements.",
                    "Added measurable outcomes, documentation, test evidence, and user-focused improvements to make the project interview-ready.",
                ],
            },
            {
                "name": f"{title} Operations Dashboard",
                "stack": "SQL, Excel, Power BI, Documentation",
                "bullets": [
                    "Created KPI tracking for task progress, quality issues, delivery timelines, and stakeholder requests.",
                    "Used reporting insights to prioritize improvements and explain project impact clearly during interviews.",
                ],
            },
            {
                "name": f"{title} Process Automation Toolkit",
                "stack": "Python, APIs, Git, Documentation",
                "bullets": [
                    "Automated repetitive checks, exports, and status updates to reduce manual effort and improve consistency.",
                    "Documented setup steps, edge cases, and results so recruiters can quickly understand ownership and execution quality.",
                ],
            },
        ],
        [
            f"Delivered practical {title.lower()} tasks using modern tools, structured documentation, and measurable quality checks.",
            "Worked with cross-functional stakeholders to clarify requirements, review feedback, and improve final deliverables.",
            "Prepared demos, reports, and project notes that show business value and technical understanding.",
        ],
        skills[:8],
        [f"{title} Professional Certificate", "Agile Project Delivery", "Communication and Stakeholder Management"],
        ["Created portfolio projects mapped directly to job-description keywords.", "Prepared interview-ready case studies explaining problem, action, tools, and impact."],
    )


ROLE_TEMPLATES.extend(build_extra_role(*spec) for spec in EXTRA_ROLE_SPECS)


def list_templates():
    return [
        {
            "key": template["key"],
            "title": template["title"],
            "summary": template["summary"],
            "skills": [skill for values in template["skills"].values() for skill in values],
            "focus": template["focus"],
        }
        for template in ROLE_TEMPLATES
    ]


def get_template(key: str):
    return next((template for template in ROLE_TEMPLATES if template["key"] == key), None)


def latex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in str(value))


def normalize_link(value: str, fallback: str) -> str:
    value = (value or fallback).strip()
    return value.replace("https://", "").replace("http://", "").rstrip("/")


def tex_items(items):
    return "\n".join(rf"  \item {latex_escape(item)}" for item in items)


def tex_skill_rows(skills):
    return "\n".join(
        rf"{latex_escape(category)}: & {latex_escape(', '.join(values))} \\"
        for category, values in skills.items()
    )


def tex_projects(projects):
    blocks = []
    for project in projects:
        bullets = tex_items(project["bullets"])
        blocks.append(
            rf"""\textbf{{{latex_escape(project["name"])}}} | \textit{{{latex_escape(project["stack"])}}}
\begin{{itemize}}
{bullets}
\end{{itemize}}"""
        )
    return "\n\n".join(blocks)


def make_latex_resume(template: dict, basics: dict[str, str]) -> str:
    name = latex_escape((basics.get("name") or "YOUR NAME").upper())
    email = latex_escape(basics.get("email") or "email@example.com")
    phone = latex_escape(basics.get("phone") or "+91 00000 00000")
    location = latex_escape(basics.get("location") or "City, India")
    linkedin = normalize_link(basics.get("linkedin"), "linkedin.com/in/your-profile")
    github = normalize_link(basics.get("github"), "github.com/your-username")
    portfolio = normalize_link(basics.get("portfolio"), "yourportfolio.com")
    education = latex_escape(basics.get("education") or "B.Tech / B.Sc / BCA / MBA, Your College")
    graduation_year = latex_escape(basics.get("graduation_year") or "2026")
    title = latex_escape(template["title"])
    summary = latex_escape(template["summary"])

    return dedent(
        rf"""
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
        % {name} -- {title} Resume
        % ATS-friendly one-page role template. Replace only basic details if needed.
        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

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
        \address{{GitHub: \href{{https://{github}}}{{{latex_escape(github)}}} \quad | \quad Portfolio: \href{{https://{portfolio}}}{{{latex_escape(portfolio)}}}}}
        \address{{LinkedIn: \href{{https://{linkedin}}}{{{latex_escape(linkedin)}}} \quad | \quad Email: \href{{mailto:{email}}}{{{email}}}}}
        \address{{Location: {location} \quad | \quad Phone: {phone}}}

        \begin{{rSection}}{{Professional Summary}}
        {summary} Strong foundation in communication, ownership, documentation, and interview-ready project storytelling.
        \end{{rSection}}

        \begin{{rSection}}{{Core Skills}}
        \begin{{tabularx}}{{\textwidth}}{{@{{}} >{{\bfseries}}l @{{\hspace{{2ex}}}} X @{{}}}}
        {tex_skill_rows(template["skills"])}
        \end{{tabularx}}
        \end{{rSection}}

        \begin{{rSection}}{{Experience}}
        \textbf{{Intern -- {title}}} \hfill {{\em Jan 2025 -- Present}}\\
        SkillBridge Labs, Remote
        \begin{{itemize}}
        {tex_items(template["experience"])}
        \end{{itemize}}
        \end{{rSection}}

        \begin{{rSection}}{{Key Projects}}
        {tex_projects(template["projects"])}
        \end{{rSection}}

        \begin{{rSection}}{{Education}}
        \textbf{{{education}}} \hfill {graduation_year}\\
        Relevant coursework: Data Structures, Databases, Statistics, Software Engineering, Business Communication
        \end{{rSection}}

        \begin{{rSection}}{{Certifications}}
        \begin{{itemize}}
        {tex_items(template["certifications"])}
        \end{{itemize}}
        \end{{rSection}}

        \begin{{rSection}}{{Achievements}}
        \begin{{itemize}}
        {tex_items(template["achievements"])}
        \end{{itemize}}
        \end{{rSection}}

        \end{{document}}
        """
    ).strip()


def generate_all_resumes(output_dir: str | Path, basics: dict[str, str] | None = None):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    basics = basics or {}
    generated = []
    for template in ROLE_TEMPLATES:
        resume_path = output_path / f"{template['key']}_resume.tex"
        resume_path.write_text(make_latex_resume(template, basics), encoding="utf-8")
        generated.append(resume_path)
    return generated
