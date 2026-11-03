-- Q3. How do store type and assortment relate to sales and customers?
-- SQL used: JOIN, GROUP BY on two columns, COUNT(DISTINCT ...).
-- Sales per customer = how much an average shopper spends per visit.
SELECT
    s.store_type,
    s.assortment,
    COUNT(DISTINCT s.store_id)                 AS stores,
    ROUND(AVG(h.sales))                        AS avg_sales_per_open_day,
    ROUND(AVG(h.customers))                    AS avg_customers_per_open_day,
    ROUND(SUM(h.sales) / SUM(h.customers), 2)  AS sales_per_customer
FROM sales_history AS h
JOIN stores AS s ON s.store_id = h.store_id
WHERE h.is_open = 1
GROUP BY s.store_type, s.assortment
ORDER BY s.store_type, s.assortment;
