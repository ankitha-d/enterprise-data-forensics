import sqlite3
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
DB_PATH = BASE_DIR / "enterprise_forensics.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


TABLES = {
    "customer_master_clean.csv": "customer_master",
    "invoice_clean.csv": "invoice",
    "erp_transactions_clean.csv": "erp_transactions",
    "payment_gateway_clean.csv": "payment_gateway",
    "bank_transactions_clean.csv": "bank_transactions",
    "entity_matches.csv": "entity_matches",
    "reconciliation.csv": "reconciliation",
    "exception_register.csv": "exception_register",
    "anomaly_detection.csv": "anomaly_detection",
}


def load_database():
    print("=" * 60)
    print("ENTERPRISE DATA FORENSICS")
    print("SQL Database Loader")
    print("=" * 60)

    print("\nConnecting to SQLite database...")
    conn = sqlite3.connect(DB_PATH)

    print("Applying database schema...")
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema)

    print("\nLoading processed datasets...")
    print("-" * 60)

    for filename, table_name in TABLES.items():
        file_path = DATA_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(
                f"Required dataset not found: {file_path}"
            )

        df = pd.read_csv(file_path)

        df.to_sql(
            table_name,
            conn,
            if_exists="replace",
            index=False
        )

        print(
            f"{table_name:<25} : {len(df):>8,} rows"
        )

    print("-" * 60)

    print("\nValidating database row counts...")
    print("-" * 60)

    for table_name in TABLES.values():
        count = conn.execute(
            f"SELECT COUNT(*) FROM {table_name}"
        ).fetchone()[0]

        print(
            f"{table_name:<25} : {count:>8,} rows"
        )

    conn.close()

    print("\nDatabase loading completed.")
    print(f"Database: {DB_PATH}")


if __name__ == "__main__":
    load_database()