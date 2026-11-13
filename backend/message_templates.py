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
            "I came across the {role_title} position{at_company} and "
            "I'm very interested — it aligns well with the kind of work "
            "I've been doing and I'd love to be considered.\n\n"
            "I'm currently working at CubexO as a Python Developer, "
            "handling client projects for Spreetail (US e-commerce) and "
            "Barclays. At Spreetail, I built ETL pipelines with PySpark "
            "and Snowflake that process 50K+ events monthly, and claims "
            "automation that recovers $2M+ per year. At Barclays, I built "
            "Ultron — an Ansible platform that automates security "
            "compliance across millions of network devices.\n\n"
            "I work across the full stack — Python, Django, FastAPI, "
            "React, PySpark, AWS — and I'm actively looking for the "
            "right opportunity to grow further in my career.\n\n"
            "I've attached my resume for your reference. If you think "
            "there's a fit, I'd really appreciate the chance to discuss "
            "this further. Please let me know if we can schedule a call "
            "or interview at your convenience.\n\n"
            "Looking forward to hearing from you.\n\n"
            "Best regards,\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },

    "ai_ml_engineer": {
        "email_subject": "{role_title} — {your_name} | {experience_years} yrs · AI/ML, NLP, Python",
        "email_body": (
            "{greeting}\n\n"
            "I noticed the {role_title} opening{at_company} and wanted "
            "to express my interest — I've been building AI-powered "
            "systems in production and this role feels like a strong "
            "match for what I bring.\n\n"
            "At my current company CubexO, I work on client projects "
            "for Spreetail and Barclays. For Spreetail, I built an email "
            "automation service using NLP that classifies messages, "
            "extracts structured data, and routes them automatically — "
            "cut response times from 4 hours to 15 minutes. I also built "
            "data pipelines with PySpark and Snowflake recovering $2M+ "
            "annually. At Barclays, I automated security compliance "
            "across millions of devices with Ansible.\n\n"
            "I'm looking for a role where I can apply my AI/ML skills "
            "at a deeper level, and this position really excites me.\n\n"
            "I've attached my resume. If you have a requirement that "
            "matches my profile, I'd love the opportunity to interview. "
            "Please let me know a good time to connect.\n\n"
            "Thanks for your time.\n\n"
            "Best regards,\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },

    "data_engineer": {
        "email_subject": "{role_title} — {your_name} | {experience_years} yrs · Spark, Snowflake, Airflow",
        "email_body": (
            "{greeting}\n\n"
            "I saw the {role_title} opening{at_company} and I'm really "
            "interested in this opportunity. Data pipelines and "
            "infrastructure are exactly what I do, and I think I'd be "
            "a great fit for your team.\n\n"
            "I'm currently at CubexO working on projects for Spreetail "
            "(US e-commerce) and Barclays. At Spreetail, I built the ETL "
            "pipelines that pull carrier data from APIs, transform it in "
            "PySpark, and load into Snowflake — processing 50K+ events "
            "monthly. This powers claims automation that recovers $2M+ "
            "per year. I also built the lost-in-transit detection pipeline "
            "that cut resolution time by 60%. At Barclays, I worked on "
            "Ultron — automating security compliance across millions of "
            "devices using Ansible.\n\n"
            "I'm actively exploring new opportunities and this role "
            "is exactly what I'm looking for.\n\n"
            "My resume is attached. If my background looks like a good "
            "fit, I'd be happy to schedule a call or interview whenever "
            "works for you. I'm available at short notice.\n\n"
            "Hope to hear from you soon.\n\n"
            "Best regards,\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },

    "cloud_devops_engineer": {
        "email_subject": "{role_title} — {your_name} | {experience_years} yrs · AWS, Docker, Ansible, CI/CD",
        "email_body": (
            "{greeting}\n\n"
            "I'm writing to express my interest in the {role_title} "
            "position{at_company}. Infrastructure automation and DevOps "
            "are a big part of my current work, and I believe I can "
            "contribute meaningfully to your team.\n\n"
            "At CubexO, I handle client projects for Barclays and "
            "Spreetail. My biggest project at Barclays was building "
            "Ultron — an Ansible-based platform that automates security "
            "compliance across their entire network fleet (millions of "
            "devices). It handles access requests, security assessments, "
            "remediation, and config updates end-to-end. At Spreetail, "
            "I built data pipelines on AWS with PySpark and Snowflake "
            "processing 50K+ events monthly, with CI/CD automation "
            "using Docker and GitHub Actions.\n\n"
            "I'm keen on taking the next step in my career and this "
            "role is really appealing to me.\n\n"
            "I've attached my resume for your review. If there's a "
            "match, I'd love to set up a call or interview. Please let "
            "me know your availability and I'll work around it.\n\n"
            "Thank you for considering my application.\n\n"
            "Best regards,\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },

    "seo_digital_marketing": {
        "email_subject": "{role_title} — {your_name} | {experience_years} yrs · SEO, Google Ads, Analytics",
        "email_body": (
            "{greeting}\n\n"
            "I came across the {role_title} position{at_company} and "
            "I'm very interested. I think I bring something different "
            "to this role — along with SEO, Google Ads, and social "
            "media marketing, I also have a strong technical background "
            "in Python and web development.\n\n"
            "That means I can implement schema markup, fix technical "
            "SEO issues, build automated reporting dashboards, and set "
            "up tracking properly — all without waiting on engineering. "
            "I've grown organic traffic through technical SEO, managed "
            "paid campaigns with strong ROAS, and built attribution "
            "models that show which channels actually drive revenue.\n\n"
            "I'm actively looking for a role that combines marketing "
            "strategy with technical execution, and this seems perfect.\n\n"
            "My resume is attached. If you think there's a fit, I'd "
            "really appreciate the chance to interview. Please feel free "
            "to schedule a call at your convenience — I'm flexible with "
            "timing.\n\n"
            "Looking forward to hearing from you.\n\n"
            "Best regards,\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },

    "software_engineer": {
        "email_subject": "{role_title} — {your_name} | {experience_years} yrs · Python, Django, FastAPI",
        "email_body": (
            "{greeting}\n\n"
            "I saw the {role_title} role{at_company} and I wanted to "
            "reach out because it matches my experience really well. "
            "I'm actively looking for new opportunities and this "
            "position stood out to me.\n\n"
            "I'm currently working at CubexO as a Software Developer, "
            "building production systems for Spreetail (US e-commerce) "
            "and Barclays. At Spreetail, I built automation that "
            "recovers $2M+ per year in carrier claims, data pipelines "
            "processing 50K+ events monthly, and an email automation "
            "system that cut response times from 4 hours to 15 minutes. "
            "At Barclays, I built Ultron — automated security compliance "
            "across millions of network devices using Ansible.\n\n"
            "I work primarily in Python (Django, FastAPI), React for "
            "frontend, and deploy on AWS with Docker.\n\n"
            "I've attached my resume. If you have a suitable opening, "
            "I'd love to discuss further and schedule an interview. "
            "I'm available at your convenience.\n\n"
            "Thanks for your time.\n\n"
            "Best regards,\n"
            "{your_name}\n"
            "{your_email} | {your_phone}"
        ),
    },
}

DEFAULT_TEMPLATE = {
    "email_subject": "{role_title} — {your_name} ({experience_years} yrs exp)",
    "email_body": (
        "{greeting}\n\n"
        "I came across the {role_title} opening{at_company} and I'm "
        "interested in applying. I've been building production systems "
        "with {top_skills} for {experience_years} years.\n\n"
        "Currently at CubexO, I work on client projects for Spreetail "
        "and Barclays — built data pipelines recovering $2M+ annually "
        "and automated security compliance across millions of devices.\n\n"
        "I've attached my resume. If there's a fit, I'd really "
        "appreciate the opportunity to interview. Please let me know "
        "if we can schedule a call.\n\n"
        "Looking forward to hearing from you.\n\n"
        "Best regards,\n"
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
