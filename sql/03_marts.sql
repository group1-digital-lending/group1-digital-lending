-- 03_marts.sql
-- PURPOSE: Build the one-row-per-applicant feature mart
-- Demonstrates: CTEs, multi-table JOIN, GROUP BY→features,
--               window functions, CASE risk bands, ratio features

-- ============================================================
-- MART 1: bureau_features
-- Aggregate external credit history per applicant
-- ============================================================
CREATE OR REPLACE TABLE mart_bureau_features AS

WITH bureau_agg AS (
    SELECT
        SK_ID_CURR,
        COUNT(SK_ID_BUREAU)                          AS bureau_loan_count,
        SUM(CASE WHEN CREDIT_ACTIVE = 'Active' THEN 1 ELSE 0 END)
                                                     AS bureau_active_loans,
        SUM(AMT_CREDIT_SUM)                          AS bureau_total_credit,
        SUM(AMT_CREDIT_SUM_DEBT)                     AS bureau_total_debt,
        SUM(AMT_CREDIT_SUM_OVERDUE)                  AS bureau_total_overdue,
        AVG(AMT_CREDIT_SUM)                          AS bureau_avg_credit,
        MAX(AMT_CREDIT_SUM)                          AS bureau_max_credit,
        SUM(CNT_CREDIT_PROLONG)                      AS bureau_total_prolonged,
        COUNT(DISTINCT CREDIT_TYPE)                  AS bureau_credit_types,
        MIN(DAYS_CREDIT)                             AS bureau_oldest_credit_days
    FROM clean_bureau
    GROUP BY SK_ID_CURR
),

bureau_overdue_rate AS (
    SELECT
        SK_ID_CURR,
        ROUND(
            SUM(CASE WHEN AMT_CREDIT_SUM_OVERDUE > 0 THEN 1 ELSE 0 END) * 1.0
            / NULLIF(COUNT(*), 0),
        4) AS bureau_overdue_rate
    FROM clean_bureau
    GROUP BY SK_ID_CURR
)

SELECT
    b.*,
    o.bureau_overdue_rate,
    ROUND(b.bureau_total_debt / NULLIF(b.bureau_total_credit, 0), 4) AS bureau_debt_ratio
FROM bureau_agg b
LEFT JOIN bureau_overdue_rate o ON b.SK_ID_CURR = o.SK_ID_CURR;


-- ============================================================
-- MART 2: installment_features
-- Payment behaviour — the most powerful default signal
-- ============================================================
CREATE OR REPLACE TABLE mart_installment_features AS

WITH instalment_agg AS (
    SELECT
        SK_ID_CURR,
        COUNT(*)                                     AS inst_total_payments,
        SUM(is_late_payment)                         AS inst_late_count,
        AVG(CASE WHEN days_late IS NOT NULL
            THEN days_late ELSE 0 END)               AS inst_avg_days_late,
        MAX(COALESCE(days_late, 0))                  AS inst_max_days_late,
        SUM(is_underpayment)                         AS inst_underpayment_count,
        AVG(AMT_PAYMENT / NULLIF(AMT_INSTALMENT, 0)) AS inst_payment_ratio
    FROM clean_installments
    GROUP BY SK_ID_CURR
)

SELECT
    a.*,
    ROUND(a.inst_late_count * 1.0 / NULLIF(a.inst_total_payments, 0), 4)
        AS inst_late_payment_rate
FROM instalment_agg a;


-- ============================================================
-- MART 3: prev_application_features
-- History of prior applications at Home Credit
-- ============================================================
CREATE OR REPLACE TABLE mart_prev_app_features AS

SELECT
    SK_ID_CURR,
    COUNT(SK_ID_PREV)                                        AS prev_app_count,
    SUM(CASE WHEN NAME_CONTRACT_STATUS = 'Approved' THEN 1 ELSE 0 END)
                                                             AS prev_approved_count,
    SUM(CASE WHEN NAME_CONTRACT_STATUS = 'Refused'  THEN 1 ELSE 0 END)
                                                             AS prev_refused_count,
    SUM(CASE WHEN NAME_CONTRACT_STATUS = 'Canceled' THEN 1 ELSE 0 END)
                                                             AS prev_canceled_count,
    AVG(AMT_APPLICATION)                                     AS prev_avg_application_amt,
    AVG(AMT_CREDIT)                                          AS prev_avg_credit_amt,
    ROUND(
        SUM(CASE WHEN NAME_CONTRACT_STATUS = 'Approved' THEN 1 ELSE 0 END) * 1.0
        / NULLIF(COUNT(SK_ID_PREV), 0),
    4) AS prev_approval_rate,
    AVG(RATE_INTEREST_PRIMARY)                               AS prev_avg_interest_rate
FROM stg_prev_app
GROUP BY SK_ID_CURR;


-- ============================================================
-- MART 4: credit_card_features
-- Monthly credit card behaviour
-- ============================================================
CREATE OR REPLACE TABLE mart_credit_card_features AS

SELECT
    SK_ID_CURR,
    COUNT(*)                                             AS cc_months_count,
    AVG(AMT_BALANCE)                                     AS cc_avg_balance,
    MAX(AMT_BALANCE)                                     AS cc_max_balance,
    AVG(SK_DPD)                                          AS cc_avg_days_past_due,
    MAX(SK_DPD)                                          AS cc_max_days_past_due,
    SUM(CASE WHEN SK_DPD > 0 THEN 1 ELSE 0 END)         AS cc_months_overdue,
    AVG(AMT_BALANCE / NULLIF(AMT_CREDIT_LIMIT_ACTUAL, 0)) AS cc_avg_utilisation
FROM stg_credit_card
GROUP BY SK_ID_CURR;


-- ============================================================
-- FINAL MART: one row per applicant with all features joined
-- ============================================================
CREATE OR REPLACE TABLE mart_applicant_features AS

SELECT
    -- Identity
    a.SK_ID_CURR,
    a.TARGET,

    -- APPLICATION FEATURES
    a.NAME_CONTRACT_TYPE,
    a.CODE_GENDER,
    a.FLAG_OWN_CAR,
    a.FLAG_OWN_REALTY,
    a.CNT_CHILDREN,
    a.AMT_INCOME_TOTAL,
    a.AMT_CREDIT,
    a.AMT_ANNUITY,
    a.NAME_INCOME_TYPE,
    a.NAME_EDUCATION_TYPE,
    a.NAME_FAMILY_STATUS,
    a.age_years,
    a.years_employed,
    a.EXT_SOURCE_1,
    a.EXT_SOURCE_2,
    a.EXT_SOURCE_3,
    a.credit_to_income_ratio,
    a.annuity_to_income_ratio,

    -- BUREAU FEATURES
    COALESCE(b.bureau_loan_count, 0)         AS bureau_loan_count,
    COALESCE(b.bureau_active_loans, 0)       AS bureau_active_loans,
    COALESCE(b.bureau_total_debt, 0)         AS bureau_total_debt,
    COALESCE(b.bureau_total_overdue, 0)      AS bureau_total_overdue,
    COALESCE(b.bureau_overdue_rate, 0)       AS bureau_overdue_rate,
    COALESCE(b.bureau_debt_ratio, 0)         AS bureau_debt_ratio,

    -- INSTALLMENT FEATURES
    COALESCE(i.inst_total_payments, 0)       AS inst_total_payments,
    COALESCE(i.inst_late_count, 0)           AS inst_late_count,
    COALESCE(i.inst_late_payment_rate, 0)    AS inst_late_payment_rate,
    COALESCE(i.inst_avg_days_late, 0)        AS inst_avg_days_late,
    COALESCE(i.inst_max_days_late, 0)        AS inst_max_days_late,
    COALESCE(i.inst_payment_ratio, 1)        AS inst_payment_ratio,

    -- PREVIOUS APPLICATION FEATURES
    COALESCE(p.prev_app_count, 0)            AS prev_app_count,
    COALESCE(p.prev_approved_count, 0)       AS prev_approved_count,
    COALESCE(p.prev_refused_count, 0)        AS prev_refused_count,
    COALESCE(p.prev_approval_rate, 0)        AS prev_approval_rate,

    -- CREDIT CARD FEATURES
    COALESCE(c.cc_avg_days_past_due, 0)      AS cc_avg_days_past_due,
    COALESCE(c.cc_max_days_past_due, 0)      AS cc_max_days_past_due,
    COALESCE(c.cc_avg_utilisation, 0)        AS cc_avg_utilisation,
    COALESCE(c.cc_months_overdue, 0)         AS cc_months_overdue,

    -- RISK BAND (CASE bucketing)
    CASE
        WHEN a.credit_to_income_ratio > 5 THEN 'Very High Risk'
        WHEN a.credit_to_income_ratio > 3 THEN 'High Risk'
        WHEN a.credit_to_income_ratio > 2 THEN 'Medium Risk'
        WHEN a.credit_to_income_ratio > 1 THEN 'Low Risk'
        ELSE 'Very Low Risk'
    END AS credit_risk_band

FROM clean_application a
LEFT JOIN mart_bureau_features       b ON a.SK_ID_CURR = b.SK_ID_CURR
LEFT JOIN mart_installment_features  i ON a.SK_ID_CURR = i.SK_ID_CURR
LEFT JOIN mart_prev_app_features     p ON a.SK_ID_CURR = p.SK_ID_CURR
LEFT JOIN mart_credit_card_features  c ON a.SK_ID_CURR = c.SK_ID_CURR;