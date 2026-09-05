# PHARVO — Pharmacy Management System

A full pharmacy management platform: POS / sales, inventory, CRM (customers,
tiers, medicine reminders, health information), orders, notifications,
purchases, supplier orders, reports and audit logging.

- **Backend** — Django 6.0 + Django REST Framework + PostgreSQL
- **Frontend** — React + Vite (in `Frontend/`, proxying `/api` to the Django server on `:8000`)

## Repository layout

| Path                          | Purpose                                                        |
| ----------------------------- | -------------------------------------------------------------- |
| `Backend/`                    | Django project (`config/` settings), apps: accounts, customers, inventory, sales, purchases, supplier, crm, notifications, audit, dashboard |
| `Frontend/`                   | React + Vite single-page application                            |
| `pharvo_db.backup`            | PostgreSQL seed dump — **the canonical dataset** (see Setup)    |
| `Backend/requirements.txt`    | Python dependencies                                             |
| `.env.example`                | Environment variables (copy to `.env`)                          |
| `scripts/restore_db.ps1`      | One-command database restore + migration reconcile              |

The tracked `pharvo_db.backup` contains the full working dataset
(8 users, 52 products, 15 customers, 28 sales, 68 sale items). Restoring it is
the quickest way to get a working environment with realistic data. A fresh,
empty database can also be created by running Django migrations.

## Prerequisites

- Python 3.13+
- PostgreSQL 18 (local server on `localhost:5432`, superuser `postgres`)
- Node.js 20+ and npm

## Setup

### 1. Backend

```powershell
cd Backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Then configure the database connection. No database password is hardcoded in the
project — it is read **only** from `.env` (gitignored) or the environment:

```powershell
copy .env.example .env     # then edit .env and set DB_PASSWORD to your local PostgreSQL password
```

> `Backend/config/settings.py` refuses to start if `DB_PASSWORD` is missing.
> `scripts/restore_db.ps1` behaves the same way.

### 2. Database — restore the seed data (recommended)

From the repository root:

```powershell
.\scripts\restore_db.ps1
```

This:
1. Creates the `pharvo_db` database if it does not exist.
2. Restores `pharvo_db.backup` into it (all tables + data). The backup already
   contains the Django `django_migrations` history, so `migrate` is a no-op.
3. Runs `python manage.py migrate` to reconcile any remaining migration state.

> **Fresh/empty database option** (optional): skip the restore and instead just
> run `python manage.py migrate` against an empty `pharvo_db`. This creates an
> identical 26-table schema with no data. Demo accounts/data come from the
> seed backup.

### 3. Frontend

```powershell
cd Frontend
npm install
npm run dev
```

The Vite dev server runs on `http://localhost:5173` and proxies `/api` to the
Django server on `http://localhost:8000`.

### 4. Run the backend

```powershell
cd Backend
python manage.py runserver
```

## Demo accounts

- Admin:  `rafi` / `787878`  (role `admin`)

Other seeded users exist with pharmacist / staff / customer roles; the admin
account can access every module.

## Version control notes

- `.gitignore` excludes `Frontend/node_modules/`, `Frontend/dist/`,
  `__pycache__/`, `.env`, and timestamped local backups (`backup_*.backup`).
- Migrations for all business apps are committed under `Backend/*/migrations/`.
- All application models are **managed** (`managed = True`), so the schema is
  owned and reconciled by Django migrations.
- The three auxiliary legacy tables (`audit_auditlog`, `crm_crmpermission`,
  `supplier_supplierorder`) exist in the live DB with legacy plain-integer FK
  columns; a fresh migrate creates them as proper `bigint` foreign keys. Data
  is fully compatible; the fresh-install form is the corrected schema.

## Verification

Run the automated UI test suite (requires a running backend + frontend):

```powershell
cd Frontend\tests
python run_all_tests.py
```