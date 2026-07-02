-- 02_clean.sql
-- PURPOSE: Clean each staging table — handle edge cases, standardise values

-- Clean application table
-- Convert DAYS_BIRTH (negative days) to age in years
-- Convert DAYS_EMPLOYED (365243 = unemployed sentinel value → NULL)
CREATE OR REPLACE TABLE clean_application AS
SELECT
    SK_ID_CURR,
    TARGET,
    NAME_CONTRACT_TYPE,
    CODE_GENDER,
    FLAG_OWN_CAR,
    FLAG_OWN_REALTY,
    CNT_CHILDREN,
    AMT_INCOME_TOTAL,
    AMT_CREDIT,
    AMT_ANNUITY,
    AMT_GOODS_PRICE,
    NAME_INCOME_TYPE,
    NAME_EDUCATION_TYPE,
    NAME_FAMILY_STATUS,
    NAME_HOUSING_TYPE,
    
    -- Convert negative DAYS_BIRTH to positive age in years
    ABS(DAYS_BIRTH) / 365.25 AS age_years,
    
    -- Clean DAYS_EMPLOYED: 365243 is a sentinel for "not employed"
    CASE 
        WHEN DAYS_EMPLOYED = 365243 THEN NULL 
        ELSE ABS(DAYS_EMPLOYED) / 365.25 
    END AS years_employed,
    
    CNT_FAM_MEMBERS,
    REGION_RATING_CLIENT,
    
    -- External scores: keep as-is, will handle nulls in feature mart
    EXT_SOURCE_1,
    EXT_SOURCE_2,
    EXT_SOURCE_3,
    
    -- Derived ratios (key risk features)
    CASE 
        WHEN AMT_INCOME_TOTAL > 0 
        THEN ROUND(AMT_CREDIT / AMT_INCOME_TOTAL, 4) 
        ELSE NULL 
    END AS credit_to_income_ratio,
    
    CASE 
        WHEN AMT_INCOME_TOTAL > 0 
        THEN ROUND(AMT_ANNUITY / AMT_INCOME_TOTAL, 4) 
        ELSE NULL 
    END AS annuity_to_income_ratio

FROM stg_application
WHERE SK_ID_CURR IS NOT NULL;

-- Clean bureau: remove records with no credit amount
CREATE OR REPLACE TABLE clean_bureau AS
SELECT
    SK_ID_CURR,
    SK_ID_BUREAU,
    CREDIT_ACTIVE,
    CREDIT_TYPE,
    COALESCE(AMT_CREDIT_SUM, 0) AS AMT_CREDIT_SUM,
    COALESCE(AMT_CREDIT_SUM_DEBT, 0) AS AMT_CREDIT_SUM_DEBT,
    COALESCE(AMT_CREDIT_SUM_OVERDUE, 0) AS AMT_CREDIT_SUM_OVERDUE,
    DAYS_CREDIT,
    CNT_CREDIT_PROLONG
FROM stg_bureau
WHERE SK_ID_CURR IS NOT NULL;

-- Clean installments: calculate payment delay (positive = paid late)
CREATE OR REPLACE TABLE clean_installments AS
SELECT
    SK_ID_CURR,
    SK_ID_PREV,
    NUM_INSTALMENT_NUMBER,
    DAYS_INSTALMENT,
    DAYS_ENTRY_PAYMENT,
    AMT_INSTALMENT,
    COALESCE(AMT_PAYMENT, 0) AS AMT_PAYMENT,
    
    -- Key derived column: how many days late was this payment?
    -- Positive = paid late, Negative = paid early, NULL = not paid
    CASE 
        WHEN DAYS_ENTRY_PAYMENT IS NOT NULL 
        THEN DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT 
        ELSE NULL 
    END AS days_late,
    
    -- Was this payment late? (binary flag)
    CASE 
        WHEN DAYS_ENTRY_PAYMENT > DAYS_INSTALMENT THEN 1 
        ELSE 0 
    END AS is_late_payment,
    
    -- Was payment amount short?
    CASE 
        WHEN AMT_PAYMENT < AMT_INSTALMENT THEN 1 
        ELSE 0 
    END AS is_underpayment

FROM stg_installments
WHERE SK_ID_CURR IS NOT NULL;