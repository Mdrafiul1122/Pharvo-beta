# Sheba Pharmacy — Backend

Django REST API for the Pharmacy POS system.

## Tech Stack

- **Django 6.0** + **Django REST Framework 3.17**
- **PostgreSQL** database
- **JWT authentication** via SimpleJWT
- **CORS** enabled for cross-origin requests

## Setup

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a PostgreSQL database:

```bash
psql -U postgres -c "CREATE DATABASE sheba_db;"
```

Update credentials in `config/settings.py` if needed (default: user `postgres`, password `787878`).

```bash
python manage.py migrate
python manage.py seed_data    # optional sample data
python manage.py runserver
```

## Apps

| App | Models | Endpoints |
|---|---|---|
| `inventory` | Category, Supplier, Product, Medicine | `/api/inventory/` |
| `customers` | Customer | `/api/customers/` |
| `sales` | Sale, SaleItem | `/api/sales/` |
| `purchases` | Purchase, PurchaseItem | `/api/purchases/` |

## API Endpoints

### Authentication
```
POST /api/auth/token/         # Login → access + refresh tokens
POST /api/auth/token/refresh/ # Refresh access token
POST /api/auth/token/verify/  # Verify token validity
```

### Inventory
```
GET/POST   /api/inventory/categories/
GET/PUT/DELETE /api/inventory/categories/{id}/
GET/POST   /api/inventory/suppliers/
GET/POST   /api/inventory/products/
GET/POST   /api/inventory/medicines/
GET/PUT/DELETE /api/inventory/medicines/{id}/
```

### Customers
```
GET/POST   /api/customers/customers/
GET/PUT/DELETE /api/customers/customers/{id}/
```

### Sales
```
GET/POST   /api/sales/sales/           # POST accepts nested items
GET/PUT/DELETE /api/sales/sales/{id}/
GET/POST   /api/sales/sale-items/
```

### Purchases
```
GET/POST   /api/purchases/purchases/   # POST accepts nested items
GET/PUT/DELETE /api/purchases/purchases/{id}/
GET/POST   /api/purchases/purchase-items/
```

All endpoints require `Authorization: Bearer <token>` header.

## Seed Data

```bash
python manage.py seed_data
```

Creates: 10 categories, 5 suppliers, 20 products, 10 customers, 20 sales, 10 purchases, and an admin user (`admin` / `admin123`).

## Admin Panel

Available at `/admin/` with the same admin credentials.
