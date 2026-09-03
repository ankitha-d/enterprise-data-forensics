import os
from datetime import datetime

import pandas as pd


PROCESSED_DATA_DIR = os.path.join("data", "processed")


# ============================================================
# Configuration
# ============================================================

HIGH_VALUE_THRESHOLD = 10000
CRITICAL_VALUE_THRESHOLD = 50000


# ============================================================
# Load reconciliation data
# ============================================================

def load_reconciliation():
    path = os.path.join(
        PROCESSED_DATA_DIR,
        "reconciliation.csv"
    )

    return pd.read_csv(path)


# ============================================================
# Financial impact
# ============================================================

def calculate_financial_impact(row):
    """
    Determine the financial exposure associated
    with an exception.
    """

    payment_difference = row.get(
        "payment_difference"
    )

    bank_difference = row.get(
        "bank_difference"
    )

    if pd.notna(payment_difference):
        payment_impact = abs(
            float(payment_difference)
        )
    else:
        payment_impact = 0.0

    if pd.notna(bank_difference):
        bank_impact = abs(
            float(bank_difference)
        )
    else:
        bank_impact = 0.0

    # Use the largest known discrepancy.
    return round(
        max(
            payment_impact,
            bank_impact
        ),
        2
    )


# ============================================================
# Severity
# ============================================================

def determine_severity(row):
    """
    Assign severity based on exception type
    and financial impact.
    """

    status = row["reconciliation_status"]
    impact = row["financial_impact"]

    # Critical conditions
    if status == "DUPLICATE" and impact >= CRITICAL_VALUE_THRESHOLD:
        return "CRITICAL"

    if status == "UNEXPECTED_PAYMENT" and impact >= CRITICAL_VALUE_THRESHOLD:
        return "CRITICAL"

    if impact >= CRITICAL_VALUE_THRESHOLD:
        return "CRITICAL"

    # High-risk conditions
    if impact >= HIGH_VALUE_THRESHOLD:
        return "HIGH"

    if status in {
        "ENTITY_UNCERTAIN",
        "MISSING_PAYMENT",
        "MISSING_BANK_SETTLEMENT",
        "UNEXPECTED_PAYMENT"
    }:
        return "HIGH"

    # Medium-risk conditions
    if status in {
        "AMOUNT_MISMATCH",
        "PARTIAL_PAYMENT",
        "OVERPAYMENT",
        "DATE_MISMATCH"
    }:
        return "MEDIUM"

    # Lower-risk conditions
    if status == "DUPLICATE":
        return "MEDIUM"

    return "LOW"


# ============================================================
# Root cause
# ============================================================

def determine_root_cause(row):
    """
    Map reconciliation results to an initial
    investigation-oriented root cause.
    """

    status = row["reconciliation_status"]

    if status == "PARTIAL_PAYMENT":
        return "Potential partial payment"

    if status == "OVERPAYMENT":
        return "Potential overpayment"

    if status == "AMOUNT_MISMATCH":
        return "Payment amount differs from ERP amount"

    if status == "MISSING_PAYMENT":
        return "ERP transaction has no payment gateway record"

    if status == "UNEXPECTED_PAYMENT":
        return "Payment exists without corresponding ERP transaction"

    if status == "MISSING_BANK_SETTLEMENT":
        return "Payment received but bank settlement is missing"

    if status == "DUPLICATE":
        return "Duplicate ERP transaction detected"

    if status == "DATE_MISMATCH":
        return "Transaction dates differ across systems"

    if status == "ENTITY_UNCERTAIN":
        return "Customer/entity relationship requires review"

    return "No exception"


# ============================================================
# Recommended action
# ============================================================

def determine_recommended_action(row):
    """
    Provide an initial business action for investigation.
    """

    status = row["reconciliation_status"]

    if status == "PARTIAL_PAYMENT":
        return "Review outstanding payment balance"

    if status == "OVERPAYMENT":
        return "Review excess payment and refund requirements"

    if status == "AMOUNT_MISMATCH":
        return "Compare ERP, gateway and settlement records"

    if status == "MISSING_PAYMENT":
        return "Verify payment gateway processing and payment status"

    if status == "UNEXPECTED_PAYMENT":
        return "Investigate payment origin and identify related transaction"

    if status == "MISSING_BANK_SETTLEMENT":
        return "Review bank settlement file and settlement cycle"

    if status == "DUPLICATE":
        return "Verify duplicate posting and reverse erroneous entry if confirmed"

    if status == "DATE_MISMATCH":
        return "Review transaction and settlement dates"

    if status == "ENTITY_UNCERTAIN":
        return "Perform manual entity verification"

    return "No action required"


# ============================================================
# Owner assignment
# ============================================================

def determine_owner(row):
    """
    Assign an investigation team based on exception type.
    """

    status = row["reconciliation_status"]

    if status in {
        "AMOUNT_MISMATCH",
        "PARTIAL_PAYMENT",
        "OVERPAYMENT"
    }:
        return "Payments"

    if status in {
        "MISSING_BANK_SETTLEMENT"
    }:
        return "Finance"

    if status in {
        "MISSING_PAYMENT",
        "UNEXPECTED_PAYMENT"
    }:
        return "Finance"

    if status == "DUPLICATE":
        return "Finance"

    if status == "ENTITY_UNCERTAIN":
        return "Data Quality"

    if status == "DATE_MISMATCH":
        return "Operations"

    return "Finance"


# ============================================================
# Exception status
# ============================================================

def determine_initial_status(row):
    """
    Every newly created exception starts as OPEN.
    """

    if row["reconciliation_status"] == "MATCHED":
        return None

    return "OPEN"


# ============================================================
# Exception ID
# ============================================================

def generate_exception_id(index):
    return f"EXC-{index:06d}"


# ============================================================
# Build exception register
# ============================================================

def build_exception_register(reconciliation):
    """
    Convert reconciliation records into an
    investigation-ready exception register.
    """

    exceptions = reconciliation[
        reconciliation["reconciliation_status"] != "MATCHED"
    ].copy()

    if exceptions.empty:
        return pd.DataFrame()

    # --------------------------------------------------------
    # Financial impact
    # --------------------------------------------------------

    exceptions["financial_impact"] = exceptions.apply(
        calculate_financial_impact,
        axis=1
    )

    # --------------------------------------------------------
    # Severity
    # --------------------------------------------------------

    exceptions["severity"] = exceptions.apply(
        determine_severity,
        axis=1
    )

    # --------------------------------------------------------
    # Root cause
    # --------------------------------------------------------

    exceptions["root_cause"] = exceptions.apply(
        determine_root_cause,
        axis=1
    )

    # --------------------------------------------------------
    # Recommended action
    # --------------------------------------------------------

    exceptions["recommended_action"] = exceptions.apply(
        determine_recommended_action,
        axis=1
    )

    # --------------------------------------------------------
    # Owner
    # --------------------------------------------------------

    exceptions["owner"] = exceptions.apply(
        determine_owner,
        axis=1
    )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    exceptions["status"] = exceptions.apply(
        determine_initial_status,
        axis=1
    )

    # --------------------------------------------------------
    # Created date
    # --------------------------------------------------------

    exceptions["created_date"] = datetime.now().strftime(
        "%Y-%m-%d"
    )

    # --------------------------------------------------------
    # Exception ID
    # --------------------------------------------------------

    exceptions.insert(
        0,
        "exception_id",
        [
            generate_exception_id(i)
            for i in range(
                1,
                len(exceptions) + 1
            )
        ]
    )

    # --------------------------------------------------------
    # Exception age
    # --------------------------------------------------------

    exceptions["exception_age_days"] = 0

    # --------------------------------------------------------
    # SLA
    # --------------------------------------------------------

    exceptions["sla_days"] = exceptions[
        "severity"
    ].map({
        "CRITICAL": 1,
        "HIGH": 3,
        "MEDIUM": 7,
        "LOW": 14
    })

    exceptions["sla_status"] = "WITHIN_SLA"

    # --------------------------------------------------------
    # Resolution fields
    # --------------------------------------------------------

    exceptions["resolution"] = None
    exceptions["resolution_date"] = None

    # --------------------------------------------------------
    # Select final columns
    # --------------------------------------------------------

    columns = [
        "exception_id",
        "transaction_id",
        "invoice_id",
        "customer_id",
        "customer_name",
        "store_id",
        "reconciliation_status",
        "severity",
        "financial_impact",
        "entity_match_score",
        "entity_match_confidence",
        "gateway",
        "erp_amount",
        "payment_amount",
        "payment_difference",
        "bank_amount",
        "bank_difference",
        "bank_status",
        "date_difference_days",
        "owner",
        "status",
        "root_cause",
        "recommended_action",
        "created_date",
        "exception_age_days",
        "sla_days",
        "sla_status",
        "resolution",
        "resolution_date"
    ]

    return exceptions[
        [
            column
            for column in columns
            if column in exceptions.columns
        ]
    ]


# ============================================================
# Save
# ============================================================

def save_exception_register(exceptions):
    output_path = os.path.join(
        PROCESSED_DATA_DIR,
        "exception_register.csv"
    )

    exceptions.to_csv(
        output_path,
        index=False
    )

    return output_path


# ============================================================
# Summary
# ============================================================

def print_summary(exceptions):

    print("\nEXCEPTION SUMMARY")
    print("-" * 60)

    print(
        f"Total exceptions : {len(exceptions):,}"
    )

    print(
        f"Financial exposure : "
        f"₹{exceptions['financial_impact'].sum():,.2f}"
    )

    print("\nBy severity:")
    print(
        exceptions[
            "severity"
        ].value_counts()
        .to_string()
    )

    print("\nBy exception type:")
    print(
        exceptions[
            "reconciliation_status"
        ].value_counts()
        .to_string()
    )

    print("\nBy owner:")
    print(
        exceptions[
            "owner"
        ].value_counts()
        .to_string()
    )

    print("\nFinancial exposure by type:")
    exposure = (
        exceptions
        .groupby(
            "reconciliation_status"
        )["financial_impact"]
        .sum()
        .sort_values(
            ascending=False
        )
    )

    print(
        exposure.to_string()
    )


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print("ENTERPRISE DATA FORENSICS")
    print("Exception Management Engine")
    print("=" * 60)

    print("\nLoading reconciliation data...")

    reconciliation = load_reconciliation()

    print(
        f"Reconciliation records: "
        f"{len(reconciliation):,}"
    )

    print("\nCreating exception register...")

    exceptions = build_exception_register(
        reconciliation
    )

    if exceptions.empty:

        print(
            "\nNo exceptions detected."
        )

        return

    output_path = save_exception_register(
        exceptions
    )

    print("\nException engine completed.")
    print("-" * 60)

    print_summary(
        exceptions
    )

    print("-" * 60)

    print(
        f"Exception register saved to: "
        f"{output_path}"
    )


if __name__ == "__main__":
    main()