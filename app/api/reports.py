from fastapi import APIRouter, HTTPException, Path, Query

from app.db.database import db
from app.models.schemas import (
    CarOut,
    MostRentedCarOut,
    RentalByCustomerOut,
    RevenueOut,
    RevenueByMonthOut,
    TopCustomerByRevenueOut,
)
from app import repositories

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/available-cars", response_model=list[CarOut])
async def available_cars() -> list[dict]:
    async with db.acquire() as connection:
        records = await repositories.query_available_cars(connection)
        return [dict(record) for record in records]


@router.get("/rentals-by-customer/{customer_id}", response_model=list[RentalByCustomerOut])
async def rentals_by_customer(customer_id: int = Path(ge=1)) -> list[dict]:
    async with db.acquire() as connection:
        records = await repositories.query_rentals_by_customer(connection, customer_id)
        return [dict(record) for record in records]


@router.get("/total-revenue", response_model=RevenueOut)
async def total_revenue() -> dict:
    async with db.acquire() as connection:
        record = await repositories.query_total_revenue(connection)
        return dict(record)


@router.get("/most-rented-car", response_model=MostRentedCarOut)
async def most_rented_car() -> dict:
    async with db.acquire() as connection:
        record = await repositories.query_most_rented_car(connection)
        if record is None:
            raise HTTPException(status_code=404, detail="No rentals found")
        return dict(record)


@router.get("/top-customers", response_model=list[TopCustomerByRevenueOut])
async def top_customers(limit: int = Query(default=5, ge=1, le=50)) -> list[dict]:
    async with db.acquire() as connection:
        records = await repositories.query_top_customers_by_revenue(connection, limit=limit)
        return [dict(record) for record in records]


@router.get("/revenue-by-month", response_model=list[RevenueByMonthOut])
async def revenue_by_month() -> list[dict]:
    async with db.acquire() as connection:
        records = await repositories.query_revenue_by_month(connection)
        return [dict(record) for record in records]


