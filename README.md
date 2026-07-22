# 💳 CreditGuard AI — Who Should We Lend To?
### Digital Credit Risk Analytics Capstone

**Group 1 | Thrive Africa / Ishango.ai | Analytics Engineering Track | March 2026**

---

## 🚀 Live Dashboard

**[👉 Click here to view the live dashboard](https://creditguard-ai-group1.streamlit.app)**

> Deployed on Streamlit Cloud — no login required, accessible from anywhere

---

## 🎯 Business Question

Digital lenders in Ghana and Nigeria live or die on credit risk. Given an
applicant's full financial history across 7 data tables, can we predict who
will default — and identify which customer segments are riskiest?

---

## 🔍 Key Findings

| Finding | Detail |
|---------|--------|
| Overall default rate | 8.07% — significant class imbalance |
| Strongest predictor | EXT_SOURCE_2 (external credit score) |
| Riskiest age group | 20–30 year olds (highest default rate) |
| Payment insight | Applicants with >20% late payments default at 3× the rate |
| Best model AUC | 0.7462 (Random Forest vs 0.50 baseline) |
| Bad debt prevented | Estimated GHS 804,000,000 |

---

## 🏗️ Pipeline
Raw CSVs (7 tables, 45M+ rows)
↓
DuckDB Database (src/ingest.py)
↓
Staging Layer (sql/01_staging.sql)
↓
Cleaning Layer (sql/02_clean.sql)
↓
Feature Mart (sql/03_marts.sql) ← one row per applicant, 26 features
↓
Analysis Layer (sql/04_analysis.sql) ← RANK, NTILE, LAG, CASE
↓
ML Model (notebooks/02_analyse_model.ipynb) ← AUC 0.7462
↓
Dashboard (dashboard/app.py) ← Live on Streamlit Cloud


---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| 🦆 DuckDB | SQL-first in-process database — no server needed |
| 🐍 Python + pandas | Pipeline orchestration and data preparation |
| 🌲 scikit-learn | ML modelling — Random Forest + Logistic Regression |
| 📊 Streamlit + Plotly | Premium interactive dashboard |
| 🐙 GitHub | Version control and portfolio showcase |

---

## 📁 Repository Structure

group1-digital-lending/
├── README.md ← You are here
├── requirements.txt ← Python dependencies
├── .gitignore ← Excludes large data files
├── data/
│ ├── raw/ ← 7 CSV files (git-ignored, 700MB+)
│ └── sample/ ← Tiny sample for reviewers
├── sql/
│ ├── 01_staging.sql ← Select key columns from raw tables
│ ├── 02_clean.sql ← Fix types, sentinel values, ratios
│ ├── 03_marts.sql ← Feature engineering (CTEs + JOINs)
│ └── 04_analysis.sql ← RANK, NTILE, LAG business queries
├── notebooks/
│ ├── 01_ingest_load.ipynb ← Data loading + QA checks
│ └── 02_analyse_model.ipynb ← Analysis, charts + ML model
├── src/
│ ├── db.py ← DuckDB connection helper
│ └── ingest.py ← CSV → DuckDB loader
├── dashboard/
│ ├── app.py ← Streamlit dashboard (deployed live)
│ ├── data/ ← Pre-computed CSV exports for cloud
│ └── charts/ ← Saved chart images
└── docs/
└── data_dictionary.md ← Full data dictionary (40+ columns)


---

## ⚡ How to Run Locally

### 1. Clone the repository
```bash
git clone https://github.com/Alfred-Doryele/group1-digital-lending.git
cd group1-digital-lending
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Download the data
Get the Home Credit Default Risk dataset from Kaggle:

https://www.kaggle.com/competitions/home-credit-default-risk/data

Place all 7 CSV files inside `data/raw/`

### 4. Load data into DuckDB
```bash
python src/ingest.py
```

### 5. Run the full SQL pipeline
```bash
python -c "
import duckdb
conn = duckdb.connect('data/home_credit.db')
for f in ['sql/01_staging.sql','sql/02_clean.sql',
          'sql/03_marts.sql','sql/04_analysis.sql']:
    conn.execute(open(f).read())
    print(f'{f} done')
print('Pipeline complete!')
"
```

### 6. Launch the dashboard locally
```bash
streamlit run dashboard/app.py
```

---

## 📊 SQL Techniques Demonstrated

| Technique | File | Purpose |
|-----------|------|---------|
| Multi-table JOIN (×5) | 03_marts.sql | Join all feature marts into one applicant row |
| Layered CTEs | 03_marts.sql | Staging → Clean → Mart pipeline |
| NTILE(5) | 04_analysis.sql | Divide applicants into 5 equal risk quintiles |
| RANK() OVER() | 04_analysis.sql | Rank education types by default rate |
| LAG() | 04_analysis.sql | Year-over-year default rate change by age |
| CASE bucketing | 02_clean.sql | Convert raw values to risk bands |
| GROUP BY + HAVING | 04_analysis.sql | Filter groups with < 100 applicants |
| COALESCE | 03_marts.sql | Replace NULLs with 0 for applicants with no history |

---

## 🎯 Model Results

| Model | AUC Score | vs Baseline |
|-------|-----------|-------------|
| Baseline (always predict 0) | 0.5000 | — |
| Logistic Regression | 0.6010 | +0.1010 ✅ |
| **Random Forest** | **0.7462** | **+0.2462 🏆** |

**Key model details:**
- Class imbalance handled with `class_weight='balanced'`
- 26 SQL-engineered features from 5 tables
- True defaulters caught: 3,357 out of 4,965
- Estimated bad debt prevented: **GHS 804,000,000**

---

## 📊 Dashboard Features

The live dashboard at **[creditguard-ai-group1.streamlit.app](https://creditguard-ai-group1.streamlit.app)** includes:

| Tab | Content |
|-----|---------|
| 📊 Risk Segmentation | Default rates by income band, education level, NTILE quintiles |
| 💳 Payment Behaviour | How payment history predicts default (strongest signal) |
| 🏦 Credit Profile | Contract type distribution, risk band analysis |
| 🎯 Model Results | AUC comparison, feature importance, business cost analysis |
| 📈 Age Trends | LAG analysis of default rates across applicant ages |

---

## 📋 Data Quality Checks

All checks run in `notebooks/01_ingest_load.ipynb`:

- ✅ **Zero duplicates** on SK_ID_CURR (307,511 unique applicants)
- ✅ **Zero null join keys** across all 4 checked tables
- ✅ **Row counts verified** — 58.9M total rows across 7 tables
- ⚠️ **Class imbalance** — 8.07% default rate (handled with class_weight)
- ✅ **Sentinel values cleaned** — DAYS_EMPLOYED 365243 → NULL
- ✅ **Missing value strategy** set for all columns

---

## 👥 Team — Group 1

| Name | Role |
|------|------|
| Alfred Doryele | SQL Pipeline, Feature Mart, ML Model, Deployment |
| [Teammate 2] | Analysis, Visualisation |
| [Teammate 3] | Dashboard, Documentation |

---

## 🔗 Links

| Resource | Link |
|----------|------|
| 🚀 Live Dashboard | [creditguard-ai-group1.streamlit.app](https://creditguard-ai-group1.streamlit.app) |
| 🐙 GitHub Repo | [github.com/Alfred-Doryele/group1-digital-lending](https://github.com/Alfred-Doryele/group1-digital-lending) |
| 📊 Dataset | [Home Credit Default Risk — Kaggle](https://www.kaggle.com/competitions/home-credit-default-risk) |

---

## 📚 Data Source

- **Dataset:** Home Credit Default Risk
- **Source:** Kaggle Competition
- **License:** Home Credit Group
- **7 tables:** application_train, bureau, bureau_balance,
  previous_application, installments_payments,
  POS_CASH_balance, credit_card_balance
- **Total rows:** 58,951,149
- **Target:** Binary classification (default=1, repaid=0)

---

*Built with ❤️ by Group 1 · Thrive Africa · March 2026*