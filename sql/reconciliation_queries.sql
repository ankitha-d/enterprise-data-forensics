-- ============================================================
-- ENTERPRISE DATA FORENSICS
-- Reconciliation Investigation Queries
-- ============================================================


-- ============================================================
-- 1. RECONCILIATION STATUS SUMMARY
-- ============================================================

SELECT
    reconciliation_status,
    COUNT(*) AS record_count,
    ROUND(
        100.0 * COUNT(*) /
        (SELECT COUNT(*) FROM reconciliation),
        2
    ) AS percentage_of_records
FROM reconciliation
GROUP BY reconciliation_status
ORDER BY record_count DESC;


-- ============================================================
-- 2. FINANCIAL EXPOSURE BY RECONCILIATION STATUS
-- ============================================================

SELECT
    reconciliation_status,
    COUNT(*) AS exception_count,
    ROUND(
        SUM(
            CASE
                WHEN payment_difference IS NOT NULL
                     AND ABS(payment_difference) >
                         ABS(COALESCE(bank_difference, 0))
                THEN ABS(payment_difference)

                WHEN bank_difference IS NOT NULL
                THEN ABS(bank_difference)

                ELSE 0
            END
        ),
        2
    ) AS financial_exposure
FROM reconciliation
WHERE reconciliation_status <> 'MATCHED'
GROUP BY reconciliation_status
ORDER BY financial_exposure DESC;


-- ============================================================
-- 3. HIGH-IMPACT EXCEPTIONS
-- ============================================================

SELECT
    transaction_id,
    reconciliation_status,
    customer_id,
    customer_name,
    store_id,
    gateway,
    erp_amount,
    payment_amount,
    bank_amount,
    payment_difference,
    bank_difference,
    entity_match_confidence
FROM reconciliation
WHERE reconciliation_status <> 'MATCHED'
ORDER BY
    CASE
        WHEN payment_difference IS NOT NULL
        THEN ABS(payment_difference)
        ELSE ABS(COALESCE(bank_difference, 0))
    END DESC
LIMIT 100;


-- ============================================================
-- 4. EXCEPTIONS BY PAYMENT GATEWAY
-- ============================================================

SELECT
    gateway,
    reconciliation_status,
    COUNT(*) AS exception_count,
    ROUND(
        SUM(
            CASE
                WHEN payment_difference IS NOT NULL
                THEN ABS(payment_difference)
                ELSE ABS(COALESCE(bank_difference, 0))
            END
        ),
        2
    ) AS financial_exposure
FROM reconciliation
WHERE reconciliation_status <> 'MATCHED'
GROUP BY gateway, reconciliation_status
ORDER BY financial_exposure DESC;


-- ============================================================
-- 5. EXCEPTIONS BY STORE
-- ============================================================

SELECT
    store_id,
    COUNT(*) AS exception_count,
    ROUND(
        SUM(
            CASE
                WHEN payment_difference IS NOT NULL
                THEN ABS(payment_difference)
                ELSE ABS(COALESCE(bank_difference, 0))
            END
        ),
        2
    ) AS financial_exposure
FROM reconciliation
WHERE reconciliation_status <> 'MATCHED'
GROUP BY store_id
ORDER BY financial_exposure DESC
LIMIT 20;


-- ============================================================
-- 6. EXCEPTIONS BY CUSTOMER
-- ============================================================

SELECT
    customer_id,
    customer_name,
    COUNT(*) AS exception_count,
    ROUND(
        SUM(
            CASE
                WHEN payment_difference IS NOT NULL
                THEN ABS(payment_difference)
                ELSE ABS(COALESCE(bank_difference, 0))
            END
        ),
        2
    ) AS financial_exposure
FROM reconciliation
WHERE reconciliation_status <> 'MATCHED'
GROUP BY customer_id, customer_name
ORDER BY financial_exposure DESC
LIMIT 20;


-- ============================================================
-- 7. DATE MISMATCH INVESTIGATION
-- ============================================================

SELECT
    transaction_id,
    customer_id,
    customer_name,
    gateway,
    date_difference_days,
    erp_amount,
    payment_amount,
    reconciliation_status
FROM reconciliation
WHERE reconciliation_status = 'DATE_MISMATCH'
ORDER BY ABS(date_difference_days) DESC;


-- ============================================================
-- 8. ENTITY UNCERTAINTY INVESTIGATION
-- ============================================================

SELECT
    transaction_id,
    customer_id,
    customer_name,
    entity_match_score,
    entity_match_confidence,
    gateway,
    erp_amount,
    payment_amount
FROM reconciliation
WHERE reconciliation_status = 'ENTITY_UNCERTAIN'
ORDER BY entity_match_score ASC;


-- ============================================================
-- 9. DUPLICATE TRANSACTION INVESTIGATION
-- ============================================================

SELECT
    transaction_id,
    COUNT(*) AS occurrence_count,
    MIN(customer_id) AS customer_id,
    MIN(customer_name) AS customer_name,
    MIN(store_id) AS store_id,
    MIN(erp_amount) AS transaction_amount
FROM reconciliation
WHERE reconciliation_status = 'DUPLICATE'
GROUP BY transaction_id
ORDER BY occurrence_count DESC, transaction_amount DESC;


-- ============================================================
-- 10. OPEN EXCEPTION WORKLOAD
-- ============================================================

SELECT
    owner,
    severity,
    status,
    COUNT(*) AS exception_count,
    ROUND(
        SUM(financial_impact),
        2
    ) AS financial_exposure
FROM exception_register
GROUP BY owner, severity, status
ORDER BY
    CASE severity
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        ELSE 4
    END,
    financial_exposure DESC;