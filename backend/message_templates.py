"""
Role-specific email templates. One per role, each genuinely different
in structure, tone, and emphasis.
"""

ACTIVE_ROLE_KEYS = [
    "python_developer",
    "ai_ml_engineer",
    "data_engineer",
    "cloud_devops_engineer",
    "seo_digital_marketing",
    "software_engineer",
]

TEMPLATES = {
    "python_developer": {
        "email_subject": "{role_title} — {your_name} | {experience_years} yrs · Python, React, AWS",
        "email_body": (
            "{greeting}\n\n"
            "Came across the {role_title} opening{at_company} — looks like "
            "a good fit for what I do.\n\n"
            "I'm currently at CubexO, building systems for Spreetail "
            "(US e-commerce). Some recent work: claims automation that "
            "recovers $2M+/yr in lost revenue (PySpark into Snowflake, "
            "orchestrated with Airflow), an AI email triage system that "
            "cut response times from 4 hours to 15 min, and real-time "
            "package tracking across 50K+ monthly events. Before that, "
            "security automation at Barclays — Ansible across millions "
            "of devices.\n\n"
            "I work across Python, Django, FastAPI, React, PySpark, "
            "AWS — wherever the problem is.\n\n"
            "Resume's attached. Happy to chat if you're interested.\n\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },

    "ai_ml_engineer": {
        "email_subject": "{role_title} — {your_name} | {experience_years} yrs · LLMs, NLP, Production ML",
        "email_body": (
            "{greeting}\n\n"
            "The {role_title} role{at_company} stood out — I spend most of "
            "my time building AI systems that actually run in production, "
            "which seems like what you're looking for.\n\n"
            "The project I'm proudest of right now: an email automation "
            "system that uses NLP to classify incoming messages, extract "
            "structured data, and route them to the right team — took "
            "response times from 4 hours to 15 minutes. I also built "
            "predictive models for logistics claims that recover $2M+/yr "
            "and anomaly detection pipelines for real-time package "
            "tracking.\n\n"
            "I work with LLMs, RAG, LangChain, PyTorch, FastAPI, and "
            "deploy on AWS. Models that ship, not models that demo.\n\n"
            "Resume's attached — would love to hear more about what "
            "you're building.\n\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },

    "data_engineer": {
        "email_subject": "{role_title} — {your_name} | {experience_years} yrs · Spark, Snowflake, Airflow",
        "email_body": (
            "{greeting}\n\n"
            "Saw the {role_title} opening{at_company}. Data pipelines are "
            "what I do all day, so I wanted to reach out.\n\n"
            "Right now I'm at CubexO building for Spreetail — I own the "
            "pipeline that ingests ~50K carrier events/month into Snowflake "
            "(PySpark transforms, Airflow orchestration). That data feeds "
            "an automation layer that recovers $2M+/yr in lost claims. I "
            "also designed the SLA breach detection pipeline — it flags "
            "late shipments automatically and kicks off resolution, cutting "
            "turnaround by 60%.\n\n"
            "My daily tools: Python, PySpark, Snowflake, Airflow, Kafka, "
            "Delta Lake, dbt, AWS.\n\n"
            "Resume's attached if you'd like the full picture. Happy to "
            "jump on a call.\n\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },

    "cloud_devops_engineer": {
        "email_subject": "{role_title} — {your_name} | {experience_years} yrs · AWS, Docker, K8s, Ansible",
        "email_body": (
            "{greeting}\n\n"
            "The {role_title} role{at_company} caught my eye — infra "
            "automation at scale is exactly my thing.\n\n"
            "My biggest project: at Barclays, I built Ultron — an Ansible "
            "platform that automates security compliance across their "
            "entire network fleet (millions of devices). It handles the "
            "full cycle: access request, security assessment, remediation, "
            "config update. What used to take hours per device now runs "
            "in minutes with zero manual work.\n\n"
            "I also manage containerized deployments on AWS (ECS/EKS), "
            "write Terraform modules, and run CI/CD with GitHub Actions. "
            "Currently at CubexO deploying the data and automation "
            "infrastructure for Spreetail.\n\n"
            "Resume's attached. Let me know if you'd like to talk.\n\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },

    "seo_digital_marketing": {
        "email_subject": "{role_title} — {your_name} | {experience_years} yrs · SEO, Google Ads, Social",
        "email_body": (
            "{greeting}\n\n"
            "Noticed the {role_title} opening{at_company} — I think I "
            "bring something unusual to this kind of role.\n\n"
            "I do the usual (Google Ads, Facebook/Instagram campaigns, "
            "SEO, content strategy, GA4) — but I also write code. Python "
            "and SQL, specifically. That means I implement schema markup "
            "myself, fix technical SEO issues without filing engineering "
            "tickets, build automated reporting dashboards, and set up "
            "tracking properly the first time.\n\n"
            "I've managed ad spend with measurable ROAS, grown organic "
            "traffic through technical SEO, and built attribution models "
            "that show which channels actually drive revenue — not just "
            "clicks.\n\n"
            "Resume's attached — would love to chat about how I can "
            "help.\n\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },

    "software_engineer": {
        "email_subject": "{role_title} — {your_name} | {experience_years} yrs · Python, Django, FastAPI",
        "email_body": (
            "{greeting}\n\n"
            "Saw the {role_title} role{at_company} — it looks like a "
            "strong fit.\n\n"
            "I've spent the last {experience_years} years building "
            "production systems — the kind where reliability and ship "
            "speed both matter. At Spreetail, I built automation that "
            "recovers $2M+/yr in revenue, an AI email system that cut "
            "response times by 95%, and monitoring pipelines for 50K+ "
            "events/month. At Barclays, I automated security ops across "
            "their entire device fleet.\n\n"
            "I work in Python (Django, FastAPI), build frontends in React, "
            "and deploy on AWS with Docker. I care about code that solves "
            "real problems, not code that's clever.\n\n"
            "Resume's attached. Happy to connect if you're interested.\n\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },
}

DEFAULT_TEMPLATE = {
    "email_subject": "{role_title} — {your_name} ({experience_years} yrs exp)",
    "email_body": (
        "{greeting}\n\n"
        "Came across the {role_title} opening{at_company} and wanted "
        "to reach out. I've been building production systems with "
        "{top_skills} for {experience_years} years — automation, APIs, "
        "data pipelines, and cloud infrastructure.\n\n"
        "At my current role, I built systems recovering $2M+/yr in "
        "revenue and cut operational response times by 90%.\n\n"
        "Resume's attached. Happy to chat if you think there's a fit.\n\n"
        "{your_name}\n"
        "{your_email} | {your_phone}"
    ),
}


def get_message_template(role_key: str, channel: str = "email") -> dict:
    """Return {"subject": str, "body": str} for the given role."""
    templates = TEMPLATES.get(role_key, DEFAULT_TEMPLATE)
    return {
        "subject": templates["email_subject"],
        "body": templates["email_body"],
    }
