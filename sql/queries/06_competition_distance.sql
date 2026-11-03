-- Q6. Do stores with a competitor nearby sell less?
-- SQL used: CASE to put each store into a distance band (NULL = unknown
-- gets its own band), then GROUP BY the band.
-- The numbers at the start of each label keep the bands in order.
SELECT
    CASE
        WHEN s.competition_distance IS NULL  THEN '5. unknown'
        WHEN s.competition_distance < 500    THEN '1. under 500 m'
        WHEN s.competition_distance < 2000   THEN '2. 500 m to 2 km'
        WHEN s.competition_distance < 10000  THEN '3. 2 km to 10 km'
        ELSE '4. 10 km or more'
    END                          AS competitor_distance,
    COUNT(DISTINCT s.store_id)   AS stores,
    ROUND(AVG(h.sales))          AS avg_sales_per_open_day
FROM sales_history AS h
JOIN stores AS s ON s.store_id = h.store_id
WHERE h.is_open = 1
GROUP BY competitor_distance
ORDER BY competitor_distance;
