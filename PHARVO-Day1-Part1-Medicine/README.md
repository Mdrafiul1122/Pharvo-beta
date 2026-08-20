# Sheba Pharmacy POS

A full-stack Pharmacy Point of Sale system with a Django REST Framework backend and a Next.js frontend.

## Architecture

```
sheba/
├── backend/     # Django REST API + PostgreSQL
└── frontend/    # Next.js client application
```

## Prerequisites

- Python 3.12+ and PostgreSQL (backend)
- Node.js 20+ (frontend)

## Quick Start

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

Create a PostgreSQL database named `sheba_db` and update credentials in `config/settings.py`.

```bash
python manage.py migrate
python manage.py seed_data    # populate with sample data
python manage.py runserver
```

Admin login: `admin` / `admin123` at `http://localhost:8000/admin/`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:3000`

## Environment Variables

| Variable | Default | Location |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000/api` | `frontend/.env.local` |
