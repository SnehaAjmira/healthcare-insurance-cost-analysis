-- Average charges by age band and risk segment.
SELECT
    age_band,
    risk_segment,
    COUNT(*) AS members,
    ROUND(AVG(charges)) AS avg_charges
FROM stg_members_segmented
GROUP BY ALL
ORDER BY age_band, risk_segment;
