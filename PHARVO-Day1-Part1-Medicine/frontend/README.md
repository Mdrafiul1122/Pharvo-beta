# Sheba Pharmacy — Frontend

Next.js client for the Pharmacy POS system.

## Tech Stack

- **Next.js 16** (App Router, TypeScript)
- **Tailwind CSS 4**
- Connects to Django REST API at `http://localhost:8000/api`

## Setup

```bash
npm install
npm run dev
```

Opens at `http://localhost:3000`.

## Auth

Login with the seeded admin account: `admin` / `admin123`.  
JWT tokens are stored in `localStorage` and auto-refreshed on 401 responses.

## Pages

| Route | Description |
|---|---|
| `/login` | Login form |
| `/dashboard` | Stats overview |
| `/products` | Product list |
| `/products/new` | Create product |
| `/categories` | Categories with inline add |
| `/suppliers` | Supplier list |
| `/customers` | Customer list |
| `/sales` | Sales history |
| `/sales/new` | POS — add items, complete sale |
| `/purchases` | Purchase history |
| `/purchases/new` | Create purchase order |

## Project Structure

```
app/             # App Router pages
components/      # Shared UI (Sidebar, DataTable)
lib/             # API client + auth context
types/           # TypeScript interfaces
```

## Environment Variables

Create `.env.local` in this directory:

```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

Default is `http://localhost:8000/api` if not set.
