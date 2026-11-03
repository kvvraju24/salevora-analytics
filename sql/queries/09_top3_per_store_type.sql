-- Q9. Which are the top 3 stores within each store type?
-- SQL used: RANK() OVER (PARTITION BY store_type ...), a ranking that restarts
-- for every store type. A window result can't be filtered in the same
-- SELECT's WHERE, so the ranking goes in a CTE and we filter afterwards.
WITH store_avg AS (
    SELECT
        s.store_type,
        h.store_id,
        AVG(h.sales) AS avg_sales
    FROM sales_history AS h
    JOIN stores AS s ON s.store_id = h.store_id
    WHERE h.is_open = 1
    GROUP BY s.store_type, h.store_id
),
ranked AS (
    SELECT
        store_type,
        store_id,
        ROUND(avg_sales) AS avg_sales_per_open_day,
        RANK() OVER (PARTITION BY store_type ORDER BY avg_sales DESC) AS rank_in_type
    FROM store_avg
)
SELECT *
FROM ranked
WHERE rank_in_type <= 3
ORDER BY store_type, rank_in_type;
