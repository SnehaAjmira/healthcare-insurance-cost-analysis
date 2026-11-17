-- How concentrated are charges? Share of members vs share of total charges.
WITH ranked AS (
    SELECT *,
           NTILE(10) OVER (ORDER BY charges DESC) AS cost_decile
    FROM stg_members
)
SELECT
    'Smokers' AS member_group,
    ROUND(100.0 * COUNT(*) FILTER (WHERE is_smoker) / COUNT(*), 1) AS pct_of_members,
    ROUND(100.0 * SUM(charges) FILTER (WHERE is_smoker) / SUM(charges), 1) AS pct_of_charges
FROM ranked
UNION ALL
SELECT
    'Top 10% of members by cost',
    ROUND(100.0 * COUNT(*) FILTER (WHERE cost_decile = 1) / COUNT(*), 1),
    ROUND(100.0 * SUM(charges) FILTER (WHERE cost_decile = 1) / SUM(charges), 1)
FROM ranked
UNION ALL
SELECT
    'Top 20% of members by cost',
    ROUND(100.0 * COUNT(*) FILTER (WHERE cost_decile <= 2) / COUNT(*), 1),
    ROUND(100.0 * SUM(charges) FILTER (WHERE cost_decile <= 2) / SUM(charges), 1)
FROM ranked
UNION ALL
SELECT
    'Smokers within top 10%',
    ROUND(100.0 * COUNT(*) FILTER (WHERE cost_decile = 1 AND is_smoker) / COUNT(*) FILTER (WHERE cost_decile = 1), 1),
    NULL
FROM ranked;
