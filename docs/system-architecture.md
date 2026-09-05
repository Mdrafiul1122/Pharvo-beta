# PHARVO System Architecture

```mermaid
flowchart TD

    U[User / Pharmacy Staff]

    F[Next.js Frontend<br/>localhost:3000]

    API[Django REST API<br/>localhost:8000]

    AUTH[Accounts & JWT Authentication]
    DASH[Dashboard]
    CUST[Customer Management]
    INV[Inventory & Medicines]
    SALES[Sales / POS]
    PUR[Purchases]
    INT[Drug Interactions]

    DB[(PostgreSQL<br/>sheba_db)]

    U --> F
    F -->|HTTP / REST API| API

    API --> AUTH
    API --> DASH
    API --> CUST
    API --> INV
    API --> SALES
    API --> PUR
    API --> INT

    AUTH --> DB
    DASH --> DB
    CUST --> DB
    INV --> DB
    SALES --> DB
    PUR --> DB
    INT --> DB