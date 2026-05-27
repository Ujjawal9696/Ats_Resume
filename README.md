# 🎯 ATSPro — AI-Powered ATS Resume Scorer

<div align="center">

![ATS Score](https://img.shields.io/badge/ATS-Scoring-667eea?style=for-the-badge&logo=target)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=for-the-badge&logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.33-FF4B4B?style=for-the-badge&logo=streamlit)
![Groq](https://img.shields.io/badge/Groq-Llama3-F55036?style=for-the-badge)
![Supabase](https://img.shields.io/badge/Supabase-Auth+DB-3ECF8E?style=for-the-badge&logo=supabase)

**Production-ready AI Resume Intelligence Platform**  
*Upload resumes · Match against JDs · Get AI-powered improvement suggestions*

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **ATS Scoring** | 0–100 ATS compatibility score using TF-IDF + cosine similarity |
| 🧠 **Semantic Match** | Sentence Transformers (all-MiniLM-L6-v2) for deep semantic analysis |
| ⚡ **Skill Extraction** | 200+ tech/soft skills database with spaCy NLP |
| 🤖 **AI Suggestions** | Groq Llama 3 (70B) for personalized improvement tips |
| 📊 **Rich Dashboard** | Radar charts, score gauges, trend lines, skill breakdowns |
| 📥 **PDF Export** | Downloadable PDF analysis reports via WeasyPrint |
| 🔐 **Auth** | Email/password + Google OAuth via Supabase |
| 📋 **History** | Save and browse all past analyses |
| 🌙 **Dark/Light Mode** | Premium SaaS UI with glassmorphism design |

---

## 🏗️ Architecture

```
ATS_SCORER/
├── backend/                  # FastAPI Backend
│   ├── main.py               # App entry point, routes registration
│   ├── config.py             # Pydantic settings (loads .env)
│   ├── auth/
│   │   └── jwt_handler.py    # JWT creation, verification, dependencies
│   ├── database/
│   │   ├── supabase_client.py  # Supabase client factory
│   │   └── schema.sql          # PostgreSQL schema + RLS policies
│   ├── models/
│   │   └── schemas.py        # Pydantic request/response models
│   ├── nlp/
│   │   ├── nlp_pipeline.py   # spaCy + Sentence Transformers + TF-IDF engine
│   │   └── skills_database.py # 200+ skills for extraction
│   ├── routes/
│   │   ├── auth.py           # POST /auth/signup, /login, /google
│   │   ├── resume.py         # POST /resume/upload
│   │   ├── analysis.py       # POST /analyze/
│   │   ├── history.py        # GET /history/
│   │   └── report.py         # GET /report/{id}/generate
│   └── services/
│       ├── file_parser.py    # PDF/DOCX/DOC text extraction
│       ├── groq_service.py   # Groq Llama 3 AI suggestions
│       └── report_generator.py  # WeasyPrint PDF export
│
├── frontend/                 # Streamlit Frontend
│   ├── streamlit_app.py      # Main app, routing, session state
│   ├── auth/
│   │   └── auth_ui.py        # Login/signup/OAuth UI
│   ├── components/
│   │   └── sidebar.py        # Sidebar navigation
│   ├── pages/
│   │   ├── analyzer.py       # Main analysis workflow page
│   │   ├── dashboard.py      # Analytics dashboard
│   │   ├── history.py        # Analysis history browser
│   │   └── settings.py       # User preferences page
│   ├── charts/
│   │   └── visualizations.py # Plotly radar, gauge, bars, heatmap
│   └── styles/
│       └── theme.py          # Full CSS injection (dark/light mode)
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & Setup Environment

```bash
git clone https://github.com/your-username/ats-scorer.git
cd ATS_SCORER

# Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Download NLP Models

```bash
python -m spacy download en_core_web_md
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your actual keys
```

Required keys:
- `SUPABASE_URL` — from your Supabase project settings
- `SUPABASE_KEY` — anon/public key
- `SUPABASE_SERVICE_ROLE_KEY` — service role key (for admin ops)
- `GROQ_API_KEY` — from [console.groq.com](https://console.groq.com)
- `SECRET_KEY` — random 32+ char string (use `openssl rand -hex 32`)

### 4. Setup Supabase Database

1. Go to [supabase.com](https://supabase.com) → Your Project → SQL Editor
2. Paste and run the contents of `backend/database/schema.sql`
3. Enable Google OAuth in Authentication → Providers (optional)

Note: If you previously ran the schema, update your `public.profiles` table to remove the foreign-key constraint to `auth.users` (the schema included in this repo no longer enforces this). Re-run the `backend/database/schema.sql` or apply the migration in Supabase SQL editor.

### 5. Start the Backend

```bash
# Windows
start_backend.bat

# OR manually
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

### 6. Start the Frontend

```bash
# Windows
start_frontend.bat

# OR manually
python -m streamlit run frontend/streamlit_app.py --server.port 8501
```

Open: http://localhost:8501

---

## 🔑 Getting API Keys

### Supabase (Free)
1. Go to [supabase.com](https://supabase.com) → New Project
2. Settings → API → copy `URL` and `anon key`
3. Settings → API → copy `service_role` key

### Groq (Free Tier Available)
1. Go to [console.groq.com](https://console.groq.com)
2. API Keys → Create New Key

### Google OAuth (Optional)
1. [console.cloud.google.com](https://console.cloud.google.com) → New Project
2. APIs & Services → Credentials → OAuth 2.0 Client IDs
3. Add redirect URI: `http://localhost:8000/auth/google/callback`

---

## 📊 ATS Scoring Algorithm

The ATS score (0–100) is a weighted combination of:

| Component | Weight | Method |
|---|---|---|
| Semantic Similarity | 25% | Sentence Transformers cosine similarity |
| Skill Overlap | 25% | Matched skills / total JD skills |
| Keyword Match | 20% | TF-IDF keyword intersection |
| TF-IDF Similarity | 10% | Document-level TF-IDF cosine |
| Section Completeness | 10% | Key sections present/missing |
| Formatting Score | 10% | Heuristic formatting checks |

---

## 🧠 NLP Pipeline

```
Resume Text → Clean Text → Section Detection → Skill Extraction
                                               → TF-IDF Keywords
                                               → spaCy NER

JD Text     → Clean Text → Required Skills    → Keywords

Both Texts  → Sentence Transformers → Semantic Similarity (cosine)
           → TF-IDF Vectorizer     → TF-IDF Similarity (cosine)

All Scores  → Weighted ATS Score
           → Groq Llama 3 → AI Suggestions JSON
```

---

## 🌐 API Reference

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/signup` | Create account |
| POST | `/auth/login` | Login → JWT token |
| GET  | `/auth/google` | Google OAuth redirect |
| GET  | `/auth/me` | Get current user profile |
| POST | `/resume/upload` | Upload + parse resume file |
| GET  | `/resume/` | List user's resumes |
| POST | `/analyze/` | Run full ATS analysis |
| GET  | `/analyze/{id}` | Get specific analysis |
| GET  | `/history/` | Get analysis history |
| DELETE | `/history/{id}` | Delete an analysis |
| GET  | `/report/{id}/generate` | Generate PDF report |
| GET  | `/report/{id}/download/{file}` | Download PDF |

---

## 🐳 Docker Deployment

```bash
# Build and run
docker-compose up --build

# Backend on: http://localhost:8000
# Frontend on: http://localhost:8501
```

---

## ☁️ Cloud Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for full deployment guides to:
- Railway
- Render
- AWS EC2
- Google Cloud Run

---

## 🔒 Security

- All API keys stored in environment variables — never in code
- JWT authentication on all protected routes
- Supabase Row Level Security (RLS) — users see only their own data
- File validation: type + size checks before processing
- Input sanitization on all text fields

---

## 📝 License

MIT License — free for personal and commercial use.

---

<div align="center">
  Built with ❤️ using FastAPI + Streamlit + Groq + Supabase
</div>
