# 🔎 Enterprise Data Forensics, Reconciliation & Exception Detection Engine

An end-to-end **Enterprise Data Forensics platform** built to reconcile multi-source financial records, resolve entities, identify discrepancies and potentially anomalous transactions, quantify financial exposure, and prioritize exceptions for investigation.

The project simulates an enterprise retail/e-commerce control and investigation workflow across **ERP transactions, payment gateway records, bank settlements, customer master data, and invoices**.

## 🚀 Live Demo

🔗 **[Open the Live Streamlit Dashboard](https://ankitha-d-enterprise-data-forensics-app-zk1gd5.streamlit.app/)**

The deployed dashboard provides interactive views of:

- Transaction reconciliation
- Exception volumes
- Financial exposure
- Severity distribution
- Root-cause patterns
- Payment gateway exposure
- Potential anomalies
- Investigation records

## 📌 Project Objective

Enterprise financial information is often distributed across multiple operational systems. Differences between those systems can result from duplicate transactions, missing payments, inconsistent identifiers, amount mismatches, date differences, and other data-quality issues.

This project implements an end-to-end **data forensics and reconciliation pipeline** that:

1. Generates realistic synthetic enterprise datasets
2. Standardizes and cleans source data
3. Resolves entities across systems
4. Reconciles financial transactions
5. Classifies reconciliation exceptions
6. Quantifies financial exposure
7. Detects potentially anomalous transactions
8. Performs root-cause analysis
9. Prioritizes exceptions for investigation
10. Produces SQL, Excel, Power BI, and Streamlit outputs

> **Important:** Anomaly-detection results are investigation indicators. They do not represent confirmed fraud or automatically imply financial loss.

## 🏗️ End-to-End Architecture

```text
ERP Transactions
       │
       ├───────────────┐
       │               │
Payment Gateway       │
       │               │
Bank Transactions     │
       │               │
Customer Master       │
       │               │
Invoices              │
       │               │
       └───────┬───────┘
               ▼
       Data Cleaning &
       Standardization
               │
               ▼
        Entity Resolution
               │
               ▼
       Transaction Matching
               │
               ▼
          Reconciliation
               │
               ▼
        Exception Detection
               │
         ┌─────┴──────┐
         ▼            ▼
   Anomaly Detection  Root-Cause
                      Analysis
         │            │
         └─────┬──────┘
               ▼
     Investigation Prioritization
               │
        ┌──────┼──────┐
        ▼      ▼      ▼
       SQL    Excel  Power BI
                       │
                       ▼
                  Streamlit
                   Live Demo
📂 Data Sources

The project simulates five enterprise data sources.

Dataset	Description
erp_transactions.csv	Primary ERP transaction records
payment_gateway.csv	Payment gateway transaction records
bank_transactions.csv	Bank settlement transactions
customer_master.csv	Customer reference/master records
invoice.csv	Invoice and billing records
ERP Transactions

Contains fields such as:

Transaction ID
Invoice ID
Customer ID
Customer name
Email
Phone
Transaction date
Amount
Currency
Payment status
Store ID
Payment Gateway

Contains:

Gateway transaction ID
Merchant reference
Customer information
Transaction date
Amount
Payment status
Gateway
Bank Transactions

Contains:

Bank transaction ID
Transaction date
Value date
Narration
Credit amount
Debit amount
Reference number
Customer Master

Contains:

Customer ID
Customer name
Email
Phone
Address
City
State
Customer type
Invoice

Contains:

Invoice ID
Customer ID
Invoice date
Invoice amount
Tax
Discount
Net amount
⚠️ Simulated Data Quality Issues

The synthetic data intentionally introduces realistic enterprise reconciliation scenarios, including:

Duplicate ERP transactions
Payment amount mismatches
Payment date mismatches
Partial payments
Overpayments
Missing payments
Unexpected payments
Customer-name variations
Email variations
Bank amount mismatches
Entity matching uncertainty

This allows the pipeline to simulate discrepancies that can occur when financial information is maintained across independent enterprise systems.

🔄 Data Processing Pipeline
1. Synthetic Data Generation

File:

src/data_generator.py

Generates reproducible synthetic enterprise datasets using a fixed random seed.

The generator creates:

10,000 customers
50,000 base ERP transactions
Payment gateway transactions
Bank transactions
Invoice records

Controlled data-quality issues are also injected so the downstream reconciliation and investigation logic can be evaluated.

2. Data Cleaning & Standardization

File:

src/cleaning.py

The cleaning layer standardizes common enterprise data inconsistencies.

It normalizes:

Customer names
Email addresses
Phone numbers
Dates
Monetary amounts

Cleaned datasets are written to:

data/processed/
3. Entity Resolution

File:

src/entity_matching.py

Payment records are matched to ERP transactions using multiple matching signals, including:

Exact matching
Fuzzy string matching
Email similarity
Customer-name similarity
Transaction amount consistency
Composite matching scores

Matching results are categorized into:

High confidence
Medium confidence
Manual review
No match

Output:

data/processed/entity_matches.csv
Entity Matching Results
HIGH_CONFIDENCE      47,899
MEDIUM_CONFIDENCE     2,085
NO_MATCH                506
MANUAL_REVIEW            10

Average matching score:

98.20
🔄 Transaction Reconciliation

File:

src/reconciliation.py

The reconciliation engine compares ERP, payment gateway, and bank information to determine the financial status of each transaction.

Reconciliation statuses include:

MATCHED
AMOUNT_MISMATCH
MISSING_PAYMENT
UNEXPECTED_PAYMENT
PARTIAL_PAYMENT
OVERPAYMENT
DUPLICATE
DATE_MISMATCH
ENTITY_UNCERTAIN
Reconciliation Results
MATCHED               46,958
DUPLICATE              1,000
PARTIAL_PAYMENT          964
OVERPAYMENT              715
MISSING_PAYMENT          494
DATE_MISMATCH            359
UNEXPECTED_PAYMENT       247
ENTITY_UNCERTAIN          10

Total reconciliation records:

50,747

Output:

data/processed/reconciliation.csv
🚨 Exception Detection

File:

src/exceptions.py

The exception engine converts reconciliation discrepancies into an investigation-ready exception register.

Each exception contains information such as:

Exception ID
Transaction ID
Severity
Financial impact
Owner
Workflow status
Root cause
Recommended action
Exception age
SLA status
Resolution information
Exception Results

Total exceptions: 3,789

Financial exposure: ₹22,796,486.36

Approximately:

₹22.8M

Severity Distribution
Severity	Exceptions
🔴 CRITICAL	18
🟠 HIGH	1,580
🟡 MEDIUM	2,191
Exception Categories
Exception Type	Count
DUPLICATE	1,000
PARTIAL_PAYMENT	964
OVERPAYMENT	715
MISSING_PAYMENT	494
DATE_MISMATCH	359
UNEXPECTED_PAYMENT	247
ENTITY_UNCERTAIN	10

Output:

data/processed/exception_register.csv
🔍 Root-Cause Analysis

File:

src/root_cause.py

The root-cause layer analyzes exception concentration across different business dimensions.

Analysis includes:

Exception types
Payment gateways
Stores
Customers
Severity
Root causes
Exception owners

Generated outputs include:

root_cause_exception_types.csv
root_cause_gateways.csv
root_cause_stores.csv
root_cause_customers.csv
root_cause_severity.csv
root_cause_root_causes.csv
root_cause_owners.csv

The analysis helps identify where exception volumes and financial exposure are concentrated.

🤖 Anomaly Detection

File:

src/anomaly_detection.py

The anomaly-detection layer supplements deterministic reconciliation rules with statistical and machine-learning methods.

Methods include:

Z-score analysis
IQR-based analysis
Isolation Forest

The implementation identifies transactions that may warrant additional investigation.

Results

Isolation Forest identified:

3,641 potential anomaly records

These are investigation candidates rather than confirmed fraudulent transactions.

Output:

data/processed/anomaly_detection.csv
🧮 SQL Investigation Layer

SQL is used to investigate reconciliation results and exception patterns.

Files:

sql/
├── schema.sql
├── reconciliation_queries.sql
└── investigation_queries.sql

The SQL layer supports analysis of:

Reconciliation statuses
Exception patterns
Financial exposure
High-impact transactions
Gateway-level concentration
Store-level concentration
Investigation priorities
Data-quality issues

The executable local database implementation uses SQLite.

📋 Excel Investigation Register

The project generates an Excel-based investigation workbook:

excel/exception_register.xlsx

The workbook contains:

Summary

High-level exception statistics.

Exception Register

Detailed investigation records including:

Exception ID
Transaction ID
Severity
Financial impact
Owner
Status
Root cause
Recommended action
Aging
SLA information
📊 Power BI Dashboard

The project includes a four-page Power BI dashboard:

powerbi/forensics_dashboard.pbix
Page 1 — Executive Overview

Provides management-level visibility into:

Total transactions
Total exceptions
Financial exposure
Severity breakdown
Root-cause exposure
Reconciliation status
Gateway exposure
Page 2 — Reconciliation Analysis

Provides:

Reconciliation status analysis
Payment differences
Bank-status analysis
Page 3 — Exception Investigation

Provides:

Exceptions by owner
Exceptions by workflow status
Financial exposure by severity
Investigation register
Page 4 — Anomaly & Root Cause

Provides:

Potential anomaly analysis
Investigation priority
Gateway exposure
Root-cause exposure
Transaction-level investigation details
🌐 Streamlit Dashboard

A live Streamlit dashboard is deployed from this repository.

🔗 Launch Live Dashboard

The application provides interactive filters for:

Severity
Exception owner
Workflow status

It presents:

Transaction KPIs
Exception KPIs
Financial exposure
Exception rate
Reconciliation status
Severity analysis
Root-cause exposure
Gateway exposure
Potential anomalies
Exception investigation register
📈 Validated Project Results

The final pipeline was validated using the generated datasets and processed outputs.

Dataset / Output	Records
Customer master	10,000
ERP transactions	50,500
Payment gateway records	49,747
Bank transactions	50,000
Invoice records	50,000
Entity matches	50,500
Reconciliation records	50,747
Exception records	3,789
Anomaly detection records	50,747
Power BI transaction records	50,247
Power BI exception records	3,789
Financial Exposure

₹22,796,486.36

Approximately:

₹22.8M

🛠️ Technology Stack

Programming & Data Processing
Python
Pandas
NumPy
RapidFuzz
Machine Learning
Scikit-learn
Isolation Forest
Statistical anomaly detection
Database & Analytics
SQL
SQLite
Reporting
Excel
OpenPyXL
Power BI
DAX
Application & Deployment
Streamlit
Git
GitHub
Streamlit Community Cloud

📂 Project Structure

enterprise-data-forensics/
│
├── data/
│   ├── raw/
│   │   ├── bank_transactions.csv
│   │   ├── customer_master.csv
│   │   ├── erp_transactions.csv
│   │   ├── invoice.csv
│   │   └── payment_gateway.csv
│   │
│   ├── processed/
│   │   ├── anomaly_detection.csv
│   │   ├── bank_transactions_clean.csv
│   │   ├── customer_master_clean.csv
│   │   ├── entity_matches.csv
│   │   ├── erp_transactions_clean.csv
│   │   ├── exception_register.csv
│   │   ├── invoice_clean.csv
│   │   ├── payment_gateway_clean.csv
│   │   ├── powerbi_exceptions.csv
│   │   ├── powerbi_transactions.csv
│   │   ├── reconciliation.csv
│   │   └── root_cause_*.csv
│   │
│   └── reference/
│
├── src/
│   ├── data_generator.py
│   ├── cleaning.py
│   ├── entity_matching.py
│   ├── reconciliation.py
│   ├── exceptions.py
│   ├── root_cause.py
│   ├── anomaly_detection.py
│   ├── load_database.py
│   ├── run_sql.py
│   ├── create_excel.py
│   ├── prepare_powerbi.py
│   └── prepare_powerbi_transactions.py
│
├── sql/
│   ├── schema.sql
│   ├── reconciliation_queries.sql
│   └── investigation_queries.sql
│
├── excel/
│   └── exception_register.xlsx
│
├── powerbi/
│   ├── forensics_dashboard.pbix
│   └── measures.dax
│
├── app.py
├── requirements.txt
└── README.md

⚙️ Installation

Clone the repository:

git clone https://github.com/ankitha-d/enterprise-data-forensics.git

Navigate into the project:

cd enterprise-data-forensics

Create a virtual environment:

python -m venv venv

Activate it on Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

▶️ Run the Pipeline

Run the scripts in sequence:

python src/data_generator.py
python src/cleaning.py
python src/entity_matching.py
python src/reconciliation.py
python src/exceptions.py
python src/root_cause.py
python src/anomaly_detection.py
python src/load_database.py
python src/run_sql.py
python src/create_excel.py
python src/prepare_powerbi.py
python src/prepare_powerbi_transactions.py

Processed outputs are written to:

data/processed/

▶️ Run the Streamlit Dashboard

Launch the dashboard locally:

streamlit run app.py

The application will open at:

http://localhost:8501
🎯 Business Value

The project demonstrates how fragmented enterprise financial data can be transformed into an investigation-ready analytical control framework.

It enables users to:

Identify cross-system reconciliation breaks
Detect missing and unexpected transactions
Identify duplicate payments and records
Quantify financial exposure
Prioritize high-severity exceptions
Analyze exception concentration
Investigate potentially anomalous transactions
Identify recurring root-cause patterns
Track investigation ownership and status
Support management reporting through dashboards

🧠 Skills Demonstrated

Enterprise Data Analytics
Data Cleaning & Standardization
Data Quality Management
Entity Resolution
Fuzzy Matching
Financial Reconciliation
Exception Detection
Exception Management
Financial Exposure Analysis
Root-Cause Analysis
Anomaly Detection
Isolation Forest
Statistical Analysis
SQL Investigation
SQLite
Excel Reporting
Power BI
DAX
Streamlit
Git / GitHub
Cloud Deployment
🔮 Future Improvements

Potential extensions include:

Persistent relational database deployment
Advanced entity-resolution models
Temporal transaction analysis
Graph-based relationship analysis
Explainable anomaly detection
Automated investigation reports
Expanded reconciliation rules
Automated unit and integration testing
CI/CD
Docker containerization
Role-based investigation workflows

👩‍💻 Author

Ankitha D

GitHub:
https://github.com/ankitha-d

⚠️ Disclaimer

This is a synthetic portfolio project.

All customers, transactions, financial records, and discrepancies are generated for demonstration purposes and do not represent real individuals, organizations, financial institutions, or confidential business information.

Anomaly-detection outputs are analytical investigation indicators and should not be interpreted as definitive fraud determinations.
