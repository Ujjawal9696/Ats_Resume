# 🚀 Deployment Guide — ATSPro ATS Resume Scorer

## 📋 Prerequisites

- Python 3.10+
- Supabase project (free tier works)
- Groq API key (free tier works)
- Git

---

## 🚂 Option 1: Railway (Recommended — Easiest)

### Deploy Backend (FastAPI)

1. Push your code to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select your repo
4. Set **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from your `.env`
6. Deploy → copy the generated URL (e.g. `https://ats-backend.railway.app`)

### Deploy Frontend (Streamlit)

1. New Service in same project → Deploy from GitHub → same repo
2. Set **Start Command**: `streamlit run frontend/streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
3. Add env var: `BACKEND_URL=https://your-backend.railway.app`
4. Deploy → access at generated URL

---

## 🎨 Option 2: Render (Free Tier)

### Backend Service
```yaml
# render.yaml
services:
  - type: web
    name: ats-backend
    runtime: python
    buildCommand: pip install -r requirements.txt && python -m spacy download en_core_web_md
    startCommand: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: GROQ_API_KEY
        sync: false
      - key: SECRET_KEY
        sync: false

  - type: web
    name: ats-frontend
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run frontend/streamlit_app.py --server.port $PORT --server.address 0.0.0.0
    envVars:
      - key: BACKEND_URL
        value: https://ats-backend.onrender.com
```

---

## 🐳 Option 3: Docker Compose (Self-hosted / VPS)

### docker-compose.yml
```yaml
version: "3.9"
services:
  backend:
    build: .
    command: uvicorn backend.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./uploads:/app/uploads
      - ./reports:/app/reports
    restart: unless-stopped

  frontend:
    build: .
    command: streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
    ports:
      - "8501:8501"
    env_file: .env
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      - backend
    restart: unless-stopped
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -m spacy download en_core_web_md

COPY . .
RUN mkdir -p uploads reports logs
```

```bash
# Deploy
docker-compose up -d --build
```

---

## ☁️ Option 4: AWS EC2

```bash
# Launch Ubuntu 22.04 EC2 instance (t3.medium recommended)
# SSH into instance

# Install Python & dependencies
sudo apt update
sudo apt install python3.11 python3.11-venv nginx certbot -y

# Clone & setup
git clone https://github.com/your-username/ats-scorer.git
cd ats-scorer
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_md

# Configure environment
cp .env.example .env
nano .env  # Fill in your keys

# Run with systemd
sudo nano /etc/systemd/system/ats-backend.service
```

```ini
[Unit]
Description=ATS Resume Scorer Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/ats-scorer
ExecStart=/home/ubuntu/ats-scorer/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable ats-backend
sudo systemctl start ats-backend

# Setup Nginx reverse proxy
sudo nano /etc/nginx/sites-available/ats
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:8501/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ats /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# SSL with Let's Encrypt
sudo certbot --nginx -d your-domain.com
```

---

## 🌍 Google Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/ats-backend

# Deploy backend
gcloud run deploy ats-backend \
  --image gcr.io/PROJECT_ID/ats-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --command "uvicorn backend.main:app --host 0.0.0.0 --port 8080" \
  --set-env-vars GROQ_API_KEY=xxx,SUPABASE_URL=xxx,SUPABASE_KEY=xxx

# Deploy frontend
gcloud run deploy ats-frontend \
  --image gcr.io/PROJECT_ID/ats-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --command "streamlit run frontend/streamlit_app.py --server.port 8080" \
  --set-env-vars BACKEND_URL=https://ats-backend-xxx.run.app
```

---

## 🔧 Post-Deployment Checklist

- [ ] `.env` configured with all API keys
- [ ] Supabase `schema.sql` run in SQL Editor
- [ ] Supabase RLS policies active
- [ ] spaCy model downloaded (`en_core_web_md`)
- [ ] `BACKEND_URL` in frontend env points to deployed backend
- [ ] `FRONTEND_URL` in backend env points to deployed frontend
- [ ] Google OAuth redirect URI updated in Google Console
- [ ] Test signup → resume upload → analysis → PDF download flow

---

## 🐛 Troubleshooting

| Issue | Fix |
|---|---|
| `spacy model not found` | Run `python -m spacy download en_core_web_md` |
| `Supabase connection error` | Check `SUPABASE_URL` and `SUPABASE_KEY` in `.env` |
| `Groq API error` | Verify `GROQ_API_KEY` and check usage limits |
| `Resume parse failed` | Ensure file is not image-based PDF; try DOCX |
| `WeasyPrint error` | Install GTK libs or use HTML fallback |
| `CORS error` | Ensure `BACKEND_URL` matches actual backend address |
