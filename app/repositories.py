from typing import Any

import asyncpg


async def create_customer(connection: asyncpg.Connection, data: dict[str, Any]) -> asyncpg.Record:
    return await connection.fetchrow(
        """
        INSERT INTO customers (full_name, email, phone, driver_license_number)
        VALUES ($1, $2, $3, $4)
        RETURNING id, full_name, email, phone, driver_license_number
        """,
        data["full_name"],
        data["email"],
        data["phone"],
        data["driver_license_number"],
    )


async def list_customers(connection: asyncpg.Connection) -> list[asyncpg.Record]:
    return await connection.fetch(
        "SELECT id, full_name, email, phone, driver_license_number FROM customers ORDER BY id"
    )


async def get_customer(connection: asyncpg.Connection, customer_id: int) -> asyncpg.Record | None:
    return await connection.fetchrow(
        "SELECT id, full_name, email, phone, driver_license_number FROM customers WHERE id = $1", customer_id
    )


async def update_customer(connection: asyncpg.Connection, customer_id: int, data: dict[str, Any]) -> asyncpg.Record | None:
    customer = await get_customer(connection, customer_id)
    if customer is None:
        return None

    merged = {**dict(customer), **data}
    return await connection.fetchrow(
        """
        UPDATE customers
        SET full_name = $1,
            email = $2,
            phone = $3,
            driver_license_number = $4
        WHERE id = $5
        RETURNING id, full_name, email, phone, driver_license_number
        """,
        merged["full_name"],
        merged["email"],
        merged["phone"],
        merged["driver_license_number"],
        customer_id,
    )


async def delete_customer(connection: asyncpg.Connection, customer_id: int) -> str:
    deleted = await connection.execute("DELETE FROM customers WHERE id = $1", customer_id)
    return "deleted" if deleted.endswith("1") else "not_found"


async def create_car(connection: asyncpg.Connection, data: dict[str, Any]) -> asyncpg.Record:
    return await connection.fetchrow(
        """
        INSERT INTO cars (brand, model, year, price_per_day, status)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id, brand, model, year, price_per_day, status
        """,
        data["brand"],
        data["model"],
        data["year"],
        data["price_per_day"],
        data["status"],
    )


async def list_cars(connection: asyncpg.Connection) -> list[asyncpg.Record]:
    return await connection.fetch("SELECT id, brand, model, year, price_per_day, status FROM cars ORDER BY id")


async def get_car(connection: asyncpg.Connection, car_id: int) -> asyncpg.Record | None:
    return await connection.fetchrow("SELECT id, brand, model, year, price_per_day, status FROM cars WHERE id = $1", car_id)


async def update_car(connection: asyncpg.Connection, car_id: int, data: dict[str, Any]) -> asyncpg.Record | None:
    car = await get_car(connection, car_id)
    if car is None:
        return None

    merged = {**dict(car), **data}
    return await connection.fetchrow(
        """
        UPDATE cars
        SET brand = $1,
            model = $2,
            year = $3,
            price_per_day = $4,
            status = $5
        WHERE id = $6
        RETURNING id, brand, model, year, price_per_day, status
        """,
        merged["brand"],
        merged["model"],
        merged["year"],
        merged["price_per_day"],
        merged["status"],
        car_id,
    )


async def delete_car(connection: asyncpg.Connection, car_id: int) -> str:
    deleted = await connection.execute("DELETE FROM cars WHERE id = $1", car_id)
    return "deleted" if deleted.endswith("1") else "not_found"


async def list_rentals(connection: asyncpg.Connection) -> list[asyncpg.Record]:
    return await connection.fetch(
        "SELECT id, customer_id, car_id, start_date, end_date, total_price, status FROM rentals ORDER BY id"
    )


async def get_rental(connection: asyncpg.Connection, rental_id: int) -> asyncpg.Record | None:
    return await connection.fetchrow(
        "SELECT id, customer_id, car_id, start_date, end_date, total_price, status FROM rentals WHERE id = $1", rental_id
    )


async def create_payment(connection: asyncpg.Connection, data: dict[str, Any]) -> asyncpg.Record:
    rental = await get_rental(connection, data["rental_id"])
    if rental is None:
        raise ValueError("Rental not found")

    return await connection.fetchrow(
        """
        INSERT INTO payments (rental_id, amount, payment_method)
        VALUES ($1, $2, $3)
        RETURNING id, rental_id, amount, payment_date, payment_method
        """,
        data["rental_id"],
        data["amount"],
        data["payment_method"],
    )


async def list_payments(connection: asyncpg.Connection) -> list[asyncpg.Record]:
    return await connection.fetch(
        "SELECT id, rental_id, amount, payment_date, payment_method FROM payments ORDER BY id"
    )


async def get_payment(connection: asyncpg.Connection, payment_id: int) -> asyncpg.Record | None:
    return await connection.fetchrow(
        "SELECT id, rental_id, amount, payment_date, payment_method FROM payments WHERE id = $1", payment_id
    )


async def update_payment(connection: asyncpg.Connection, payment_id: int, data: dict[str, Any]) -> asyncpg.Record | None:
    payment = await get_payment(connection, payment_id)
    if payment is None:
        return None

    merged = {**dict(payment), **data}
    return await connection.fetchrow(
        """
        UPDATE payments
        SET amount = $1,
            payment_method = $2
        WHERE id = $3
        RETURNING id, rental_id, amount, payment_date, payment_method
        """,
        merged["amount"],
        merged["payment_method"],
        payment_id,
    )


async def delete_payment(connection: asyncpg.Connection, payment_id: int) -> str:
    deleted = await connection.execute("DELETE FROM payments WHERE id = $1", payment_id)
    return "deleted" if deleted.endswith("1") else "not_found"


async def query_available_cars(connection: asyncpg.Connection) -> list[asyncpg.Record]:
    return await connection.fetch(
        "SELECT id, brand, model, year, price_per_day, status FROM cars WHERE status = 'available' ORDER BY id"
    )


async def query_rentals_by_customer(connection: asyncpg.Connection, customer_id: int) -> list[asyncpg.Record]:
    return await connection.fetch(
        """
        SELECT
            r.id AS rental_id,
            c.full_name AS customer_name,
            CONCAT(car.brand, ' ', car.model) AS car_name,
            r.start_date,
            r.end_date,
            r.status,
            r.total_price
        FROM rentals r
        JOIN customers c ON c.id = r.customer_id
        JOIN cars car ON car.id = r.car_id
        WHERE c.id = $1
        ORDER BY r.start_date DESC
        """,
        customer_id,
    )


async def query_total_revenue(connection: asyncpg.Connection) -> asyncpg.Record:
    return await connection.fetchrow("SELECT COALESCE(SUM(amount), 0) AS total_revenue FROM payments")


async def query_most_rented_car(connection: asyncpg.Connection) -> asyncpg.Record | None:
    return await connection.fetchrow(
        """
        SELECT
            car.id AS car_id,
            car.brand,
            car.model,
            COUNT(r.id)::INT AS rent_count
        FROM rentals r
        JOIN cars car ON car.id = r.car_id
        GROUP BY car.id, car.brand, car.model
        ORDER BY rent_count DESC, car.id ASC
        LIMIT 1
        """
    )


async def query_top_customers_by_revenue(
    connection: asyncpg.Connection,
    limit: int = 5,
) -> list[asyncpg.Record]:
    return await connection.fetch(
        """
        SELECT
            c.id AS customer_id,
            c.full_name,
            COALESCE(SUM(p.amount), 0)::NUMERIC(10, 2) AS total_spent
        FROM customers c
        JOIN rentals r ON r.customer_id = c.id
        JOIN payments p ON p.rental_id = r.id
        GROUP BY c.id, c.full_name
        ORDER BY total_spent DESC, c.id ASC
        LIMIT $1
        """,
        limit,
    )


async def query_revenue_by_month(connection: asyncpg.Connection) -> list[asyncpg.Record]:
    return await connection.fetch(
        """
        SELECT
            DATE_TRUNC('month', payment_date)::date AS month,
            COALESCE(SUM(amount), 0)::NUMERIC(10, 2) AS total_revenue
        FROM payments
        GROUP BY month
        ORDER BY month
        """
    )


