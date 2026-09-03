from pathlib import Path

import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"


st.set_page_config(
    page_title="Enterprise Data Forensics",
    page_icon="🔍",
    layout="wide",
)


@st.cache_data
def load_data():
    transactions = pd.read_csv(
        DATA_DIR / "powerbi_transactions.csv"
    )
    exceptions = pd.read_csv(
        DATA_DIR / "powerbi_exceptions.csv"
    )

    return transactions, exceptions


transactions, exceptions = load_data()


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("🔍 Enterprise Data Forensics")
st.caption(
    "Transaction Reconciliation • Exception Detection • "
    "Anomaly Investigation • Root Cause Analysis"
)

st.divider()


# ---------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------

st.sidebar.header("Investigation Filters")

severity_options = sorted(
    exceptions["severity"].dropna().unique()
)

selected_severity = st.sidebar.multiselect(
    "Severity",
    severity_options,
    default=severity_options,
)

owner_options = sorted(
    exceptions["owner"].dropna().unique()
)

selected_owner = st.sidebar.multiselect(
    "Owner",
    owner_options,
    default=owner_options,
)

status_options = sorted(
    exceptions["status"].dropna().unique()
)

selected_status = st.sidebar.multiselect(
    "Workflow Status",
    status_options,
    default=status_options,
)


filtered_exceptions = exceptions[
    exceptions["severity"].isin(selected_severity)
    & exceptions["owner"].isin(selected_owner)
    & exceptions["status"].isin(selected_status)
]


# ---------------------------------------------------------
# Executive KPIs
# ---------------------------------------------------------

st.subheader("Executive Overview")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "Transactions",
        f"{transactions['transaction_id'].nunique():,}",
    )

with c2:
    st.metric(
        "Exceptions",
        f"{filtered_exceptions['exception_id'].nunique():,}",
    )

with c3:
    exposure = filtered_exceptions["financial_impact"].sum()
    st.metric(
        "Financial Exposure",
        f"₹{exposure:,.2f}",
    )

with c4:
    total_transactions = transactions["transaction_id"].nunique()
    exception_count = filtered_exceptions["exception_id"].nunique()

    exception_rate = (
        exception_count / total_transactions * 100
        if total_transactions
        else 0
    )

    st.metric(
        "Exception Rate",
        f"{exception_rate:.2f}%",
    )


st.divider()


# ---------------------------------------------------------
# Reconciliation overview
# ---------------------------------------------------------

st.subheader("Reconciliation Overview")

left, right = st.columns(2)

with left:
    status_counts = (
        transactions["reconciliation_status"]
        .value_counts()
        .rename_axis("Status")
        .reset_index(name="Transactions")
    )

    st.bar_chart(
        status_counts.set_index("Status")
    )

with right:
    severity_counts = (
        filtered_exceptions["severity"]
        .value_counts()
        .rename_axis("Severity")
        .reset_index(name="Exceptions")
    )

    st.bar_chart(
        severity_counts.set_index("Severity")
    )


# ---------------------------------------------------------
# Financial exposure
# ---------------------------------------------------------

st.subheader("Financial Exposure by Root Cause")

root_cause = (
    filtered_exceptions
    .groupby("root_cause", as_index=False)["financial_impact"]
    .sum()
    .sort_values("financial_impact", ascending=False)
)

st.bar_chart(
    root_cause.set_index("root_cause")
)


# ---------------------------------------------------------
# Gateway analysis
# ---------------------------------------------------------

st.subheader("Financial Exposure by Payment Gateway")

gateway = (
    filtered_exceptions
    .groupby("gateway", as_index=False)["financial_impact"]
    .sum()
    .sort_values("financial_impact", ascending=False)
)

st.bar_chart(
    gateway.set_index("gateway")
)


# ---------------------------------------------------------
# Anomaly investigation
# ---------------------------------------------------------

st.subheader("Anomaly Investigation")

anomaly_col = "potential_anomaly"

if anomaly_col in transactions.columns:

    anomaly_counts = (
        transactions[anomaly_col]
        .value_counts()
        .rename_axis("Classification")
        .reset_index(name="Transactions")
    )

    st.bar_chart(
        anomaly_counts.set_index("Classification")
    )


# ---------------------------------------------------------
# Exception investigation table
# ---------------------------------------------------------

st.subheader("Exception Investigation Register")

display_columns = [
    "exception_id",
    "transaction_id",
    "severity",
    "financial_impact",
    "owner",
    "status",
    "root_cause",
    "recommended_action",
    "exception_age_days",
    "sla_status",
]

display_columns = [
    column
    for column in display_columns
    if column in filtered_exceptions.columns
]

st.dataframe(
    filtered_exceptions[display_columns]
    .sort_values("financial_impact", ascending=False),
    width='stretch',
    hide_index=True,
)


# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------

st.divider()

st.caption(
    "Synthetic portfolio project • "
    "Anomaly flags are investigation indicators and "
    "are not definitive fraud determinations."
)
