-- Q10. Was chain-wide demand rising or falling at the end of the history?
-- SQL used: moving averages, AVG() OVER (ORDER BY ... ROWS BETWEEN n PRECEDING
-- AND CURRENT ROW). A 7-day window removes the weekly pattern (most stores
-- close on Sunday). But promotions usually run every other week (see promo_share),
-- so it takes a 14-day window to see the trend underneath the promo cycle.
-- The date filter comes AFTER the averages are computed; filtering first
-- would cut the first windows short.
WITH daily AS (
    SELECT
        sale_date,
        SUM(sales)             AS total_sales,
        ROUND(AVG(promo), 2)   AS promo_share  -- 1.00 = every store on promo
    FROM sales_history
    GROUP BY sale_date
),
smoothed AS (
    SELECT
        sale_date,
        total_sales,
        promo_share,
        AVG(total_sales) OVER (ORDER BY sale_date
                               ROWS BETWEEN 6 PRECEDING AND CURRENT ROW)  AS avg_7,
        AVG(total_sales) OVER (ORDER BY sale_date
                               ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS avg_14
    FROM daily
)
SELECT
    sale_date,
    total_sales,
    promo_share,
    ROUND(avg_7)   AS moving_avg_7_days,
    ROUND(avg_14)  AS moving_avg_14_days
FROM smoothed
WHERE sale_date >= '2015-06-01'
ORDER BY sale_date;
