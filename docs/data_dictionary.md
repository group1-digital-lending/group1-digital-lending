# Data Dictionary
## Group 1 — Digital Lending Credit Risk Capstone
### Thrive Africa / Ishango.ai · Analytics Engineering · March 2026

---

## Source Tables (7 tables, primary key: SK_ID_CURR)

| # | Table | Grain | Rows | Description |
|---|-------|-------|------|-------------|
| 1 | application_train | 1 row per applicant | 307,511 | Main table. TARGET=1 means defaulted, 0 means repaid |
| 2 | bureau | 1 row per external loan | 1,716,428 | Credit history at other banks (reported to Credit Bureau) |
| 3 | bureau_balance | 1 row per loan per month | 27,299,925 | Monthly status of external bureau loans |
| 4 | previous_application | 1 row per prior application | 1,670,214 | Past loan applications at Home Credit |
| 5 | installments_payments | 1 row per installment | 13,605,401 | Payment history — due date vs actual payment date |
| 6 | POS_CASH_balance | 1 row per loan per month | 10,001,358 | Monthly snapshots of POS and cash loans |
| 7 | credit_card_balance | 1 row per card per month | 3,840,312 | Monthly credit card statements |

---

## Staging Tables (sql/01_staging.sql)

| Table | Source | Purpose |
|-------|--------|---------|
| stg_application | application_train | Selected columns only — establishes applicant grain |
| stg_bureau | bureau | External credit history columns |
| stg_prev_app | previous_application | Prior application history |
| stg_installments | installments_payments | Payment due vs paid dates |
| stg_credit_card | credit_card_balance | Monthly card balance and DPD |

---

## Clean Tables (sql/02_clean.sql)

| Table | Key Transformations |
|-------|-------------------|
| clean_application | DAYS_BIRTH → age_years; DAYS_EMPLOYED 365243 sentinel → NULL; credit_to_income_ratio; annuity_to_income_ratio |
| clean_bureau | COALESCE nulls to 0 on amount columns |
| clean_installments | days_late = DAYS_ENTRY_PAYMENT - DAYS_INSTALMENT; is_late_payment flag; is_underpayment flag |

---

## Feature Mart (sql/03_marts.sql)

### mart_applicant_features — ONE ROW PER APPLICANT

| Column | Type | Source | Description |
|--------|------|--------|-------------|
| SK_ID_CURR | INT | application_train | Primary key — unique applicant ID |
| TARGET | INT | application_train | 1 = defaulted, 0 = repaid |
| NAME_CONTRACT_TYPE | TEXT | application_train | Cash loans or Revolving loans |
| CODE_GENDER | TEXT | application_train | M or F |
| FLAG_OWN_CAR | TEXT | application_train | Y or N — owns a car |
| FLAG_OWN_REALTY | TEXT | application_train | Y or N — owns property |
| CNT_CHILDREN | INT | application_train | Number of children |
| AMT_INCOME_TOTAL | FLOAT | application_train | Annual income |
| AMT_CREDIT | FLOAT | application_train | Loan credit amount |
| AMT_ANNUITY | FLOAT | application_train | Monthly loan annuity |
| NAME_INCOME_TYPE | TEXT | application_train | Employment type |
| NAME_EDUCATION_TYPE | TEXT | application_train | Highest education level |
| NAME_FAMILY_STATUS | TEXT | application_train | Marital status |
| age_years | FLOAT | clean_application | Age in years (from DAYS_BIRTH) |
| years_employed | FLOAT | clean_application | Years at current job (NULL if unemployed) |
| EXT_SOURCE_1 | FLOAT | application_train | External credit score 1 |
| EXT_SOURCE_2 | FLOAT | application_train | External credit score 2 (strongest predictor) |
| EXT_SOURCE_3 | FLOAT | application_train | External credit score 3 |
| credit_to_income_ratio | FLOAT | clean_application | AMT_CREDIT / AMT_INCOME_TOTAL |
| annuity_to_income_ratio | FLOAT | clean_application | AMT_ANNUITY / AMT_INCOME_TOTAL |
| bureau_loan_count | INT | bureau | Total number of external loans |
| bureau_active_loans | INT | bureau | Number of currently active external loans |
| bureau_total_debt | FLOAT | bureau | Total outstanding debt at other banks |
| bureau_total_overdue | FLOAT | bureau | Total overdue amount at other banks |
| bureau_overdue_rate | FLOAT | bureau | Fraction of bureau loans with overdue amounts |
| bureau_debt_ratio | FLOAT | bureau | bureau_total_debt / bureau_total_credit |
| inst_total_payments | INT | installments_payments | Total number of installment payments made |
| inst_late_count | INT | installments_payments | Number of late payments |
| inst_late_payment_rate | FLOAT | installments_payments | inst_late_count / inst_total_payments |
| inst_avg_days_late | FLOAT | installments_payments | Average days late per payment |
| inst_max_days_late | FLOAT | installments_payments | Maximum days late on any single payment |
| inst_payment_ratio | FLOAT | installments_payments | AMT_PAYMENT / AMT_INSTALMENT ratio |
| prev_app_count | INT | previous_application | Total prior applications at Home Credit |
| prev_approved_count | INT | previous_application | Number of prior approved applications |
| prev_refused_count | INT | previous_application | Number of prior refused applications |
| prev_approval_rate | FLOAT | previous_application | prev_approved / prev_total |
| cc_avg_days_past_due | FLOAT | credit_card_balance | Average days past due on credit card |
| cc_max_days_past_due | FLOAT | credit_card_balance | Maximum days past due ever |
| cc_avg_utilisation | FLOAT | credit_card_balance | Average balance / credit limit ratio |
| cc_months_overdue | INT | credit_card_balance | Number of months with overdue balance |
| credit_risk_band | TEXT | clean_application | CASE bucket: Very Low / Low / Medium / High / Very High Risk |

---

## Analysis Tables (sql/04_analysis.sql)

| Table | Business Question | SQL Techniques |
|-------|------------------|----------------|
| analysis_default_by_income | Default rate by income band | CASE, GROUP BY, HAVING |
| analysis_default_by_contract | Default rate by contract type | GROUP BY, window share-of-total |
| analysis_ntile_risk | Risk quintiles by credit burden | NTILE(5) window function |
| analysis_education_rank | Education level risk ranking | RANK() window function |
| analysis_payment_behaviour | Payment history vs default | CASE bucketing, GROUP BY |
| analysis_riskiest_segments | Top 10 riskiest segments | RANK(), multi-column GROUP BY |
| analysis_age_default_trend | Default rate trend by age | LAG() window function |

---

## Key Business Findings

1. **Default rate:** 8.07% overall — significant class imbalance
2. **Strongest predictor:** EXT_SOURCE_2 (external credit score)
3. **Payment behaviour:** Applicants with >20% late payment rate 
   default at 3x the rate of never-late applicants
4. **Age effect:** Younger applicants (20-30) carry significantly 
   higher default risk
5. **Income paradox:** Lower income bands have higher default rates 
   but mid-range (100k-200k) is actually riskiest

---

## Model Performance

| Model | AUC Score | vs Baseline |
|-------|-----------|-------------|
| Baseline (always predict 0) | 0.5000 | — |
| Logistic Regression | 0.6010 | +0.1010 |
| Random Forest | 0.7462 | +0.2462 |

**Best model:** Random Forest with `class_weight='balanced'`  
**Features used:** 26 SQL-engineered features from 5 tables  
**Estimated bad debt prevented:** GHS 804,000,000

---

*Data source: Home Credit Default Risk — Kaggle*  
*License: Belongs to Home Credit Group*  
*Group 1 · Thrive Africa · March 2026*