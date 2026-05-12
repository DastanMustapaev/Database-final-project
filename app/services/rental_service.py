from datetime import date

import asyncpg

from app.models.schemas import RentalCreate, RentalStatus, RentalUpdate
from app.services.pricing import calculate_total_price


class RentalService:
    @staticmethod
    async def _has_other_active_rentals(
        connection: asyncpg.Connection,
        car_id: int,
        exclude_rental_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> bool:
        if start_date is None or end_date is None:
            return await connection.fetchval(
                """
                SELECT EXISTS (
                    SELECT 1 FROM rentals
                    WHERE car_id = $1
                      AND status = 'active'
                      AND ($2::int IS NULL OR id IS DISTINCT FROM $2)
                )
                """,
                car_id,
                exclude_rental_id,
            )

        return await connection.fetchval(
            """
            SELECT EXISTS (
                SELECT 1 FROM rentals
                WHERE car_id = $1
                  AND status = 'active'
                  AND ($2::int IS NULL OR id IS DISTINCT FROM $2)
                  AND daterange(start_date, end_date, '[]') && daterange($3::date, $4::date, '[]')
            )
            """,
            car_id,
            exclude_rental_id,
            start_date,
            end_date,
        )

    @staticmethod
    async def _sync_car_status_after_rental_change(
        connection: asyncpg.Connection,
        car_id: int,
        exclude_rental_id: int | None = None,
    ) -> None:
        has_active_rentals = await RentalService._has_other_active_rentals(
            connection,
            car_id,
            exclude_rental_id=exclude_rental_id,
        )
        target_status = "rented" if has_active_rentals else "available"
        await connection.execute("UPDATE cars SET status = $1 WHERE id = $2 AND status <> 'maintenance'", target_status, car_id)

    @staticmethod
    async def create_rental(connection: asyncpg.Connection, payload: RentalCreate) -> asyncpg.Record:
        async with connection.transaction():
            customer = await connection.fetchrow("SELECT id FROM customers WHERE id = $1", payload.customer_id)
            if customer is None:
                raise ValueError("Customer not found")

            car = await connection.fetchrow(
                "SELECT id, status, price_per_day FROM cars WHERE id = $1 FOR UPDATE", payload.car_id
            )
            if car is None:
                raise ValueError("Car not found")
            if car["status"] != "available":
                raise ValueError("Car is not available for rent")

            overlap = await RentalService._has_other_active_rentals(
                connection,
                payload.car_id,
                start_date=payload.start_date,
                end_date=payload.end_date,
            )
            if overlap:
                raise ValueError("Car is already rented for selected dates")

            total_price = calculate_total_price(payload.start_date, payload.end_date, car["price_per_day"])
            rental = await connection.fetchrow(
                """
                INSERT INTO rentals (customer_id, car_id, start_date, end_date, total_price, status)
                VALUES ($1, $2, $3, $4, $5, 'active')
                RETURNING id, customer_id, car_id, start_date, end_date, total_price, status
                """,
                payload.customer_id,
                payload.car_id,
                payload.start_date,
                payload.end_date,
                total_price,
            )
            await connection.execute("UPDATE cars SET status = 'rented' WHERE id = $1", payload.car_id)
            return rental

    @staticmethod
    async def update_rental(
        connection: asyncpg.Connection,
        rental_id: int,
        payload: RentalUpdate,
    ) -> asyncpg.Record | None:
        async with connection.transaction():
            rental = await connection.fetchrow("SELECT * FROM rentals WHERE id = $1 FOR UPDATE", rental_id)
            if rental is None:
                return None

            start_date = payload.start_date or rental["start_date"]
            end_date = payload.end_date or rental["end_date"]
            status = payload.status.value if payload.status else rental["status"]
            previous_status = rental["status"]

            car = await connection.fetchrow("SELECT id, price_per_day FROM cars WHERE id = $1", rental["car_id"])
            total_price = calculate_total_price(start_date, end_date, car["price_per_day"])

            if status == RentalStatus.active.value:
                overlap = await RentalService._has_other_active_rentals(
                    connection,
                    rental["car_id"],
                    exclude_rental_id=rental_id,
                    start_date=start_date,
                    end_date=end_date,
                )
                if overlap:
                    raise ValueError("Car is already rented for selected dates")

            if status == RentalStatus.active.value:
                car_status = await connection.fetchval("SELECT status FROM cars WHERE id = $1", rental["car_id"])
                if car_status == "maintenance":
                    raise ValueError("Car in maintenance cannot have active rental")
            updated_rental = await connection.fetchrow(
                """
                UPDATE rentals
                SET start_date = $1,
                    end_date = $2,
                    total_price = $3,
                    status = $4
                WHERE id = $5
                RETURNING id, customer_id, car_id, start_date, end_date, total_price, status
                """,
                start_date,
                end_date,
                total_price,
                status,
                rental_id,
            )

            if status == RentalStatus.active.value:
                await connection.execute("UPDATE cars SET status = 'rented' WHERE id = $1", rental["car_id"])
            elif status in {RentalStatus.completed.value, RentalStatus.cancelled.value} and previous_status == RentalStatus.active.value:
                await RentalService._sync_car_status_after_rental_change(connection, rental["car_id"])

            return updated_rental

    @staticmethod
    async def delete_rental(connection: asyncpg.Connection, rental_id: int) -> str:
        async with connection.transaction():
            rental = await connection.fetchrow("SELECT id, car_id, status FROM rentals WHERE id = $1", rental_id)
            if rental is None:
                return "not_found"

            await connection.execute("DELETE FROM rentals WHERE id = $1", rental_id)

            if rental["status"] == RentalStatus.active.value:
                await RentalService._sync_car_status_after_rental_change(connection, rental["car_id"])

            return "deleted"

