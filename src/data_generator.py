import os
import random
import string
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# ============================================================
# Configuration
# ============================================================

SEED = 42
NUM_CUSTOMERS = 10000
NUM_TRANSACTIONS = 50000

RAW_DATA_DIR = os.path.join("data", "raw")

random.seed(SEED)
np.random.seed(SEED)


# ============================================================
# Helper functions
# ============================================================

def random_name():
    first_names = [
        "Rahul", "Priya", "Amit", "Sneha", "Arjun",
        "Neha", "Rohan", "Ananya", "Vikram", "Kavya",
        "Aditya", "Pooja", "Karan", "Meera", "Nikhil"
    ]

    last_names = [
        "Kumar", "Sharma", "Reddy", "Patel", "Das",
        "Singh", "Gupta", "Verma", "Rao", "Iyer",
        "Mehta", "Nair", "Joshi", "Mishra", "Kapoor"
    ]

    return f"{random.choice(first_names)} {random.choice(last_names)}"


def random_phone():
    return "9" + "".join(random.choices(string.digits, k=9))


def random_email(name):
    clean_name = name.lower().replace(" ", ".")
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    return f"{clean_name}{random.randint(1, 999)}@{random.choice(domains)}"


def random_date(start_date, end_date):
    days = (end_date - start_date).days
    return start_date + timedelta(days=random.randint(0, days))


def random_amount():
    return round(random.uniform(500, 100000), 2)


def generate_customer_id(index):
    return f"CUST{index:06d}"


def generate_transaction_id(index):
    return f"TX{index:07d}"


def generate_invoice_id(index):
    return f"INV{index:07d}"


# ============================================================
# Customer Master
# ============================================================

def generate_customer_master():
    records = []

    start_date = datetime(2026, 1, 1)
    end_date = datetime(2026, 8, 31)

    for i in range(1, NUM_CUSTOMERS + 1):
        name = random_name()

        records.append({
            "customer_id": generate_customer_id(i),
            "customer_name": name,
            "email": random_email(name),
            "phone": random_phone(),
            "address": f"{random.randint(1, 999)}, Main Road",
            "city": random.choice([
                "Hyderabad",
                "Bengaluru",
                "Mumbai",
                "Delhi",
                "Chennai",
                "Pune",
                "Kolkata",
                "Ahmedabad"
            ]),
            "state": random.choice([
                "Telangana",
                "Karnataka",
                "Maharashtra",
                "Delhi",
                "Tamil Nadu",
                "West Bengal",
                "Gujarat"
            ]),
            "customer_type": random.choice([
                "Individual",
                "Business"
            ]),
            "created_date": random_date(start_date, end_date)
        })

    return pd.DataFrame(records)


# ============================================================
# Invoice Data
# ============================================================

def generate_invoices(customer_master):
    records = []

    start_date = datetime(2026, 8, 1)
    end_date = datetime(2026, 8, 31)

    for i in range(1, NUM_TRANSACTIONS + 1):
        customer = customer_master.sample(
            n=1,
            random_state=SEED + i
        ).iloc[0]

        invoice_date = random_date(start_date, end_date)
        invoice_amount = random_amount()

        tax = round(invoice_amount * random.uniform(0.05, 0.18), 2)
        discount = round(invoice_amount * random.uniform(0, 0.10), 2)

        net_amount = round(
            invoice_amount + tax - discount,
            2
        )

        records.append({
            "invoice_id": generate_invoice_id(i),
            "customer_id": customer["customer_id"],
            "invoice_date": invoice_date,
            "invoice_amount": invoice_amount,
            "tax": tax,
            "discount": discount,
            "net_amount": net_amount
        })

    return pd.DataFrame(records)


# ============================================================
# ERP Transactions
# ============================================================

def generate_erp_transactions(invoices, customer_master):
    records = []

    customer_lookup = customer_master.set_index("customer_id")

    for i, invoice in invoices.iterrows():

        customer = customer_lookup.loc[invoice["customer_id"]]

        transaction_id = generate_transaction_id(i + 1)

        records.append({
            "transaction_id": transaction_id,
            "invoice_id": invoice["invoice_id"],
            "customer_id": invoice["customer_id"],
            "customer_name": customer["customer_name"],
            "email": customer["email"],
            "phone": customer["phone"],
            "transaction_date": invoice["invoice_date"],
            "amount": invoice["net_amount"],
            "currency": "INR",
            "payment_status": random.choice([
                "PAID",
                "PAID",
                "PAID",
                "PENDING"
            ]),
            "store_id": f"STORE{random.randint(1, 250):03d}"
        })

    return pd.DataFrame(records)


# ============================================================
# Payment Gateway
# ============================================================

def generate_payment_gateway(erp):
    records = []

    gateways = ["Gateway_A", "Gateway_B", "Gateway_C"]

    for _, transaction in erp.iterrows():

        records.append({
            "gateway_transaction_id": f"PG{random.randint(10000000, 99999999)}",
            "merchant_reference": transaction["transaction_id"],
            "customer_name": transaction["customer_name"],
            "email": transaction["email"],
            "transaction_date": transaction["transaction_date"],
            "amount": transaction["amount"],
            "payment_status": random.choice([
                "SUCCESS",
                "SUCCESS",
                "SUCCESS",
                "FAILED"
            ]),
            "gateway": random.choice(gateways)
        })

    return pd.DataFrame(records)


# ============================================================
# Bank Transactions
# ============================================================

def generate_bank_transactions(payment_gateway):
    records = []

    for _, payment in payment_gateway.iterrows():

        transaction_date = payment["transaction_date"]

        settlement_delay = random.choice([0, 0, 1, 1, 2])

        value_date = transaction_date + timedelta(
            days=settlement_delay
        )

        records.append({
            "bank_transaction_id": (
                f"BNK{random.randint(10000000, 99999999)}"
            ),
            "transaction_date": transaction_date,
            "value_date": value_date,
            "narration": (
                f"{payment['customer_name']} "
                f"{payment['gateway_transaction_id']}"
            ),
            "credit_amount": payment["amount"],
            "debit_amount": 0.0,
            "reference_number": payment["gateway_transaction_id"]
        })

    return pd.DataFrame(records)


# ============================================================
# Data corruption / anomaly injection
# ============================================================

def inject_corruption(
    erp,
    payment_gateway,
    bank
):
    print("Injecting controlled data-quality issues...")

    # --------------------------------------------------------
    # 1. Duplicate ERP transactions
    # --------------------------------------------------------

    duplicate_count = int(len(erp) * 0.01)

    duplicates = erp.sample(
        n=duplicate_count,
        random_state=SEED
    ).copy()

    erp = pd.concat(
        [erp, duplicates],
        ignore_index=True
    )

    # --------------------------------------------------------
    # 2. Amount mismatches
    # --------------------------------------------------------

    mismatch_count = int(len(payment_gateway) * 0.02)

    mismatch_indices = payment_gateway.sample(
        n=mismatch_count,
        random_state=SEED + 1
    ).index

    payment_gateway.loc[
        mismatch_indices,
        "amount"
    ] = (
        payment_gateway.loc[
            mismatch_indices,
            "amount"
        ] * np.random.uniform(
            0.7,
            1.3,
            size=mismatch_count
        )
    ).round(2)

    # --------------------------------------------------------
    # 3. Date mismatches
    # --------------------------------------------------------

    date_mismatch_count = int(len(payment_gateway) * 0.015)

    date_indices = payment_gateway.sample(
        n=date_mismatch_count,
        random_state=SEED + 2
    ).index

    payment_gateway.loc[
        date_indices,
        "transaction_date"
    ] = pd.to_datetime(
        payment_gateway.loc[
            date_indices,
            "transaction_date"
        ]
    ) + pd.to_timedelta(
        np.random.choice(
            [-2, -1, 1, 2],
            size=date_mismatch_count
        ),
        unit="D"
    )

    # --------------------------------------------------------
    # 4. Partial payments
    # --------------------------------------------------------

    partial_count = int(len(payment_gateway) * 0.01)

    partial_indices = payment_gateway.sample(
        n=partial_count,
        random_state=SEED + 3
    ).index

    payment_gateway.loc[
        partial_indices,
        "amount"
    ] = (
        payment_gateway.loc[
            partial_indices,
            "amount"
        ] * np.random.uniform(
            0.4,
            0.8,
            size=partial_count
        )
    ).round(2)

    # --------------------------------------------------------
    # 5. Overpayments
    # --------------------------------------------------------

    overpayment_count = int(len(payment_gateway) * 0.005)

    overpayment_indices = payment_gateway.sample(
        n=overpayment_count,
        random_state=SEED + 4
    ).index

    payment_gateway.loc[
        overpayment_indices,
        "amount"
    ] = (
        payment_gateway.loc[
            overpayment_indices,
            "amount"
        ] * np.random.uniform(
            1.1,
            1.5,
            size=overpayment_count
        )
    ).round(2)

    # --------------------------------------------------------
    # 6. Name variations
    # --------------------------------------------------------

    name_variation_count = int(len(payment_gateway) * 0.02)

    name_indices = payment_gateway.sample(
        n=name_variation_count,
        random_state=SEED + 5
    ).index

    for idx in name_indices:
        name = payment_gateway.at[idx, "customer_name"]

        variation_type = random.choice([
            "upper",
            "double_space",
            "reverse"
        ])

        if variation_type == "upper":
            payment_gateway.at[idx, "customer_name"] = name.upper()

        elif variation_type == "double_space":
            payment_gateway.at[idx, "customer_name"] = name.replace(
                " ",
                "  ",
                1
            )

        elif variation_type == "reverse":
            parts = name.split()

            if len(parts) >= 2:
                payment_gateway.at[idx, "customer_name"] = (
                    f"{parts[-1]} {' '.join(parts[:-1])}"
                )

    # --------------------------------------------------------
    # 7. Email variations
    # --------------------------------------------------------

    email_variation_count = int(len(payment_gateway) * 0.015)

    email_indices = payment_gateway.sample(
        n=email_variation_count,
        random_state=SEED + 6
    ).index

    for idx in email_indices:
        email = payment_gateway.at[idx, "email"]

        payment_gateway.at[idx, "email"] = random.choice([
            email.upper(),
            f" {email} ",
            email.lower()
        ])

    # --------------------------------------------------------
    # 8. Missing payments
    # --------------------------------------------------------

    missing_count = int(len(payment_gateway) * 0.01)

    missing_indices = payment_gateway.sample(
        n=missing_count,
        random_state=SEED + 7
    ).index

    payment_gateway = payment_gateway.drop(
        missing_indices
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # 9. Unexpected payments
    # --------------------------------------------------------

    unexpected_count = int(len(payment_gateway) * 0.005)

    unexpected_records = []

    for i in range(unexpected_count):
        unexpected_records.append({
            "gateway_transaction_id": f"PG_UNEXPECTED_{i + 1:05d}",
            "merchant_reference": f"UNKNOWN_TX_{i + 1:05d}",
            "customer_name": random_name(),
            "email": "unknown@example.com",
            "transaction_date": datetime(2026, 8, random.randint(1, 31)),
            "amount": random_amount(),
            "payment_status": "SUCCESS",
            "gateway": random.choice([
                "Gateway_A",
                "Gateway_B",
                "Gateway_C"
            ])
        })

    payment_gateway = pd.concat(
        [
            payment_gateway,
            pd.DataFrame(unexpected_records)
        ],
        ignore_index=True
    )

    # --------------------------------------------------------
    # 10. Bank amount mismatches
    # --------------------------------------------------------

    bank_mismatch_count = int(len(bank) * 0.01)

    bank_indices = bank.sample(
        n=bank_mismatch_count,
        random_state=SEED + 8
    ).index

    bank.loc[
        bank_indices,
        "credit_amount"
    ] = (
        bank.loc[
            bank_indices,
            "credit_amount"
        ] * np.random.uniform(
            0.8,
            1.2,
            size=bank_mismatch_count
        )
    ).round(2)

    return erp, payment_gateway, bank


# ============================================================
# Save datasets
# ============================================================

def save_data(
    customer_master,
    invoices,
    erp,
    payment_gateway,
    bank
):
    os.makedirs(RAW_DATA_DIR, exist_ok=True)

    customer_master.to_csv(
        os.path.join(
            RAW_DATA_DIR,
            "customer_master.csv"
        ),
        index=False
    )

    invoices.to_csv(
        os.path.join(
            RAW_DATA_DIR,
            "invoice.csv"
        ),
        index=False
    )

    erp.to_csv(
        os.path.join(
            RAW_DATA_DIR,
            "erp_transactions.csv"
        ),
        index=False
    )

    payment_gateway.to_csv(
        os.path.join(
            RAW_DATA_DIR,
            "payment_gateway.csv"
        ),
        index=False
    )

    bank.to_csv(
        os.path.join(
            RAW_DATA_DIR,
            "bank_transactions.csv"
        ),
        index=False
    )


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print("ENTERPRISE DATA FORENSICS")
    print("Synthetic Data Generator")
    print("=" * 60)

    print("\nGenerating customer master...")
    customer_master = generate_customer_master()

    print("Generating invoices...")
    invoices = generate_invoices(customer_master)

    print("Generating ERP transactions...")
    erp = generate_erp_transactions(
        invoices,
        customer_master
    )

    print("Generating payment gateway transactions...")
    payment_gateway = generate_payment_gateway(erp)

    print("Generating bank transactions...")
    bank = generate_bank_transactions(
        payment_gateway
    )

    erp, payment_gateway, bank = inject_corruption(
        erp,
        payment_gateway,
        bank
    )

    save_data(
        customer_master,
        invoices,
        erp,
        payment_gateway,
        bank
    )

    print("\nData generation completed.")
    print("-" * 60)

    print(f"Customer Master : {len(customer_master):,}")
    print(f"Invoices        : {len(invoices):,}")
    print(f"ERP             : {len(erp):,}")
    print(f"Payment Gateway : {len(payment_gateway):,}")
    print(f"Bank            : {len(bank):,}")

    print("-" * 60)
    print(f"Files saved to: {RAW_DATA_DIR}")


if __name__ == "__main__":
    main()