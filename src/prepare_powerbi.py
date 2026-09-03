from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "processed"
OUTPUT_PATH = DATA_DIR / "powerbi_exceptions.csv"


def prepare_powerbi_dataset():

    print("=" * 60)
    print("ENTERPRISE DATA FORENSICS")
    print("Power BI Dataset Preparation")
    print("=" * 60)

    print("\nLoading datasets...")

    exceptions = pd.read_csv(
        DATA_DIR / "exception_register.csv"
    )

    reconciliation = pd.read_csv(
        DATA_DIR / "reconciliation.csv"
    )

    anomalies = pd.read_csv(
        DATA_DIR / "anomaly_detection.csv"
    )

    print(f"Exception records       : {len(exceptions):,}")
    print(f"Reconciliation records : {len(reconciliation):,}")
    print(f"Anomaly records        : {len(anomalies):,}")

    # --------------------------------------------------------
    # Build one transaction-level reconciliation record.
    #
    # Duplicate ERP rows intentionally exist in reconciliation.
    # For the dashboard, keep one representative reconciliation
    # record per transaction_id so the exception grain remains
    # one row per exception.
    # --------------------------------------------------------

    reconciliation_columns = [
        "transaction_id",
        "invoice_id",
        "customer_id",
        "customer_name",
        "store_id",
        "erp_amount",
        "payment_amount",
        "payment_difference",
        "bank_amount",
        "bank_difference",
        "bank_status",
        "date_difference_days",
        "reconciliation_status",
        "entity_match_score",
        "entity_match_confidence",
        "gateway",
    ]

    reconciliation = reconciliation[
        reconciliation_columns
    ]

    reconciliation = (
        reconciliation
        .drop_duplicates(
            subset=["transaction_id"],
            keep="first"
        )
    )

    # --------------------------------------------------------
    # Build one transaction-level anomaly record.
    # --------------------------------------------------------

    anomaly_columns = [
        "transaction_id",
        "amount_z_score",
        "amount_z_anomaly",
        "amount_iqr_anomaly",
        "isolation_forest_anomaly",
        "isolation_forest_score",
        "anomaly_methods_triggered",
        "potential_anomaly",
        "anomaly_status",
        "known_exception",
        "investigation_priority",
    ]

    anomalies = anomalies[anomaly_columns]

    anomalies = (
        anomalies
        .drop_duplicates(
            subset=["transaction_id"],
            keep="first"
        )
    )

    # --------------------------------------------------------
    # Exception register is the primary grain.
    # One row = one exception.
    # --------------------------------------------------------

    exception_columns = [
        "exception_id",
        "transaction_id",
        "severity",
        "financial_impact",
        "owner",
        "status",
        "root_cause",
        "recommended_action",
        "created_date",
        "exception_age_days",
        "sla_days",
        "sla_status",
        "resolution",
        "resolution_date",
    ]

    exceptions = exceptions[exception_columns]

    # --------------------------------------------------------
    # Join transaction-level context onto exceptions.
    # --------------------------------------------------------

    dashboard = exceptions.merge(
        reconciliation,
        on="transaction_id",
        how="left",
        validate="many_to_one"
    )

    dashboard = dashboard.merge(
        anomalies,
        on="transaction_id",
        how="left",
        validate="many_to_one"
    )

    # --------------------------------------------------------
    # Numeric fields
    # --------------------------------------------------------

    numeric_columns = [
        "financial_impact",
        "erp_amount",
        "payment_amount",
        "payment_difference",
        "bank_amount",
        "bank_difference",
        "date_difference_days",
        "entity_match_score",
        "amount_z_score",
        "isolation_forest_score",
        "anomaly_methods_triggered",
        "exception_age_days",
        "sla_days",
    ]

    for column in numeric_columns:
        dashboard[column] = pd.to_numeric(
            dashboard[column],
            errors="coerce"
        )

    dashboard["financial_impact"] = (
        dashboard["financial_impact"]
        .fillna(0)
    )

    # --------------------------------------------------------
    # Dashboard flags
    # --------------------------------------------------------

    dashboard["is_exception"] = True

    dashboard["potential_anomaly"] = (
        dashboard["potential_anomaly"]
        .fillna(False)
        .astype(bool)
    )

    dashboard["known_exception"] = True

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    dashboard.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nPower BI dataset created.")
    print("-" * 60)
    print(f"Rows: {len(dashboard):,}")
    print(f"Columns: {len(dashboard.columns)}")
    print(
        f"Unique exceptions: "
        f"{dashboard['exception_id'].nunique():,}"
    )
    print(
        f"Unique transactions: "
        f"{dashboard['transaction_id'].nunique():,}"
    )
    print(
        f"Potential anomalies: "
        f"{int(dashboard['potential_anomaly'].sum()):,}"
    )
    print(
        f"Financial exposure: "
        f"₹{dashboard['financial_impact'].sum():,.2f}"
    )
    print(f"\nOutput: {OUTPUT_PATH}")


if __name__ == "__main__":
    prepare_powerbi_dataset()