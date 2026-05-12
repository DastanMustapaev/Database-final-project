from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.cars import router as cars_router
from app.api.customers import router as customers_router
from app.api.payments import router as payments_router
from app.api.rentals import router as rentals_router
from app.api.reports import router as reports_router
from app.db.database import db


@asynccontextmanager
async def lifespan(_: FastAPI):
    await db.connect()
    await db.create_tables()
    try:
        yield
    finally:
        await db.disconnect()


app = FastAPI(title="Car Rental System API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers_router)
app.include_router(cars_router)
app.include_router(rentals_router)
app.include_router(payments_router)
app.include_router(reports_router)


@app.get("/")
async def healthcheck() -> dict[str, str]:
    return {"message": "Car Rental System API is running"}
