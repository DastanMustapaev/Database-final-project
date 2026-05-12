-- Schema for Car Rental System
-- Source of truth: app/db/schema.py

-- Needed for EXCLUDE constraints with equality on int (car_id)
CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(30) NOT NULL,
    driver_license_number VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cars (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(80) NOT NULL,
    model VARCHAR(80) NOT NULL,
    year INT NOT NULL CHECK (year BETWEEN 1980 AND 2100),
    price_per_day NUMERIC(10, 2) NOT NULL CHECK (price_per_day > 0),
    status VARCHAR(20) NOT NULL CHECK (status IN ('available', 'rented', 'maintenance'))
);

CREATE TABLE IF NOT EXISTS rentals (
    id SERIAL PRIMARY KEY,
    customer_id INT NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    car_id INT NOT NULL REFERENCES cars(id) ON DELETE RESTRICT,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_price NUMERIC(10, 2) NOT NULL CHECK (total_price >= 0),
    status VARCHAR(20) NOT NULL CHECK (status IN ('active', 'completed', 'cancelled')),
    CHECK (end_date >= start_date)
);

-- Prevent overlapping ACTIVE rentals for the same car (DB-enforced business rule)
-- Note: requires btree_gist extension above.
ALTER TABLE rentals
    ADD CONSTRAINT rentals_no_overlap_active_per_car
    EXCLUDE USING gist (
        car_id WITH =,
        daterange(start_date, end_date, '[]') WITH &&
    )
    WHERE (status = 'active');

CREATE TABLE IF NOT EXISTS payments (
    id SERIAL PRIMARY KEY,
    rental_id INT NOT NULL UNIQUE REFERENCES rentals(id) ON DELETE CASCADE,
    amount NUMERIC(10, 2) NOT NULL CHECK (amount > 0),
    payment_date TIMESTAMP NOT NULL DEFAULT NOW(),
    payment_method VARCHAR(20) NOT NULL CHECK (payment_method IN ('cash', 'card', 'bank_transfer'))
);

CREATE INDEX IF NOT EXISTS idx_rentals_customer_id ON rentals(customer_id);
CREATE INDEX IF NOT EXISTS idx_rentals_car_id ON rentals(car_id);
CREATE INDEX IF NOT EXISTS idx_rentals_status ON rentals(status);
CREATE INDEX IF NOT EXISTS idx_rentals_car_status_dates ON rentals(car_id, status, start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_cars_status ON cars(status);

