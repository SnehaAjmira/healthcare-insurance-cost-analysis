-- Data quality profile reported in the README.
SELECT 'Raw rows' AS check_name, COUNT(*)::VARCHAR AS result FROM raw_members
UNION ALL SELECT 'Exact duplicate rows removed', (SELECT COUNT(*) FROM raw_members) - (SELECT COUNT(*) FROM stg_members)
UNION ALL SELECT 'Rows analyzed', COUNT(*)::VARCHAR FROM stg_members
UNION ALL SELECT 'Null values (any column)', COUNT(*)::VARCHAR FROM raw_members
    WHERE age IS NULL OR sex IS NULL OR bmi IS NULL OR children IS NULL
       OR smoker IS NULL OR region IS NULL OR charges IS NULL
UNION ALL SELECT 'Age range', MIN(age)::VARCHAR || ' to ' || MAX(age)::VARCHAR FROM stg_members
UNION ALL SELECT 'BMI range', MIN(bmi)::VARCHAR || ' to ' || MAX(bmi)::VARCHAR FROM stg_members
UNION ALL SELECT 'Charges range (USD)', ROUND(MIN(charges))::VARCHAR || ' to ' || ROUND(MAX(charges))::VARCHAR FROM stg_members;
