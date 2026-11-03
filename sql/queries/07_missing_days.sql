-- Q7. Which stores are missing days in their history, and when?
-- SQL used: HAVING (a filter applied after GROUP BY), a subquery for the
-- number of days a complete store has, and SUM(condition) to count the days
-- each store has in July-December 2014 (a true condition counts as 1).
SELECT
    days_recorded,
    COUNT(*)                 AS stores,
    MIN(store_id)            AS example_store,
    MIN(first_day)           AS first_day,
    MAX(last_day)            AS last_day,
    MAX(days_jul_dec_2014)   AS days_jul_dec_2014
FROM (
    SELECT
        store_id,
        COUNT(*)        AS days_recorded,
        MIN(sale_date)  AS first_day,
        MAX(sale_date)  AS last_day,
        SUM(sale_date BETWEEN '2014-07-01' AND '2014-12-31')  AS days_jul_dec_2014
    FROM sales_history
    GROUP BY store_id
    HAVING COUNT(*) < (SELECT COUNT(DISTINCT sale_date) FROM sales_history)
) AS incomplete
GROUP BY days_recorded
ORDER BY days_recorded;
