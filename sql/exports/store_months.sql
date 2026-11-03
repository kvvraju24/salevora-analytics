-- Tableau export: one row per store per month.
-- Sums, not averages, so Tableau can compute ratios correctly at any level:
-- sales per open day = SUM(sales) / SUM(open_days).
SELECT
    store_id,
    DATE_SUB(sale_date, INTERVAL DAYOFMONTH(sale_date) - 1 DAY)  AS month,  -- first day of the month
    SUM(sales)       AS sales,
    SUM(customers)   AS customers,
    SUM(is_open)     AS open_days,
    SUM(promo)       AS promo_days,
    COUNT(*)         AS days_recorded
FROM sales_history
GROUP BY store_id, month
ORDER BY store_id, month;
