import asyncpg
from fastapi import APIRouter, HTTPException, Path, status

from app.db.database import db
from app.models.schemas import CarCreate, CarOut, CarUpdate
from app import repositories

router = APIRouter(prefix="/cars", tags=["cars"])


@router.post("", response_model=CarOut, status_code=status.HTTP_201_CREATED)
async def create_car(payload: CarCreate) -> dict:
    async with db.acquire() as connection:
        record = await repositories.create_car(connection, payload.model_dump())
        return dict(record)


@router.get("", response_model=list[CarOut])
async def get_cars() -> list[dict]:
    async with db.acquire() as connection:
        records = await repositories.list_cars(connection)
        return [dict(record) for record in records]


@router.get("/{car_id}", response_model=CarOut)
async def get_car(car_id: int = Path(ge=1)) -> dict:
    async with db.acquire() as connection:
        record = await repositories.get_car(connection, car_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Car not found")
        return dict(record)


@router.put("/{car_id}", response_model=CarOut)
async def update_car(car_id: int = Path(ge=1), payload: CarUpdate = ...) -> dict:
    async with db.acquire() as connection:
        record = await repositories.update_car(connection, car_id, payload.model_dump(exclude_none=True))
        if record is None:
            raise HTTPException(status_code=404, detail="Car not found")
        return dict(record)


@router.delete("/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_car(car_id: int = Path(ge=1)) -> None:
    async with db.acquire() as connection:
        try:
            result = await repositories.delete_car(connection, car_id)
            if result == "not_found":
                raise HTTPException(status_code=404, detail="Car not found")
        except asyncpg.ForeignKeyViolationError as exc:
            raise HTTPException(status_code=400, detail="Cannot delete car with rental history") from exc

