-- 01_staging.sql
-- PURPOSE: Create typed, named staging tables from raw ingested data
-- This is where we confirm data types and establish the grain of each table

-- Staging: Main application table (one row per applicant)
CREATE OR REPLACE TABLE stg_application AS
SELECT
    SK_ID_CURR,
    TARGET,                              -- 1 = defaulted, 0 = repaid
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
    DAYS_BIRTH,                          -- negative = days before application
    DAYS_EMPLOYED,                       -- negative = days before application
    DAYS_REGISTRATION,
    DAYS_ID_PUBLISH,
    CNT_FAM_MEMBERS,
    REGION_RATING_CLIENT,
    EXT_SOURCE_1,                        -- external credit scores
    EXT_SOURCE_2,
    EXT_SOURCE_3
FROM application_train;

-- Staging: Bureau (external credit history)
CREATE OR REPLACE TABLE stg_bureau AS
SELECT
    SK_ID_CURR,
    SK_ID_BUREAU,
    CREDIT_ACTIVE,
    CREDIT_TYPE,
    AMT_CREDIT_SUM,
    AMT_CREDIT_SUM_DEBT,
    AMT_CREDIT_SUM_OVERDUE,
    DAYS_CREDIT,
    DAYS_CREDIT_ENDDATE,
    CNT_CREDIT_PROLONG
FROM bureau;

-- Staging: Previous applications at Home Credit
CREATE OR REPLACE TABLE stg_prev_app AS
SELECT
    SK_ID_CURR,
    SK_ID_PREV,
    NAME_CONTRACT_TYPE,
    AMT_APPLICATION,
    AMT_CREDIT,
    NAME_CONTRACT_STATUS,               -- Approved / Refused / Canceled / Unused offer
    DAYS_DECISION,
    NAME_PAYMENT_TYPE,
    CODE_REJECT_REASON,
    AMT_DOWN_PAYMENT,
    RATE_INTEREST_PRIMARY
FROM previous_application;

-- Staging: Installment payments
CREATE OR REPLACE TABLE stg_installments AS
SELECT
    SK_ID_CURR,
    SK_ID_PREV,
    NUM_INSTALMENT_NUMBER,
    DAYS_INSTALMENT,                    -- when payment was due
    DAYS_ENTRY_PAYMENT,                 -- when payment was actually made
    AMT_INSTALMENT,
    AMT_PAYMENT
FROM installments_payments;

-- Staging: Credit card balance
CREATE OR REPLACE TABLE stg_credit_card AS
SELECT
    SK_ID_CURR,
    SK_ID_PREV,
    MONTHS_BALANCE,
    AMT_BALANCE,
    AMT_CREDIT_LIMIT_ACTUAL,
    AMT_DRAWINGS_CURRENT,
    AMT_PAYMENT_CURRENT,
    SK_DPD                              -- days past due
FROM credit_card_balance;