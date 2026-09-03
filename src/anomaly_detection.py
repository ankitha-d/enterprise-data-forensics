from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_PATH = BASE_DIR / "data" / "processed" / "reconciliation.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "anomaly_detection.csv"


def calculate_z_scores(series):
    mean = series.mean()
    std = series.std()

    if std == 0 or pd.isna(std):
        return pd.Series(0.0, index=series.index)

    return (series - mean) / std


def calculate_iqr_flags(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    return (
        (series < lower_bound)
        | (series > upper_bound)
    )


def run_anomaly_detection():

    print("=" * 60)
    print("ENTERPRISE DATA FORENSICS")
    print("Anomaly Detection Engine")
    print("=" * 60)

    print("\nLoading reconciliation data...")

    df = pd.read_csv(INPUT_PATH)

    print(f"Reconciliation records: {len(df):,}")

    # --------------------------------------------------------
    # Prepare numerical features
    # --------------------------------------------------------

    numeric_columns = [
        "erp_amount",
        "payment_amount",
        "bank_amount",
        "payment_difference",
        "bank_difference",
        "date_difference_days",
        "entity_match_score",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    for column in numeric_columns:
        df[column] = df[column].fillna(0)

    # --------------------------------------------------------
    # Z-score analysis
    # --------------------------------------------------------

    df["amount_z_score"] = calculate_z_scores(
        df["erp_amount"]
    )

    df["amount_z_anomaly"] = (
        df["amount_z_score"].abs() >= 3
    )

    # --------------------------------------------------------
    # IQR analysis
    # --------------------------------------------------------

    df["amount_iqr_anomaly"] = calculate_iqr_flags(
        df["erp_amount"]
    )

    # --------------------------------------------------------
    # Isolation Forest
    # --------------------------------------------------------

    features = [
        "erp_amount",
        "payment_amount",
        "bank_amount",
        "payment_difference",
        "bank_difference",
        "date_difference_days",
        "entity_match_score",
    ]

    scaler = StandardScaler()

    scaled_features = scaler.fit_transform(
        df[features]
    )

    model = IsolationForest(
        n_estimators=200,
        contamination="auto",
        random_state=42,
        n_jobs=-1
    )

    predictions = model.fit_predict(
        scaled_features
    )

    anomaly_scores = model.decision_function(
        scaled_features
    )

    df["isolation_forest_anomaly"] = (
        predictions == -1
    )

    df["isolation_forest_score"] = (
        anomaly_scores
    )

    # --------------------------------------------------------
    # Combined anomaly indicator
    # --------------------------------------------------------
    #
    # Any statistical detector can flag a potential anomaly.
    # This avoids hiding useful Isolation Forest findings when
    # global amount-based methods find no extreme outliers.
    #

    df["anomaly_methods_triggered"] = (
        df["amount_z_anomaly"].astype(int)
        + df["amount_iqr_anomaly"].astype(int)
        + df["isolation_forest_anomaly"].astype(int)
    )

    df["potential_anomaly"] = (
        df["anomaly_methods_triggered"] >= 1
    )

    # --------------------------------------------------------
    # Investigation classification
    # --------------------------------------------------------

    df["anomaly_status"] = np.where(
        df["potential_anomaly"],
        "POTENTIAL_ANOMALY",
        "NORMAL_RANGE"
    )

    # --------------------------------------------------------
    # Known exception context
    # --------------------------------------------------------

    df["known_exception"] = (
        df["reconciliation_status"] != "MATCHED"
    )

    df["investigation_priority"] = np.select(
        [
            (
                df["potential_anomaly"]
                & df["known_exception"]
            ),
            (
                df["potential_anomaly"]
                & ~df["known_exception"]
            ),
            df["known_exception"],
        ],
        [
            "HIGH",
            "MEDIUM",
            "EXCEPTION_REVIEW",
        ],
        default="NORMAL",
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print("\nAnomaly detection completed.")
    print("-" * 60)

    print(
        "Z-score anomalies       :",
        int(df["amount_z_anomaly"].sum())
    )

    print(
        "IQR anomalies           :",
        int(df["amount_iqr_anomaly"].sum())
    )

    print(
        "Isolation Forest        :",
        int(df["isolation_forest_anomaly"].sum())
    )

    print(
        "Potential anomalies     :",
        int(df["potential_anomaly"].sum())
    )

    print("\nAnomaly status:")
    print(
        df["anomaly_status"]
        .value_counts()
        .to_string()
    )

    print("\nInvestigation priority:")
    print(
        df["investigation_priority"]
        .value_counts()
        .to_string()
    )

    print(
        f"\nResults saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    run_anomaly_detection()