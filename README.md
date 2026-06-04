# Email Resume Bulk Sender

This workspace contains a FastAPI backend and a Next.js frontend for sending bulk emails with resume attachments. 

## Setup

### Backend

1. Change into the backend folder:
   ```bash
   cd backend
   ```
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and configure SMTP:
   ```bash
   cp .env.example .env
   ```

### Frontend

1. Change into the frontend folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```

## Running the app

1. Start the backend from the `backend` folder:
   ```bash
   uvicorn main:app --reload
   ```
2. Start the frontend from the `frontend` folder:
   ```bash
   npm run dev
   ```
3. Open the UI at `http://localhost:3000`

## How it works

- Add records with recipient email, message type, and resume attachment.
- Click Execute to send all pending emails.
- After execution, the backend removes pending records and attached files.
