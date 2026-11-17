-- Secondary factors: region, sex, and number of dependents.
SELECT 'Region' AS factor, region AS level, COUNT(*) AS members,
       ROUND(AVG(charges)) AS avg_charges,
       ROUND(100.0 * AVG(is_smoker::INT), 1) AS smoker_pct
FROM stg_members GROUP BY ALL
UNION ALL
SELECT 'Sex', sex, COUNT(*), ROUND(AVG(charges)), ROUND(100.0 * AVG(is_smoker::INT), 1)
FROM stg_members GROUP BY ALL
UNION ALL
SELECT 'Dependents', CASE WHEN children >= 3 THEN '3+' ELSE children::VARCHAR END, COUNT(*),
       ROUND(AVG(charges)), ROUND(100.0 * AVG(is_smoker::INT), 1)
FROM stg_members GROUP BY ALL
ORDER BY factor, level;
