-- Tableau export: one row per store, with readable labels.
-- Links to store_months.csv through store_id.
SELECT
    s.store_id,
    s.store_type,
    CASE s.assortment
        WHEN 'a' THEN 'basic'
        WHEN 'b' THEN 'extra'
        WHEN 'c' THEN 'extended'
    END                                     AS assortment,
    s.competition_distance,
    CASE
        WHEN s.competition_distance IS NULL  THEN '5. unknown'
        WHEN s.competition_distance < 500    THEN '1. under 500 m'
        WHEN s.competition_distance < 2000   THEN '2. 500 m to 2 km'
        WHEN s.competition_distance < 10000  THEN '3. 2 km to 10 km'
        ELSE '4. 10 km or more'
    END                                     AS competitor_distance,
    s.promo2,
    f.store_id IS NOT NULL                  AS has_forecast  -- 1 for the 856 forecast stores
FROM stores AS s
LEFT JOIN (SELECT DISTINCT store_id FROM forecast_schedule) AS f ON f.store_id = s.store_id
ORDER BY s.store_id;
