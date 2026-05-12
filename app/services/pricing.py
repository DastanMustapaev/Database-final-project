from datetime import date
from decimal import Decimal


def calculate_total_price(start_date: date, end_date: date, price_per_day: Decimal) -> Decimal:
    if end_date < start_date:
        raise ValueError("end_date must be equal to or after start_date")
    total_days = (end_date - start_date).days + 1
    return (price_per_day * total_days).quantize(Decimal("0.01"))

