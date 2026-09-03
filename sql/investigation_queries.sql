-- ============================================================
-- ENTERPRISE DATA FORENSICS
-- Combined Investigation Queries
-- ============================================================


-- ============================================================
-- 1. HIGH-PRIORITY INVESTIGATION QUEUE
-- ============================================================

SELECT
    a.transaction_id,
    a.reconciliation_status,
    a.investigation_priority,
    a.isolation_forest_score,
    a.entity_match_score,
    r.customer_id,
    r.customer_name,
    r.store_id,
    r.gateway,
    r.erp_amount,
    r.payment_amount,
    r.bank_amount,
    e.exception_id,
    e.severity,
    e.financial_impact,
    e.owner,
    e.status,
    e.root_cause
FROM anomaly_detection a
LEFT JOIN reconciliation r
    ON a.transaction_id = r.transaction_id
LEFT JOIN exception_register e
    ON a.transaction_id = e.transaction_id
WHERE a.investigation_priority IN ('HIGH', 'MEDIUM')
ORDER BY
    CASE a.investigation_priority
        WHEN 'HIGH' THEN 1
        WHEN 'MEDIUM' THEN 2
        ELSE 3
    END,
    COALESCE(e.financial_impact, 0) DESC,
    a.isolation_forest_score ASC
LIMIT 100;


-- ============================================================
-- 2. STATISTICAL ANOMALIES AMONG MATCHED TRANSACTIONS
-- ============================================================

SELECT
    a.transaction_id,
    r.customer_id,
    r.customer_name,
    r.store_id,
    r.gateway,
    r.erp_amount,
    a.amount_z_score,
    a.amount_iqr_anomaly,
    a.isolation_forest_score,
    a.investigation_priority
FROM anomaly_detection a
JOIN reconciliation r
    ON a.transaction_id = r.transaction_id
WHERE r.reconciliation_status = 'MATCHED'
  AND a.potential_anomaly = 1
ORDER BY a.isolation_forest_score ASC
LIMIT 100;


-- ============================================================
-- 3. ANOMALIES BY GATEWAY
-- ============================================================

SELECT
    r.gateway,
    COUNT(*) AS potential_anomalies,
    ROUND(
        SUM(COALESCE(e.financial_impact, 0)),
        2
    ) AS related_financial_exposure
FROM anomaly_detection a
JOIN reconciliation r
    ON a.transaction_id = r.transaction_id
LEFT JOIN exception_register e
    ON a.transaction_id = e.transaction_id
WHERE a.potential_anomaly = 1
GROUP BY r.gateway
ORDER BY potential_anomalies DESC;


-- ============================================================
-- 4. ANOMALIES BY STORE
-- ============================================================

SELECT
    r.store_id,
    COUNT(*) AS potential_anomalies,
    ROUND(
        SUM(COALESCE(e.financial_impact, 0)),
        2
    ) AS related_financial_exposure
FROM anomaly_detection a
JOIN reconciliation r
    ON a.transaction_id = r.transaction_id
LEFT JOIN exception_register e
    ON a.transaction_id = e.transaction_id
WHERE a.potential_anomaly = 1
GROUP BY r.store_id
ORDER BY potential_anomalies DESC
LIMIT 20;


-- ============================================================
-- 5. EXCEPTION EXPOSURE BY OWNER
-- ============================================================

SELECT
    owner,
    COUNT(*) AS exception_count,
    SUM(
        CASE
            WHEN severity = 'CRITICAL'
            THEN 1
            ELSE 0
        END
    ) AS critical_count,
    SUM(
        CASE
            WHEN severity = 'HIGH'
            THEN 1
            ELSE 0
        END
    ) AS high_count,
    ROUND(
        SUM(financial_impact),
        2
    ) AS financial_exposure
FROM exception_register
GROUP BY owner
ORDER BY financial_exposure DESC;


-- ============================================================
-- 6. EXCEPTION AGING / SLA
-- ============================================================

SELECT
    severity,
    sla_status,
    COUNT(*) AS exception_count,
    ROUND(
        SUM(financial_impact),
        2
    ) AS financial_exposure
FROM exception_register
GROUP BY severity, sla_status
ORDER BY
    CASE severity
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        ELSE 4
    END;


-- ============================================================
-- 7. ROOT CAUSE CONCENTRATION
-- ============================================================

SELECT
    root_cause,
    COUNT(*) AS exception_count,
    ROUND(
        SUM(financial_impact),
        2
    ) AS financial_exposure
FROM exception_register
GROUP BY root_cause
ORDER BY financial_exposure DESC;


-- ============================================================
-- 8. FINANCIAL EXPOSURE CONCENTRATION
-- ============================================================

SELECT
    exception_id,
    transaction_id,
    reconciliation_status,
    severity,
    financial_impact,
    owner,
    root_cause,
    recommended_action
FROM exception_register
WHERE financial_impact > 0
ORDER BY financial_impact DESC
LIMIT 100;


-- ============================================================
-- 9. EXCEPTION STATUS WORKLOAD
-- ============================================================

SELECT
    status,
    COUNT(*) AS exception_count,
    ROUND(
        SUM(financial_impact),
        2
    ) AS financial_exposure
FROM exception_register
GROUP BY status
ORDER BY exception_count DESC;


-- ============================================================
-- 10. EXECUTIVE INVESTIGATION METRICS
-- ============================================================

SELECT
    (SELECT COUNT(*)
     FROM reconciliation
     WHERE reconciliation_status <> 'MATCHED')
        AS total_exceptions,

    (SELECT ROUND(SUM(financial_impact), 2)
     FROM exception_register)
        AS total_financial_exposure,

    (SELECT COUNT(*)
     FROM exception_register
     WHERE severity = 'CRITICAL')
        AS critical_exceptions,

    (SELECT COUNT(*)
     FROM exception_register
     WHERE severity = 'HIGH')
        AS high_exceptions,

    (SELECT COUNT(*)
     FROM anomaly_detection
     WHERE potential_anomaly = 1)
        AS potential_anomalies,

    (SELECT COUNT(*)
     FROM anomaly_detection
     WHERE potential_anomaly = 1
       AND reconciliation_status = 'MATCHED')
        AS anomalous_matched_transactions;