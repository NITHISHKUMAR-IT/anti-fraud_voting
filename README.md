# Secure Smart Voting Verification System (SSVVS)

Multi-layer biometric voter verification system with face recognition, fingerprint matching, and indelible ink detection.

---

## Tech Stack

| Layer | Tech |
|---|---|
| Frontend | React 18 + Vite + CSS Modules |
| Backend | FastAPI (Python 3.11) + SQLAlchemy async |
| Database | PostgreSQL 16 |
| CV / AI | OpenCV · face_recognition (dlib) / InsightFace |
| Auth | JWT (python-jose + passlib/bcrypt) |
| Container | Docker + Docker Compose |

---

## Quick Start

### 1. Clone and configure

```bash
cp .env.example .env
# Edit .env — set a strong SECRET_KEY
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

- Frontend → http://localhost:5173
- Backend API → http://localhost:8000
- API Docs → http://localhost:8000/docs

### 3. Default login

| Field | Value |
|---|---|
| Badge Number | `ADMIN-001` |
| Password | `Admin@123` |

> **Change this password immediately in production.**

---

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Running Tests

```bash
cd backend
pytest app/tests/ -v
```

---

## Project Structure

```
secure-smart-voting-system/
├── backend/
│   └── app/
│       ├── api/routes/         # voter, verification, alerts, logs
│       ├── core/               # config, JWT security
│       ├── models/             # SQLAlchemy ORM models
│       ├── schemas/            # Pydantic request/response schemas
│       ├── services/           # face_verification, fingerprint_verification,
│       │                         ink_detection, decision_engine, voter_service
│       ├── db/                 # session, base, init_db
│       └── tests/              # pytest unit & integration tests
├── frontend/
│   └── src/
│       ├── components/         # Layout, StatCard, DataTable, Badge, PageHeader
│       ├── pages/              # Login, Dashboard, Verify, Enroll, Voters, Alerts, Logs
│       ├── services/           # axios API wrappers
│       ├── hooks/              # useAuth
│       └── utils/              # format helpers
├── database/
│   └── init.sql
├── docker-compose.yml
└── .env.example
```

---

## Verification Flow

```
Voter arrives → ID lookup → Face capture (webcam)
             → Fingerprint scan (hardware / file upload)
             → Finger photo (ink detection)
             → Decision Engine
                 ├── BLOCK if already voted    (DUPLICATE)
                 ├── BLOCK if ink detected     (INK_DETECTED)
                 ├── BLOCK if face mismatch    (FACE_MISMATCH)
                 ├── BLOCK if FP mismatch      (FINGERPRINT_MISMATCH)
                 └── ALLOW + mark voted + audit log
```

---

## Fingerprint Hardware Integration

The fingerprint service is in **simulation mode** by default (SHA-256 hash comparison).
To connect real hardware:

1. Install your SDK (e.g., Mantra MFS100, Secugen, DigitalPersona).
2. Set `_SDK_AVAILABLE = True` in `backend/app/services/fingerprint_verification.py`.
3. Replace the stub `NotImplementedError` calls with your SDK's `enroll()` and `match()` functions.

---

## Face Recognition Backend

- **Default**: `face_recognition` (dlib, 128-d embeddings) — pure Python, no extra setup.
- **Production upgrade**: Install `insightface` for ArcFace (512-d) — higher accuracy.
  ```bash
  pip install insightface onnxruntime
  ```
  The service auto-detects InsightFace and falls back to dlib if not installed.

---

## Security Notes

- All access attempts are logged in `audit_logs` (immutable — rows are never updated/deleted).
- JWTs expire after 60 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`).
- Change `SECRET_KEY` and all default credentials before any deployment.
- Run behind HTTPS (nginx / Caddy reverse proxy) in production.
