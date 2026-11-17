-- Smoking and obesity interaction: cost by segment and lift over the baseline.
WITH seg AS (
    SELECT
        is_smoker,
        is_obese,
        COUNT(*) AS members,
        AVG(charges) AS avg_charges,
        MEDIAN(charges) AS median_charges
    FROM stg_members
    GROUP BY ALL
)
SELECT
    CASE WHEN is_smoker THEN 'Smoker' ELSE 'Non-smoker' END AS smoking_status,
    CASE WHEN is_obese THEN 'BMI 30+' ELSE 'BMI under 30' END AS bmi_group,
    members,
    ROUND(avg_charges) AS avg_charges,
    ROUND(median_charges) AS median_charges,
    ROUND(avg_charges / FIRST_VALUE(avg_charges) OVER (ORDER BY is_smoker, is_obese), 2) AS cost_multiple_vs_baseline
FROM seg
ORDER BY is_smoker, is_obese;
