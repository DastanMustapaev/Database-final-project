-- Sample queries for Car Rental System

-- 1) Get all available cars
SELECT id, brand, model, year, price_per_day
FROM cars
WHERE status = 'available'
ORDER BY id;

-- 2) Get rentals by customer (JOIN)
-- Replace $1 with customer_id
SELECT
    r.id AS rental_id,
    c.full_name AS customer_name,
    CONCAT(car.brand, ' ', car.model) AS car_name,
    r.start_date,
    r.end_date,
    r.status,
    r.total_price
FROM rentals r
JOIN customers c ON c.id = r.customer_id
JOIN cars car ON car.id = r.car_id
WHERE c.id = $1
ORDER BY r.start_date DESC;

-- 3) Calculate total revenue (aggregation)
SELECT COALESCE(SUM(amount), 0) AS total_revenue
FROM payments;

-- 4) Find the most rented car (GROUP BY + ORDER)
SELECT
    car.id AS car_id,
    car.brand,
    car.model,
    COUNT(r.id)::INT AS rent_count
FROM rentals r
JOIN cars car ON car.id = r.car_id
GROUP BY car.id, car.brand, car.model
ORDER BY rent_count DESC, car.id ASC
LIMIT 1;

-- 5) Top customers by total payments (advanced report)
-- Replace $1 with a limit value
SELECT
    c.id AS customer_id,
    c.full_name,
    COALESCE(SUM(p.amount), 0)::NUMERIC(10, 2) AS total_spent
FROM customers c
JOIN rentals r ON r.customer_id = c.id
JOIN payments p ON p.rental_id = r.id
GROUP BY c.id, c.full_name
ORDER BY total_spent DESC, c.id ASC
LIMIT $1;

-- 6) Revenue by month (advanced report)
SELECT
    DATE_TRUNC('month', payment_date)::date AS month,
    COALESCE(SUM(amount), 0)::NUMERIC(10, 2) AS total_revenue
FROM payments
GROUP BY month
ORDER BY month;

