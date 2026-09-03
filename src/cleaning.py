import os
import re

import pandas as pd


RAW_DATA_DIR = os.path.join("data", "raw")
PROCESSED_DATA_DIR = os.path.join("data", "processed")


def clean_name(series):
    """
    Standardize customer names:
    - Convert to string
    - Uppercase
    - Remove extra whitespace
    """
    return (
        series.astype("string")
        .str.upper()
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )


def clean_email(series):
    """
    Standardize email addresses.
    """
    return (
        series.astype("string")
        .str.lower()
        .str.strip()
    )


def clean_phone(series):
    """
    Standardize phone numbers:
    - Keep digits only
    - Retain the last 10 digits
    """
    cleaned = (
        series.astype("string")
        .str.replace(r"\D", "", regex=True)
    )

    return cleaned.str[-10:]


def clean_amount(series):
    """
    Convert monetary values to numeric.
    Invalid values become NaN.
    """
    return pd.to_numeric(series, errors="coerce").round(2)


def clean_date(series):
    """
    Convert date columns to pandas datetime.
    Invalid dates become NaT.
    """
    return pd.to_datetime(series, errors="coerce")


def clean_customer_master(df):
    df = df.copy()

    df["customer_name_clean"] = clean_name(
        df["customer_name"]
    )

    df["email_clean"] = clean_email(
        df["email"]
    )

    df["phone_clean"] = clean_phone(
        df["phone"]
    )

    df["created_date"] = clean_date(
        df["created_date"]
    )

    return df


def clean_invoice(df):
    df = df.copy()

    df["invoice_date"] = clean_date(
        df["invoice_date"]
    )

    df["invoice_amount"] = clean_amount(
        df["invoice_amount"]
    )

    df["tax"] = clean_amount(
        df["tax"]
    )

    df["discount"] = clean_amount(
        df["discount"]
    )

    df["net_amount"] = clean_amount(
        df["net_amount"]
    )

    return df


def clean_erp(df):
    df = df.copy()

    df["customer_name_clean"] = clean_name(
        df["customer_name"]
    )

    df["email_clean"] = clean_email(
        df["email"]
    )

    df["phone_clean"] = clean_phone(
        df["phone"]
    )

    df["transaction_date"] = clean_date(
        df["transaction_date"]
    )

    df["amount"] = clean_amount(
        df["amount"]
    )

    return df


def clean_payment_gateway(df):
    df = df.copy()

    df["customer_name_clean"] = clean_name(
        df["customer_name"]
    )

    df["email_clean"] = clean_email(
        df["email"]
    )

    df["transaction_date"] = clean_date(
        df["transaction_date"]
    )

    df["amount"] = clean_amount(
        df["amount"]
    )

    return df


def clean_bank_transactions(df):
    df = df.copy()

    df["transaction_date"] = clean_date(
        df["transaction_date"]
    )

    df["value_date"] = clean_date(
        df["value_date"]
    )

    df["credit_amount"] = clean_amount(
        df["credit_amount"]
    )

    df["debit_amount"] = clean_amount(
        df["debit_amount"]
    )

    return df


def load_raw_data():
    """
    Load all raw enterprise datasets.
    """
    return {
        "customer_master": pd.read_csv(
            os.path.join(
                RAW_DATA_DIR,
                "customer_master.csv"
            )
        ),
        "invoice": pd.read_csv(
            os.path.join(
                RAW_DATA_DIR,
                "invoice.csv"
            )
        ),
        "erp": pd.read_csv(
            os.path.join(
                RAW_DATA_DIR,
                "erp_transactions.csv"
            )
        ),
        "payment_gateway": pd.read_csv(
            os.path.join(
                RAW_DATA_DIR,
                "payment_gateway.csv"
            )
        ),
        "bank": pd.read_csv(
            os.path.join(
                RAW_DATA_DIR,
                "bank_transactions.csv"
            )
        ),
    }


def save_processed_data(datasets):
    """
    Save standardized datasets to data/processed/.
    """
    os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

    filenames = {
        "customer_master": "customer_master_clean.csv",
        "invoice": "invoice_clean.csv",
        "erp": "erp_transactions_clean.csv",
        "payment_gateway": "payment_gateway_clean.csv",
        "bank": "bank_transactions_clean.csv",
    }

    for name, df in datasets.items():
        df.to_csv(
            os.path.join(
                PROCESSED_DATA_DIR,
                filenames[name]
            ),
            index=False
        )


def main():
    print("=" * 60)
    print("ENTERPRISE DATA FORENSICS")
    print("Data Cleaning & Standardization")
    print("=" * 60)

    raw = load_raw_data()

    print("\nCleaning Customer Master...")
    raw["customer_master"] = clean_customer_master(
        raw["customer_master"]
    )

    print("Cleaning Invoices...")
    raw["invoice"] = clean_invoice(
        raw["invoice"]
    )

    print("Cleaning ERP Transactions...")
    raw["erp"] = clean_erp(
        raw["erp"]
    )

    print("Cleaning Payment Gateway...")
    raw["payment_gateway"] = clean_payment_gateway(
        raw["payment_gateway"]
    )

    print("Cleaning Bank Transactions...")
    raw["bank"] = clean_bank_transactions(
        raw["bank"]
    )

    save_processed_data(raw)

    print("\nCleaning completed successfully.")
    print("-" * 60)

    for name, df in raw.items():
        print(f"{name:20s}: {len(df):,} rows")

    print("-" * 60)
    print(f"Processed data saved to: {PROCESSED_DATA_DIR}")


if __name__ == "__main__":
    main()