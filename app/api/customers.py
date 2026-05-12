import asyncpg
from fastapi import APIRouter, HTTPException, Path, status

from app.db.database import db
from app.models.schemas import CustomerCreate, CustomerOut, CustomerUpdate
from app import repositories

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerOut, status_code=status.HTTP_201_CREATED)
async def create_customer(payload: CustomerCreate) -> dict:
    async with db.acquire() as connection:
        try:
            record = await repositories.create_customer(connection, payload.model_dump())
            return dict(record)
        except asyncpg.UniqueViolationError as exc:
            raise HTTPException(status_code=400, detail="Email or driver license already exists") from exc


@router.get("", response_model=list[CustomerOut])
async def get_customers() -> list[dict]:
    async with db.acquire() as connection:
        records = await repositories.list_customers(connection)
        return [dict(record) for record in records]


@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(customer_id: int = Path(ge=1)) -> dict:
    async with db.acquire() as connection:
        record = await repositories.get_customer(connection, customer_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        return dict(record)


@router.put("/{customer_id}", response_model=CustomerOut)
async def update_customer(customer_id: int = Path(ge=1), payload: CustomerUpdate = ...) -> dict:
    async with db.acquire() as connection:
        try:
            record = await repositories.update_customer(
                connection,
                customer_id,
                payload.model_dump(exclude_none=True),
            )
            if record is None:
                raise HTTPException(status_code=404, detail="Customer not found")
            return dict(record)
        except asyncpg.UniqueViolationError as exc:
            raise HTTPException(status_code=400, detail="Email or driver license already exists") from exc


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: int = Path(ge=1)) -> None:
    async with db.acquire() as connection:
        try:
            result = await repositories.delete_customer(connection, customer_id)
            if result == "not_found":
                raise HTTPException(status_code=404, detail="Customer not found")
        except asyncpg.ForeignKeyViolationError as exc:
            raise HTTPException(status_code=400, detail="Cannot delete customer with rental history") from exc

