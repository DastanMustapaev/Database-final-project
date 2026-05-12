from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


class CarStatus(str, Enum):
    available = "available"
    rented = "rented"
    maintenance = "maintenance"


class RentalStatus(str, Enum):
    active = "active"
    completed = "completed"
    cancelled = "cancelled"


class PaymentMethod(str, Enum):
    cash = "cash"
    card = "card"
    bank_transfer = "bank_transfer"


class CustomerCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: str = Field(min_length=5, max_length=30)
    driver_license_number: str = Field(min_length=4, max_length=50)


class CustomerUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=5, max_length=30)
    driver_license_number: str | None = Field(default=None, min_length=4, max_length=50)


class CustomerOut(CustomerCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class CarCreate(BaseModel):
    brand: str = Field(min_length=2, max_length=80)
    model: str = Field(min_length=1, max_length=80)
    year: int = Field(ge=1980, le=2100)
    price_per_day: Decimal = Field(gt=0)
    status: CarStatus = CarStatus.available


class CarUpdate(BaseModel):
    brand: str | None = Field(default=None, min_length=2, max_length=80)
    model: str | None = Field(default=None, min_length=1, max_length=80)
    year: int | None = Field(default=None, ge=1980, le=2100)
    price_per_day: Decimal | None = Field(default=None, gt=0)
    status: CarStatus | None = None


class CarOut(CarCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


class RentalCreate(BaseModel):
    customer_id: int = Field(gt=0)
    car_id: int = Field(gt=0)
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def validate_date_range(self) -> "RentalCreate":
        if self.end_date < self.start_date:
            raise ValueError("end_date must be equal to or after start_date")
        return self


class RentalUpdate(BaseModel):
    start_date: date | None = None
    end_date: date | None = None
    status: RentalStatus | None = None

    @model_validator(mode="after")
    def validate_date_range(self) -> "RentalUpdate":
        if self.start_date is not None and self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date must be equal to or after start_date")
        return self


class RentalOut(BaseModel):
    id: int
    customer_id: int
    car_id: int
    start_date: date
    end_date: date
    total_price: Decimal
    status: RentalStatus

    model_config = ConfigDict(from_attributes=True)


class PaymentCreate(BaseModel):
    rental_id: int = Field(gt=0)
    amount: Decimal = Field(gt=0)
    payment_method: PaymentMethod


class PaymentUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0)
    payment_method: PaymentMethod | None = None


class PaymentOut(BaseModel):
    id: int
    rental_id: int
    amount: Decimal
    payment_date: datetime
    payment_method: PaymentMethod

    model_config = ConfigDict(from_attributes=True)


class RentalByCustomerOut(BaseModel):
    rental_id: int
    customer_name: str
    car_name: str
    start_date: date
    end_date: date
    status: RentalStatus
    total_price: Decimal


class RevenueOut(BaseModel):
    total_revenue: Decimal


class MostRentedCarOut(BaseModel):
    car_id: int
    brand: str
    model: str
    rent_count: int


class TopCustomerByRevenueOut(BaseModel):
    customer_id: int
    full_name: str
    total_spent: Decimal


class RevenueByMonthOut(BaseModel):
    month: date
    total_revenue: Decimal


