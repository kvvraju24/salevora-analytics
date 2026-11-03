-- Q8. How did average sales change from month to month?
-- SQL used: a CTE (WITH) to build monthly figures first, then LAG(), a window
-- function that reads the previous row (last month) without a self-join.
-- We use sales per open store-day, so the 2014 gap (180 missing stores)
-- doesn't look like a sales drop.
WITH monthly AS (
    SELECT
        YEAR(sale_date)             AS year,
        MONTH(sale_date)            AS month,
        SUM(sales) / SUM(is_open)   AS avg_sales
    FROM sales_history
    GROUP BY YEAR(sale_date), MONTH(sale_date)
)
SELECT
    year,
    month,
    ROUND(avg_sales)  AS avg_sales_per_open_day,
    ROUND(100 * (avg_sales / LAG(avg_sales) OVER (ORDER BY year, month) - 1), 1)
                      AS change_vs_last_month_pct
FROM monthly
ORDER BY year, month;
