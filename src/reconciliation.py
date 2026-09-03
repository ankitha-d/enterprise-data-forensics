import os

import pandas as pd


PROCESSED_DATA_DIR = os.path.join("data", "processed")


def load_data():
    """
    Load cleaned ERP, payment gateway, bank,
    and entity matching datasets.
    """

    erp = pd.read_csv(
        os.path.join(
            PROCESSED_DATA_DIR,
            "erp_transactions_clean.csv"
        )
    )

    payment = pd.read_csv(
        os.path.join(
            PROCESSED_DATA_DIR,
            "payment_gateway_clean.csv"
        )
    )

    bank = pd.read_csv(
        os.path.join(
            PROCESSED_DATA_DIR,
            "bank_transactions_clean.csv"
        )
    )

    entity_matches = pd.read_csv(
        os.path.join(
            PROCESSED_DATA_DIR,
            "entity_matches.csv"
        )
    )

    return erp, payment, bank, entity_matches


def prepare_payment_data(payment):
    """
    Prepare payment gateway data for reconciliation.

    merchant_reference links a payment to the ERP
    transaction_id.
    """

    payment = payment.copy()

    payment["transaction_date"] = pd.to_datetime(
        payment["transaction_date"],
        errors="coerce"
    )

    payment["amount"] = pd.to_numeric(
        payment["amount"],
        errors="coerce"
    )

    return payment


def prepare_bank_data(bank):
    """
    Prepare bank settlement data.

    reference_number contains the payment gateway
    transaction reference.
    """

    bank = bank.copy()

    bank["transaction_date"] = pd.to_datetime(
        bank["transaction_date"],
        errors="coerce"
    )

    bank["value_date"] = pd.to_datetime(
        bank["value_date"],
        errors="coerce"
    )

    bank["credit_amount"] = pd.to_numeric(
        bank["credit_amount"],
        errors="coerce"
    )

    return bank


def calculate_status(
    erp_amount,
    payment_amount,
    payment_exists,
    bank_exists,
    entity_confidence,
    duplicate_transaction,
    date_difference
):
    """
    Determine the primary reconciliation status.
    """

    # Duplicate ERP transaction
    if duplicate_transaction:
        return "DUPLICATE"

    # No corresponding payment
    if not payment_exists:
        return "MISSING_PAYMENT"

    # Payment exists but entity relationship is uncertain
    if entity_confidence == "MANUAL_REVIEW":
        return "ENTITY_UNCERTAIN"

    # Amount comparison
    if payment_amount is not None:

        difference = round(
            erp_amount - payment_amount,
            2
        )

        # Partial payment
        if payment_amount < erp_amount:
            return "PARTIAL_PAYMENT"

        # Overpayment
        if payment_amount > erp_amount:
            return "OVERPAYMENT"

        # Exact amount but date differs significantly
        if abs(date_difference) > 1:
            return "DATE_MISMATCH"

        # Exact reconciliation
        if difference == 0:

            # Payment exists but bank settlement does not
            if not bank_exists:
                return "MISSING_BANK_SETTLEMENT"

            return "MATCHED"

        return "AMOUNT_MISMATCH"

    return "AMOUNT_MISMATCH"


def reconcile_transactions(
    erp,
    payment,
    bank,
    entity_matches
):
    """
    Reconcile ERP transactions against payment gateway
    and bank settlement records.
    """

    erp = erp.copy()

    payment = prepare_payment_data(payment)
    bank = prepare_bank_data(bank)

    # --------------------------------------------------------
    # Payment lookup
    # --------------------------------------------------------

    payment_lookup = (
        payment
        .drop_duplicates(
            subset=["merchant_reference"],
            keep="first"
        )
        .set_index("merchant_reference")
    )

    # --------------------------------------------------------
    # Bank lookup
    # --------------------------------------------------------

    bank_lookup = (
        bank
        .drop_duplicates(
            subset=["reference_number"],
            keep="first"
        )
        .set_index("reference_number")
    )

    # --------------------------------------------------------
    # Entity match lookup
    # --------------------------------------------------------

    entity_lookup = (
        entity_matches
        .drop_duplicates(
            subset=["transaction_id"],
            keep="first"
        )
        .set_index("transaction_id")
    )

    # --------------------------------------------------------
    # Duplicate ERP transaction IDs
    # --------------------------------------------------------

    duplicate_ids = set(
        erp.loc[
            erp["transaction_id"].duplicated(
                keep=False
            ),
            "transaction_id"
        ]
    )

    results = []

    # ========================================================
    # ERP → Payment → Bank reconciliation
    # ========================================================

    for _, erp_row in erp.iterrows():

        transaction_id = erp_row["transaction_id"]

        erp_amount = float(
            erp_row["amount"]
        )

        erp_date = pd.to_datetime(
            erp_row["transaction_date"],
            errors="coerce"
        )

        # ----------------------------------------------------
        # Payment lookup
        # ----------------------------------------------------

        payment_exists = (
            transaction_id in payment_lookup.index
        )

        payment_row = None

        if payment_exists:
            payment_row = payment_lookup.loc[
                transaction_id
            ]

        # ----------------------------------------------------
        # Payment values
        # ----------------------------------------------------

        if payment_exists:

            payment_amount = float(
                payment_row["amount"]
            )

            payment_date = pd.to_datetime(
                payment_row["transaction_date"],
                errors="coerce"
            )

            gateway_transaction_id = (
                payment_row["gateway_transaction_id"]
            )

            gateway = payment_row["gateway"]

        else:

            payment_amount = None
            payment_date = None
            gateway_transaction_id = None
            gateway = None

        # ----------------------------------------------------
        # Bank lookup
        # ----------------------------------------------------

        bank_exists = False
        bank_row = None

        if gateway_transaction_id is not None:

            bank_exists = (
                gateway_transaction_id
                in bank_lookup.index
            )

            if bank_exists:
                bank_row = bank_lookup.loc[
                    gateway_transaction_id
                ]

        # ----------------------------------------------------
        # Bank values
        # ----------------------------------------------------

        if bank_exists:

            bank_amount = float(
                bank_row["credit_amount"]
            )

            bank_date = pd.to_datetime(
                bank_row["value_date"],
                errors="coerce"
            )

        else:

            bank_amount = None
            bank_date = None

        # ----------------------------------------------------
        # Entity confidence
        # ----------------------------------------------------

        if transaction_id in entity_lookup.index:

            entity_confidence = (
                entity_lookup.loc[
                    transaction_id,
                    "entity_match_confidence"
                ]
            )

            entity_score = float(
                entity_lookup.loc[
                    transaction_id,
                    "entity_match_score"
                ]
            )

        else:

            entity_confidence = "NO_MATCH"
            entity_score = 0.0

        # ----------------------------------------------------
        # Date difference
        # ----------------------------------------------------

        if payment_date is not None and pd.notna(payment_date):
            date_difference = (
                payment_date - erp_date
            ).days
        else:
            date_difference = None

        date_difference_for_status = (
            date_difference
            if date_difference is not None
            else 0
        )

        # ----------------------------------------------------
        # Amount differences
        # ----------------------------------------------------

        if payment_amount is not None:

            payment_difference = round(
                erp_amount - payment_amount,
                2
            )

        else:

            payment_difference = None

        if bank_amount is not None and payment_amount is not None:

            bank_difference = round(
                payment_amount - bank_amount,
                2
            )

        else:

            bank_difference = None

        # ----------------------------------------------------
        # Primary reconciliation status
        # ----------------------------------------------------

        status = calculate_status(
            erp_amount=erp_amount,
            payment_amount=payment_amount,
            payment_exists=payment_exists,
            bank_exists=bank_exists,
            entity_confidence=entity_confidence,
            duplicate_transaction=(
                transaction_id in duplicate_ids
            ),
            date_difference=date_difference_for_status
        )

        # ----------------------------------------------------
        # Bank settlement status
        # ----------------------------------------------------

        if bank_exists:

            bank_status = "SETTLED"

            bank_difference = round(
                payment_amount - bank_amount,
                2
            )

        else:

            bank_status = "MISSING_SETTLEMENT"

        # ----------------------------------------------------
        # Record
        # ----------------------------------------------------

        results.append({

            "transaction_id": transaction_id,

            "invoice_id": erp_row["invoice_id"],

            "customer_id": erp_row["customer_id"],

            "customer_name": erp_row["customer_name"],

            "store_id": erp_row["store_id"],

            "erp_transaction_date": erp_date,

            "erp_amount": erp_amount,

            "gateway_transaction_id":
                gateway_transaction_id,

            "gateway": gateway,

            "payment_transaction_date":
                payment_date,

            "payment_amount":
                payment_amount,

            "payment_difference":
                payment_difference,

            "bank_transaction_date":
                bank_date,

            "bank_amount":
                bank_amount,

            "bank_difference":
                bank_difference,

            "bank_status":
                bank_status,

            "date_difference_days":
                date_difference,

            "entity_match_score":
                entity_score,

            "entity_match_confidence":
                entity_confidence,

            "reconciliation_status":
                status
        })

    return pd.DataFrame(results)


def add_unexpected_payments(
    reconciliation,
    payment,
    erp
):
    """
    Add payment gateway records that have no
    corresponding ERP transaction.
    """

    erp_transaction_ids = set(
        erp["transaction_id"]
    )

    unexpected = payment[
        ~payment["merchant_reference"].isin(
            erp_transaction_ids
        )
    ].copy()

    if unexpected.empty:
        return reconciliation

    unexpected_records = []

    for _, payment_row in unexpected.iterrows():

        unexpected_records.append({

            "transaction_id":
                payment_row["merchant_reference"],

            "invoice_id": None,

            "customer_id": None,

            "customer_name":
                payment_row["customer_name"],

            "store_id": None,

            "erp_transaction_date": None,

            "erp_amount": None,

            "gateway_transaction_id":
                payment_row["gateway_transaction_id"],

            "gateway":
                payment_row["gateway"],

            "payment_transaction_date":
                payment_row["transaction_date"],

            "payment_amount":
                payment_row["amount"],

            "payment_difference": None,

            "bank_transaction_date": None,

            "bank_amount": None,

            "bank_difference": None,

            "bank_status":
                "UNKNOWN",

            "date_difference_days": None,

            "entity_match_score": 0.0,

            "entity_match_confidence":
                "NO_MATCH",

            "reconciliation_status":
                "UNEXPECTED_PAYMENT"
        })

    unexpected_df = pd.DataFrame(
        unexpected_records
    )

    return pd.concat(
        [
            reconciliation,
            unexpected_df
        ],
        ignore_index=True
    )


def save_reconciliation(df):
    output_path = os.path.join(
        PROCESSED_DATA_DIR,
        "reconciliation.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    return output_path
def print_summary(df):

    print("\nRECONCILIATION STATUS")
    print("-" * 60)

    status_counts = (
        df["reconciliation_status"]
        .value_counts()
    )

    print(
        status_counts.to_string()
    )

    print("\nFINANCIAL IMPACT")
    print("-" * 60)

    df = df.copy()

    df["payment_difference"] = pd.to_numeric(
        df["payment_difference"],
        errors="coerce"
    )

    impact = (
        df.groupby(
            "reconciliation_status"
        )["payment_difference"]
        .apply(
            lambda x: x.abs().sum()
        )
        .sort_values(
            ascending=False
        )
    )

    print(
        impact.to_string()
    )


def main():

    print("=" * 60)
    print("ENTERPRISE DATA FORENSICS")
    print("Transaction Reconciliation Engine")
    print("=" * 60)

    print("\nLoading processed datasets...")

    erp, payment, bank, entity_matches = load_data()

    print(f"ERP records          : {len(erp):,}")
    print(f"Payment records      : {len(payment):,}")
    print(f"Bank records         : {len(bank):,}")
    print(f"Entity match records : {len(entity_matches):,}")

    print("\nRunning reconciliation...")

    reconciliation = reconcile_transactions(
        erp,
        payment,
        bank,
        entity_matches
    )

    print("Checking unexpected payments...")

    reconciliation = add_unexpected_payments(
        reconciliation,
        payment,
        erp
    )

    output_path = save_reconciliation(
        reconciliation
    )

    print("\nReconciliation completed.")
    print("-" * 60)

    print(
        f"Total reconciliation records: "
        f"{len(reconciliation):,}"
    )

    print_summary(
        reconciliation
    )

    print("-" * 60)
    print(
        f"Results saved to: {output_path}"
    )


if __name__ == "__main__":
    main()