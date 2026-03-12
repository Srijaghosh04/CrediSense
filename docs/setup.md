# CreditSense Setup

## Prerequisites

- Python 3.10+
- Node.js 20.19+
- Supabase CLI (`brew install supabase/tap/supabase`)
- A [Supabase](https://supabase.com) account (free)
- A [Google Gemini API Key](https://aistudio.google.com/apikey) (free)

---

## 1. Backend (FastAPI Server)

### Install Dependencies

```bash
cd servers
python -m venv venv
source venv/bin/activate        # macOS/Linux
# .\venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your credentials:
```
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_KEY=<anon-public-key>
SUPABASE_JWT_SECRET=<jwt-secret>
GEMINI_API_KEY=<your-gemini-key>
```

> Get Supabase keys from: Dashboard → Settings → API
> Get Gemini key from: [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### Run the Server

```bash
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`. API docs at `http://localhost:8000/docs`.

---

## 2. Database (Supabase)

### First-Time Setup

```bash
cd servers
supabase login
supabase init
supabase link --project-ref <your-project-ref>
supabase db push
```

This creates all 7 tables (`applications`, `ingested_documents`, `research_results`, `risk_alerts`, `primary_insights`, `cam_reports`) with enums, foreign keys, and triggers.

### After Project Pause (Restoring Database)

If Supabase pauses your project after inactivity:

```bash
# Create a new project on Supabase dashboard, then:
supabase link --project-ref <new-project-ref>
supabase db push
# Update .env with the new SUPABASE_URL and keys
```

### Adding New Migrations

```bash
supabase migration new <migration_name>
# Edit the new .sql file in supabase/migrations/
supabase db push
```

---

## 3. Authentication

### How It Works

1. Frontend authenticates users via **Supabase Auth** (Google OAuth)
2. Supabase returns a **JWT token** signed with `SUPABASE_JWT_SECRET`
3. Frontend sends the token as `Authorization: Bearer <token>` with every API request
4. Backend middleware (`authentication/auth.py`) verifies the JWT before processing

### Enable Google OAuth

1. Go to **Supabase Dashboard → Authentication → Providers → Google**
2. Create OAuth credentials at [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
3. Add the Client ID and Secret in Supabase

### Protected Routes

| Route | Auth Required |
|---|---|
| `GET /api/v1/health` | ❌ Public |
| All other routes | ✅ Bearer token required |

### Development Mode

If `SUPABASE_JWT_SECRET` is not set in `.env`, authentication is **skipped** — useful for local testing via Swagger UI.

---

## 4. Frontend (React/Vite)

```bash
cd website
npm install
npm run dev
```

Opens at `http://localhost:5173`.

---

## 5. Testing the API

Open `http://localhost:8000/docs` (Swagger UI) and test in this order:

### Step 1: Create an Application
```
POST /api/v1/applications
Body: {
  "company_name": "Zenith Metals Ltd",
  "pan": "AABCZ1234F",
  "gstin": "27AABCZ1234F1Z5",
  "sector": "Industrials"
}
```
→ Copy the returned `id` (e.g., `APP-a3b8d1`)

### Step 2: Upload a PDF (Annual Report)
```
POST /api/v1/ingest/document
Form: file=<pdf>, application_id=APP-a3b8d1, file_type=annual_report
```
→ Returns extracted financials (revenue, debt, equity, covenants)

### Step 3: Upload Structured Data (GST/Bank Statement)
```
POST /api/v1/ingest/structured
Form: file=<csv>, application_id=APP-a3b8d1, file_type=gst_filing
```
→ Returns anomaly detection results (GSTR mismatches, circular trading)

### Step 4: Add Primary Insights
```
POST /api/v1/engine/primary-insights
Body: {
  "application_id": "APP-a3b8d1",
  "category": "site_visit",
  "note": "Factory operating at 40% capacity",
  "impact": "negative"
}
```

### Step 5: Generate CAM Report
```
POST /api/v1/engine/generate-cam?application_id=APP-a3b8d1
```

---

## Project Structure

```
CrediSense/
├── servers/                    # FastAPI Backend
│   ├── api/routes.py           # 12 API endpoints
│   ├── authentication/auth.py  # JWT middleware
│   ├── models/schemas.py       # Pydantic models (15 models, 8 enums)
│   ├── services/
│   │   ├── ingestor.py         # PDF parsing + CSV anomaly detection
│   │   ├── researcher.py       # Web research agent
│   │   └── engine.py           # CAM generation engine
│   ├── store.py                # Supabase database connection
│   ├── supabase/migrations/    # SQL migrations (git-tracked)
│   ├── main.py                 # FastAPI app entry point
│   ├── .env.example            # Environment variable template
│   └── requirements.txt        # Python dependencies
├── website/                    # React/Vite Frontend
└── docs/                       # Documentation + sample data
```
