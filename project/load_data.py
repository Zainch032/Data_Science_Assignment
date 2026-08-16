"""
NexaTel Churn Database - Data Loader
Reads the Telco CSV, splits into normalized tables, loads into SQLite
Phase 1 - Database Design & SQL
"""

import sqlite3
import pandas as pd
import os

# ── Config ──────────────────────────────────────────────────
CSV_PATH = "telco_churn.csv"
DB_PATH  = "nexatel_churn.db"

# ── Load & Clean CSV ─────────────────────────────────────────
print("Loading CSV...")
df = pd.read_csv(CSV_PATH)

# Fix TotalCharges: stored as string with blank entries (tenure=0 customers)
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df["TotalCharges"] = df["TotalCharges"].fillna(0.0)

print(f"  Rows: {len(df)} | Columns: {len(df.columns)}")
print(f"  TotalCharges nulls fixed: {df['TotalCharges'].isnull().sum()}")

# ── Connect to SQLite & Create Schema ────────────────────────
print(f"\nSetting up SQLite database: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Execute schema file
with open("schema.sql", "r") as f:
    schema_sql = f.read()
conn.executescript(schema_sql)
conn.commit()
print("  Schema created (4 tables)")

# ── Split CSV into Normalized Tables ─────────────────────────

# TABLE 1: customers
customers_df = df[[
    "customerID", "gender", "SeniorCitizen",
    "Partner", "Dependents", "tenure"
]].rename(columns={
    "customerID":    "customer_id",
    "SeniorCitizen": "senior_citizen"
})

# TABLE 2: accounts
accounts_df = df[[
    "customerID", "Contract", "PaperlessBilling",
    "PaymentMethod", "MonthlyCharges", "TotalCharges"
]].rename(columns={
    "customerID":       "customer_id",
    "Contract":         "contract",
    "PaperlessBilling": "paperless_billing",
    "PaymentMethod":    "payment_method",
    "MonthlyCharges":   "monthly_charges",
    "TotalCharges":     "total_charges"
})

# TABLE 3: services
services_df = df[[
    "customerID", "PhoneService", "MultipleLines", "InternetService",
    "OnlineSecurity", "OnlineBackup", "DeviceProtection",
    "TechSupport", "StreamingTV", "StreamingMovies"
]].rename(columns={
    "customerID":        "customer_id",
    "PhoneService":      "phone_service",
    "MultipleLines":     "multiple_lines",
    "InternetService":   "internet_service",
    "OnlineSecurity":    "online_security",
    "OnlineBackup":      "online_backup",
    "DeviceProtection":  "device_protection",
    "TechSupport":       "tech_support",
    "StreamingTV":       "streaming_tv",
    "StreamingMovies":   "streaming_movies"
})

# TABLE 4: churn_status
churn_df = df[["customerID", "Churn"]].rename(columns={
    "customerID": "customer_id",
    "Churn":      "churn"
})

# ── Load Into SQLite ─────────────────────────────────────────
print("\nLoading data into tables...")

customers_df.to_sql("customers",    conn, if_exists="replace", index=False)
accounts_df.to_sql("accounts",      conn, if_exists="replace", index=False)
services_df.to_sql("services",      conn, if_exists="replace", index=False)
churn_df.to_sql("churn_status",     conn, if_exists="replace", index=False)

conn.commit()

# ── Verify ───────────────────────────────────────────────────
print("\nVerification:")
for table in ["customers", "accounts", "services", "churn_status"]:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"  {table}: {count} rows")

conn.close()
print(f"\nDatabase ready: {DB_PATH}")
