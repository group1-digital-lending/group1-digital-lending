import duckdb
import os

conn = duckdb.connect("data/home_credit.db")
os.makedirs("dashboard/data", exist_ok=True)

# Export all analysis tables
tables = [
    "analysis_default_by_income",
    "analysis_default_by_contract",
    "analysis_ntile_risk",
    "analysis_education_rank",
    "analysis_payment_behaviour",
    "analysis_riskiest_segments",
    "analysis_age_default_trend",
]

for t in tables:
    df = conn.execute(f"SELECT * FROM {t}").fetchdf()
    df.to_csv(f"dashboard/data/{t}.csv", index=False)
    print(f"Exported {t} — {len(df)} rows")

# Export KPI metrics
kpi = conn.execute("""
    SELECT
        COUNT(*) AS total_apps,
        ROUND(AVG(TARGET)*100, 2) AS default_rate,
        ROUND(AVG(AMT_CREDIT), 0) AS avg_credit,
        ROUND(AVG(CASE WHEN credit_risk_band IN
            ('High Risk','Very High Risk')
            THEN 1.0 ELSE 0.0 END)*100, 1) AS high_risk_pct,
        SUM(TARGET) AS total_defaults
    FROM mart_applicant_features
""").fetchdf()
kpi.to_csv("dashboard/data/kpi_metrics.csv", index=False)
print("Exported KPI metrics")

# Export contract type data
contract = conn.execute("""
    SELECT NAME_CONTRACT_TYPE, COUNT(*) AS count,
           ROUND(AVG(TARGET)*100,2) AS default_rate
    FROM mart_applicant_features
    GROUP BY NAME_CONTRACT_TYPE
""").fetchdf()
contract.to_csv("dashboard/data/contract_type.csv", index=False)
print("Exported contract type")

# Export risk band data
risk_band = conn.execute("""
    SELECT credit_risk_band,
           COUNT(*) AS applicants,
           ROUND(AVG(TARGET)*100,2) AS default_rate
    FROM mart_applicant_features
    GROUP BY credit_risk_band
    ORDER BY default_rate DESC
""").fetchdf()
risk_band.to_csv("dashboard/data/risk_band.csv", index=False)
print("Exported risk bands")

conn.close()
print("All done! CSV files saved to dashboard/data/")