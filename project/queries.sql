-- ============================================================
-- NexaTel Communications - Business SQL Queries
-- Phase 1 | Author: Zain
-- All queries use JOINs across normalized tables
-- ============================================================


-- ────────────────────────────────────────────────────────────
-- QUERY 1: Overall Churn Rate
-- Business Question: What percentage of our total customers have churned?
-- This is the headline KPI the VP of Retention tracks monthly.
-- ────────────────────────────────────────────────────────────
SELECT
    COUNT(*)                                              AS total_customers,
    SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END)       AS churned_customers,
    ROUND(
        100.0 * SUM(CASE WHEN churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                     AS churn_rate_pct
FROM churn_status;


-- ────────────────────────────────────────────────────────────
-- QUERY 2: Churn Rate by Contract Type
-- Business Question: Do customers on month-to-month contracts churn more?
-- Helps justify pushing customers toward longer-term contracts.
-- ────────────────────────────────────────────────────────────
SELECT
    a.contract,
    COUNT(*)                                              AS total_customers,
    SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END)    AS churned,
    ROUND(
        100.0 * SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                     AS churn_rate_pct
FROM accounts a
JOIN churn_status cs ON a.customer_id = cs.customer_id
GROUP BY a.contract
ORDER BY churn_rate_pct DESC;


-- ────────────────────────────────────────────────────────────
-- QUERY 3: Churn Rate by Internet Service Type
-- Business Question: Does the type of internet service affect churn?
-- Fiber optic customers paying more but churning more could signal pricing issues.
-- ────────────────────────────────────────────────────────────
SELECT
    s.internet_service,
    COUNT(*)                                              AS total_customers,
    SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END)    AS churned,
    ROUND(
        100.0 * SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                     AS churn_rate_pct
FROM services s
JOIN churn_status cs ON s.customer_id = cs.customer_id
GROUP BY s.internet_service
ORDER BY churn_rate_pct DESC;


-- ────────────────────────────────────────────────────────────
-- QUERY 4: Average Tenure of Churned vs. Retained Customers
-- Business Question: How long do churned customers typically stay before leaving?
-- Knowing this helps us identify the critical intervention window.
-- ────────────────────────────────────────────────────────────
SELECT
    cs.churn,
    ROUND(AVG(c.tenure), 2)          AS avg_tenure_months,
    MIN(c.tenure)                    AS min_tenure,
    MAX(c.tenure)                    AS max_tenure
FROM customers c
JOIN churn_status cs ON c.customer_id = cs.customer_id
GROUP BY cs.churn;


-- ────────────────────────────────────────────────────────────
-- QUERY 5: Average Monthly Charges of Churned vs. Retained Customers
-- Business Question: Are higher-paying customers churning more?
-- Identifies if pricing is a key driver of churn.
-- ────────────────────────────────────────────────────────────
SELECT
    cs.churn,
    ROUND(AVG(a.monthly_charges), 2)   AS avg_monthly_charges,
    ROUND(AVG(a.total_charges), 2)     AS avg_total_charges
FROM accounts a
JOIN churn_status cs ON a.customer_id = cs.customer_id
GROUP BY cs.churn;


-- ────────────────────────────────────────────────────────────
-- QUERY 6: Top 5 Customer Segments with Highest Churn (Contract × Payment Method)
-- Business Question: Which contract + payment method combinations produce the most churn?
-- Helps retention team target outreach at the riskiest customer segments.
-- ────────────────────────────────────────────────────────────
SELECT
    a.contract,
    a.payment_method,
    COUNT(*)                                                AS total_customers,
    SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END)      AS churned,
    ROUND(
        100.0 * SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                       AS churn_rate_pct
FROM accounts a
JOIN churn_status cs ON a.customer_id = cs.customer_id
GROUP BY a.contract, a.payment_method
ORDER BY churn_rate_pct DESC
LIMIT 5;


-- ────────────────────────────────────────────────────────────
-- QUERY 7: Total Monthly Revenue at Risk (from Churned Customers)
-- Business Question: What is the monthly revenue impact of current churn?
-- This is the headline dollar figure for Finance and the VP of Retention.
-- ────────────────────────────────────────────────────────────
SELECT
    SUM(CASE WHEN cs.churn = 'Yes' THEN a.monthly_charges ELSE 0 END)  AS monthly_revenue_lost,
    COUNT(CASE WHEN cs.churn = 'Yes' THEN 1 END)                        AS churned_customers,
    ROUND(
        AVG(CASE WHEN cs.churn = 'Yes' THEN a.monthly_charges END), 2
    )                                                                    AS avg_charge_per_churned_customer
FROM accounts a
JOIN churn_status cs ON a.customer_id = cs.customer_id;


-- ────────────────────────────────────────────────────────────
-- QUERY 8: Churn Rate for Early-Tenure Customers with No Tech Support
-- Business Question: Are new customers without tech support a high-risk group?
-- Justifies offering free/discounted tech support to new customers in first 6 months.
-- ────────────────────────────────────────────────────────────
SELECT
    COUNT(*)                                               AS total_customers,
    SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END)     AS churned,
    ROUND(
        100.0 * SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                      AS churn_rate_pct
FROM customers c
JOIN services s   ON c.customer_id = s.customer_id
JOIN churn_status cs ON c.customer_id = cs.customer_id
WHERE c.tenure <= 6
  AND s.tech_support = 'No';


-- ────────────────────────────────────────────────────────────
-- QUERY 9: Churn Rate vs. Number of Subscribed Add-on Services (JOIN across tables)
-- Business Question: Do customers with more add-ons churn less?
-- Tests whether service bundling is a retention strategy worth investing in.
-- ────────────────────────────────────────────────────────────
SELECT
    (
        (CASE WHEN s.online_security   = 'Yes' THEN 1 ELSE 0 END) +
        (CASE WHEN s.online_backup     = 'Yes' THEN 1 ELSE 0 END) +
        (CASE WHEN s.device_protection = 'Yes' THEN 1 ELSE 0 END) +
        (CASE WHEN s.tech_support      = 'Yes' THEN 1 ELSE 0 END) +
        (CASE WHEN s.streaming_tv      = 'Yes' THEN 1 ELSE 0 END) +
        (CASE WHEN s.streaming_movies  = 'Yes' THEN 1 ELSE 0 END)
    )                                                             AS num_addons,
    COUNT(*)                                                      AS total_customers,
    SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END)            AS churned,
    ROUND(
        100.0 * SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                             AS churn_rate_pct
FROM services s
JOIN churn_status cs ON s.customer_id = cs.customer_id
GROUP BY num_addons
ORDER BY num_addons;


-- ────────────────────────────────────────────────────────────
-- QUERY 10: Churn Rate by Payment Method
-- Business Question: Does how customers pay affect their likelihood to churn?
-- Manual/paper check payers often indicate lower commitment or lower tech engagement.
-- ────────────────────────────────────────────────────────────
SELECT
    a.payment_method,
    COUNT(*)                                               AS total_customers,
    SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END)     AS churned,
    ROUND(
        100.0 * SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                      AS churn_rate_pct
FROM accounts a
JOIN churn_status cs ON a.customer_id = cs.customer_id
GROUP BY a.payment_method
ORDER BY churn_rate_pct DESC;


-- ────────────────────────────────────────────────────────────
-- QUERY 11: Churn Rate by Senior Citizen Status
-- Business Question: Do senior citizens churn at a different rate?
-- Helps design targeted loyalty programs for vulnerable demographics.
-- ────────────────────────────────────────────────────────────
SELECT
    CASE WHEN c.senior_citizen = 1 THEN 'Senior' ELSE 'Non-Senior' END  AS customer_type,
    COUNT(*)                                                              AS total_customers,
    SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END)                    AS churned,
    ROUND(
        100.0 * SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                                     AS churn_rate_pct
FROM customers c
JOIN churn_status cs ON c.customer_id = cs.customer_id
GROUP BY c.senior_citizen;


-- ────────────────────────────────────────────────────────────
-- QUERY 12: Churn Rate by Paperless Billing Enrollment
-- Business Question: Does paperless billing correlate with churn?
-- Helps understand whether digital customers behave differently.
-- ────────────────────────────────────────────────────────────
SELECT
    a.paperless_billing,
    COUNT(*)                                               AS total_customers,
    SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END)     AS churned,
    ROUND(
        100.0 * SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                      AS churn_rate_pct
FROM accounts a
JOIN churn_status cs ON a.customer_id = cs.customer_id
GROUP BY a.paperless_billing;


-- ────────────────────────────────────────────────────────────
-- QUERY 13: Full At-Risk Customer Profile (High-Risk Segment Deep Dive)
-- Business Question: Who exactly are our most at-risk customers right now?
-- Returns actual customer IDs the retention team can act on immediately.
-- Criteria: Month-to-month + Fiber optic + No tech support + tenure < 12
-- ────────────────────────────────────────────────────────────
SELECT
    c.customer_id,
    c.tenure,
    a.contract,
    a.monthly_charges,
    a.payment_method,
    s.internet_service,
    s.tech_support,
    cs.churn
FROM customers c
JOIN accounts a      ON c.customer_id = a.customer_id
JOIN services s      ON c.customer_id = s.customer_id
JOIN churn_status cs ON c.customer_id = cs.customer_id
WHERE a.contract        = 'Month-to-month'
  AND s.internet_service = 'Fiber optic'
  AND s.tech_support     = 'No'
  AND c.tenure          < 12
ORDER BY a.monthly_charges DESC
LIMIT 20;


-- ────────────────────────────────────────────────────────────
-- QUERY 14: Churn Rate by Tenure Bucket (0-6, 7-24, 25-48, 49-72 months)
-- Business Question: At what stage of customer life does churn peak?
-- Defines exactly when retention offers should be triggered.
-- ────────────────────────────────────────────────────────────
SELECT
    CASE
        WHEN c.tenure BETWEEN 0  AND 6  THEN '0-6 months (New)'
        WHEN c.tenure BETWEEN 7  AND 24 THEN '7-24 months (Growing)'
        WHEN c.tenure BETWEEN 25 AND 48 THEN '25-48 months (Established)'
        ELSE '49+ months (Loyal)'
    END                                                     AS tenure_group,
    COUNT(*)                                                AS total_customers,
    SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END)      AS churned,
    ROUND(
        100.0 * SUM(CASE WHEN cs.churn = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2
    )                                                       AS churn_rate_pct
FROM customers c
JOIN churn_status cs ON c.customer_id = cs.customer_id
GROUP BY tenure_group
ORDER BY churn_rate_pct DESC;
