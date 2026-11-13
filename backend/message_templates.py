"""
Role-specific email and LinkedIn message templates with round-robin variation.
Each role has 4-5 email body variations that cycle automatically.
"""

_variation_counter: dict[str, int] = {}

TEMPLATES = {
    "python_developer": {
        "email_subject": "{role_title} -- {your_name} ({experience_years} yrs exp)",
        "email_variations": [
            (
                "{greeting}\n\n"
                "I came across the {role_title} opening{at_company} and wanted to reach out. "
                "I'm a Python developer with {experience_years} years of experience across "
                "the full stack -- backend APIs with Django and FastAPI, frontend dashboards "
                "in React, data pipelines with PySpark and Snowflake, and infrastructure on "
                "AWS with Docker and Kubernetes.\n\n"
                "At my current role, I've built ETL pipelines processing 50K+ events monthly, "
                "automated claims workflows recovering $2M+ annually, and shipped production "
                "systems across e-commerce and fintech clients in the US and Europe.\n\n"
                "I've attached my resume with the full details. Would love to chat if you "
                "think there's a fit.\n\n"
                "Thanks,\n{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "Saw the {role_title} role{at_company} and it looks like a solid fit for "
                "what I do. I've been building Python systems for {experience_years} years "
                "-- APIs, data pipelines, React dashboards, cloud deployments. The full "
                "picture.\n\n"
                "Quick highlights: automated workflows that recover $2M+/year in lost "
                "revenue, built pipelines handling 50K+ monthly events in PySpark/Snowflake, "
                "and deployed services on AWS with Docker. Happy to share more -- resume's "
                "attached.\n\n"
                "Let me know if you'd like to hop on a quick call.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "I noticed the {role_title} position{at_company} and wanted to connect. "
                "Here's what I've delivered in {experience_years} years of building Python "
                "systems:\n\n"
                "- Built claims automation recovering $2M+ annually in previously unclaimed revenue\n"
                "- Designed data pipelines processing 50K+ package events monthly (PySpark, Snowflake, Airflow)\n"
                "- Cut email response times from 4 hours to 15 minutes with an AI-powered triage system\n"
                "- Automated security compliance across millions of network devices using Ansible\n\n"
                "I work across the stack -- Django, FastAPI, React, AWS, Docker -- and I ship "
                "production code. Resume attached with the full breakdown.\n\n"
                "Happy to chat whenever works.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "The {role_title} opening{at_company} caught my eye. I've spent "
                "{experience_years} years building production systems in Python and wanted "
                "to share my background.\n\n"
                "My stack: Python, Django, FastAPI, React.js on the application side. "
                "PySpark, Snowflake, Airflow, Kafka for data engineering. AWS, Docker, "
                "Kubernetes, Terraform for infrastructure. PostgreSQL for storage. "
                "Git, CI/CD, Linux for the day-to-day.\n\n"
                "I've used this stack to build ETL pipelines, REST APIs, real-time "
                "dashboards, and automation workflows for clients across e-commerce, "
                "healthcare, fintech, and enterprise SaaS. Resume's attached with the "
                "specifics.\n\n"
                "Would love to discuss how I can contribute to your team.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "I saw the {role_title} role{at_company} and it resonated with the kind "
                "of problems I solve. For the last {experience_years} years, I've been the "
                "person teams call when they need to turn messy manual processes into "
                "automated systems that just work.\n\n"
                "Whether it's an ops team drowning in email (built an AI triage system, "
                "cut response time from 4 hours to 15 min), packages going missing with "
                "no tracking (built real-time monitoring pipelines), or security audits "
                "taking weeks (automated with Ansible across millions of devices) -- I "
                "build the Python backend, data pipeline, or React dashboard that fixes it.\n\n"
                "Resume attached. Happy to walk through any of this in more detail.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
        ],
        "linkedin_body": (
            "Hi! I'm a Python developer ({experience_years} yrs) building APIs, "
            "data pipelines, and dashboards with Django, FastAPI, React, PySpark, "
            "and AWS. Noticed the {role_title} role{at_company} -- would love to "
            "connect and share my background."
        ),
    },

    "ai_ml_engineer": {
        "email_subject": "{role_title} -- {your_name} ({experience_years} yrs exp)",
        "email_variations": [
            (
                "{greeting}\n\n"
                "I came across the {role_title} opening{at_company} and wanted to reach "
                "out. I've been building and shipping AI/ML systems for {experience_years} "
                "years -- RAG pipelines, LLM-powered automation, classification models, "
                "and inference APIs.\n\n"
                "At my current role, I built an AI email triage system that classifies "
                "incoming messages, extracts structured data, and routes tickets "
                "automatically -- cutting response time from 4 hours to 15 minutes. I've "
                "also worked on predictive models for logistics optimization and NLP "
                "pipelines for document processing.\n\n"
                "My stack: Python, LangChain, LlamaIndex, FastAPI, PyTorch, AWS SageMaker, "
                "vector databases. I care about models that work in production, not just "
                "in notebooks. Resume attached.\n\n"
                "Would love to discuss the role if you think there's a fit.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "Saw the {role_title} role{at_company} -- it's right in my wheelhouse. "
                "I've spent {experience_years} years building AI systems that actually ship "
                "to production.\n\n"
                "Recent work: an AI-powered email automation service that parses, classifies, "
                "and routes operational emails using NLP -- took response times from 4 hours "
                "to 15 minutes. Also built predictive pipelines for claims automation "
                "(recovering $2M+/year) and real-time anomaly detection for logistics "
                "tracking.\n\n"
                "I work with LLMs, RAG pipelines, LangChain, and deploy on AWS. Resume's "
                "attached.\n\n"
                "Let me know if you'd like to chat.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "The {role_title} position{at_company} looks like a great match. I "
                "specialize in taking ML and AI concepts from prototype to production -- "
                "{experience_years} years of shipping models that handle real traffic and "
                "solve real business problems.\n\n"
                "I've built NLP systems for email classification and routing, predictive "
                "models for supply chain optimization, and RAG pipelines for document "
                "intelligence. My approach: ship fast, measure impact, iterate. The email "
                "triage system I built processes hundreds of messages daily with 95%+ "
                "classification accuracy.\n\n"
                "Tech: Python, LangChain, LlamaIndex, PyTorch, FastAPI, PostgreSQL, AWS. "
                "Resume attached.\n\n"
                "Happy to jump on a call if this aligns with what you're looking for.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "I noticed the {role_title} opening{at_company} and wanted to connect. I "
                "build AI-powered systems -- the kind where you need ML models that run "
                "reliably at scale, not just proof-of-concepts.\n\n"
                "My background ({experience_years} years): LLM integration and prompt "
                "engineering, RAG pipelines with vector databases, NLP for classification "
                "and entity extraction, predictive analytics for operational automation. "
                "I've deployed models on AWS SageMaker and built inference APIs with "
                "FastAPI.\n\n"
                "The work I'm proudest of: an AI email automation system that eliminated "
                "hours of manual triage daily. Resume has the full picture.\n\n"
                "Would love to hear more about the role.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "I saw the {role_title} role{at_company} and it caught my attention. For "
                "{experience_years} years, I've been focused on one thing: making AI useful "
                "in production.\n\n"
                "That means building RAG systems that give accurate answers (not "
                "hallucinations), NLP pipelines that handle messy real-world text, and ML "
                "models that improve operations measurably -- like the claims prediction "
                "system I built that helps recover $2M+ per year.\n\n"
                "I work across the AI/ML stack: Python, LangChain, LlamaIndex, PyTorch, "
                "vector DBs, FastAPI for serving, AWS for deployment. Resume's attached.\n\n"
                "Happy to chat about how I can help.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
        ],
        "linkedin_body": (
            "Hi! I build AI/ML systems -- RAG pipelines, LLMs, NLP -- "
            "{experience_years} yrs shipping models to production. Saw the "
            "{role_title} role{at_company}, would love to connect!"
        ),
    },

    "data_engineer": {
        "email_subject": "{role_title} -- {your_name} ({experience_years} yrs exp)",
        "email_variations": [
            (
                "{greeting}\n\n"
                "I came across the {role_title} opening{at_company} and wanted to reach "
                "out. I've been building data pipelines and warehouse architectures for "
                "{experience_years} years, primarily with PySpark, Snowflake, Airflow, "
                "and Kafka.\n\n"
                "At my current role, I built ETL pipelines that ingest 50K+ package events "
                "monthly into Snowflake, orchestrated with Airflow. The downstream "
                "automation -- claims processing, SLA monitoring, anomaly detection -- "
                "runs on this data and recovers $2M+ annually. I've also designed streaming "
                "pipelines with Kafka and batch jobs with dbt.\n\n"
                "My focus: data that's reliable, fresh, and actually usable by downstream "
                "teams. Resume attached.\n\n"
                "Would love to chat if you think there's alignment.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "The {role_title} role{at_company} looks like a strong fit. I've spent "
                "{experience_years} years making sure data gets where it needs to go -- "
                "reliably, on schedule, at scale.\n\n"
                "Quick snapshot: PySpark + Snowflake pipelines processing 50K+ events/month. "
                "Airflow orchestration across 5+ active workflows. Delta Lake for incremental "
                "loads. Kafka for real-time streaming. All deployed on AWS.\n\n"
                "I've built pipelines for e-commerce logistics, healthcare records, "
                "automotive telemetry, and financial trading -- different domains, same "
                "fundamentals. Resume's attached.\n\n"
                "Happy to hop on a call.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "I noticed the {role_title} position{at_company}. I build data pipelines "
                "and have been doing it for {experience_years} years. Here's what that "
                "looks like in practice:\n\n"
                "- Designed a lost-in-transit pipeline ingesting 50K+ events monthly into "
                "Snowflake, flagging SLA breaches automatically. Cut resolution time by 60%.\n"
                "- Built ETL workflows with PySpark and Airflow that power $2M+/year in "
                "automated claims recovery.\n"
                "- Set up real-time streaming with Kafka for operational monitoring and "
                "alerting.\n\n"
                "Stack: Python, PySpark, Snowflake, Airflow, Kafka, Delta Lake, dbt, AWS. "
                "Resume attached with the full picture.\n\n"
                "Would love to discuss the role.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "Saw the {role_title} opening{at_company} and wanted to share my "
                "background. I'm a data engineer with {experience_years} years building "
                "the infrastructure that makes data actually useful.\n\n"
                "I've designed warehouse schemas in Snowflake, written PySpark "
                "transformations for high-volume event data, orchestrated complex DAGs "
                "in Airflow, and set up Kafka streaming for real-time analytics. I also "
                "build the FastAPI services that serve this data to dashboards and "
                "downstream consumers.\n\n"
                "My pipelines process tens of thousands of events daily across logistics, "
                "healthcare, and fintech. Resume has the specifics.\n\n"
                "Let me know if you'd like to connect.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "The {role_title} role{at_company} resonated with the kind of work I do. "
                "For {experience_years} years, I've been the person who builds the data "
                "pipeline when the team says \"we need this data, but it's a mess.\"\n\n"
                "Carrier APIs with inconsistent schemas? Built PySpark transformations "
                "that normalize and validate everything before it hits Snowflake. Hundreds "
                "of daily emails that need structured data extracted? Built a parsing "
                "pipeline that classifies and routes automatically. Manual reporting that "
                "takes hours? Replaced it with Airflow-orchestrated jobs and real-time "
                "dashboards.\n\n"
                "Resume attached. Happy to walk through any of this.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
        ],
        "linkedin_body": (
            "Hi! I build data pipelines -- PySpark, Snowflake, Airflow, Kafka. "
            "{experience_years} yrs processing 50K+ events/month at scale. Saw the "
            "{role_title} role{at_company}, let's connect!"
        ),
    },

    "cloud_devops_engineer": {
        "email_subject": "{role_title} -- {your_name} ({experience_years} yrs exp)",
        "email_variations": [
            (
                "{greeting}\n\n"
                "I came across the {role_title} opening{at_company} and wanted to reach "
                "out. I've been building and automating cloud infrastructure for "
                "{experience_years} years -- AWS, Docker, Kubernetes, Terraform, and CI/CD "
                "pipelines.\n\n"
                "At Barclays, I built Ultron -- an Ansible-based automation platform that "
                "handles security compliance across millions of network devices. Full "
                "workflow: access request, assessment, remediation, config update. Cut "
                "remediation time from hours to minutes per device.\n\n"
                "I also deploy and maintain containerized services on AWS, set up Terraform "
                "for infrastructure-as-code, and build GitHub Actions pipelines for "
                "continuous deployment. Resume attached.\n\n"
                "Would love to discuss the role.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "The {role_title} role{at_company} looks like a great match. I've spent "
                "{experience_years} years automating infrastructure and deployment "
                "workflows.\n\n"
                "My background: AWS (EC2, ECS, EKS, S3, RDS, Lambda), Docker and "
                "Kubernetes for containerization, Terraform for IaC, Ansible for config "
                "management, and CI/CD with GitHub Actions and Jenkins.\n\n"
                "Highlight: built Ansible playbooks at Barclays that automated security "
                "remediation across millions of devices -- replacing a manual process "
                "that took hours per device. Resume's attached with the full picture.\n\n"
                "Happy to chat.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "I noticed the {role_title} position{at_company}. I automate the boring "
                "stuff -- deployments, compliance, scaling, monitoring -- so teams can "
                "focus on building. {experience_years} years of doing this.\n\n"
                "Results: automated security compliance across millions of devices "
                "(Ansible + Python), reducing remediation from hours to minutes. Built "
                "Docker/K8s deployment pipelines for microservices. Set up Terraform "
                "modules for reproducible AWS infrastructure. Maintained CI/CD pipelines "
                "shipping code daily.\n\n"
                "Stack: AWS, Docker, Kubernetes, Terraform, Ansible, GitHub Actions, "
                "Jenkins, Linux, Python. Resume attached.\n\n"
                "Let me know if you'd like to connect.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "Saw the {role_title} opening{at_company}. I've been doing DevOps and "
                "cloud infrastructure for {experience_years} years -- the kind of work "
                "where reliability matters more than cleverness.\n\n"
                "I deploy on AWS (ECS, EKS, Lambda), containerize with Docker, orchestrate "
                "with Kubernetes, codify infrastructure with Terraform, and automate "
                "everything I can with Ansible and Python. I've also built monitoring "
                "dashboards that give ops teams real-time visibility into system health "
                "and compliance status.\n\n"
                "The work I'm most proud of: automating network security remediation at "
                "scale for Barclays -- millions of devices, zero manual intervention. "
                "Resume has the details.\n\n"
                "Would love to chat.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "The {role_title} role{at_company} caught my eye. For {experience_years} "
                "years, I've been building the infrastructure and automation that keeps "
                "production running.\n\n"
                "My approach: everything as code, automate every repeatable process, "
                "monitor everything that matters. I've applied this across security "
                "compliance automation (Ansible at Barclays -- millions of devices), "
                "container orchestration (Docker + K8s), and cloud infrastructure "
                "management (Terraform + AWS).\n\n"
                "I write Python, Bash, and YAML in roughly equal measure. Resume attached "
                "with the specifics.\n\n"
                "Happy to jump on a call.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
        ],
        "linkedin_body": (
            "Hi! DevOps engineer ({experience_years} yrs) -- AWS, Docker, K8s, "
            "Terraform, Ansible. Automated security compliance at Barclays across "
            "millions of devices. Saw the {role_title} role{at_company}, let's connect!"
        ),
    },

    "seo_digital_marketing": {
        "email_subject": "{role_title} -- {your_name} ({experience_years} yrs exp)",
        "email_variations": [
            (
                "{greeting}\n\n"
                "I came across the {role_title} opening{at_company} and wanted to reach "
                "out. I've been driving organic traffic and managing paid campaigns across "
                "Google Ads, Facebook, and Instagram for {experience_years} years.\n\n"
                "My work spans SEO strategy (technical SEO, content optimization, link "
                "building), PPC campaign management with measurable ROI, and social media "
                "advertising. I'm data-driven -- I use GA4, Search Console, and A/B "
                "testing to optimize every campaign.\n\n"
                "I also have a strong technical background (Python, SQL, web development), "
                "which helps me implement tracking, automate reporting, and work closely "
                "with engineering teams. Resume attached.\n\n"
                "Would love to discuss how I can contribute to your marketing efforts.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "The {role_title} role{at_company} looks like a great fit. I combine "
                "technical skills with marketing expertise -- {experience_years} years "
                "growing organic traffic and optimizing paid campaigns.\n\n"
                "Quick highlights: managed Google Ads and social media campaigns across "
                "Facebook and Instagram, improved organic search rankings through technical "
                "SEO and content strategy, and built automated reporting dashboards to "
                "track KPIs in real time.\n\n"
                "What sets me apart: I write code (Python, SQL) and understand web "
                "architecture, so I can implement schema markup, fix crawl issues, set up "
                "tracking pixels, and automate repetitive marketing workflows without "
                "waiting on engineering. Resume's attached.\n\n"
                "Happy to chat.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "I noticed the {role_title} position{at_company}. I drive measurable "
                "growth through SEO and paid digital marketing -- {experience_years} years "
                "of running campaigns that deliver ROI.\n\n"
                "My approach: audit the current SEO baseline, identify high-impact keyword "
                "opportunities, optimize on-page and technical SEO, then layer in targeted "
                "paid campaigns on Google, Facebook, and Instagram. Everything measured in "
                "GA4 with clear attribution.\n\n"
                "I also bring technical depth -- I can build landing pages, set up "
                "conversion tracking, automate reporting with Python, and work directly "
                "with product/engineering teams. Resume attached.\n\n"
                "Would love to discuss the opportunity.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "Saw the {role_title} opening{at_company} and wanted to connect. I've "
                "spent {experience_years} years at the intersection of marketing and "
                "technology -- running SEO, Google Ads, and social media campaigns backed "
                "by data and automation.\n\n"
                "I manage campaigns across Google Ads, Facebook Ads, and Instagram Ads with "
                "a focus on conversion optimization and ROAS. On the organic side, I handle "
                "technical SEO, content strategy, and link building. I track everything "
                "through GA4, Search Console, and custom dashboards.\n\n"
                "What's different about me: I'm also a developer, so I automate reporting, "
                "build tracking systems, and fix technical SEO issues directly. Resume has "
                "the details.\n\n"
                "Let me know if you'd like to chat.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "The {role_title} role{at_company} resonated with me. I believe the best "
                "marketing is measurable, and I've spent {experience_years} years proving "
                "it.\n\n"
                "I've grown organic traffic through technical SEO and content optimization, "
                "managed paid campaigns across Google Ads, Facebook, and Instagram, and "
                "built analytics dashboards that tie every dollar spent to business "
                "outcomes. My technical background (Python, SQL, web development) means I "
                "can implement solutions, not just recommend them.\n\n"
                "Resume attached -- happy to walk through specific campaign results.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
        ],
        "linkedin_body": (
            "Hi! I run SEO and paid campaigns (Google Ads, Facebook, Instagram) -- "
            "{experience_years} yrs driving measurable growth. Saw the {role_title} "
            "role{at_company}, would love to connect!"
        ),
    },

    "software_engineer": {
        "email_subject": "{role_title} -- {your_name} ({experience_years} yrs exp)",
        "email_variations": [
            (
                "{greeting}\n\n"
                "I came across the {role_title} opening{at_company} and wanted to reach "
                "out. I've been working with Python for about {experience_years} years now, "
                "mostly building backend systems and shipping production code for clients "
                "across the US and Europe.\n\n"
                "I've attached my resume -- it covers the specifics better than I can in an "
                "email, but the short version is that I've spent most of my career solving "
                "real operational problems: automating manual workflows, building data "
                "pipelines, and getting things into production reliably.\n\n"
                "Would love to chat if you think there's a fit. Happy to jump on a quick "
                "call whenever works for you.\n\n"
                "Thanks,\n{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "The {role_title} role{at_company} looks like a strong fit for my "
                "background. I've been building software in Python for {experience_years} "
                "years -- REST APIs, automation tools, and production systems.\n\n"
                "I've worked across e-commerce logistics, healthcare, fintech, and "
                "enterprise SaaS -- building Django and FastAPI backends, React frontends, "
                "and deployment pipelines on AWS. My resume has the full breakdown.\n\n"
                "Happy to jump on a call if you'd like to discuss.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "I noticed the {role_title} position{at_company}. I'm a software developer "
                "with {experience_years} years of experience building production systems "
                "in Python.\n\n"
                "Highlights: automated claims processing recovering $2M+/year, built "
                "monitoring pipelines handling 50K+ events monthly, and shipped AI-powered "
                "email triage that cut response times from 4 hours to 15 minutes. I work "
                "across the stack -- Django, FastAPI, React, PostgreSQL, AWS, Docker.\n\n"
                "Resume attached. Would love to discuss the role.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "Saw the {role_title} opening{at_company} and wanted to share my "
                "background. I build software that solves real problems -- {experience_years} "
                "years of Python, APIs, automation, and production deployments.\n\n"
                "My approach: understand the business problem, build the simplest thing "
                "that works, ship it, then iterate. I've applied this across e-commerce, "
                "healthcare, fintech, and enterprise clients, always focused on code that's "
                "maintainable and reliable.\n\n"
                "Resume's attached with the details. Let me know if you'd like to chat.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
            (
                "{greeting}\n\n"
                "The {role_title} role{at_company} caught my attention. I've been building "
                "software for {experience_years} years and I'm at my best when there's a "
                "messy problem that needs a clean technical solution.\n\n"
                "I've automated manual workflows, built monitoring systems, designed APIs, "
                "and shipped dashboards -- mostly in Python (Django, FastAPI) with React on "
                "the frontend and AWS under the hood. Each project started with someone "
                "saying \"this process is broken\" and ended with something that runs on "
                "its own.\n\n"
                "Resume attached. Happy to chat about how I can help your team.\n\n"
                "{your_name}\n{your_email} | {your_phone}"
            ),
        ],
        "linkedin_body": (
            "Hi! Software developer ({experience_years} yrs) -- Python, Django, "
            "FastAPI, React, AWS. Saw the {role_title} role{at_company} and would "
            "love to connect!"
        ),
    },
}

DEFAULT_TEMPLATE = {
    "email_subject": "{role_title} -- {your_name} ({experience_years} yrs exp)",
    "email_variations": [
        (
            "{greeting}\n\n"
            "I came across the {role_title} opening{at_company} and wanted to reach out. "
            "I've been working with {top_skills} for about {experience_years} years now, "
            "mostly building backend systems and shipping production code for clients "
            "across the US and Europe.\n\n"
            "I've attached my resume -- it covers the specifics better than I can in an "
            "email, but the short version is that I've spent most of my career solving "
            "real operational problems: automating manual workflows, building data "
            "pipelines, and getting things into production reliably.\n\n"
            "Would love to chat if you think there's a fit.\n\n"
            "Thanks,\n{your_name}\n{your_email} | {your_phone}"
        ),
    ],
    "linkedin_body": (
        "Hi! I'm a developer ({experience_years} yrs) with experience in {top_skills}. "
        "Saw the {role_title} role{at_company}, would love to connect!"
    ),
}


def get_message_template(role_key: str, channel: str = "email") -> dict:
    """
    Return {"subject": str, "body": str, "variation": int, "total_variations": int}.
    For email channel, cycles through variations round-robin.
    For linkedin channel, returns the single linkedin body.
    """
    templates = TEMPLATES.get(role_key, DEFAULT_TEMPLATE)

    if channel == "linkedin":
        return {
            "subject": "",
            "body": templates["linkedin_body"],
            "variation": 0,
            "total_variations": 1,
        }

    variations = templates["email_variations"]
    counter_key = role_key or "_default"
    idx = _variation_counter.get(counter_key, 0)
    body = variations[idx % len(variations)]
    _variation_counter[counter_key] = (idx + 1) % len(variations)

    return {
        "subject": templates["email_subject"],
        "body": body,
        "variation": (idx % len(variations)) + 1,
        "total_variations": len(variations),
    }
