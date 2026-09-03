-- ============================================================
-- ENTERPRISE DATA FORENSICS
-- SQLite Database Schema
-- ============================================================

PRAGMA foreign_keys = ON;

-- ============================================================
-- CUSTOMER MASTER
-- ============================================================

CREATE TABLE IF NOT EXISTS customer_master (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT,
    email TEXT,
    phone TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    customer_type TEXT
);

-- ============================================================
-- INVOICES
-- ============================================================

CREATE TABLE IF NOT EXISTS invoice (
    invoice_id TEXT PRIMARY KEY,
    customer_id TEXT,
    invoice_date TEXT,
    invoice_amount REAL,
    tax REAL,
    discount REAL,
    net_amount REAL,
    FOREIGN KEY (customer_id)
        REFERENCES customer_master(customer_id)
);

-- ============================================================
-- ERP TRANSACTIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS erp_transactions (
    transaction_id TEXT,
    invoice_id TEXT,
    customer_id TEXT,
    customer_name TEXT,
    email TEXT,
    phone TEXT,
    transaction_date TEXT,
    amount REAL,
    currency TEXT,
    payment_status TEXT,
    store_id TEXT
);

-- ============================================================
-- PAYMENT GATEWAY
-- ============================================================

CREATE TABLE IF NOT EXISTS payment_gateway (
    gateway_transaction_id TEXT PRIMARY KEY,
    merchant_reference TEXT,
    customer_name TEXT,
    email TEXT,
    transaction_date TEXT,
    amount REAL,
    payment_status TEXT,
    gateway TEXT
);

-- ============================================================
-- BANK TRANSACTIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS bank_transactions (
    bank_transaction_id TEXT PRIMARY KEY,
    transaction_date TEXT,
    value_date TEXT,
    narration TEXT,
    credit_amount REAL,
    debit_amount REAL,
    reference_number TEXT
);

-- ============================================================
-- ENTITY MATCH RESULTS
-- ============================================================

CREATE TABLE IF NOT EXISTS entity_matches (
    transaction_id TEXT,
    gateway_transaction_id TEXT,
    merchant_reference TEXT,
    entity_match_score REAL,
    entity_match_confidence TEXT
);

-- ============================================================
-- RECONCILIATION RESULTS
-- ============================================================

CREATE TABLE IF NOT EXISTS reconciliation (
    transaction_id TEXT,
    invoice_id TEXT,
    customer_id TEXT,
    customer_name TEXT,
    store_id TEXT,
    erp_amount REAL,
    payment_amount REAL,
    payment_difference REAL,
    bank_amount REAL,
    bank_difference REAL,
    bank_status TEXT,
    date_difference_days REAL,
    reconciliation_status TEXT,
    entity_match_score REAL,
    entity_match_confidence TEXT,
    gateway TEXT
);

-- ============================================================
-- EXCEPTION REGISTER
-- ============================================================

CREATE TABLE IF NOT EXISTS exception_register (
    exception_id TEXT PRIMARY KEY,
    transaction_id TEXT,
    invoice_id TEXT,
    customer_id TEXT,
    customer_name TEXT,
    store_id TEXT,
    reconciliation_status TEXT,
    severity TEXT,
    financial_impact REAL,
    entity_match_score REAL,
    entity_match_confidence TEXT,
    gateway TEXT,
    erp_amount REAL,
    payment_amount REAL,
    payment_difference REAL,
    bank_amount REAL,
    bank_difference REAL,
    bank_status TEXT,
    date_difference_days REAL,
    owner TEXT,
    status TEXT,
    root_cause TEXT,
    recommended_action TEXT,
    created_date TEXT,
    exception_age_days INTEGER,
    sla_days INTEGER,
    sla_status TEXT,
    resolution TEXT,
    resolution_date TEXT
);

-- ============================================================
-- INDEXES FOR INVESTIGATION
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_erp_transaction
    ON erp_transactions(transaction_id);

CREATE INDEX IF NOT EXISTS idx_erp_customer
    ON erp_transactions(customer_id);

CREATE INDEX IF NOT EXISTS idx_payment_reference
    ON payment_gateway(merchant_reference);

CREATE INDEX IF NOT EXISTS idx_bank_reference
    ON bank_transactions(reference_number);

CREATE INDEX IF NOT EXISTS idx_reconciliation_status
    ON reconciliation(reconciliation_status);

CREATE INDEX IF NOT EXISTS idx_exception_status
    ON exception_register(status);

CREATE INDEX IF NOT EXISTS idx_exception_severity
    ON exception_register(severity);

CREATE INDEX IF NOT EXISTS idx_exception_owner
    ON exception_register(owner);

CREATE INDEX IF NOT EXISTS idx_exception_gateway
    ON exception_register(gateway);

CREATE INDEX IF NOT EXISTS idx_exception_store
    ON exception_register(store_id);