-- Q5. What happens to sales on public holidays?
-- SQL used: CASE to turn codes into labels. The average of a 0/1 column is
-- the share of 1s, so 100 * AVG(is_open) = percent of store-days open.
SELECT
    CASE state_holiday
        WHEN '0' THEN 'No public holiday'
        WHEN 'a' THEN 'Public holiday'
        WHEN 'b' THEN 'Easter'
        WHEN 'c' THEN 'Christmas'
    END                                               AS holiday,
    COUNT(*)                                          AS store_days,
    ROUND(100 * AVG(is_open), 1)                      AS pct_open,
    ROUND(AVG(CASE WHEN is_open = 1 THEN sales END))  AS avg_sales_when_open
FROM sales_history
GROUP BY state_holiday
ORDER BY state_holiday;
