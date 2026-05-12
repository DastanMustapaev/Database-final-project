import asyncpg
from fastapi import APIRouter, HTTPException, Path, status

from app.db.database import db
from app.models.schemas import RentalCreate, RentalOut, RentalUpdate
from app import repositories
from app.services.rental_service import RentalService

router = APIRouter(prefix="/rentals", tags=["rentals"])


@router.post("", response_model=RentalOut, status_code=status.HTTP_201_CREATED)
async def create_rental(payload: RentalCreate) -> dict:
    async with db.acquire() as connection:
        try:
            record = await RentalService.create_rental(connection, payload)
            return dict(record)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[RentalOut])
async def get_rentals() -> list[dict]:
    async with db.acquire() as connection:
        records = await repositories.list_rentals(connection)
        return [dict(record) for record in records]


@router.get("/{rental_id}", response_model=RentalOut)
async def get_rental(rental_id: int = Path(ge=1)) -> dict:
    async with db.acquire() as connection:
        record = await repositories.get_rental(connection, rental_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Rental not found")
        return dict(record)


@router.put("/{rental_id}", response_model=RentalOut)
async def update_rental(rental_id: int = Path(ge=1), payload: RentalUpdate = ...) -> dict:
    async with db.acquire() as connection:
        try:
            record = await RentalService.update_rental(connection, rental_id, payload)
            if record is None:
                raise HTTPException(status_code=404, detail="Rental not found")
            return dict(record)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/{rental_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rental(rental_id: int = Path(ge=1)) -> None:
    async with db.acquire() as connection:
        result = await RentalService.delete_rental(connection, rental_id)
        if result == "not_found":
            raise HTTPException(status_code=404, detail="Rental not found")

