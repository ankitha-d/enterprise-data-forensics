from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def main():
    reconciliation_path = PROCESSED_DIR / "reconciliation.csv"
    anomaly_path = PROCESSED_DIR / "anomaly_detection.csv"
    output_path = PROCESSED_DIR / "powerbi_transactions.csv"

    reconciliation = pd.read_csv(reconciliation_path)
    anomalies = pd.read_csv(anomaly_path)

    # Reconciliation can contain duplicate transaction rows because
    # duplicate ERP transactions are intentionally part of the dataset.
    # Keep one row per transaction for the Power BI transaction-level table.
    priority = {
        "MATCHED": 0,
        "DATE_MISMATCH": 1,
        "PARTIAL_PAYMENT": 2,
        "OVERPAYMENT": 3,
        "MISSING_PAYMENT": 4,
        "UNEXPECTED_PAYMENT": 5,
        "DUPLICATE": 6,
        "ENTITY_UNCERTAIN": 7,
        "AMOUNT_MISMATCH": 8,
    }

    reconciliation["_status_priority"] = (
        reconciliation["reconciliation_status"]
        .map(priority)
        .fillna(9)
    )

    reconciliation = (
        reconciliation
        .sort_values(["transaction_id", "_status_priority"])
        .drop_duplicates("transaction_id", keep="last")
        .drop(columns="_status_priority")
    )

    # Anomaly detection should also contribute only one record per transaction.
    anomalies = anomalies.drop_duplicates("transaction_id", keep="first")

    reconciliation_columns = [
        "transaction_id",
        "invoice_id",
        "customer_id",
        "customer_name",
        "store_id",
        "erp_transaction_date",
        "erp_amount",
        "gateway_transaction_id",
        "gateway",
        "payment_transaction_date",
        "payment_amount",
        "payment_difference",
        "bank_transaction_date",
        "bank_amount",
        "bank_difference",
        "bank_status",
        "date_difference_days",
        "entity_match_score",
        "entity_match_confidence",
        "reconciliation_status",
    ]

    reconciliation = reconciliation[reconciliation_columns]

    output = reconciliation.merge(
        anomalies,
        on="transaction_id",
        how="left",
        suffixes=("", "_anomaly"),
    )

    output["is_exception"] = (
        output["reconciliation_status"] != "MATCHED"
    )

    output.to_csv(output_path, index=False)

    print(f"Created: {output_path}")
    print(f"Rows: {len(output):,}")
    print(
        f"Unique transaction IDs: "
        f"{output['transaction_id'].nunique():,}"
    )
    print("\nReconciliation status:")
    print(
        output["reconciliation_status"]
        .value_counts()
        .to_string()
    )


if __name__ == "__main__":
    main()