import asyncio
from datetime import date, datetime
from decimal import Decimal

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncpg

from app.config import settings
from app.db.schema import SCHEMA_SQL
from app.services.pricing import calculate_total_price


async def seed() -> None:
    connection = await asyncpg.connect(dsn=settings.database_url)
    try:
        await connection.execute(SCHEMA_SQL)

        await connection.execute("TRUNCATE payments, rentals, customers, cars RESTART IDENTITY CASCADE")

        await connection.executemany(
            """
            INSERT INTO customers (full_name, email, phone, driver_license_number)
            VALUES ($1, $2, $3, $4)
            """,
            [
                ("Asel Asanova", "asel@example.com", "+996 777 77 77 77 ", "DL-0000001"),
                ("Belek Uzakov", "belek@example.com", "+996 555 55 55 55", "DL-0000002"),
                ("Asan Bolotov", "asan@example.com", "+996 222 22 22 22", "DL-0000003"),
                ("Batma Turanova", "batma@example.com", "+996 999 99 99 99 ", "DL-0000004"),
                ("Aziz Usonov", "aziz@example.com", "+996 770 12 34 56", "DL-0000005"),
            ],
        )

        await connection.executemany(
            """
            INSERT INTO cars (brand, model, year, price_per_day, status)
            VALUES ($1, $2, $3, $4, $5)
            """,
            [
                ("Toyota", "Camry", 2021, 45.00, "available"),
                ("Honda", "Civic", 2020, 50.00, "available"),
                ("BMW", "X3", 2022, 120.00, "maintenance"),
                ("Lexus", "RX570", 2020, 90.00, "available"),
                ("Mercedes", "E220", 2017, 40.00, "maintenance"),
                ("Kia", "K5", 2020, 50.00, "maintenance"),
                ("Honda", "Accord", 2018, 45.00, "available"),
            ],
        )

        total_price = calculate_total_price(date(2026, 4, 1), date(2026, 4, 4), Decimal("45.00"))
        rental_id = await connection.fetchval(
            """
            INSERT INTO rentals (customer_id, car_id, start_date, end_date, total_price, status)
            VALUES (1, 1, '2026-04-01', '2026-04-04', $1, 'completed')
            RETURNING id
            """,
            total_price,
        )
        await connection.execute("UPDATE cars SET status = 'available' WHERE id = 1")

        await connection.execute(
            """
            INSERT INTO payments (rental_id, amount, payment_method)
            VALUES ($1, $2, 'card')
            """,
            rental_id,
            total_price,
        )

        extra_rentals = [
            (2, 2, date(2026, 3, 10), date(2026, 3, 15), Decimal("50.00"), datetime(2026, 3, 16), "cash"),
            (3, 4, date(2026, 2, 5), date(2026, 2, 8), Decimal("90.00"), datetime(2026, 2, 9), "card"),
            (4, 7, date(2026, 1, 20), date(2026, 1, 23), Decimal("45.00"), datetime(2026, 1, 24), "bank_transfer"),
        ]

        for customer_id, car_id, start_date, end_date, price_per_day, payment_date, method in extra_rentals:
            rental_price = calculate_total_price(start_date, end_date, price_per_day)
            extra_rental_id = await connection.fetchval(
                """
                INSERT INTO rentals (customer_id, car_id, start_date, end_date, total_price, status)
                VALUES ($1, $2, $3, $4, $5, 'completed')
                RETURNING id
                """,
                customer_id,
                car_id,
                start_date,
                end_date,
                rental_price,
            )
            await connection.execute("UPDATE cars SET status = 'available' WHERE id = $1", car_id)
            await connection.execute(
                """
                INSERT INTO payments (rental_id, amount, payment_method, payment_date)
                VALUES ($1, $2, $3, $4::timestamp)
                """,
                extra_rental_id,
                rental_price,
                method,
                payment_date,
            )

        print("Seed data inserted successfully")
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(seed())
