# PHARVO — Smart Pharmacy Management

A full-stack pharmacy management system with a **Django REST Framework** backend
and a **React (Vite)** frontend, organized as a single monorepo.

## Repository structure

```
PHARVO/
├── Backend/            # Django REST API (config, apps, tests, requirements)
└── Frontend/           # React + Vite single-page application
```

## Backend (Django + DRF)

- JWT authentication (`rest_framework_simplejwt`)
- Modules: Accounts, Customers, Inventory, Purchases, Sales, POS, CRM,
  Dashboard, Reports, Notifications
- PostgreSQL database (`pharvo_db`)
- Automated regression test suite under `Backend/tests/`

```bash
cd Backend
cp .env.example .env      # then fill in real values
pip install -r requirements.txt
python manage.py migrate
python manage.py check
python manage.py test
python manage.py runserver   # http://127.0.0.1:8000
```

## Frontend (React + Vite)

```bash
cd Frontend
npm install
npm run dev        # http://localhost:5173 (proxies /api to the backend)
npm run build
```

## Development

The Vite dev server proxies `/api` requests to the Django backend at
`http://127.0.0.1:8000` (see `Frontend/vite.config.js`). Start the backend
first, then the frontend.