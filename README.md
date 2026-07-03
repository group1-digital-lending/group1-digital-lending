markdown# 💳 CreditGuard AI — Who Should We Lend To?
### Digital Credit Risk Analytics Capstone

**Group 1 | Thrive Africa / Ishango.ai | Analytics Engineering Track | March 2026**

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
| Riskiest age group | 20-30 year olds (highest default rate) |
| Payment insight | Applicants with >20% late payments default at 3x the rate |
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
Feature Mart (sql/03_marts.sql) ← one row per applicant
↓
Analysis Layer (sql/04_analysis.sql) ← business questions
↓
ML Model (notebooks/02_analyse_model.ipynb)
↓
Dashboard (dashboard/app.py) ← Streamlit

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| 🦆 DuckDB | SQL-first in-process database |
| 🐍 Python + pandas | Pipeline orchestration |
| 🌲 scikit-learn | ML modelling (Random Forest, Logistic Regression) |
| 📊 Streamlit + Plotly | Interactive dashboard |
| 🐙 GitHub | Version control & portfolio |

---

## 📁 Repository Structure
group1-digital-lending/
├── README.md                    ← You are here
├── requirements.txt             ← Python dependencies
├── .gitignore
├── data/
│   ├── raw/                     ← CSVs (git-ignored, too large)
│   └── sample/                  ← Tiny sample for reviewers
├── sql/
│   ├── 01_staging.sql           ← Load & type raw tables
│   ├── 02_clean.sql             ← Dedupe, fix types, conform keys
│   ├── 03_marts.sql             ← Feature engineering (CTEs + window functions)
│   └── 04_analysis.sql          ← Business questions (RANK, NTILE, LAG)
├── notebooks/
│   ├── 01_ingest_load.ipynb     ← Data loading + QA checks
│   └── 02_analyse_model.ipynb   ← Analysis, visualisation + ML model
├── src/
│   ├── db.py                    ← Database connection helper
│   └── ingest.py                ← CSV → DuckDB loader
├── dashboard/
│   ├── app.py                   ← Streamlit dashboard
│   └── charts/                  ← Saved chart images
└── docs/
└── data_dictionary.md       ← Full data dictionary

---

## ⚡ How to Run

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
Get the Home Credit Default Risk dataset from:
https://www.kaggle.com/competitions/home-credit-default-risk/data

Place all 7 CSV files in `data/raw/`

### 4. Load data into DuckDB
```bash
python src/ingest.py
```

### 5. Run the SQL pipeline
```bash
python -c "
import duckdb
conn = duckdb.connect('data/home_credit.db')
for f in ['sql/01_staging.sql','sql/02_clean.sql',
          'sql/03_marts.sql','sql/04_analysis.sql']:
    conn.execute(open(f).read())
print('Pipeline complete!')
"
```

### 6. Launch the dashboard
```bash
streamlit run dashboard/app.py
```

---

## 📊 SQL Techniques Demonstrated

| Technique | Where Used |
|-----------|-----------|
| Multi-table JOIN (5 tables) | sql/03_marts.sql |
| Layered CTEs (staging → mart) | sql/03_marts.sql |
| NTILE(5) window function | sql/04_analysis.sql |
| RANK() OVER (PARTITION BY) | sql/04_analysis.sql |
| LAG() period-over-period | sql/04_analysis.sql |
| CASE bucketing & pivoting | sql/02_clean.sql, sql/04_analysis.sql |
| GROUP BY ... HAVING | sql/04_analysis.sql |
| Window share-of-total | sql/04_analysis.sql |
| Data quality QA block | notebooks/01_ingest_load.ipynb |

---

## 🎯 Model Results

| Model | AUC Score | vs Baseline |
|-------|-----------|-------------|
| Baseline (always predict 0) | 0.5000 | — |
| Logistic Regression | 0.6010 | +0.1010 ✅ |
| **Random Forest** | **0.7462** | **+0.2462 🏆** |

- **Class imbalance handled:** `class_weight='balanced'`
- **Features:** 26 SQL-engineered features from 5 tables
- **True defaulters caught:** 3,357
- **Estimated bad debt prevented:** GHS 804,000,000

---

## 👥 Team

| Name | Role |
|------|------|
| Alfred Doryele | SQL Pipeline, Feature Mart, Modelling |
| [Teammate 2] | Analysis, Visualisation |
| [Teammate 3] | Dashboard, Documentation |

---

## 📚 Data Source

- **Dataset:** Home Credit Default Risk
- **Source:** Kaggle Competition
- **License:** Home Credit Group
- **Tables:** 7 related tables, 45M+ total rows
- **Target:** Binary classification (default = 1, repaid = 0)

---

*Built with ❤️ by Group 1 · Thrive Africa · March 2026*
