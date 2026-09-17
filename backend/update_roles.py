"""
Populate all 10 roles with multi-client CubexO experience data.
Each role has 5 clients, shown based on experience_years threshold.
"""
from dotenv import load_dotenv
load_dotenv()

from database import NeonSessionLocal
from neon_models import Role, RoleSkill, RoleExperience

# ─── 5 Clients (shared across all roles, work varies by role) ───────────────
# min_years: minimum experience to show this client
# position_index: 0 = most recent

CLIENTS = [
    {"name": "Spreetail", "location": "US", "min_years": 1, "pos": 0},
    {"name": "Meridian Health Group", "location": "UK", "min_years": 3, "pos": 1},
    {"name": "AutoVerse GmbH", "location": "Germany", "min_years": 5, "pos": 2},
    {"name": "Apex Financial Corp", "location": "US", "min_years": 7, "pos": 3},
    {"name": "NordTech Solutions", "location": "Netherlands", "min_years": 9, "pos": 4},
]

ROLE_DATA = {
    # ═══════════════════════════════════════════════════════════════════════════
    "software_engineer": {
        "title": "Software Developer",
        "summary": (
            "Python backend developer with a focus on workflow automation, REST API design, "
            "and getting things running reliably in production. Most of my work has been building "
            "FastAPI and Django services backed by PostgreSQL, deploying on AWS with Docker, "
            "and replacing slow manual processes with code that just runs."
        ),
        "skills": {
            "Languages": ["Python", "SQL"],
            "Backend Frameworks": ["Django", "FastAPI"],
            "Databases": ["PostgreSQL", "MongoDB", "MySQL"],
            "Cloud & DevOps": ["AWS", "Docker", "GitHub Actions", "Jenkins"],
            "Tools": ["Git", "GitHub", "Jira", "Confluence", "Linux", "Postman"],
        },
        "clients": {
            "Spreetail": [
                "Spreetail is a US-based e-commerce logistics company. Their carrier claims process with OnTrac was entirely manual -- the ops team spent hours every day filing claims by hand and losing millions in unrecovered shipping costs. Built a Python pipeline that pulls claim data automatically, validates it, and files with OnTrac daily. Cut processing time by 80% and started recovering costs that were just being written off before.",
                "The ops team was also drowning in inbound emails -- hundreds a day, all needing someone to read them, figure out what department they belonged to, and respond. Built an AI-powered email system that parses incoming messages, figures out intent, routes tickets automatically, and handles the routine stuff without a human ever touching it.",
                "Packages kept getting lost in transit and nobody knew until a customer complained. Built an event-driven monitoring system that watches logistics endpoints in real time, tracks every item's lifecycle, and kicks off resolution steps automatically when something goes missing. Took what used to be a reactive fire drill and made it proactive.",
                "Owned the core backend infrastructure across all these systems -- designed the REST APIs in FastAPI and Django, set up PostgreSQL for data storage, and built out the CI/CD pipeline with Docker on AWS so we could ship changes without breaking things.",
            ],
            "Meridian Health Group": [
                "Meridian is a UK healthcare provider managing records for 200K+ patients. They needed a modern API layer for their electronic health records that met HIPAA requirements. Built a Django REST API with role-based access control, audit logging, and encrypted storage -- passed their compliance audit on the first try.",
                "Their appointment scheduling was a mess -- double bookings, no automated reminders, and patients just not showing up. Wrote a FastAPI scheduling service that handles multi-provider calendars, resolves conflicts automatically, and sends reminders. No-show rates dropped 35%.",
                "Doctors were switching between four different systems to see a patient's full picture. Built backend services that pull vitals, lab results, and medication history from all their data sources into one real-time clinical dashboard.",
            ],
            "AutoVerse GmbH": [
                "AutoVerse is a German connected-car company with 50K+ vehicles across 12 EU markets. They needed to ingest real-time OBD-II telemetry from all those cars and actually do something useful with it. Built a high-throughput ingestion service with FastAPI and PostgreSQL that processes the telemetry stream and triggers predictive maintenance alerts -- cut unscheduled workshop visits by 32%.",
                "Their fleet operators (200+ companies) had no centralized way to track vehicles or schedule maintenance. Built REST APIs for GPS tracking, maintenance scheduling, and EU compliance reporting. Added geofencing with PostGIS so operators get alerted when vehicles go off-route.",
                "When manufacturer recalls came out, AutoVerse had no automated way to figure out which of their vehicles were affected. Built a service that cross-references their VIN database against recall bulletins, notifies owners automatically, and books workshop appointments through the dealer portal.",
            ],
            "Apex Financial Corp": [
                "Apex is a US wealth management and trading firm. They needed trade execution APIs that could route orders across NYSE, NASDAQ, and LSE with minimal latency. Built FastAPI endpoints handling 5K+ orders per minute with sub-100ms response times and a full audit trail in PostgreSQL for regulatory compliance.",
                "Portfolio managers had no self-service way to see risk metrics or performance attribution -- they were waiting on analysts to run reports. Built a Django analytics backend that computes VaR, Sharpe ratio, and P&L attribution across 15 years of market data and serves it to real-time dashboards used by 40+ PMs daily.",
                "Monthly client statements were being assembled manually from multiple data sources -- trade history, fees, performance charts. Automated the entire pipeline with Celery workers that generate personalized PDFs for 8K+ clients on schedule.",
            ],
            "NordTech Solutions": [
                "NordTech is a Dutch enterprise SaaS company serving 200+ business clients. Each client needed custom workflow rules -- approval chains, document routing, SLA escalations -- but every change required developer time. Built a configurable workflow engine with Django and Celery where clients define their own rules through a JSON config layer, no code changes needed.",
                "Their platform needed to talk to 15+ third-party systems -- SAP, Salesforce, Jira, Slack, Microsoft 365 -- and each integration was built differently. Built a centralized API gateway in FastAPI with unified OAuth 2.0 auth, per-tenant rate limiting, and bidirectional data transformations so all integrations work the same way.",
                "NordTech had no visibility into whether they were meeting SLA commitments across tenant workflows. Built a real-time monitoring service that tracks response times, uptime, and escalation deadlines, and automatically generates incident reports when contractual thresholds get breached.",
            ],
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    "ai_ml_engineer": {
        "title": "Software Developer -- AI/ML",
        "summary": (
            "AI/ML engineer focused on shipping ML models and LLM-powered features into production. "
            "I build RAG pipelines, train classification models, and deploy inference APIs -- "
            "the kind of work where you need to care about both model accuracy and whether "
            "the thing actually runs reliably at scale. Python, FastAPI, LangChain, and AWS mostly."
        ),
        "skills": {
            "Languages": ["Python", "SQL"],
            "AI & Machine Learning": ["LLMs", "LangChain", "LlamaIndex", "RAG Pipelines", "Prompt Engineering", "Vector DBs"],
            "Backend": ["FastAPI", "Django", "Pydantic", "SQLAlchemy", "Celery", "REST APIs"],
            "Databases": ["PostgreSQL", "MongoDB", "Redis"],
            "Cloud & DevOps": ["AWS", "Docker", "GitHub Actions", "Linux"],
        },
        "clients": {
            "Spreetail": [
                "Spreetail is a US e-commerce logistics company. Their internal teams were constantly searching through scattered documentation -- product specs, SOPs, vendor contracts -- and wasting hours finding answers. Built a RAG system using LangChain and a vector database that indexes all their internal docs, with a FastAPI backend so people can just ask questions in natural language. Cut query resolution time by 60%.",
                "Their ops team was manually reading and triaging hundreds of inbound emails daily. Integrated LLMs for semantic parsing and intent recognition so the system can understand what each email is about, route it to the right department, and auto-respond to routine queries. Killed 90% of manual email triage.",
                "Carrier claims with OnTrac were being filed manually and a lot of money was slipping through the cracks. Built a Python extraction pipeline with strict Pydantic validation that aggregates and files claims daily -- recovered millions in logistics costs that were just being lost before.",
                "Also owned the core REST API layer and CI/CD setup -- FastAPI services deployed on AWS with Docker and GitHub Actions.",
            ],
            "Meridian Health Group": [
                "Meridian is a UK healthcare provider. Their clinical notes are all free-text -- doctors write however they want, and the billing team had to manually read through notes to extract diagnoses and procedures for coding. Built an NLP pipeline with HuggingFace transformers and spaCy that extracts structured medical data from those notes at 94% F1-score, feeding directly into automated billing.",
                "They wanted to flag patients at risk of readmission before discharge, but had no predictive tooling. Trained XGBoost models on historical patient data and served predictions through FastAPI endpoints that plug right into the clinical dashboard -- so doctors see the risk score in real time while making decisions.",
                "Clinicians were spending too much time searching through medical literature and internal protocols. Built a RAG search system with LlamaIndex that lets them query everything in natural language -- dropped research time by 70%.",
            ],
            "AutoVerse GmbH": [
                "AutoVerse is a German connected-car company running 50K+ vehicles across Europe. Cars break down and owners don't know until it happens. Built survival models using XGBoost and CoxPH on OBD-II telemetry data to predict component failures 7 days out with 89% precision. Deployed as FastAPI inference endpoints on SageMaker -- cut unplanned workshop visits by 40%.",
                "Their insurance partners wanted per-driver risk scoring but had no way to analyze driving behavior at scale. Built a CNN+LSTM classifier in PyTorch that categorizes driving patterns from 10Hz accelerometer data -- harsh braking, aggressive cornering, speeding -- and assigns risk tiers for each driver.",
                "Insurance claims required a human adjuster to review every photo of vehicle damage. Trained a YOLOv8 model on 50K+ labeled images to detect dents, scratches, and paint damage from customer uploads -- automated the initial assessment and cut adjuster workload by 25%.",
            ],
            "Apex Financial Corp": [
                "Apex is a US wealth management and trading firm. Credit card fraud was costing them millions, and their rule-based system had too many false positives. Built a real-time fraud scoring pipeline using an ensemble of XGBoost, isolation forest, and autoencoders processing 10K+ transactions per minute via Kafka. Reduced fraud losses by 28% and false positives by 35%.",
                "Analysts were spending days manually reading through SEC filings, earnings reports, and compliance docs. Built an LLM extraction pipeline with LangChain and GPT-4 that parses these documents into structured JSON -- processes 500+ docs daily at 97% field-level accuracy.",
                "The quant team wanted market sentiment signals but had no NLP infrastructure. Built a pipeline using fine-tuned FinBERT to analyze 10K+ daily news articles and earnings call transcripts for sentiment, feeding scores into their trading models. Contributed to a 1.8% alpha improvement.",
            ],
            "NordTech Solutions": [
                "NordTech is a Dutch enterprise SaaS platform serving 200+ clients. Every client sends in a mix of invoices, contracts, support tickets, and legal docs -- and someone had to manually sort and route each one. Fine-tuned BERT models to classify documents across 50+ workflow categories at 96% accuracy, saving each client about 4 hours of daily manual sorting.",
                "Their enterprise clients kept submitting L1 support tickets for questions that were already answered in documentation. Built a RAG chatbot with LangChain, GPT-4, and Pinecone that searches across product docs, HR policies, and IT runbooks. Handles 2K+ questions daily and resolves 85% on first response -- cut L1 tickets by 45%.",
                "NordTech had no way to detect unusual activity across tenant workflows -- someone could approve their own requests or access data they shouldn't. Built an anomaly detection system using autoencoders and isolation forests that monitors workflow patterns in real time and flags suspicious behavior for the security team.",
            ],
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    "data_engineer": {
        "title": "Software Developer -- Data Engineering",
        "summary": (
            "Data engineer who builds ETL pipelines, data warehouses, and streaming systems. "
            "Mostly working with Airflow, Kafka, Spark, and Snowflake on AWS. "
            "I spend most of my time making sure data gets where it needs to go -- "
            "reliably, on time, and without breaking downstream dashboards or ML models."
        ),
        "skills": {
            "Languages": ["Python", "SQL"],
            "Data Engineering": ["Apache Spark", "Apache Kafka", "Apache Airflow", "dbt", "ETL/ELT Pipelines"],
            "Databases & Warehouses": ["PostgreSQL", "Snowflake", "AWS Redshift", "MongoDB"],
            "Cloud & DevOps": ["AWS", "Docker", "Terraform", "GitHub Actions"],
            "Tools": ["Git", "Linux", "Great Expectations", "Power BI", "Jira"],
        },
        "clients": {
            "Spreetail": [
                "Spreetail is a US e-commerce logistics company that files thousands of carrier claims daily. Their claim data was scattered across multiple logistics APIs with no unified pipeline. Built Airflow-orchestrated ETL jobs in Python that pull from all their carrier APIs, transform the data, and load it into a centralized PostgreSQL warehouse -- processing 500K+ records a day at 99.9% accuracy.",
                "Shipment tracking was batch-processed overnight, so when packages went missing nobody knew for hours. Set up a Kafka streaming pipeline that ingests real-time tracking events as they happen -- gave the ops team sub-minute visibility into lost-in-transit inventory and feeds the analytics dashboards live.",
                "Bad data kept making it into production -- wrong formats, missing fields, schema changes from upstream APIs that nobody caught. Built a data quality layer with Great Expectations and custom validators that catches anomalies, enforces schema contracts, and alerts on drift before it hits dashboards.",
                "Managed the core data infrastructure on AWS -- S3 for storage, Glue for cataloging, Redshift for analytics. Set up partitioning and incremental loads that cut warehouse query costs by 60%.",
            ],
            "Meridian Health Group": [
                "Meridian is a UK healthcare provider. Patient data lived in 12+ separate systems -- EMR, pharmacy, billing, labs -- and nobody could get a unified view. Built a HIPAA-compliant data warehouse on Snowflake that integrates all of them into one place for patient analytics.",
                "Clinical systems exchange data using HL7 and FHIR standards, but the messages come in messy and inconsistent. Built real-time Kafka pipelines in Python that ingest 1M+ clinical events daily, normalize the formats, deduplicate, and validate schemas before loading.",
                "Research teams were spending weeks manually preparing patient data for clinical studies. Wrote dbt transformation models that produce analytics-ready cohort tables on demand -- what used to take weeks now takes hours.",
            ],
            "AutoVerse GmbH": [
                "AutoVerse is a German connected-car company with 50K+ vehicles across 12 EU markets streaming sensor data constantly. They had no way to store and process it at scale. Built a data lake on S3 with Apache Spark and Delta Lake that handles 100M+ telemetry events per day with ACID transactions and time-travel queries for debugging.",
                "Their ML team needed feature data from vehicle sensors -- rolling averages, standard deviations, FFT transforms -- computed over sliding windows. Built Airflow ETL workflows that process 500GB of sensor data daily into a feature store with automated quality checks, so the predictive maintenance models always have fresh, validated inputs.",
                "Vehicle telemetry, dealer CRM, and warranty claims all lived in separate systems. Built a Snowflake analytics warehouse that joins them together -- the cross-domain view let them spot a recurring transmission fault that saved EUR 3M in recall costs.",
            ],
            "Apex Financial Corp": [
                "Apex is a US trading and wealth management firm that needs real-time market data from multiple exchanges. Built Kafka-based pipelines that ingest Level 2 feeds from NYSE, NASDAQ, LSE, Eurex, and CME, normalize tick data into Parquet format for trading systems with sub-200ms end-to-end latency.",
                "Financial regulations require daily transaction reports to multiple agencies -- MiFID II, Dodd-Frank, EMIR. Built Airflow + dbt workflows that generate all required reports from 500K+ daily trades. Three years of 100% on-time submission, zero regulatory penalties.",
                "The quant research team wanted alternative data -- satellite imagery metadata, web traffic estimates, credit card aggregates -- but each source had its own format and quality issues. Built Python connectors that ingest, normalize, and quality-score 8 alternative data sources into the analytics warehouse.",
            ],
            "NordTech Solutions": [
                "NordTech is a Dutch enterprise SaaS company with 200+ clients, each needing isolated data pipelines. Built a multi-tenant pipeline architecture on Snowflake with row-level security, automated schema provisioning for new tenants, and per-tenant compute scaling so one client's heavy queries don't slow down another.",
                "They needed a complete audit trail of every workflow change across every tenant for compliance. Built an event-sourcing system using Kafka, Debezium CDC, and PostgreSQL that captures state changes in real time -- supports full audit trails, point-in-time reconstruction, and cross-service analytics.",
                "Data quality issues were getting caught too late -- bad row counts, schema drift, distribution shifts that silently corrupted downstream reports. Built a monitoring framework with Great Expectations that runs automated checks across all tenant pipelines, alerts on Slack when something looks wrong, and triggers self-healing reconciliation jobs.",
            ],
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    "data_scientist": {
        "title": "Software Developer -- Data Science",
        "summary": (
            "Data scientist who builds predictive models, runs experiments, and turns messy data "
            "into things people can actually act on. Mostly Python -- XGBoost, scikit-learn, "
            "time-series forecasting, NLP. I focus on models that ship to production, not just notebooks."
        ),
        "skills": {
            "Languages": ["Python", "SQL"],
            "ML & Statistics": ["Scikit-learn", "XGBoost", "LightGBM", "Hypothesis Testing", "A/B Testing", "Time Series", "Feature Engineering"],
            "AI & NLP": ["LLMs", "Prompt Engineering", "RAG", "Text Analytics", "Sentiment Analysis"],
            "Visualization": ["Tableau", "Power BI", "Plotly", "Matplotlib", "Seaborn"],
            "Cloud & Tools": ["AWS", "Docker", "MLflow", "Git", "Jupyter", "Pandas"],
        },
        "clients": {
            "Spreetail": [
                "Spreetail is a US e-commerce logistics company that files carrier claims with OnTrac daily. A lot of claims were getting denied and the team had no way to prioritize which ones to push. Built an XGBoost classifier that predicts claim approval likelihood so the automated system files high-probability claims first -- improved recovery rates by 25%.",
                "Packages would go missing in transit and nobody noticed until customers complained. Built anomaly detection pipelines with scikit-learn that spot unusual shipment patterns early, so the team can investigate proactively instead of reactively. Cut resolution times by 40%.",
                "Hundreds of operational emails came in daily and someone had to read each one to figure out what it was about. Trained NLP classification models that categorize by intent and urgency at 92% accuracy -- routine stuff gets handled automatically now.",
                "Leadership had no clear view of logistics performance. Built Tableau dashboards showing claim recovery rates, delivery success metrics, and operational trends so execs could make decisions based on actual data.",
            ],
            "Meridian Health Group": [
                "Meridian is a UK healthcare provider. Patients were being readmitted within 30 days at a high rate, costing the hospital and hurting outcomes. Built an ensemble model combining XGBoost and logistic regression that predicts readmission risk at 0.87 AUC-ROC -- doctors now see the risk score at discharge and can target interventions. Readmissions dropped 18%.",
                "Clinical trials were struggling to find eligible patients because the data was buried in unstructured medical records. Built an NLP matching system using text embeddings that identifies candidates from free-text notes -- cut enrollment timelines in half.",
                "Budget planning was basically guesswork. Built time-series forecasting models with Prophet and LightGBM that predict monthly healthcare costs by department, giving planners 12-month projections at 8% MAPE.",
            ],
            "AutoVerse GmbH": [
                "AutoVerse is a German connected-car company with 50K+ vehicles across Europe. Car components were failing unexpectedly, costing owners money and dealer reputation. Built survival analysis and XGBoost models on OBD-II telemetry, engine temps, and mileage data to predict failures 14 days out at 89% precision. Cut unplanned breakdowns by 40%, saved EUR 2M annually.",
                "Insurance partners wanted to price policies based on actual driving behavior, not just demographics. Engineered features from 10Hz accelerometer data -- harsh braking, cornering G-force, speed compliance -- and built a scoring model that classifies drivers into 5 risk tiers. Processes 2M+ driving sessions per month.",
                "Warranty costs were unpredictable and procurement had no forward visibility. Built Prophet + LightGBM time-series models that forecast claim volumes and costs by vehicle model and component, giving teams 6-month projections at 12% MAPE.",
            ],
            "Apex Financial Corp": [
                "Apex is a US trading and wealth management firm. Their rule-based fraud detection flagged too many legitimate transactions while missing real fraud. Built a real-time scoring pipeline with stacked isolation forests and XGBoost processing 10K+ transactions per minute via Kafka. Fraud losses down 28%, false positives down 35% -- saved the investigations team 200+ hours a month.",
                "Wealth management clients needed better portfolio optimization but the existing approach was too simplistic. Built a mean-variance optimization model with real-world constraints -- ESG compliance, sector limits, liquidity thresholds. Backtested across 15 years of data with walk-forward validation, consistently beat S&P 500 by 2.3% annually.",
                "Relationship managers had no way to know which clients were most valuable long-term. Built a probabilistic CLV model using BG/NBD and Gamma-Gamma submodels that forecasts 3-year revenue potential for 8K+ clients, so the team can prioritize retention and advisory for the accounts that matter most.",
            ],
            "NordTech Solutions": [
                "NordTech is a Dutch enterprise SaaS company with 200+ clients. They were losing accounts and didn't see it coming until cancellation. Built a churn prediction model using survival analysis and LightGBM that combines usage metrics, support ticket sentiment, and billing patterns to flag at-risk accounts 60 days before renewal at 82% precision.",
                "Product and sales teams had no idea how different clients actually used the platform. Applied clustering (K-means + DBSCAN with UMAP reduction) to identify 8 distinct usage personas across tenants -- helped prioritize the roadmap, decide which features to sunset, and customize onboarding.",
                "Feature experiments were being decided by gut feel. Built a Bayesian A/B testing framework with sequential analysis and early stopping so the product team can run rigorous experiments on UI changes, pricing, and onboarding flows across all 200+ tenants.",
            ],
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    "data_analyst_bi": {
        "title": "Software Developer -- Data Analytics",
        "summary": (
            "Data analyst who builds dashboards, writes SQL, and turns raw data into reports "
            "that people actually use. Power BI, Tableau, Looker -- I've built 30+ dashboards "
            "for executive teams and cut reporting turnaround by 70%. I care about making data "
            "accessible, not just accurate."
        ),
        "skills": {
            "Analytics & SQL": ["SQL", "Window Functions", "CTEs", "Cohort Analysis", "Funnel Analysis"],
            "BI & Visualization": ["Power BI", "Tableau", "Looker", "DAX", "Power Query", "Excel"],
            "Languages": ["Python", "SQL"],
            "Databases": ["PostgreSQL", "MySQL", "Snowflake", "BigQuery"],
            "Tools": ["Jira", "Confluence", "Google Sheets", "GA4", "Git"],
        },
        "clients": {
            "Spreetail": [
                "Spreetail is a US e-commerce logistics company that files carrier claims with OnTrac. Leadership had no real-time view into how claims were performing. Built Power BI dashboards tracking claim rates, approval rates, recovery amounts, and processing timelines so ops leadership can see what's happening without asking anyone.",
                "The logistics team was managing carrier relationships without hard numbers on actual performance. Wrote SQL analytical models measuring delivery success rates, lost-in-transit ratios, and carrier benchmarks -- gave the team data to back up vendor negotiations and enforce SLAs.",
                "They had an AI email automation system running but no way to tell if it was actually working well. Built funnel analysis reports tracking resolution rates, response times, and escalation patterns so the team can see what's improving and what needs tuning.",
                "Engineering and ops teams were each tracking different metrics in spreadsheets. Worked across teams to define a shared KPI framework and automated the recurring reports with Python scripts -- cut manual reporting effort by 70%.",
            ],
            "Meridian Health Group": [
                "Meridian is a UK healthcare provider running 8 hospital departments. They had no centralized view of operational efficiency. Built Tableau dashboards tracking patient wait times, bed occupancy, and physician utilization -- the resource optimization that followed cut average wait times by 22%.",
                "Billing was leaking money through claim denials, but nobody could see the patterns. Built Power BI reports analyzing denial rates, reimbursement patterns, and billing efficiency. The denial pattern analysis alone identified $1.2M in recoverable revenue.",
                "Patient satisfaction surveys were being collected but never analyzed systematically. Ran cohort analysis on survey data using SQL and Python, found the key satisfaction drivers, and presented recommendations to hospital leadership.",
            ],
            "AutoVerse GmbH": [
                "AutoVerse is a German connected-car company managing 50K+ vehicles across 12 EU markets. Fleet managers had no consolidated view of their vehicles' health. Built real-time Tableau dashboards with 15+ views covering uptime, maintenance costs, fuel efficiency, and driver utilization -- helped them find EUR 500K in annual cost savings.",
                "Warranty claims were piling up but nobody was looking at them analytically. Built SQL models with window functions and cohort analysis on 3 years of claims data, and surfaced a recurring transmission defect in 2023 models that led to a targeted recall -- saved EUR 3M in potential litigation.",
                "Executives were getting monthly reports from 8 different systems in 8 different formats. Automated the whole monthly business review into a single Power BI dashboard covering sales, after-market revenue, NPS, and operational KPIs.",
            ],
            "Apex Financial Corp": [
                "Apex is a US trading and wealth management firm. Portfolio managers and compliance officers needed daily visibility into trade execution quality. Built Power BI dashboards tracking fill rates, slippage, latency, and P&L attribution by strategy and trader -- used daily by 40+ people.",
                "Regulatory compliance required daily metrics and exception reports for MiFID II and Dodd-Frank. Built automated SQL pipelines with CTEs and recursive queries that generate everything needed for auditors. Maintained 100% audit readiness across 3 consecutive regulatory examinations.",
                "Wealth management clients were calling in constantly to ask about their portfolio performance. Built automated Tableau dashboards showing allocations, returns, benchmarks, and fee breakdowns -- generates 8K+ personalized monthly reports and cut client inquiry volume by 30%.",
            ],
            "NordTech Solutions": [
                "NordTech is a Dutch enterprise SaaS company with 200+ tenants. Product team had no visibility into how clients actually use the platform. Built Looker dashboards tracking feature adoption, engagement funnels, WAU cohorts, and time-to-value -- directly informed the roadmap and improved trial-to-paid conversion by 20%.",
                "Customer success managers had no systematic way to tell which accounts were at risk. Built a composite health score combining 12 metrics -- DAU/MAU, support ticket volume, feature usage breadth, billing consistency, NPS -- that flags at-risk accounts 45 days before renewal. Reduced annual churn by 15%.",
                "Sales team was doing outreach without knowing which features correlate with expansion revenue. Built SQL-based attribution models tracking revenue per tenant and feature-level usage-to-revenue correlations. Gave sales data-backed expansion playbooks that increased average contract value by 18%.",
            ],
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    "business_analyst": {
        "title": "Business Analyst",
        "summary": (
            "Business analyst who sits between stakeholders and engineering to make sure "
            "what gets built is actually what the business needs. I write requirements docs, "
            "map processes, run UAT, and track KPIs. Managed requirements for 10+ product releases "
            "and cut development rework by half by getting specs right before code starts."
        ),
        "skills": {
            "Business Analysis": ["Requirement Gathering", "Process Mapping", "Gap Analysis", "Root Cause Analysis"],
            "Documentation": ["BRD", "FRD", "User Stories", "Acceptance Criteria", "SOPs", "Wireframes"],
            "Analytics & Tools": ["SQL", "Excel", "Power BI", "KPI Reporting"],
            "Project Management": ["Jira", "Agile/Scrum", "UAT", "Stakeholder Management", "Sprint Planning"],
            "Design": ["Figma", "Miro", "Confluence", "Lucidchart", "Postman"],
        },
        "clients": {
            "Spreetail": [
                "Spreetail is a US e-commerce logistics company. Their carrier claim process with OnTrac was manual and nobody had documented how it actually worked end-to-end. Led requirements gathering, mapped the existing process, wrote detailed BRDs and FRDs with acceptance criteria, and coordinated UAT -- reduced development rework by 40% because the engineers knew exactly what to build.",
                "They were building an AI system to handle inbound operational emails, but engineering and ops had different ideas about what it should do. Sat down with both teams, aligned on functional requirements, wrote user stories and workflow diagrams, and got the first release right without major rework.",
                "Operations leadership wanted dashboards but couldn't articulate exactly what metrics mattered. Gathered and prioritized reporting requirements, translated business needs into wireframes and KPI definitions that the engineering team could actually build from.",
                "Looked at the existing manual workflows across the logistics operation, identified where automation would have the highest ROI, and presented data-backed recommendations to senior management.",
            ],
            "Meridian Health Group": [
                "Meridian is a UK healthcare provider. They wanted to build a patient-facing health portal but had 15 different stakeholder groups with conflicting requirements. Led requirements elicitation across all of them, produced 120+ user stories with acceptance criteria and Figma wireframes that everyone could agree on.",
                "They needed to pass HIPAA and GDPR compliance audits but didn't know where their systems fell short. Mapped every regulation to system capabilities, identified 23 compliance gaps, and wrote remediation plans that got them through the audit.",
                "Appointment booking was painfully slow -- took staff 12 minutes per patient. Ran process mapping workshops with clinical staff, redesigned the scheduling workflow, and got it down to 4 minutes.",
            ],
            "AutoVerse GmbH": [
                "AutoVerse is a German connected-car company. They were building a vehicle telemetry platform but the stakeholders -- OEMs, fleet operators, insurance partners -- all spoke different languages. Did 30+ interviews, translated CAN bus technical specs into 80+ user stories the engineering team could work from.",
                "Fleet operators across Germany, France, and the Netherlands were testing new releases, and UAT was chaotic. Took over UAT coordination -- managed 200+ test cases in Jira, handled defect tracking and formal sign-offs for bi-weekly releases. Got first-pass UAT approval up to 98%.",
                "Dealers were spending too much time on admin for service bookings. Mapped the as-is process with 15 dealership managers, found 8 bottlenecks, and designed a streamlined digital booking flow that cut dealer admin overhead by 35%.",
            ],
            "Apex Financial Corp": [
                "Apex is a US trading and wealth management firm. Their trade execution platform had complex logic -- order routing, partial fills, cross-exchange settlement -- and none of it was documented clearly. Worked with quant traders and risk managers to write 150+ user stories with decision matrices, translating trading logic into specs engineers could implement.",
                "Financial regulations -- MiFID II, Dodd-Frank, EMIR -- required detailed reporting and nobody had mapped what data came from where. Created BRDs with data lineage diagrams covering 50+ compliance obligations, mapping each to system features, data sources, and transformation rules.",
                "Client onboarding took 18 days and passed through 6 departments. Mapped the KYC journey, found 14 redundant handoffs and 3 compliance bottlenecks. Designed a streamlined process with SOPs that cut onboarding to 7 days while staying fully compliant.",
            ],
            "NordTech Solutions": [
                "NordTech is a Dutch enterprise SaaS company. Their clients needed custom workflow rules -- approval chains, escalations, routing -- but every change required a developer. Designed the requirements for a configurable workflow engine with a no-code interface, writing the domain-specific language spec that lets enterprise admins set up their own rules through drag-and-drop.",
                "The platform needed to integrate with 15+ third-party systems -- SAP, Salesforce, Jira, Slack, Microsoft 365 -- and each had different APIs and data formats. Documented integration requirements for every system: data mappings, API contracts, error handling protocols.",
                "Customer success had no standardized playbook -- each CSM handled at-risk accounts differently. Partnered with CSM leadership to define health metrics, escalation triggers, and intervention steps. Built Confluence docs and Jira workflow templates that cut average resolution time for at-risk accounts by 40%.",
            ],
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    "full_stack_developer": {
        "title": "Full-Stack Python Developer",
        "summary": (
            "Full-stack Python developer -- I build the backend APIs and the frontend that talks to them. "
            "Django and FastAPI on the server side, React.js on the client side, PostgreSQL for data. "
            "I like owning the full picture from database schema to the UI the user actually sees."
        ),
        "skills": {
            "Languages": ["Python", "JavaScript", "SQL"],
            "Backend": ["Django", "FastAPI", "Flask", "Celery", "REST APIs"],
            "Frontend": ["React.js", "Next.js", "HTML5", "CSS3", "Tailwind CSS"],
            "Databases": ["PostgreSQL", "MongoDB", "Redis"],
            "Cloud & DevOps": ["AWS", "Docker", "GitHub Actions", "Nginx"],
        },
        "clients": {
            "Spreetail": [
                "Spreetail is a US e-commerce logistics company. Their carrier claim filing with OnTrac was fully manual -- someone had to pull data, review it, and file each claim by hand. Built the whole platform end to end: FastAPI backend for automated data extraction and validation, React.js frontend for the claim review dashboard, PostgreSQL for storage. Replaced the manual process and started recovering millions that were being left on the table.",
                "They also needed a system to handle inbound operational emails automatically. Built the Python backend microservices for email parsing and ticket routing, plus a React.js admin interface where the ops team can monitor automation performance and tweak escalation rules.",
                "Packages going missing was a constant problem with no visibility. Built a FastAPI backend that monitors logistics endpoints in real time, paired with a React.js dashboard showing item lifecycles and resolution progress -- turned a blind spot into a live operations view.",
                "Owned the shared infrastructure across all these projects -- REST API design in FastAPI and Django, responsive frontends in React.js and Tailwind, CI/CD with Docker on AWS.",
            ],
            "Meridian Health Group": [
                "Meridian is a UK healthcare provider. Patients had no self-service way to interact with the hospital -- everything required a phone call. Built a full-stack patient portal with Django backend and React.js frontend for viewing medical records, booking appointments, and secure messaging with doctors.",
                "Nurses were switching between multiple systems to check on patients. Built real-time clinical dashboards using FastAPI WebSockets and React.js with Chart.js showing vitals, lab results, and medication schedules across 8 departments -- all on one screen.",
                "COVID pushed them toward virtual consultations but they had no telemedicine capability. Built a video consultation platform with WebRTC on a Django backend handling session management, scheduling, and prescription generation.",
            ],
            "AutoVerse GmbH": [
                "AutoVerse is a German connected-car company with 50K+ vehicles across Europe. Their 200+ fleet operators had no centralized tool to track vehicles. Built a full-stack fleet management app -- FastAPI backend, React.js frontend with Mapbox GL maps showing real-time GPS positions updating every 5 seconds via WebSockets, plus maintenance scheduling with drag-and-drop calendar and driver assignment workflows.",
                "Vehicle owners (100K+) had no way to see what was going on with their car between service visits. Built a customer-facing diagnostics portal with Django REST and React.js -- real-time telemetry dashboards, trip history with route visualization, service appointment booking, and push notifications for predictive maintenance alerts.",
                "Dealers were managing service bookings manually with phone calls and paper. Built a dealer-facing booking app with Django and React.js that integrates with parts inventory and workshop calendars for real-time scheduling and automated service reminders.",
            ],
            "Apex Financial Corp": [
                "Apex is a US trading and wealth management firm. Portfolio managers needed real-time market data but their tools were outdated. Built a trading dashboard with FastAPI WebSockets and React.js with D3.js charts -- live Level 2 market data, positions, P&L heatmaps, and trade blotter with sub-second updates. Dark/light themes and customizable widget layouts for 40+ daily users.",
                "Client onboarding took 5 days because everything was paper-based. Built a multi-step KYC portal in Django and React.js with drag-and-drop document upload, identity verification via Onfido, risk questionnaires, and automated compliance approval chains. Cut onboarding to 4 hours.",
                "Compliance officers were managing regulatory filings through email and shared drives with no version control. Built a secure document management app in Django and React.js for uploading, version-tracking, and digitally signing SEC submissions -- full audit trails and role-based access.",
            ],
            "NordTech Solutions": [
                "NordTech is a Dutch enterprise SaaS company. Their 200+ clients needed custom workflow configurations but every change required developer involvement. Built a drag-and-drop workflow builder with React Flow and a FastAPI backend -- enterprise admins can now design approval chains, conditional branches, and routing rules visually with real-time validation.",
                "Managing 200+ enterprise accounts -- users, permissions, SSO, billing -- was scattered across multiple admin tools. Built a unified admin panel in Django and React.js covering RBAC, SAML/OIDC integration, API key management, usage metering, and white-label theming.",
                "End-users at client companies had no self-service option -- everything went through the admin. Built a white-labeled portal with Next.js and FastAPI for support tickets, workflow status tracking, and knowledge base access, with per-tenant theming and SSO.",
            ],
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    "backend_engineer": {
        "title": "Back-End Developer",
        "summary": (
            "Backend developer focused on Python APIs, microservices, and making databases fast. "
            "FastAPI and Django are my main tools. Most of my work involves designing services "
            "that handle real traffic reliably -- event-driven systems, job queues, and "
            "containerized deployments on AWS."
        ),
        "skills": {
            "Languages": ["Python", "SQL", "Bash"],
            "Backend Frameworks": ["FastAPI", "Django", "Flask", "Celery"],
            "Databases & Messaging": ["PostgreSQL", "Redis", "MongoDB", "RabbitMQ"],
            "Architecture": ["REST APIs", "GraphQL", "Microservices", "System Design", "Event-Driven"],
            "Cloud & DevOps": ["AWS", "Docker", "Kubernetes", "Nginx", "GitHub Actions"],
        },
        "clients": {
            "Spreetail": [
                "Spreetail is a US e-commerce logistics company. They were losing millions in carrier claims because the filing process with OnTrac was manual and error-prone. Built a scheduled FastAPI pipeline that pulls claim data from multiple logistics APIs, validates everything with Pydantic, and files claims automatically with retry logic. Recovered millions annually.",
                "Their ops team was manually reading inbound emails, figuring out what each one was about, and routing them to the right department. Built Python microservices that parse email content, extract intent with NLP, route tickets, and auto-respond to routine queries -- no human needed for most of it.",
                "Lost packages were a constant problem and the resolution process was reactive. Built a state-machine workflow engine in FastAPI with Redis that monitors logistics endpoints, tracks item lifecycle events, and runs resolution steps automatically with full audit logging.",
                "Owned the core API layer across all systems -- high-throughput REST APIs serving 10K+ RPM, PostgreSQL connection pooling and query optimization, Docker-based CI/CD on AWS.",
            ],
            "Meridian Health Group": [
                "Meridian is a UK healthcare provider that needed a modern API layer for electronic health records. Their existing system didn't meet HIPAA requirements. Built a FastAPI microservices architecture with field-level encryption, consent-based data sharing, and audit trails that passed compliance review.",
                "Patient vitals from IoT medical devices were being collected but nobody was monitoring them in real time. Built an event-driven service with FastAPI and Redis Streams that processes vitals as they come in and triggers clinical alerts within 2 seconds when thresholds are breached.",
                "Their 12+ hospital systems needed to exchange data but each spoke a different protocol. Built an HL7/FHIR message broker with Python and RabbitMQ that handles reliable delivery, dead-letter queues, and automatic retries across all systems.",
            ],
            "AutoVerse GmbH": [
                "AutoVerse is a German connected-car company with 50K+ vehicles streaming sensor data across Europe. They needed to ingest 100M+ OBD-II and CAN bus events daily without dropping data. Built a FastAPI ingestion service with asyncio and PostgreSQL COPY protocol -- batch processing with uvloop gets sustained 50K events/second at P99 latency under 15ms.",
                "Firmware updates to vehicles had to be rolled out carefully -- a bad update could brick a car. Built an OTA update system with Django and Celery that manages staged rollouts across 12 EU markets with semantic versioning, A/B deployment groups, automatic rollback on error spikes, and delivery confirmation via MQTT.",
                "The mobile app needed to control vehicles remotely -- lock/unlock, climate pre-conditioning, horn and flash. Built a secure command API in FastAPI with mTLS authentication, certificate pinning, and command queuing for offline vehicles.",
            ],
            "Apex Financial Corp": [
                "Apex is a US trading firm. Their order management system needed to route trades across NYSE, NASDAQ, and LSE with minimal latency. Built a FastAPI backend handling smart order routing, partial fills, and T+1 settlement at sub-50ms P99 latency with immutable audit logging to PostgreSQL.",
                "Portfolio risk calculations were too slow -- a full VaR computation across 10K+ positions took 45 seconds. Built a distributed computation service with Celery workers and Redis that runs Monte Carlo VaR, Greeks, and stress scenarios in parallel with intelligent caching. Cut it to 8 seconds.",
                "SEC and FINRA auditors needed to reconstruct complete transaction histories on demand. Built an event-sourcing service in FastAPI and PostgreSQL that captures every trade modification, approval, and system access event immutably -- supports sub-second historical queries for audit requests.",
            ],
            "NordTech Solutions": [
                "NordTech is a Dutch enterprise SaaS company serving 200+ clients. Each tenant needs isolated data and configuration but the backend had to scale horizontally. Built the multi-tenant backend in Django with PostgreSQL schema-level isolation -- one schema per tenant, independent migrations, and connection-pooled routing middleware.",
                "They had 20+ internal microservices with no unified entry point -- each had its own auth, rate limiting, and docs. Built a centralized API gateway in FastAPI that handles JWT and API key auth, rate limiting, circuit breakers, OpenAPI doc aggregation, and Prometheus metrics for all services.",
                "Long-running tenant operations -- bulk imports, report generation, data migrations -- were blocking request threads and timing out. Built a distributed job framework with Celery and Redis using priority queuing, WebSocket progress notifications, and automatic retry with exponential backoff.",
            ],
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    "cloud_devops_engineer": {
        "title": "Software Developer -- Cloud & DevOps",
        "summary": (
            "Cloud and DevOps engineer who keeps production running. I design AWS infrastructure, "
            "build CI/CD pipelines, containerize services with Docker and Kubernetes, and set up "
            "monitoring so problems get caught before users notice. Most of my work is making "
            "deployments faster, infrastructure cheaper, and systems more reliable."
        ),
        "skills": {
            "Cloud Platforms": ["AWS", "Infrastructure as Code"],
            "Containers": ["Docker", "Kubernetes", "Helm", "Docker Compose"],
            "CI/CD & Automation": ["GitHub Actions", "Jenkins", "Terraform", "Ansible"],
            "Monitoring": ["Prometheus", "Grafana", "CloudWatch", "ELK Stack"],
            "Languages & Tools": ["Python", "Bash", "Linux", "Nginx", "Git"],
        },
        "clients": {
            "Spreetail": [
                "Spreetail is a US e-commerce logistics company running several automation systems that need to be up 24/7. Owned the AWS infrastructure -- EC2, S3, RDS, ECS -- with auto-scaling and load balancing. Maintained 99.9% uptime while cutting monthly infra costs by 30%.",
                "Releases used to take days because everything was manual -- build, test, deploy. Set up end-to-end CI/CD with GitHub Actions and Docker for all backend services. Releases now take under 30 minutes with zero-downtime deployments.",
                "Python microservices were running directly on VMs with no isolation. Containerized everything with Docker, deployed on ECS with auto-scaling, and added health checks, log aggregation, and rolling updates.",
                "When things broke, the team scrambled because there was no monitoring. Set up Prometheus, Grafana, and CloudWatch with alerting for all critical metrics. Wrote runbooks that cut mean time to resolution by 60%.",
            ],
            "Meridian Health Group": [
                "Meridian is a UK healthcare provider. Their AWS setup didn't meet HIPAA requirements -- no VPC isolation, no encryption enforcement, no compliance scanning. Redesigned the infrastructure with VPC isolation, encryption at rest and in transit, and automated compliance checks using AWS Config and Security Hub.",
                "They had no disaster recovery plan -- a single AZ outage would take down patient systems. Built a multi-AZ DR architecture with automated failover, hitting RPO of 5 minutes and RTO of 15 minutes.",
                "New environments were provisioned manually, taking 2 days each. Migrated everything to Terraform so environments are reproducible and spin up in 30 minutes.",
            ],
            "AutoVerse GmbH": [
                "AutoVerse is a German connected-car company with 50K+ vehicles and 50+ service centers. They needed edge computing across 8 manufacturing facilities to handle telemetry and firmware updates. Set up AWS IoT Core with Greengrass edge nodes, managing OTA deployments, 100M daily telemetry events, and device shadow state sync.",
                "Telemetry ingestion loads spike during European driving hours -- mornings and evenings. Built auto-scaling Kubernetes clusters on EKS with Karpenter node provisioning and custom HPA policies tied to Kafka consumer lag. The cluster scales from 5 to 40 pods automatically when traffic peaks.",
                "AWS costs were growing unchecked. Did a full infrastructure audit and implemented Reserved Instances, Spot Fleet for batch jobs, and S3 Intelligent Tiering -- cut monthly spend by EUR 15K (28%) without touching performance SLAs.",
            ],
            "Apex Financial Corp": [
                "Apex is a US trading firm where microseconds matter. Their infrastructure wasn't optimized for low-latency workloads. Designed AWS infra with cluster placement groups, ENA-enhanced networking, dedicated hosts, and kernel bypass (DPDK) on c6in instances -- got consistent sub-100-microsecond network latency between order management and exchange gateways.",
                "SOX and PCI-DSS compliance required immutable audit trails and continuous compliance verification. Set up CloudTrail, S3 Object Lock with governance mode, and AWS Config rules with automated remediation. Runs quarterly automated penetration testing to verify everything stays compliant.",
                "Database credentials, API keys, and TLS certificates were hardcoded across the trading infrastructure. Implemented HashiCorp Vault with automated rotation for all secrets -- eliminated hardcoded credentials and achieved PCI-DSS compliance for credential handling.",
            ],
            "NordTech Solutions": [
                "NordTech is a Dutch enterprise SaaS company with 200+ clients that each need isolated infrastructure. Built a multi-tenant Kubernetes platform on EKS with namespace isolation, resource quotas, Calico network policies, and OPA Gatekeeper admission controllers -- each tenant gets guaranteed resources and network segmentation.",
                "Deploying 20+ microservices was manual and error-prone. Implemented ArgoCD-based GitOps with automated canary deployments, progressive traffic shifting, auto-rollback on SLO breaches, and Slack approval gates for production promotions.",
                "Cloud costs were opaque -- nobody knew which tenant was costing what. Implemented FinOps practices with automated resource tagging, per-tenant cost allocation dashboards, and Spot Instance strategies for batch workloads. Cut overall cloud spend by 35%.",
            ],
        },
    },
    # ═══════════════════════════════════════════════════════════════════════════
    "software_tester_qa": {
        "title": "Software Developer -- QA & Testing",
        "summary": (
            "QA engineer who writes automated tests and makes sure things don't break in production. "
            "pytest, Selenium, Playwright -- I build test suites that run in CI and catch regressions "
            "before they ship. I care about the boring stuff: coverage, contract tests, "
            "load testing, and making sure the release pipeline blocks on real failures."
        ),
        "skills": {
            "Testing Frameworks": ["pytest", "Selenium", "Playwright", "unittest"],
            "API & Performance": ["Postman", "API Testing", "Load Testing", "Locust"],
            "Languages": ["Python", "SQL", "Bash"],
            "CI/CD & Tools": ["GitHub Actions", "Jenkins", "Docker", "Git", "Jira"],
            "Methodologies": ["Test Cases", "Regression Testing", "Integration Testing", "TDD", "BDD"],
        },
        "clients": {
            "Spreetail": [
                "Spreetail is a US e-commerce logistics company. Their carrier claim pipeline with OnTrac had no automated tests -- bugs made it to production regularly. Built comprehensive pytest suites covering unit tests, integration tests, and end-to-end API tests. Got coverage above 95% and caught 30+ critical bugs before they hit production.",
                "They were rolling out an AI email resolution system with NLP components that needed thorough testing. Built test frameworks including mock-based unit tests for the NLP pieces, API contract tests for microservice interfaces, and regression suites that run on every PR through GitHub Actions.",
                "The Lost-in-Transit tracking dashboard had complex state machine logic that was hard to test manually. Built Selenium and Playwright end-to-end suites that validate state transitions, API data integrity, and cross-browser UI rendering.",
                "Test suites existed but weren't wired into the deployment pipeline -- people just ran them sometimes. Integrated everything into GitHub Actions with parallel execution, coverage reports, and automatic PR blocking on failures. Production bug rate dropped 70%.",
            ],
            "Meridian Health Group": [
                "Meridian is a UK healthcare provider handling sensitive patient data. Their APIs needed to pass HIPAA compliance and nobody had systematically tested the security surface. Built security-focused test suites covering authentication, authorization, and data encryption across all patient data endpoints, including targeted penetration testing.",
                "Clinical workflows -- patient registration, appointment scheduling, prescriptions -- were being released bi-weekly with no automated regression coverage. Built Playwright suites covering all critical paths, ensuring zero regressions across releases.",
                "Their 12+ hospital systems exchange data through HL7/FHIR interfaces, and upstream changes kept breaking integrations. Implemented contract testing that catches breaking API changes before they deploy.",
            ],
            "AutoVerse GmbH": [
                "AutoVerse is a German connected-car company. Their telemetry pipeline processes data from raw CAN bus sensors through Spark transformations into a Snowflake warehouse -- and bad data was reaching dashboards undetected. Built validation frameworks with pytest and Great Expectations that test data accuracy at every stage. Automated daily reconciliation checks that catch quality issues before they propagate.",
                "Firmware OTA updates go out to 50K+ vehicles and a bad update can brick a car. Built end-to-end test suites for the entire OTA workflow -- rollback scenarios, version compatibility matrices across 30+ vehicle models, staged rollout verification, and MQTT delivery confirmation.",
                "The vehicle command APIs (lock/unlock, climate control) are safety-critical. Ran comprehensive security testing with OWASP ZAP and custom pytest scripts to validate mTLS certificate pinning, authorization chains, and replay attack prevention.",
            ],
            "Apex Financial Corp": [
                "Apex is a US trading firm where a bug in the order execution path means real money lost. Built pytest suites for the trade execution API covering smart order routing, partial fill handling, cross-exchange settlement reconciliation, and regulatory compliance checks -- 400+ parameterized test cases with 100% critical path coverage.",
                "They had no idea how the system would behave under peak trading load. Built Locust load tests simulating 10K+ concurrent traders with realistic order patterns -- market orders, limit orders, cancellations. Found and fixed 5 critical bottlenecks in connection pooling and serialization that improved peak throughput by 60%.",
                "Regulatory compliance (MiFID II, Dodd-Frank, SOX) required verified correctness. Built automated compliance test suites that validate best-execution requirements, reporting accuracy, and audit trail completeness -- integrated into the release pipeline so non-compliant code can't reach production.",
            ],
            "NordTech Solutions": [
                "NordTech is a Dutch enterprise SaaS company with 200+ tenants. The biggest risk is data leaking between tenants. Built automated test suites that verify isolation -- cross-tenant API access prevention, schema isolation validation, resource quota enforcement, network policy checks. Runs nightly across all tenant environments.",
                "With 500+ API endpoints across 20 microservices, manual regression testing was impossible. Built a pytest + requests framework with response schema validation, backward compatibility checks, and automatic performance regression detection. Integrated into the ArgoCD GitOps pipeline with auto-rollback on test failures.",
                "Nobody knew what would happen if a service went down or the database became unreachable. Implemented chaos testing with Litmus and custom Python scripts -- simulated service failures, network partitions, and DB outages. Validated graceful degradation and recovery procedures, improving the system resilience score from 72% to 95%.",
            ],
        },
    },
}


def update_roles():
    db = NeonSessionLocal()
    try:
        for key, data in ROLE_DATA.items():
            role = db.query(Role).filter(Role.key == key).first()
            if not role:
                print(f"  SKIP {key} (not found)")
                continue

            role.title = data["title"]
            role.previous_title = ""
            role.summary = data["summary"]

            # Update skills
            for s in role.skills:
                db.delete(s)
            db.flush()
            for i, (cat, skills) in enumerate(data["skills"].items()):
                db.add(RoleSkill(role_id=role.id, category=cat, skills=skills, sort_order=i))

            # Update experience (one entry per client)
            for e in role.experiences:
                db.delete(e)
            db.flush()
            for client_meta in CLIENTS:
                cname = client_meta["name"]
                bullets = data["clients"].get(cname, [])
                if not bullets:
                    continue
                db.add(RoleExperience(
                    role_id=role.id,
                    position_index=client_meta["pos"],
                    bullets=bullets,
                    client_name=cname,
                    client_location=client_meta["location"],
                    min_years=client_meta["min_years"],
                ))

            print(f"  OK {key}: {data['title']} ({len(data['clients'])} clients)")

        db.commit()
        print("\nAll roles updated.")
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_roles()
