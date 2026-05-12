import asyncpg
from fastapi import APIRouter, HTTPException, Path, status

from app.db.database import db
from app.models.schemas import PaymentCreate, PaymentOut, PaymentUpdate
from app import repositories

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
async def create_payment(payload: PaymentCreate) -> dict:
    async with db.acquire() as connection:
        try:
            record = await repositories.create_payment(connection, payload.model_dump())
            return dict(record)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except asyncpg.UniqueViolationError as exc:
            raise HTTPException(status_code=400, detail="Rental already has a payment") from exc


@router.get("", response_model=list[PaymentOut])
async def get_payments() -> list[dict]:
    async with db.acquire() as connection:
        records = await repositories.list_payments(connection)
        return [dict(record) for record in records]


@router.get("/{payment_id}", response_model=PaymentOut)
async def get_payment(payment_id: int = Path(ge=1)) -> dict:
    async with db.acquire() as connection:
        record = await repositories.get_payment(connection, payment_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Payment not found")
        return dict(record)


@router.put("/{payment_id}", response_model=PaymentOut)
async def update_payment(payment_id: int = Path(ge=1), payload: PaymentUpdate = ...) -> dict:
    async with db.acquire() as connection:
        record = await repositories.update_payment(connection, payment_id, payload.model_dump(exclude_none=True))
        if record is None:
            raise HTTPException(status_code=404, detail="Payment not found")
        return dict(record)


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(payment_id: int = Path(ge=1)) -> None:
    async with db.acquire() as connection:
        result = await repositories.delete_payment(connection, payment_id)
        if result == "not_found":
            raise HTTPException(status_code=404, detail="Payment not found")

