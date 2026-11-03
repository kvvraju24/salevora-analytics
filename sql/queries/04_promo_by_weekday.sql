-- Q4. How much higher are sales on promotion days, for each weekday?
-- SQL used: CASE inside AVG. "CASE WHEN promo = 1 THEN sales END" is NULL on
-- non-promo days, and AVG skips NULLs, so it averages promo days only.
-- This shows an association, not proof that promotions cause the increase.
SELECT
    day_of_week,  -- 1 = Monday ... 7 = Sunday
    ROUND(AVG(CASE WHEN promo = 1 THEN sales END))  AS avg_sales_promo,
    ROUND(AVG(CASE WHEN promo = 0 THEN sales END))  AS avg_sales_no_promo,
    ROUND(100 * (AVG(CASE WHEN promo = 1 THEN sales END)
               / AVG(CASE WHEN promo = 0 THEN sales END) - 1), 1)  AS promo_uplift_pct
FROM sales_history
WHERE is_open = 1
GROUP BY day_of_week
ORDER BY day_of_week;
