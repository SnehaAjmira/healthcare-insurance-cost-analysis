-- Staging: load raw member records, remove exact duplicates, derive analysis fields.
CREATE OR REPLACE TABLE raw_members AS
SELECT * FROM read_csv_auto('data/raw/insurance.csv');

CREATE OR REPLACE TABLE stg_members AS
SELECT DISTINCT
    age,
    sex,
    bmi,
    children,
    smoker = 'yes' AS is_smoker,
    region,
    charges,
    CASE
        WHEN age < 30 THEN '18-29'
        WHEN age < 40 THEN '30-39'
        WHEN age < 50 THEN '40-49'
        ELSE '50-64'
    END AS age_band,
    CASE                                   -- WHO adult BMI classes
        WHEN bmi < 18.5 THEN 'Underweight'
        WHEN bmi < 25   THEN 'Healthy'
        WHEN bmi < 30   THEN 'Overweight'
        ELSE 'Obese'
    END AS bmi_class,
    bmi >= 30 AS is_obese
FROM raw_members;

CREATE OR REPLACE TABLE stg_members_segmented AS
SELECT *,
    CASE
        WHEN NOT is_smoker THEN 'Non-smoker'
        WHEN is_obese      THEN 'Smoker, BMI 30+'
        ELSE 'Smoker, BMI under 30'
    END AS risk_segment
FROM stg_members;
