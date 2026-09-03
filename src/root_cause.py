import os

import pandas as pd


PROCESSED_DATA_DIR = os.path.join("data", "processed")


# ============================================================
# Load exception register
# ============================================================

def load_exceptions():
    path = os.path.join(
        PROCESSED_DATA_DIR,
        "exception_register.csv"
    )

    return pd.read_csv(path)


# ============================================================
# Exception type analysis
# ============================================================

def analyze_exception_types(df):
    """
    Identify exception categories and their
    financial impact.
    """

    result = (
        df.groupby(
            "reconciliation_status",
            dropna=False
        )
        .agg(
            exception_count=(
                "exception_id",
                "count"
            ),
            financial_exposure=(
                "financial_impact",
                "sum"
            ),
            average_impact=(
                "financial_impact",
                "mean"
            )
        )
        .reset_index()
        .sort_values(
            "financial_exposure",
            ascending=False
        )
    )

    return result


# ============================================================
# Gateway analysis
# ============================================================

def analyze_gateways(df):
    """
    Identify payment gateways generating
    the highest number and value of exceptions.
    """

    result = (
        df.dropna(subset=["gateway"])
        .groupby("gateway")
        .agg(
            exceptions=(
                "exception_id",
                "count"
            ),
            financial_exposure=(
                "financial_impact",
                "sum"
            ),
            average_impact=(
                "financial_impact",
                "mean"
            )
        )
        .reset_index()
        .sort_values(
            "financial_exposure",
            ascending=False
        )
    )

    return result


# ============================================================
# Store analysis
# ============================================================

def analyze_stores(df):
    """
    Identify stores with the greatest
    exception concentration.
    """

    result = (
        df.dropna(subset=["store_id"])
        .groupby("store_id")
        .agg(
            exceptions=(
                "exception_id",
                "count"
            ),
            financial_exposure=(
                "financial_impact",
                "sum"
            ),
            average_impact=(
                "financial_impact",
                "mean"
            )
        )
        .reset_index()
        .sort_values(
            "financial_exposure",
            ascending=False
        )
    )

    return result


# ============================================================
# Customer analysis
# ============================================================

def analyze_customers(df):
    """
    Identify customers with repeated exceptions
    and high cumulative financial impact.
    """

    result = (
        df.dropna(subset=["customer_id"])
        .groupby(
            [
                "customer_id",
                "customer_name"
            ],
            dropna=False
        )
        .agg(
            exception_count=(
                "exception_id",
                "count"
            ),
            financial_exposure=(
                "financial_impact",
                "sum"
            )
        )
        .reset_index()
        .sort_values(
            [
                "exception_count",
                "financial_exposure"
            ],
            ascending=False
        )
    )

    return result


# ============================================================
# Severity analysis
# ============================================================

def analyze_severity(df):
    """
    Summarize exception concentration by severity.
    """

    result = (
        df.groupby("severity")
        .agg(
            exception_count=(
                "exception_id",
                "count"
            ),
            financial_exposure=(
                "financial_impact",
                "sum"
            )
        )
        .reset_index()
    )

    severity_order = [
        "CRITICAL",
        "HIGH",
        "MEDIUM",
        "LOW"
    ]

    result["severity"] = pd.Categorical(
        result["severity"],
        categories=severity_order,
        ordered=True
    )

    return result.sort_values("severity")


# ============================================================
# Root cause analysis
# ============================================================

def analyze_root_causes(df):
    """
    Summarize the root causes assigned by the
    exception engine.
    """

    result = (
        df.groupby("root_cause")
        .agg(
            exception_count=(
                "exception_id",
                "count"
            ),
            financial_exposure=(
                "financial_impact",
                "sum"
            )
        )
        .reset_index()
        .sort_values(
            "financial_exposure",
            ascending=False
        )
    )

    return result


# ============================================================
# Owner analysis
# ============================================================

def analyze_owners(df):
    """
    Identify which teams are receiving the
    largest exception workload.
    """

    result = (
        df.groupby("owner")
        .agg(
            exception_count=(
                "exception_id",
                "count"
            ),
            financial_exposure=(
                "financial_impact",
                "sum"
            )
        )
        .reset_index()
        .sort_values(
            "financial_exposure",
            ascending=False
        )
    )

    return result


# ============================================================
# Exception concentration
# ============================================================

def calculate_concentration(df):
    """
    Calculate what percentage of total financial
    exposure comes from the top exception categories.
    """

    total_exposure = df[
        "financial_impact"
    ].sum()

    if total_exposure == 0:
        return 0.0

    top_10_exposure = (
        df.sort_values(
            "financial_impact",
            ascending=False
        )
        .head(10)[
            "financial_impact"
        ]
        .sum()
    )

    return round(
        (top_10_exposure / total_exposure) * 100,
        2
    )


# ============================================================
# Save analysis outputs
# ============================================================

def save_analysis(name, df):
    output_path = os.path.join(
        PROCESSED_DATA_DIR,
        f"root_cause_{name}.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    return output_path


# ============================================================
# Print analysis
# ============================================================

def print_section(title, df, rows=10):

    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)

    if df.empty:
        print("No data available.")
        return

    print(
        df.head(rows).to_string(
            index=False
        )
    )


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print("ENTERPRISE DATA FORENSICS")
    print("Root Cause Analysis Engine")
    print("=" * 60)

    print("\nLoading exception register...")

    df = load_exceptions()

    print(
        f"Exception records: {len(df):,}"
    )

    # --------------------------------------------------------
    # Run analyses
    # --------------------------------------------------------

    print("\nRunning root-cause analysis...")

    exception_types = analyze_exception_types(df)
    gateways = analyze_gateways(df)
    stores = analyze_stores(df)
    customers = analyze_customers(df)
    severity = analyze_severity(df)
    root_causes = analyze_root_causes(df)
    owners = analyze_owners(df)

    concentration = calculate_concentration(df)

    # --------------------------------------------------------
    # Save outputs
    # --------------------------------------------------------

    save_analysis(
        "exception_types",
        exception_types
    )

    save_analysis(
        "gateways",
        gateways
    )

    save_analysis(
        "stores",
        stores
    )

    save_analysis(
        "customers",
        customers
    )

    save_analysis(
        "severity",
        severity
    )

    save_analysis(
        "root_causes",
        root_causes
    )

    save_analysis(
        "owners",
        owners
    )

    # --------------------------------------------------------
    # Display results
    # --------------------------------------------------------

    print_section(
        "EXCEPTION TYPES",
        exception_types
    )

    print_section(
        "TOP PAYMENT GATEWAYS",
        gateways
    )

    print_section(
        "TOP STORES",
        stores
    )

    print_section(
        "TOP CUSTOMERS",
        customers
    )

    print_section(
        "SEVERITY",
        severity
    )

    print_section(
        "ROOT CAUSES",
        root_causes
    )

    print_section(
        "OWNER WORKLOAD",
        owners
    )

    # --------------------------------------------------------
    # Executive insight
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("KEY INVESTIGATION INSIGHT")
    print("=" * 60)

    print(
        f"Total financial exposure: "
        f"₹{df['financial_impact'].sum():,.2f}"
    )

    print(
        f"Top 10 exceptions account for "
        f"{concentration:.2f}% of total exposure."
    )

    if not exception_types.empty:

        top_type = exception_types.iloc[0]

        print(
            f"Largest exposure category: "
            f"{top_type['reconciliation_status']} "
            f""
            f"(₹{top_type['financial_exposure']:,.2f})"
        )

    if not gateways.empty:

        top_gateway = gateways.iloc[0]

        print(
            f"Highest-impact gateway: "
            f"{top_gateway['gateway']} "
            f""
            f"(₹{top_gateway['financial_exposure']:,.2f})"
        )

    if not stores.empty:

        top_store = stores.iloc[0]

        print(
            f"Highest-impact store: "
            f"{top_store['store_id']} "
            f""
            f"(₹{top_store['financial_exposure']:,.2f})"
        )

    print("\nRoot-cause analysis completed.")


if __name__ == "__main__":
    main()