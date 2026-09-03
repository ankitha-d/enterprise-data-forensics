import os

import pandas as pd
from rapidfuzz import fuzz


PROCESSED_DATA_DIR = os.path.join("data", "processed")


def load_data():
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

    customer_master = pd.read_csv(
        os.path.join(
            PROCESSED_DATA_DIR,
            "customer_master_clean.csv"
        )
    )

    return erp, payment, customer_master


def similarity(value_1, value_2):
    """
    Return a fuzzy similarity score from 0 to 100.
    """
    if pd.isna(value_1) or pd.isna(value_2):
        return 0.0

    value_1 = str(value_1)
    value_2 = str(value_2)

    if not value_1 or not value_2:
        return 0.0

    return float(
        fuzz.ratio(value_1, value_2)
    )


def exact_match(value_1, value_2):
    """
    Check whether two standardized values match exactly.
    """
    if pd.isna(value_1) or pd.isna(value_2):
        return False

    return str(value_1) == str(value_2)


def calculate_match_score(erp_row, payment_row):
    """
    Calculate entity match confidence between
    an ERP transaction and payment gateway record.

    Available evidence in the current datasets:

        Email  = 50%
        Name   = 30%
        Amount = 20%

    Phone and address are intentionally not used because
    the payment gateway source does not contain those fields.
    """

    email_exact = exact_match(
        erp_row["email_clean"],
        payment_row["email_clean"]
    )

    email_score = (
        100.0
        if email_exact
        else similarity(
            erp_row["email_clean"],
            payment_row["email_clean"]
        )
    )

    name_score = similarity(
        erp_row["customer_name_clean"],
        payment_row["customer_name_clean"]
    )

    amount_score = 100.0 if (
        round(float(erp_row["amount"]), 2)
        == round(float(payment_row["amount"]), 2)
    ) else 0.0

    composite_score = (
        0.50 * email_score
        + 0.30 * name_score
        + 0.20 * amount_score
    )

    return round(composite_score, 2)


def classify_match(score):
    if score >= 95:
        return "HIGH_CONFIDENCE"

    if score >= 80:
        return "MEDIUM_CONFIDENCE"

    return "MANUAL_REVIEW"


def match_transactions(erp, payment):
    """
    Match ERP transactions to payment gateway records.

    Primary linkage:
        merchant_reference == transaction_id

    The entity score is then calculated to determine
    confidence in the relationship.
    """

    payment_lookup = (
        payment
        .drop_duplicates(
            subset=["merchant_reference"],
            keep="first"
        )
        .set_index("merchant_reference")
    )

    results = []

    for _, erp_row in erp.iterrows():

        transaction_id = erp_row["transaction_id"]

        if transaction_id in payment_lookup.index:

            payment_row = payment_lookup.loc[
                transaction_id
            ]

            score = calculate_match_score(
                erp_row,
                payment_row
            )

            confidence = classify_match(score)

            results.append({
                "transaction_id": transaction_id,
                "gateway_transaction_id": (
                    payment_row["gateway_transaction_id"]
                ),
                "erp_customer_id": erp_row["customer_id"],
                "erp_customer_name": (
                    erp_row["customer_name"]
                ),
                "payment_customer_name": (
                    payment_row["customer_name"]
                ),
                "entity_match_score": score,
                "entity_match_confidence": confidence,
                "erp_amount": erp_row["amount"],
                "payment_amount": payment_row["amount"]
            })

        else:

            results.append({
                "transaction_id": transaction_id,
                "gateway_transaction_id": None,
                "erp_customer_id": erp_row["customer_id"],
                "erp_customer_name": (
                    erp_row["customer_name"]
                ),
                "payment_customer_name": None,
                "entity_match_score": 0.0,
                "entity_match_confidence": "NO_MATCH",
                "erp_amount": erp_row["amount"],
                "payment_amount": None
            })

    return pd.DataFrame(results)


def save_results(results):
    output_path = os.path.join(
        PROCESSED_DATA_DIR,
        "entity_matches.csv"
    )

    results.to_csv(
        output_path,
        index=False
    )

    return output_path


def main():

    print("=" * 60)
    print("ENTERPRISE DATA FORENSICS")
    print("Entity Resolution Engine")
    print("=" * 60)

    print("\nLoading processed datasets...")

    erp, payment, customer_master = load_data()

    print(f"ERP records     : {len(erp):,}")
    print(f"Payment records : {len(payment):,}")
    print(f"Customers       : {len(customer_master):,}")

    print("\nMatching ERP transactions to payment records...")

    results = match_transactions(
        erp,
        payment
    )

    output_path = save_results(
        results
    )

    print("\nEntity matching completed.")
    print("-" * 60)

    print(
        results["entity_match_confidence"]
        .value_counts()
        .to_string()
    )

    print("-" * 60)

    print(
        f"Average match score: "
        f"{results['entity_match_score'].mean():.2f}"
    )

    print(
        f"Results saved to: {output_path}"
    )


if __name__ == "__main__":
    main()