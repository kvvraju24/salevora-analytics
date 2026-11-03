-- Q1. How did sales change from year to year?
-- SQL used: GROUP BY with aggregate functions (SUM, COUNT) and YEAR(), plus
-- CASE inside SUM to look at January-June only.
-- Totals alone mislead here: 2015 stops on 31 July, and 180 stores have no
-- data for July-December 2014. So we compare sales per open store-day, and
-- January-June of each year (same months, all 1,115 stores).
SELECT
    YEAR(sale_date)                    AS year,
    MIN(sale_date)                     AS first_day,
    MAX(sale_date)                     AS last_day,
    COUNT(DISTINCT store_id)           AS stores,
    SUM(sales)                         AS total_sales,
    SUM(is_open)                       AS open_store_days,
    ROUND(SUM(sales) / SUM(is_open))   AS avg_sales_per_open_day,
    ROUND(SUM(CASE WHEN MONTH(sale_date) <= 6 THEN sales END)
        / SUM(CASE WHEN MONTH(sale_date) <= 6 THEN is_open END))  AS avg_per_open_day_jan_jun
FROM sales_history
GROUP BY YEAR(sale_date)
ORDER BY year;
