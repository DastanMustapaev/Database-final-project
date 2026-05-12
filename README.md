# Car Rental System (FastAPI + PostgreSQL + asyncpg)

Backend final project for a Database course. The system models a real car rental workflow with a normalized relational schema, CRUD APIs, and reporting queries.

## Project Description
Car rentals are hard to track when cars, customers, and payments live in separate spreadsheets. This project provides a single source of truth: customers rent cars, rentals track dates and price, and payments record revenue. The focus is on database design, constraints, and SQL reporting.

## Database Design
Schema sources:
- `sql/schema.sql`
- `app/db/schema.py`

ER diagram (Mermaid):
```mermaid
erDiagram
    CUSTOMERS ||--o{ RENTALS : places
    CARS ||--o{ RENTALS : used_in
    RENTALS ||--|| PAYMENTS : paid_by

    CUSTOMERS {
        int id PK
        string full_name
        string email UNIQUE
        string phone
        string driver_license_number UNIQUE
    }

    CARS {
        int id PK
        string brand
        string model
        int year CHECK_1980_2100
        decimal price_per_day CHECK_gt_0
        string status CHECK_available_rented_maintenance
    }

    RENTALS {
        int id PK
        int customer_id FK
        int car_id FK
        date start_date
        date end_date
        decimal total_price CHECK_ge_0
        string status CHECK_active_completed_cancelled
    }

    PAYMENTS {
        int id PK
        int rental_id FK_UNIQUE
        decimal amount CHECK_gt_0
        datetime payment_date
        string payment_method CHECK_cash_card_bank_transfer
    }
```

## Tables, Relationships, Constraints
- `customers`: unique by `email` and `driver_license_number`.
- `cars`: positive `price_per_day`; status is constrained to `available`, `rented`, `maintenance`.
- `rentals`: many-to-one with `customers` and `cars`; `end_date >= start_date`; status constrained to `active`, `completed`, `cancelled`.
- `payments`: one-to-one with `rentals` (`UNIQUE(rental_id)`), so each rental has at most one payment.
- FK policy: `rentals -> customers/cars` uses `ON DELETE RESTRICT`; `payments -> rentals` uses `ON DELETE CASCADE`.

## Tech Stack
- PostgreSQL
- FastAPI
- asyncpg
- Pydantic v2
- pytest

## Setup & Run
1. Create a PostgreSQL database (example: `car_rental_db`).
2. Copy `.env.example` to `.env` and set `DATABASE_URL`.
3. Install dependencies and run the API.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Open Swagger docs: `http://127.0.0.1:8000/docs`
Open simple UI: `http://127.0.0.1:8000/ui`

### Seed Sample Data
```bash
source .venv/bin/activate
python scripts/seed_data.py
```

## Sample Queries (and Purpose)
Full list: `sql/sample_queries.sql`.

1) **Available cars** — list cars ready to rent.
```sql
SELECT id, brand, model, year, price_per_day
FROM cars
WHERE status = 'available';
```

2) **Rentals by customer** — JOIN across customer, rental, car.
```sql
SELECT r.id, c.full_name, car.brand, car.model, r.start_date, r.end_date, r.total_price
FROM rentals r
JOIN customers c ON c.id = r.customer_id
JOIN cars car ON car.id = r.car_id
WHERE c.id = $1;
```

3) **Total revenue** — aggregation over payments.
```sql
SELECT COALESCE(SUM(amount), 0) AS total_revenue
FROM payments;
```

4) **Most rented car** — GROUP BY + ORDER.
```sql
SELECT car.id, car.brand, car.model, COUNT(r.id) AS rent_count
FROM rentals r
JOIN cars car ON car.id = r.car_id
GROUP BY car.id, car.brand, car.model
ORDER BY rent_count DESC
LIMIT 1;
```

5) **Top customers** — rank customers by total spend.
```sql
SELECT c.id AS customer_id, c.full_name, COALESCE(SUM(p.amount), 0) AS total_spent
FROM customers c
JOIN rentals r ON r.customer_id = c.id
JOIN payments p ON p.rental_id = r.id
GROUP BY c.id, c.full_name
ORDER BY total_spent DESC
LIMIT 5;
```

6) **Revenue by month** — time-based reporting.
```sql
SELECT DATE_TRUNC('month', payment_date)::date AS month,
       COALESCE(SUM(amount), 0) AS total_revenue
FROM payments
GROUP BY month
ORDER BY month;
```

## API Endpoints
- `GET /` healthcheck
- `GET /ui` simple visualization UI
- CRUD for `/customers`, `/cars`, `/rentals`, `/payments`
- Reports:
  - `GET /reports/available-cars`
  - `GET /reports/rentals-by-customer/{customer_id}`
  - `GET /reports/total-revenue`
  - `GET /reports/most-rented-car`
  - `GET /reports/top-customers?limit=5`
  - `GET /reports/revenue-by-month`

## Screenshots & Diagrams
Detailed visual representations of the project are stored in the `docs/` folder:
- **`docs/ER-Diagram.png`** — The Entity-Relationship diagram showing database normalization and constraints.
- **`docs/Dashboard.png`**  — Working interface of the dashboard system.
- **`docs/Cars.png`**       — Frontend user interface displaying the cars catalog and inventory.
- **`docs/Rentals.png`**    — User interface for viewing and managing active car rentals.
- **`docs/Payments.png`**   — Interface showing the payment history and transaction records.
- **`docs/Customers.png`**  — Management view showing the registered customer list.

## Video Presentation & Feedback
- **Video Presentation:** [https://drive.google.com/file/d/1EkWbLs12eE1g44VWbXOGDHj88msKn8vG/view?usp=drive_link]
- **Classmate Feedback:** [https://drive.google.com/file/d/1R_RVxbn-lcYfvEa18xPy6R0OOiJddKVF/view?usp=drive_link]
- **Presentation PDF:**   [https://drive.google.com/file/d/1CgXL0WeP-rIuOkPZvWb_6kI9JcLF248B/view?usp=drive_link]

## Project Structure
- `app/main.py` - FastAPI app and startup lifecycle
- `app/db/schema.py` - SQL schema (`CREATE TABLE IF NOT EXISTS`)
- `app/db/database.py` - asyncpg pool manager
- `app/models/schemas.py` - Pydantic request/response models
- `app/repositories.py` - SQL CRUD and analytics queries
- `app/services/rental_service.py` - rental domain logic + validations
- `scripts/seed_data.py` - seed/test data insertion
- `tests/test_pricing.py` - small test harness
- `tests/test_schemas.py` - request schema validation tests

## Run Tests
```bash
source .venv/bin/activate
pytest -q
```
