-- 04_analysis.sql
-- PURPOSE: Answer business questions with advanced SQL
-- Demonstrates: RANK, NTILE, LAG, GROUP BY HAVING, 
--               window share-of-total, CASE bucketing

-- ============================================================
-- Q1: Default rate by income band
-- Techniques: CASE bucketing, GROUP BY, HAVING
-- ============================================================
CREATE OR REPLACE TABLE analysis_default_by_income AS
SELECT
    CASE
        WHEN AMT_INCOME_TOTAL < 100000  THEN '1. Under 100k'
        WHEN AMT_INCOME_TOTAL < 200000  THEN '2. 100k-200k'
        WHEN AMT_INCOME_TOTAL < 400000  THEN '3. 200k-400k'
        WHEN AMT_INCOME_TOTAL < 700000  THEN '4. 400k-700k'
        ELSE                                 '5. 700k+'
    END AS income_band,
    COUNT(*)                            AS applicant_count,
    SUM(TARGET)                         AS defaults,
    ROUND(AVG(TARGET) * 100, 2)         AS default_rate_pct
FROM clean_application
GROUP BY income_band
HAVING COUNT(*) > 100
ORDER BY income_band;


-- ============================================================
-- Q2: Default rate by contract type + window share-of-total
-- Techniques: GROUP BY, window function share-of-total
-- ============================================================
CREATE OR REPLACE TABLE analysis_default_by_contract AS
SELECT
    NAME_CONTRACT_TYPE,
    COUNT(*)                                            AS total,
    SUM(TARGET)                                         AS defaults,
    ROUND(AVG(TARGET) * 100, 2)                         AS default_rate_pct,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2)  AS pct_of_all_applicants
FROM clean_application
GROUP BY NAME_CONTRACT_TYPE
ORDER BY default_rate_pct DESC;


-- ============================================================
-- Q3: NTILE risk quintiles based on credit-to-income ratio
-- Techniques: NTILE window function
-- ============================================================
CREATE OR REPLACE TABLE analysis_ntile_risk AS
SELECT
    risk_quintile,
    COUNT(*)                                      AS applicants,
    ROUND(AVG(TARGET) * 100, 2)                   AS default_rate_pct,
    ROUND(AVG(credit_to_income_ratio), 2)         AS avg_credit_income_ratio
FROM (
    SELECT
        SK_ID_CURR,
        TARGET,
        credit_to_income_ratio,
        NTILE(5) OVER (ORDER BY credit_to_income_ratio) AS risk_quintile
    FROM clean_application
    WHERE credit_to_income_ratio IS NOT NULL
)
GROUP BY risk_quintile
ORDER BY risk_quintile;


-- ============================================================
-- Q4: Rank education types by default rate
-- Techniques: RANK window function
-- ============================================================
CREATE OR REPLACE TABLE analysis_education_rank AS
SELECT
    NAME_EDUCATION_TYPE,
    COUNT(*)                                                AS applicants,
    ROUND(AVG(TARGET) * 100, 2)                             AS default_rate_pct,
    RANK() OVER (ORDER BY AVG(TARGET) DESC)                 AS risk_rank
FROM clean_application
GROUP BY NAME_EDUCATION_TYPE
HAVING COUNT(*) > 200
ORDER BY risk_rank;


-- ============================================================
-- Q5: Payment behaviour vs default rate
-- Techniques: CASE bucketing, GROUP BY
-- ============================================================
CREATE OR REPLACE TABLE analysis_payment_behaviour AS
SELECT
    CASE
        WHEN inst_late_payment_rate = 0        THEN '1. Never Late'
        WHEN inst_late_payment_rate < 0.05     THEN '2. Rarely Late (<5%)'
        WHEN inst_late_payment_rate < 0.20     THEN '3. Sometimes Late (5-20%)'
        WHEN inst_late_payment_rate < 0.50     THEN '4. Often Late (20-50%)'
        ELSE                                        '5. Mostly Late (>50%)'
    END AS payment_behaviour,
    COUNT(*)                                   AS applicants,
    ROUND(AVG(TARGET) * 100, 2)                AS default_rate_pct
FROM mart_applicant_features
WHERE inst_total_payments > 0
GROUP BY payment_behaviour
ORDER BY payment_behaviour;


-- ============================================================
-- Q6: Top 10 riskiest segments (multi-column grouping + RANK)
-- Techniques: RANK, GROUP BY, HAVING, multi-column grouping
-- ============================================================
CREATE OR REPLACE TABLE analysis_riskiest_segments AS
SELECT
    NAME_CONTRACT_TYPE,
    NAME_INCOME_TYPE,
    credit_risk_band,
    COUNT(*)                                AS applicants,
    ROUND(AVG(TARGET) * 100, 2)             AS default_rate_pct,
    RANK() OVER (ORDER BY AVG(TARGET) DESC) AS risk_rank
FROM mart_applicant_features
GROUP BY NAME_CONTRACT_TYPE, NAME_INCOME_TYPE, credit_risk_band
HAVING COUNT(*) > 50
ORDER BY risk_rank
LIMIT 10;


-- ============================================================
-- Q7: LAG — Month-over-month trend (using age as time proxy)
-- Techniques: LAG window function
-- ============================================================
CREATE OR REPLACE TABLE analysis_age_default_trend AS
WITH age_groups AS (
    SELECT
        CAST(age_years AS INT) AS age,
        COUNT(*) AS applicants,
        ROUND(AVG(TARGET) * 100, 2) AS default_rate
    FROM clean_application
    WHERE age_years IS NOT NULL
    GROUP BY CAST(age_years AS INT)
)
SELECT
    age,
    applicants,
    default_rate,
    LAG(default_rate) OVER (ORDER BY age) AS prev_age_default_rate,
    ROUND(default_rate - LAG(default_rate) OVER (ORDER BY age), 2) AS change_vs_prev_age
FROM age_groups
ORDER BY age;