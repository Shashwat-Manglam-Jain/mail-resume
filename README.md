# Email Resume Bulk Sender

A self-hosted tool that generates role-specific ATS resumes and bulk-sends them to recruiters. You configure your profile once, pick a role, and the app builds a tailored resume (PDF + LaTeX) and emails it -- all from a single dark-themed UI.

## Features

- **10 Python-focused resume roles** stored in a Neon PostgreSQL database, fully editable from the UI
- **Multi-client experience model**: one employer (CubexO), multiple clients shown based on years of experience (1-10 scale)
- **ATS-friendly output**: both PDF (fpdf2) and LaTeX (roboto font, `\resumeSubheading` macros)
- **Mail queue**: add recipients, preview the email, validate addresses (syntax + MX + SMTP), send one-by-one or all at once
- **Email validation**: typo detection, disposable domain blocking, MX record checks, catch-all detection, SMTP RCPT TO verification
- **Resume Builder UI**: edit roles, skills, client experience, achievements directly in the browser
- **Profile management**: edit your personal details in-app (stored in DB, `.env` as fallback)
- **Experience-based filtering**: set experience years (1-10) per email -- the resume automatically shows the right number of client engagements
- **Bulk generation CLI**: generate all resumes from the command line
- **Vercel-deployable backend** (optional)

## Architecture

```
email-resume/
  backend/             FastAPI (Python 3.12)
    main.py            API endpoints
    models.py          SQLite model (mail queue)
    neon_models.py     PostgreSQL models (profile, roles, skills, experience)
    database.py        Dual DB connections (SQLite + Neon)
    resume_templates.py  PDF + LaTeX generators
    email_checker.py   8-step email validation
    update_roles.py    Seed/update all 10 roles with client data
    seed_roles.py      Initial DB seeder
    generate_all_resumes.py  CLI batch generator
    test_main.py       155 tests
  frontend/            Next.js 14 (Pages Router)
    pages/index.js     Single-page app (Mail Queue + Resume Builder tabs)
    styles/globals.css  Dark theme
```

### Databases

| Database | Engine | Purpose | Data |
|----------|--------|---------|------|
| Local SQLite | `records.db` | Mail queue | Queued email records |
| Neon PostgreSQL | Remote | Resume data | Profile, roles, skills, client experience, achievements, focus areas |

## Prerequisites

- Python 3.10+
- Node.js 18+
- A [Neon](https://neon.tech) PostgreSQL database (free tier works)
- Gmail account with [App Password](https://myaccount.google.com/apppasswords) (or any SMTP server)

## Setup

### 1. Clone and configure

```bash
git clone <repo-url>
cd email-resume
```

### 2. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create your `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your details:

```env
# Required -- SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your-16-char-app-password    # NOT your Gmail password
SMTP_FROM=you@gmail.com

# Required -- Neon PostgreSQL
NEON_DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/dbname?sslmode=require

# Your profile (fallback -- you can also edit these in the UI)
YOUR_NAME=Your Name
YOUR_EMAIL=you@example.com
YOUR_PHONE=+91 98765 43210
YOUR_LOCATION=City, India
YOUR_EDUCATION=B.Tech Computer Science, Your College
YOUR_GRADUATION_YEAR=2022 -- 2026
```

See `.env.example` for the full list of variables.

### 3. Initialize the database

Run Alembic migrations to create the Neon tables:

```bash
cd backend
alembic upgrade head
```

Seed the 10 roles with client experience data:

```bash
python seed_roles.py
```

This populates the database with roles, skills, and experience bullets. To update roles later (e.g. after editing `update_roles.py`):

```bash
python update_roles.py
```

### 4. Frontend

```bash
cd frontend
npm install
```

## Running

Start both servers (in separate terminals):

```bash
# Terminal 1 -- Backend (port 8000)
cd backend
source .venv/bin/activate
uvicorn main:app --reload

# Terminal 2 -- Frontend (port 3000)
cd frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Usage

### Mail Queue tab

1. Select a **role** from the dropdown (e.g. "Software Developer -- AI/ML")
2. Fill in **recipient email**, **HR name**, **company name**
3. Set **experience years** (1-10) -- this controls how many client engagements appear on the resume
4. Click **Add to Queue**
5. Preview the email with **Preview Message**
6. Send individually or use **Send All**

### Resume Builder tab

- **Left panel**: list of all roles -- click to edit
- **Right panel**: edit summary, skills, client experience bullets, achievements
- **Download section**: Preview PDF, Download PDF, or Download LaTeX with experience years selector
- **Edit Profile**: update your personal details (name, email, education, etc.)
- **Create Role**: add new custom roles

### CLI: Generate all resumes

```bash
cd backend
python generate_all_resumes.py
```

With overrides:

```bash
python generate_all_resumes.py \
  --name "Your Name" \
  --email "you@example.com" \
  --experience-years 6 \
  --output ./my_resumes
```

## Available Roles

| # | Role Key | Resume Title |
|---|----------|-------------|
| 1 | `software_engineer` | Software Developer |
| 2 | `ai_ml_engineer` | Software Developer -- AI/ML |
| 3 | `data_engineer` | Software Developer -- Data Engineering |
| 4 | `data_scientist` | Software Developer -- Data Science |
| 5 | `data_analyst_bi` | Software Developer -- Data Analytics |
| 6 | `business_analyst` | Business Analyst |
| 7 | `full_stack_developer` | Full-Stack Python Developer |
| 8 | `backend_engineer` | Back-End Developer |
| 9 | `cloud_devops_engineer` | Software Developer -- Cloud & DevOps |
| 10 | `software_tester_qa` | Software Developer -- QA & Testing |

You can add more roles via the UI or by editing `update_roles.py`.

## Multi-Client Experience Model

The resume uses a single employer (CubexO Software Solutions) with multiple client engagements. Which clients appear depends on the `experience_years` setting:

| Client | Location | Min Years | Shows When |
|--------|----------|-----------|------------|
| Spreetail | US | 1 | Always |
| Meridian Health Group | UK | 3 | 3+ years |
| AutoVerse GmbH | Germany | 5 | 5+ years |
| Apex Financial Corp | US | 7 | 7+ years |
| NordTech Solutions | Netherlands | 9 | 9+ years |

Date ranges are computed automatically, working backwards from today.

## API Reference

### Profile

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/profile` | Get current profile (DB with .env fallback) |
| `PUT` | `/profile` | Update profile fields |

### Roles

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/roles` | List all active roles (summary) |
| `GET` | `/roles/{key}` | Full role detail (skills, clients, achievements) |
| `POST` | `/roles` | Create a new role |
| `PUT` | `/roles/{key}` | Update role fields (title, summary, coursework) |
| `DELETE` | `/roles/{key}` | Delete a role and all its data |
| `GET` | `/roles/{key}/skills` | Get categorized skills |
| `PUT` | `/roles/{key}/skills` | Replace all skill categories |
| `PUT` | `/roles/{key}/experience` | Replace client experience entries |
| `PUT` | `/roles/{key}/achievements` | Replace achievements |
| `PUT` | `/roles/{key}/focus` | Replace focus areas |

### Mail Queue

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/records` | List all queued records |
| `POST` | `/records` | Add a record (validates email) |
| `PUT` | `/records/{id}` | Update a record |
| `DELETE` | `/records/{id}` | Delete a record |
| `DELETE` | `/records` | Clear all records |
| `PATCH` | `/records/{id}/cc` | Update CC emails |
| `POST` | `/records/{id}/send` | Send one email |
| `POST` | `/send-all` | Send all queued emails |
| `POST` | `/message-preview` | Preview email subject + body |
| `POST` | `/validate-email` | Validate an email address |

### Resumes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/resume/{key}/pdf?experience_years=4` | Download PDF resume |
| `GET` | `/resume/{key}/latex?experience_years=4` | Download LaTeX source |
| `POST` | `/resume/compile-latex` | Compile raw LaTeX to PDF |
| `GET` | `/resumes/download-all` | Download all resumes as ZIP |
| `POST` | `/resumes/generate` | Regenerate all cached PDFs |
| `GET` | `/resumes/status` | Check resume cache status |

## Email Validation

Every email address goes through an 8-step validation pipeline before being queued:

1. **Syntax check** -- RFC-compliant format
2. **Typo detection** -- catches `gmial.com`, `yaho.com`, etc. (60+ known typos)
3. **Disposable domain** -- blocks `mailinator.com`, `yopmail.com`, etc.
4. **Role address** -- warns on `noreply@`, `postmaster@`, etc.
5. **MX records** -- verifies the domain can receive email
6. **DNS health** -- checks A/AAAA records
7. **Catch-all detection** -- detects domains that accept any address
8. **SMTP RCPT TO** -- verifies the specific mailbox exists

## Testing

```bash
cd backend
python -m pytest test_main.py -v
```

155 tests covering: record CRUD, send flows, SMTP behavior, email validation, message compose, resume generation (PDF + LaTeX), role CRUD, profile management, experience filtering, template helpers, and edge cases.

## Gmail SMTP Setup

1. Enable 2-Step Verification on your Google account
2. Go to [App Passwords](https://myaccount.google.com/apppasswords)
3. Generate a new App Password (select "Mail" and your device)
4. Copy the 16-character password into `.env` as `SMTP_PASSWORD`

**Do NOT use your Gmail account password.** App Passwords are separate credentials that bypass 2FA for SMTP.

If you get a `535 Authentication failed` error, your App Password may have expired -- generate a new one.

## Deployment (Vercel)

The backend includes a `vercel.json` for serverless deployment:

```bash
cd backend
vercel deploy
```

Set environment variables in the Vercel dashboard (same as `.env`). Add `VERCEL=1` to enable Vercel mode (uses `/tmp` for SQLite and resume cache).

Set `FRONTEND_URL` to your frontend domain for CORS:

```env
FRONTEND_URL=https://your-app.vercel.app
```

## Project Structure Detail

```
backend/
  main.py                  FastAPI app -- all API endpoints
  models.py                SQLite Record model (mail queue)
  neon_models.py           Neon PostgreSQL models:
                             Profile, Role, RoleSkill, RoleExperience,
                             RoleAchievement, RoleFocusArea
  database.py              SQLite + Neon DB connections
  resume_templates.py      PDF generator (_ResumePDF), LaTeX generator,
                             DB-to-dict converters, date computation
  email_checker.py         8-step email validation pipeline
  update_roles.py          Update all 10 roles (skills + 5 clients each)
  seed_roles.py            Initial database seeder
  generate_all_resumes.py  CLI tool to batch-generate PDFs + LaTeX
  test_main.py             Comprehensive test suite (155 tests)
  alembic/                 Database migrations
  alembic.ini              Alembic config (reads NEON_DATABASE_URL from .env)
  requirements.txt         Python dependencies
  .env.example             Template for environment variables
  vercel.json              Vercel deployment config
  api/index.py             Vercel entry point

frontend/
  pages/
    index.js               Single-page app (Mail Queue + Resume Builder)
    _app.js                Next.js app wrapper
    _document.js           Custom document head
  styles/
    globals.css            Dark theme stylesheet
  package.json             Node dependencies (Next.js 14, React 18)
```

## License

Private project.
