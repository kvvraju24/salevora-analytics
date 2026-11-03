-- Q2. Which 10 stores sell the most on an average open day?
-- SQL used: WHERE to keep open days only, JOIN to add store details,
-- GROUP BY, ORDER BY ... DESC and LIMIT.
SELECT
    h.store_id,
    s.store_type,
    s.assortment,
    ROUND(AVG(h.sales))  AS avg_sales_per_open_day,
    COUNT(*)             AS open_days
FROM sales_history AS h
JOIN stores AS s ON s.store_id = h.store_id
WHERE h.is_open = 1
GROUP BY h.store_id, s.store_type, s.assortment
ORDER BY avg_sales_per_open_day DESC
LIMIT 10;
