-- ============================================================
-- NexaTel Communications - Customer Churn Database Schema
-- Normalized to 3rd Normal Form (3NF)
-- Author: Zain | Phase 1 - Database Design & SQL
-- ============================================================

-- Drop tables if they exist (for re-runs)
DROP TABLE IF EXISTS churn_status;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS customers;

-- ============================================================
-- TABLE 1: customers
-- Stores demographic information about each customer
-- ============================================================
CREATE TABLE customers (
    customer_id     TEXT PRIMARY KEY,
    gender          TEXT CHECK(gender IN ('Male', 'Female')),
    senior_citizen  INTEGER CHECK(senior_citizen IN (0, 1)),  -- 0=No, 1=Yes
    partner         TEXT CHECK(partner IN ('Yes', 'No')),
    dependents      TEXT CHECK(dependents IN ('Yes', 'No')),
    tenure          INTEGER CHECK(tenure >= 0)
);

-- ============================================================
-- TABLE 2: accounts
-- Stores billing and contract information per customer
-- ============================================================
CREATE TABLE accounts (
    customer_id         TEXT PRIMARY KEY,
    contract            TEXT CHECK(contract IN ('Month-to-month', 'One year', 'Two year')),
    paperless_billing   TEXT CHECK(paperless_billing IN ('Yes', 'No')),
    payment_method      TEXT,
    monthly_charges     REAL CHECK(monthly_charges >= 0),
    total_charges       REAL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- ============================================================
-- TABLE 3: services
-- Stores all subscribed services per customer
-- ============================================================
CREATE TABLE services (
    customer_id         TEXT PRIMARY KEY,
    phone_service       TEXT CHECK(phone_service IN ('Yes', 'No')),
    multiple_lines      TEXT,
    internet_service    TEXT CHECK(internet_service IN ('DSL', 'Fiber optic', 'No')),
    online_security     TEXT,
    online_backup       TEXT,
    device_protection   TEXT,
    tech_support        TEXT,
    streaming_tv        TEXT,
    streaming_movies    TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- ============================================================
-- TABLE 4: churn_status
-- Stores the target variable - whether customer churned
-- ============================================================
CREATE TABLE churn_status (
    customer_id     TEXT PRIMARY KEY,
    churn           TEXT CHECK(churn IN ('Yes', 'No')),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);
