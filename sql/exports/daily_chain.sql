-- Tableau export: one row per day for the whole chain.
-- Used for the weekday and promotion views. Promotions are chain-wide
-- (all stores or none on any day, see docs/findings.md Q10), so MAX(promo)
-- is that day's promo flag.
SELECT
    sale_date                              AS date,
    DAYNAME(sale_date)                     AS weekday,
    day_of_week,                           -- 1 = Monday, for sorting
    SUM(sales)                             AS sales,
    SUM(is_open)                           AS open_stores,
    COUNT(*)                               AS stores_reporting,
    MAX(promo)                             AS promo,
    ROUND(AVG(state_holiday <> '0'), 2)    AS holiday_share
FROM sales_history
GROUP BY sale_date, day_of_week
ORDER BY sale_date;
