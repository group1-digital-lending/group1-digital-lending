import duckdb
import os
from db import get_connection

DATA_DIR = "data/raw"

TABLES = {
    "application_train": "application_train.csv",
    "bureau": "bureau.csv",
    "bureau_balance": "bureau_balance.csv",
    "previous_application": "previous_application.csv",
    "installments_payments": "installments_payments.csv",
    "pos_cash_balance": "POS_CASH_balance.csv",
    "credit_card_balance": "credit_card_balance.csv",
}

def load_all_tables():
    conn = get_connection()
    for table_name, filename in TABLES.items():
        filepath = os.path.join(DATA_DIR, filename)
        print(f"Loading {table_name} from {filename}...")
        conn.execute(f"""
            CREATE OR REPLACE TABLE {table_name} AS
            SELECT * FROM read_csv_auto('{filepath}', header=True)
        """)
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"  Loaded {count:,} rows")
    conn.close()
    print("\nAll tables loaded successfully!")

if __name__ == "__main__":
    load_all_tables()