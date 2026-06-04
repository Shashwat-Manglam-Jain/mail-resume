from datetime import date
from textwrap import dedent


ROLE_TEMPLATES = [
    {
        "key": "ai_ml_engineer",
        "title": "AI/ML Engineer",
        "salary": "₹10,00,000",
        "summary": "AI/ML engineer focused on production machine learning, model evaluation, and reliable inference pipelines.",
        "skills": ["Python", "PyTorch", "TensorFlow", "scikit-learn", "NLP", "Computer Vision", "MLOps", "Docker", "FastAPI", "AWS"],
        "projects": [
            ("Resume Screening Assistant", "Built an NLP ranking system using transformer embeddings, improving recruiter shortlisting speed by 45%."),
            ("Demand Forecasting Model", "Created a time-series forecasting pipeline with automated validation and model drift checks."),
        ],
    },
    {
        "key": "data_engineer",
        "title": "Data Engineer",
        "salary": "₹10,00,000",
        "summary": "Data engineer experienced in batch pipelines, warehouse modeling, and high-quality analytics datasets.",
        "skills": ["Python", "SQL", "Spark", "Airflow", "dbt", "Kafka", "Snowflake", "BigQuery", "AWS Glue", "Data Modeling"],
        "projects": [
            ("Customer 360 Pipeline", "Designed a Spark and Airflow pipeline that unified CRM, billing, and product events into curated marts."),
            ("Streaming Metrics Platform", "Implemented Kafka ingestion and warehouse loading for near-real-time operational dashboards."),
        ],
    },
    {
        "key": "data_scientist",
        "title": "Data Scientist",
        "salary": "₹12,00,000",
        "summary": "Data scientist skilled in experimentation, predictive modeling, and business-focused statistical analysis.",
        "skills": ["Python", "R", "SQL", "Pandas", "NumPy", "scikit-learn", "Statistics", "A/B Testing", "Tableau", "Power BI"],
        "projects": [
            ("Churn Prediction Model", "Built an interpretable model that identified high-risk customers and supported retention campaigns."),
            ("Pricing Experiment Analysis", "Designed A/B test metrics and measured revenue lift with confidence intervals and segment cuts."),
        ],
    },
    {
        "key": "data_analyst_bi",
        "title": "Data Analyst / BI Analyst",
        "salary": "₹7,00,000",
        "summary": "BI analyst focused on clean dashboards, KPI definitions, and actionable business reporting.",
        "skills": ["SQL", "Excel", "Power BI", "Tableau", "Looker", "Python", "Data Cleaning", "DAX", "Dashboard Design", "Stakeholder Reporting"],
        "projects": [
            ("Executive Revenue Dashboard", "Created a Power BI dashboard tracking ARR, churn, pipeline, and renewal trends."),
            ("Sales Funnel Analysis", "Analyzed funnel conversion and recommended lead-source changes that improved MQL quality."),
        ],
    },
    {
        "key": "business_analyst",
        "title": "Business Analyst",
        "salary": "₹8,00,000",
        "summary": "Business analyst experienced in requirement gathering, process mapping, and KPI-backed recommendations.",
        "skills": ["Requirement Analysis", "SQL", "Excel", "Power BI", "User Stories", "Process Mapping", "Jira", "UAT", "Stakeholder Management", "Documentation"],
        "projects": [
            ("Loan Origination Workflow", "Mapped approval steps and reduced manual handoffs through clearer acceptance criteria."),
            ("Operations KPI Pack", "Built weekly reporting for SLA, backlog, and productivity across support teams."),
        ],
    },
    {
        "key": "full_stack_developer",
        "title": "Full-Stack Software Developer",
        "salary": "₹7,00,000",
        "summary": "Full-stack developer building responsive interfaces, robust APIs, and maintainable product workflows.",
        "skills": ["React", "Next.js", "Node.js", "Express", "Python", "FastAPI", "PostgreSQL", "REST APIs", "TypeScript", "Docker"],
        "projects": [
            ("Job Application Tracker", "Built a full-stack tracker with authentication, kanban stages, reminders, and analytics."),
            ("Invoice Automation Portal", "Created upload, approval, and payment-status modules with role-based access control."),
        ],
    },
    {
        "key": "backend_engineer",
        "title": "Back-end Developer",
        "salary": "₹8,00,000",
        "summary": "Backend engineer specializing in API design, database performance, and reliable service integrations.",
        "skills": ["Python", "FastAPI", "Django", "Node.js", "PostgreSQL", "Redis", "REST", "GraphQL", "Docker", "System Design"],
        "projects": [
            ("Notification Service", "Designed a queue-backed email and SMS service with retry handling and delivery logs."),
            ("Inventory API", "Built a secure API with caching, pagination, audit trails, and database indexing improvements."),
        ],
    },
    {
        "key": "frontend_engineer",
        "title": "Front-end Developer",
        "salary": "₹6,00,000",
        "summary": "Frontend engineer focused on accessible interfaces, reusable components, and polished user flows.",
        "skills": ["React", "Next.js", "JavaScript", "TypeScript", "HTML", "CSS", "Redux", "Accessibility", "Testing Library", "Figma"],
        "projects": [
            ("Analytics Workspace UI", "Created responsive dashboard views with filters, saved reports, and accessible charts."),
            ("Design System Components", "Built reusable inputs, tables, modals, and navigation patterns used across multiple modules."),
        ],
    },
    {
        "key": "ui_ux_engineer",
        "title": "UI/UX Engineer",
        "salary": "₹9,00,000",
        "summary": "UI/UX engineer combining interaction design, prototyping, and front-end implementation.",
        "skills": ["Figma", "React", "HTML", "CSS", "Design Systems", "Wireframing", "Prototyping", "Usability Testing", "Accessibility", "User Flows"],
        "projects": [
            ("Checkout Redesign", "Redesigned checkout flow and implemented UI changes that reduced friction across mobile screens."),
            ("Component Library", "Documented tokens, states, and responsive patterns for a shared product design system."),
        ],
    },
    {
        "key": "cloud_devops_engineer",
        "title": "Cloud & DevOps Engineer",
        "salary": "₹11,00,000",
        "summary": "DevOps engineer experienced in cloud infrastructure, CI/CD automation, and production observability.",
        "skills": ["AWS", "Azure", "Docker", "Kubernetes", "Terraform", "Jenkins", "GitHub Actions", "Linux", "Prometheus", "Grafana"],
        "projects": [
            ("CI/CD Modernization", "Built automated build, test, and deployment workflows with rollback support."),
            ("Kubernetes Migration", "Containerized services and deployed them with autoscaling, secrets, and monitoring."),
        ],
    },
    {
        "key": "cybersecurity_analyst",
        "title": "Cybersecurity Analyst",
        "salary": "₹8,00,000",
        "summary": "Cybersecurity professional focused on threat monitoring, vulnerability management, and secure operations.",
        "skills": ["SIEM", "Splunk", "Network Security", "Vulnerability Assessment", "Incident Response", "Linux", "Python", "OWASP", "IAM", "Risk Analysis"],
        "projects": [
            ("SOC Alert Triage Playbook", "Created response procedures for phishing, brute force, malware, and data exfiltration alerts."),
            ("Vulnerability Remediation Tracker", "Built prioritization dashboards for CVSS, asset criticality, and SLA aging."),
        ],
    },
    {
        "key": "mobile_app_developer",
        "title": "Mobile App Developer",
        "salary": "₹7,00,000",
        "summary": "Mobile developer building performant apps with clean architecture and reliable API integrations.",
        "skills": ["Flutter", "React Native", "Kotlin", "Swift", "Dart", "Firebase", "REST APIs", "State Management", "App Store", "Play Store"],
        "projects": [
            ("Expense Manager App", "Built cross-platform budgeting features with offline sync and category insights."),
            ("Field Service App", "Implemented job assignment, GPS check-ins, image upload, and push notifications."),
        ],
    },
    {
        "key": "web_developer",
        "title": "Web Developer",
        "salary": "₹5,00,000",
        "summary": "Web developer creating fast, responsive websites and practical CMS-driven experiences.",
        "skills": ["HTML", "CSS", "JavaScript", "React", "WordPress", "PHP", "SEO Basics", "Responsive Design", "Git", "Web Performance"],
        "projects": [
            ("Portfolio CMS Website", "Created a responsive site with reusable sections, contact forms, and optimized media."),
            ("Local Business Website", "Improved page speed, mobile usability, and on-page SEO for service pages."),
        ],
    },
    {
        "key": "software_tester_qa",
        "title": "Software Tester (QA)",
        "salary": "₹6,00,000",
        "summary": "QA tester focused on test planning, defect analysis, automation, and release confidence.",
        "skills": ["Manual Testing", "Selenium", "Playwright", "Postman", "API Testing", "Jira", "Test Cases", "Regression Testing", "SQL", "Agile"],
        "projects": [
            ("E-commerce Regression Suite", "Automated checkout, payment, search, and order-status scenarios for weekly releases."),
            ("API Test Collection", "Built Postman tests for authentication, validation errors, and response contract checks."),
        ],
    },
    {
        "key": "graphic_designer",
        "title": "Graphic Designer",
        "salary": "₹5,00,000",
        "summary": "Graphic designer creating brand assets, campaign visuals, and polished digital layouts.",
        "skills": ["Adobe Photoshop", "Illustrator", "InDesign", "Figma", "Branding", "Typography", "Social Media Design", "Print Design", "Color Theory", "Layout"],
        "projects": [
            ("Brand Identity Kit", "Designed logo options, color palette, typography rules, and social templates for a startup."),
            ("Campaign Creative Pack", "Created ad banners, email graphics, and brochure layouts for a product launch."),
        ],
    },
    {
        "key": "video_editor",
        "title": "Video Editor",
        "salary": "₹5,00,000",
        "summary": "Video editor skilled in storytelling, pacing, motion graphics, and platform-ready content delivery.",
        "skills": ["Premiere Pro", "After Effects", "DaVinci Resolve", "Color Grading", "Audio Cleanup", "Motion Graphics", "Storyboarding", "YouTube", "Reels", "Subtitles"],
        "projects": [
            ("Product Demo Series", "Edited short-form demos with motion callouts, captions, and clean audio for social channels."),
            ("Training Video Library", "Created structured learning videos with intros, overlays, and chapter-friendly cuts."),
        ],
    },
    {
        "key": "seo_specialist",
        "title": "SEO Specialist",
        "salary": "₹6,00,000",
        "summary": "SEO specialist improving organic visibility through technical audits, content strategy, and keyword research.",
        "skills": ["Keyword Research", "Google Search Console", "GA4", "Ahrefs", "SEMrush", "Technical SEO", "On-page SEO", "Content Briefs", "Schema", "Reporting"],
        "projects": [
            ("Technical SEO Audit", "Identified crawl, metadata, internal linking, and Core Web Vitals issues across a content site."),
            ("Keyword Growth Plan", "Built topic clusters and content briefs to improve rankings for commercial pages."),
        ],
    },
    {
        "key": "applications_engineer",
        "title": "Applications Engineer",
        "salary": "₹6,00,000",
        "summary": "Applications engineer supporting implementation, troubleshooting, and customer-specific product configuration.",
        "skills": ["SQL", "Python", "APIs", "Troubleshooting", "SaaS Configuration", "Customer Support", "Linux", "Documentation", "UAT", "Integration Testing"],
        "projects": [
            ("Client Integration Rollout", "Configured APIs, validated data mapping, and supported go-live issue resolution."),
            ("Support Knowledge Base", "Documented recurring implementation fixes and reduced repeat escalations."),
        ],
    },
    {
        "key": "systems_developer",
        "title": "Systems Developer",
        "salary": "₹6,00,000",
        "summary": "Systems developer building reliable internal tools, automation scripts, and platform integrations.",
        "skills": ["Python", "C++", "Linux", "Shell Scripting", "Networking", "Databases", "APIs", "Automation", "Git", "Debugging"],
        "projects": [
            ("Log Processing Utility", "Built a CLI tool to parse logs, detect errors, and export investigation reports."),
            ("Internal Automation Scripts", "Automated user provisioning, report generation, and environment health checks."),
        ],
    },
    {
        "key": "software_engineer",
        "title": "Software Engineer",
        "salary": "₹8,00,000",
        "summary": "Software engineer with experience delivering maintainable services, clean code, and product features.",
        "skills": ["Java", "Python", "JavaScript", "SQL", "Data Structures", "REST APIs", "Testing", "Git", "System Design", "Agile"],
        "projects": [
            ("Task Management Platform", "Implemented assignments, comments, notifications, and audit history for team workflows."),
            ("Search Optimization", "Improved query performance and relevance using indexing and API response tuning."),
        ],
    },
    {
        "key": "ux_writer",
        "title": "UX Writer",
        "salary": "₹10,00,000",
        "summary": "UX writer crafting clear product copy, error states, onboarding flows, and content guidelines.",
        "skills": ["UX Writing", "Microcopy", "Content Design", "Figma", "User Research", "Information Architecture", "A/B Testing", "Style Guides", "Accessibility", "Localization"],
        "projects": [
            ("Onboarding Copy Refresh", "Rewrote sign-up and setup flows to reduce confusion and improve completion."),
            ("Error Message System", "Created reusable voice, tone, and recovery patterns for product errors."),
        ],
    },
    {
        "key": "ux_researcher",
        "title": "UX Researcher",
        "salary": "₹12,00,000",
        "summary": "UX researcher using qualitative and quantitative methods to uncover user needs and product risks.",
        "skills": ["User Interviews", "Usability Testing", "Survey Design", "Journey Mapping", "Research Synthesis", "Figma", "Persona Creation", "Analytics", "A/B Testing", "Stakeholder Workshops"],
        "projects": [
            ("Checkout Usability Study", "Moderated sessions and synthesized findings that informed flow simplification."),
            ("Persona Research Sprint", "Built evidence-backed personas and opportunity maps for product planning."),
        ],
    },
    {
        "key": "ui_designer",
        "title": "User Interface (UI) Designer",
        "salary": "₹6,00,000",
        "summary": "UI designer producing clean visual systems, responsive layouts, and production-ready design specs.",
        "skills": ["Figma", "Visual Design", "Typography", "Color Systems", "Component Design", "Prototyping", "Design QA", "Responsive Layouts", "Icons", "Accessibility"],
        "projects": [
            ("SaaS Dashboard Redesign", "Designed dense table, filter, and chart layouts for operational users."),
            ("Mobile UI Kit", "Created reusable screens, controls, and states for a consumer app prototype."),
        ],
    },
    {
        "key": "ux_designer",
        "title": "UX Designer",
        "salary": "₹9,00,000",
        "summary": "UX designer creating user flows, wireframes, prototypes, and validated product experiences.",
        "skills": ["Figma", "Wireframing", "Prototyping", "User Flows", "Journey Mapping", "Usability Testing", "Design Systems", "Information Architecture", "Accessibility", "Product Thinking"],
        "projects": [
            ("Self-Service Support Portal", "Designed search, category navigation, ticket creation, and status tracking flows."),
            ("Booking Flow Prototype", "Reduced steps and clarified decision points through iterative usability testing."),
        ],
    },
    {
        "key": "product_designer",
        "title": "Product Designer",
        "salary": "₹11,00,000",
        "summary": "Product designer connecting user needs, business goals, and polished interface execution.",
        "skills": ["Product Strategy", "Figma", "User Research", "Wireframing", "Prototyping", "Design Systems", "Analytics", "A/B Testing", "Interaction Design", "Roadmapping"],
        "projects": [
            ("Subscription Upgrade Flow", "Designed experiment variants and improved upgrade clarity across plan comparison screens."),
            ("Admin Console Redesign", "Simplified navigation and key workflows for high-frequency operational tasks."),
        ],
    },
    {
        "key": "account_manager",
        "title": "Account Manager",
        "salary": "₹9,00,000",
        "summary": "Account manager focused on client relationships, renewals, adoption, and revenue growth.",
        "skills": ["Client Management", "CRM", "Renewals", "Upselling", "Presentation", "Negotiation", "Account Planning", "Stakeholder Mapping", "Reporting", "Customer Success"],
        "projects": [
            ("Renewal Risk Program", "Built account health tracking and saved at-risk renewals through proactive outreach."),
            ("Quarterly Business Review Pack", "Created usage and value reports for enterprise client meetings."),
        ],
    },
    {
        "key": "business_development_associate",
        "title": "Business Development Associate",
        "salary": "₹5,00,000",
        "summary": "Business development associate skilled in prospecting, outreach, qualification, and pipeline creation.",
        "skills": ["Lead Generation", "Cold Outreach", "CRM", "LinkedIn Sales Navigator", "Email Campaigns", "Discovery Calls", "Market Research", "Sales Reporting", "Negotiation", "Communication"],
        "projects": [
            ("Outbound Prospecting Campaign", "Built targeted prospect lists and email sequences for mid-market accounts."),
            ("Lead Qualification Playbook", "Standardized discovery questions and improved handoff quality to sales managers."),
        ],
    },
    {
        "key": "business_development_manager",
        "title": "Business Development Manager",
        "salary": "₹9,00,000",
        "summary": "Business development manager driving partnerships, strategic sales, and new-market expansion.",
        "skills": ["Partnerships", "Enterprise Sales", "Pipeline Management", "CRM", "Negotiation", "Market Expansion", "Forecasting", "Proposal Writing", "Team Leadership", "Revenue Strategy"],
        "projects": [
            ("Channel Partner Program", "Defined partner tiers, onboarding process, and co-selling motion for new regions."),
            ("Enterprise Pipeline Build", "Created account plans and proposal templates for high-value prospects."),
        ],
    },
    {
        "key": "sales_representative",
        "title": "Sales Representative",
        "salary": "₹5,00,000",
        "summary": "Sales representative experienced in prospecting, demos, follow-ups, and closing customer opportunities.",
        "skills": ["Prospecting", "CRM", "Cold Calling", "Product Demos", "Negotiation", "Follow-ups", "Lead Qualification", "Presentation", "Objection Handling", "Sales Reporting"],
        "projects": [
            ("Demo Conversion Drive", "Improved demo follow-up cadence and increased opportunity conversion."),
            ("Territory Prospect List", "Created segmented account lists and outreach scripts for regional sales activity."),
        ],
    },
]


def list_templates():
    return [
        {
            "key": template["key"],
            "title": template["title"],
            "salary": template["salary"],
            "summary": template["summary"],
            "skills": template["skills"],
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
    return "".join(replacements.get(char, char) for char in value)


def make_latex_resume(template: dict, basics: dict[str, str]) -> str:
    name = latex_escape(basics.get("name") or "YOUR NAME")
    email = latex_escape(basics.get("email") or "email@example.com")
    phone = latex_escape(basics.get("phone") or "+91 00000 00000")
    location = latex_escape(basics.get("location") or "City, India")
    linkedin = latex_escape(basics.get("linkedin") or "linkedin.com/in/your-profile")
    github = latex_escape(basics.get("github") or "github.com/your-username")
    education = latex_escape(basics.get("education") or "B.Tech / B.Sc / MBA, Your College")
    graduation_year = latex_escape(basics.get("graduation_year") or "2026")
    title = latex_escape(template["title"])
    salary = latex_escape(template["salary"])
    summary = latex_escape(template["summary"])
    skills = ", ".join(latex_escape(skill) for skill in template["skills"])
    project_items = "\n".join(
        rf"\resumeProject{{{latex_escape(project)}}}{{{latex_escape(description)}}}"
        for project, description in template["projects"]
    )

    return dedent(
        rf"""
        \documentclass[10pt,a4paper]{{article}}
        \usepackage[margin=0.65in]{{geometry}}
        \usepackage{{titlesec}}
        \usepackage{{enumitem}}
        \usepackage[hidelinks]{{hyperref}}
        \usepackage{{xcolor}}

        \definecolor{{heading}}{{HTML}}{{0F172A}}
        \definecolor{{accent}}{{HTML}}{{2563EB}}
        \pagenumbering{{gobble}}
        \setlength{{\parindent}}{{0pt}}
        \setlist[itemize]{{leftmargin=*, itemsep=2pt, topsep=2pt}}
        \titleformat{{\section}}{{\large\bfseries\color{{heading}}}}{{}}{{0em}}{{}}[\titlerule]
        \titlespacing*{{\section}}{{0pt}}{{8pt}}{{5pt}}

        \newcommand{{\resumeProject}}[2]{{\textbf{{#1}}\\[-2pt]\begin{{itemize}}\item #2\end{{itemize}}}}
        \newcommand{{\resumeRole}}[4]{{\textbf{{#1}} \hfill #2\\\textit{{#3}} \hfill \textit{{#4}}\\[-4pt]}}

        \begin{{document}}

        \begin{{center}}
            {{\LARGE \textbf{{{name}}}}}\\
            {title} \quad | \quad Expected CTC Benchmark: {salary}\\
            {email} \quad | \quad {phone} \quad | \quad {location}\\
            \href{{https://{linkedin}}}{{{linkedin}}} \quad | \quad \href{{https://{github}}}{{{github}}}
        \end{{center}}

        \section*{{Professional Summary}}
        {summary} Strong foundation in problem solving, communication, documentation, and collaborative delivery.

        \section*{{Skills}}
        {skills}

        \section*{{Projects}}
        {project_items}

        \section*{{Experience}}
        \resumeRole{{Junior {title}}}{{Jan 2025 -- Present}}{{DummyTech Solutions}}{{Remote}}
        \begin{{itemize}}
            \item Delivered role-relevant features, reports, or workflows using modern tools and measurable quality checks.
            \item Coordinated with product, design, QA, and business stakeholders to clarify scope and close implementation gaps.
            \item Documented reusable processes and improved handoff quality for future project work.
        \end{{itemize}}

        \resumeRole{{Intern - {title}}}{{Jun 2024 -- Dec 2024}}{{SkillBridge Labs}}{{Hybrid}}
        \begin{{itemize}}
            \item Supported production-style tasks, reviewed requirements, and converted feedback into practical improvements.
            \item Prepared demos, progress notes, and test evidence for mentor and stakeholder review.
        \end{{itemize}}

        \section*{{Education}}
        \textbf{{{education}}} \hfill {graduation_year}\\
        Relevant coursework: Data Structures, Databases, Statistics, Software Engineering, Business Communication

        \section*{{Certifications}}
        Role-focused certification in {title}; Cloud fundamentals; Agile project delivery

        \end{{document}}
        """
    ).strip()
