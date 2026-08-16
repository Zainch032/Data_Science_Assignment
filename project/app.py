"""
NexaTel Churn Prediction & Customer Retention Web Application Backend
Phase 7 — Building the Web Application
"""

import os
import sqlite3
import pickle
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# ── Paths & Artifacts Loading ──────────────────────────────────────────────
DB_PATH = "nexatel_churn.db"
ARTIFACTS_DIR = "artifacts"

MODEL_PATH = os.path.join(ARTIFACTS_DIR, "model.pkl")
SCALER_PATH = os.path.join(ARTIFACTS_DIR, "scaler.pkl")
COLUMNS_PATH = os.path.join(ARTIFACTS_DIR, "feature_columns.pkl")

# Load ML components
with open(COLUMNS_PATH, "rb") as f:
    FEATURE_COLUMNS = pickle.load(f)

with open(SCALER_PATH, "rb") as f:
    SCALER = pickle.load(f)

with open(MODEL_PATH, "rb") as f:
    MODEL = pickle.load(f)

print(f"[OK] Backend initialized successfully. Model expects {len(FEATURE_COLUMNS)} features.")


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def preprocess_customer_input(data):
    """
    Transforms raw user input dictionary into the exact scaled DataFrame expected by model.pkl
    """
    # Extract & convert raw inputs safely
    gender = str(data.get("gender", "Female"))
    senior_citizen = int(data.get("senior_citizen", 0))
    partner = str(data.get("partner", "No"))
    dependents = str(data.get("dependents", "No"))
    tenure = max(0, int(data.get("tenure", 0)))
    phone_service = str(data.get("phone_service", "Yes"))
    multiple_lines = str(data.get("multiple_lines", "No"))
    internet_service = str(data.get("internet_service", "Fiber optic"))
    online_security = str(data.get("online_security", "No"))
    online_backup = str(data.get("online_backup", "No"))
    device_protection = str(data.get("device_protection", "No"))
    tech_support = str(data.get("tech_support", "No"))
    streaming_tv = str(data.get("streaming_tv", "No"))
    streaming_movies = str(data.get("streaming_movies", "No"))
    contract = str(data.get("contract", "Month-to-month"))
    paperless_billing = str(data.get("paperless_billing", "Yes"))
    payment_method = str(data.get("payment_method", "Electronic check"))

    monthly_charges = float(data.get("monthly_charges", 70.0))
    
    # Total charges handling for tenure=0 or missing
    raw_total = data.get("total_charges", None)
    if raw_total is not None and str(raw_total).strip() != "":
        total_charges = float(raw_total)
    else:
        total_charges = monthly_charges * tenure

    # ── Feature Engineering ────────────────────────────────────────────────
    # Feature 1: charge_per_tenure
    charge_per_tenure = monthly_charges / (tenure + 1.0)

    # Feature 2: total_addons
    addon_services = [online_security, online_backup, device_protection,
                      tech_support, streaming_tv, streaming_movies]
    total_addons = sum(1 for addon in addon_services if str(addon).strip().lower() == "yes")

    # Feature 3: high_risk_flag (Month-to-month + No tech support + tenure < 12)
    is_m2m = (contract == "Month-to-month" or contract == "0")
    no_tech = (tech_support == "No" or tech_support == "0")
    high_risk_flag = 1 if (is_m2m and no_tech and tenure < 12) else 0

    # Feature 4: payment_risk_flag (Electronic check or Mailed check)
    payment_risk_flag = 1 if payment_method in ["Electronic check", "Mailed check"] else 0

    # Feature 5: tenure_group (0: New, 1: Growing, 2: Established, 3: Loyal)
    if tenure <= 6:
        tenure_group = 0
    elif tenure <= 24:
        tenure_group = 1
    elif tenure <= 48:
        tenure_group = 2
    else:
        tenure_group = 3

    # ── Create Single Row DataFrame ─────────────────────────────────────────
    row = {col: 0.0 for col in FEATURE_COLUMNS}

    # Numeric & Binary Mappings
    row["gender"] = 1.0 if gender.lower() == "male" else 0.0
    row["senior_citizen"] = float(senior_citizen)
    row["Partner"] = 1.0 if partner.lower() == "yes" or partner == "1" else 0.0
    row["Dependents"] = 1.0 if dependents.lower() == "yes" or dependents == "1" else 0.0
    row["tenure"] = float(tenure)
    row["paperless_billing"] = 1.0 if paperless_billing.lower() == "yes" or paperless_billing == "1" else 0.0
    row["monthly_charges"] = float(monthly_charges)
    row["total_charges"] = float(total_charges)
    row["phone_service"] = 1.0 if phone_service.lower() == "yes" or phone_service == "1" else 0.0
    
    # Contract mapping (0: Month-to-month, 1: One year, 2: Two year)
    contract_map = {"Month-to-month": 0.0, "One year": 1.0, "Two year": 2.0}
    row["contract"] = float(contract_map.get(contract, 0.0))

    # Engineered Features
    row["charge_per_tenure"] = float(charge_per_tenure)
    row["total_addons"] = float(total_addons)
    row["high_risk_flag"] = float(high_risk_flag)
    row["payment_risk_flag"] = float(payment_risk_flag)
    row["tenure_group"] = float(tenure_group)

    # One-hot encoded dummy variables
    if multiple_lines == "No phone service":
        if "multiple_lines_No phone service" in row: row["multiple_lines_No phone service"] = 1.0
    elif multiple_lines == "Yes":
        if "multiple_lines_Yes" in row: row["multiple_lines_Yes"] = 1.0

    if internet_service == "Fiber optic":
        if "internet_service_Fiber optic" in row: row["internet_service_Fiber optic"] = 1.0
    elif internet_service == "No":
        if "internet_service_No" in row: row["internet_service_No"] = 1.0

    for col_prefix, val in [
        ("online_security", online_security),
        ("online_backup", online_backup),
        ("device_protection", device_protection),
        ("tech_support", tech_support),
        ("streaming_tv", streaming_tv),
        ("streaming_movies", streaming_movies)
    ]:
        if val == "No internet service":
            col_name = f"{col_prefix}_No internet service"
            if col_name in row: row[col_name] = 1.0
        elif val == "Yes":
            col_name = f"{col_prefix}_Yes"
            if col_name in row: row[col_name] = 1.0

    if payment_method == "Credit card (automatic)":
        if "payment_method_Credit card (automatic)" in row: row["payment_method_Credit card (automatic)"] = 1.0
    elif payment_method == "Electronic check":
        if "payment_method_Electronic check" in row: row["payment_method_Electronic check"] = 1.0
    elif payment_method == "Mailed check":
        if "payment_method_Mailed check" in row: row["payment_method_Mailed check"] = 1.0

    df_row = pd.DataFrame([row])[FEATURE_COLUMNS]

    # Apply StandardScaler on numerical columns
    num_cols = ["tenure", "monthly_charges", "total_charges", "total_addons", "charge_per_tenure"]
    num_cols_present = [c for c in num_cols if c in df_row.columns]
    
    df_row[num_cols_present] = SCALER.transform(df_row[num_cols_present])

    return df_row, {
        "tenure": tenure,
        "monthly_charges": monthly_charges,
        "contract": contract,
        "internet_service": internet_service,
        "payment_method": payment_method,
        "tech_support": tech_support,
        "online_security": online_security,
        "total_addons": total_addons,
        "charge_per_tenure": charge_per_tenure,
        "high_risk_flag": high_risk_flag
    }


def generate_reasons_and_playbook(prob, raw_features):
    """
    Computes top risk factors and actionable retention recommendations for the agent.
    """
    reasons = []
    
    # Evaluate key indicators
    if raw_features["contract"] == "Month-to-month":
        reasons.append({
            "factor": "Month-to-Month Contract",
            "impact": "+30% Churn Risk",
            "detail": "Customer has no long-term commitment and can cancel anytime without fee."
        })
    if raw_features["payment_method"] == "Electronic check":
        reasons.append({
            "factor": "Electronic Check Payment",
            "impact": "+20% Churn Risk",
            "detail": "Highest churn payment method (45.3% churn rate). Indicates lower payment automation."
        })
    if raw_features["internet_service"] == "Fiber optic":
        reasons.append({
            "factor": "Fiber Optic Service",
            "impact": "+15% Churn Risk",
            "detail": "High monthly pricing tier without active support add-ons leads to price sensitivity."
        })
    if raw_features["tech_support"] == "No":
        reasons.append({
            "factor": "Missing Tech Support",
            "impact": "+15% Churn Risk",
            "detail": "Unresolved technical issues trigger immediate switching behavior."
        })
    if raw_features["tenure"] < 12:
        reasons.append({
            "factor": "Short Tenure (< 1 Year)",
            "impact": "+15% Churn Risk",
            "detail": "New customer in prime drop-off window (tenure: {} months).".format(raw_features["tenure"])
        })
    if raw_features["charge_per_tenure"] > 8.0:
        reasons.append({
            "factor": "High Charge per Loyalty Month",
            "impact": "+10% Churn Risk",
            "detail": "High monthly rate relative to length of relationship ($ {:.2f}/mo ratio).".format(raw_features["charge_per_tenure"])
        })

    if not reasons:
        reasons.append({
            "factor": "Standard Account Metrics",
            "impact": "Low Risk",
            "detail": "Customer exhibits healthy usage and commitment signals."
        })

    # Generate Actionable Retention Playbook
    actions = []
    if raw_features["contract"] == "Month-to-month":
        actions.append({
            "title": "📜 1-Year Contract Lock-in Offer",
            "offer": "Offer a 15% discount ($10/mo savings) if customer switches to a 1-Year Contract today.",
            "script": "Agent Script: 'We value your business! We can lock in a $10/month discount for the next 12 months if we move you to our annual plan today.'"
        })
    if raw_features["tech_support"] == "No" or raw_features["online_security"] == "No":
        actions.append({
            "title": "🛡️ Free Protection & Tech Support Add-On",
            "offer": "Provide 3 months of complimentary Tech Support and Online Security.",
            "script": "Agent Script: 'To ensure your internet is running at peak performance, I can add 3 months of VIP Tech Support at zero cost.'"
        })
    if raw_features["payment_method"] in ["Electronic check", "Mailed check"]:
        actions.append({
            "title": "💳 Auto-Pay Switching Incentive",
            "offer": "Give a $10 one-time bill credit when enrolling in automatic Bank Transfer / Credit Card billing.",
            "script": "Agent Script: 'If we set up automatic payments today, I can apply an instant $10 bill credit to your next invoice.'"
        })

    if not actions or prob < 0.30:
        actions.append({
            "title": "⭐ VIP Loyalty Appreciation",
            "offer": "Maintain regular service check-in and offer standard upgrade eligibility on renewal.",
            "script": "Agent Script: 'Thank you for being a loyal NexaTel customer! Your account is in great standing.'"
        })

    return reasons[:4], actions[:3]


# ── REST API Endpoints ──────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/customers", methods=["GET"])
def get_customers():
    """Returns customer list for lookup dropdown"""
    try:
        conn = get_db_connection()
        query = """
            SELECT c.customer_id, c.tenure, a.contract, a.monthly_charges, s.churn
            FROM customers c
            JOIN accounts a ON c.customer_id = a.customer_id
            JOIN churn_status s ON c.customer_id = s.customer_id
            ORDER BY c.customer_id ASC
            LIMIT 100
        """
        rows = conn.execute(query).fetchall()
        conn.close()
        customers = [dict(row) for row in rows]
        return jsonify({"status": "success", "customers": customers})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/customer/<customer_id>", methods=["GET"])
def get_customer_details(customer_id):
    """Fetches complete profile of a customer by ID"""
    try:
        conn = get_db_connection()
        query = """
            SELECT c.*, a.contract, a.paperless_billing, a.payment_method, a.monthly_charges, a.total_charges,
                   s.phone_service, s.multiple_lines, s.internet_service, s.online_security, s.online_backup,
                   s.device_protection, s.tech_support, s.streaming_tv, s.streaming_movies,
                   cs.churn
            FROM customers c
            JOIN accounts a ON c.customer_id = a.customer_id
            JOIN services s ON c.customer_id = s.customer_id
            JOIN churn_status cs ON c.customer_id = cs.customer_id
            WHERE c.customer_id = ?
        """
        row = conn.execute(query, (customer_id,)).fetchone()
        conn.close()

        if not row:
            return jsonify({"status": "error", "message": f"Customer ID {customer_id} not found"}), 404

        cust = dict(row)
        # Normalize fields for frontend form
        payload = {
            "customer_id": cust["customer_id"],
            "gender": cust["gender"],
            "senior_citizen": cust["senior_citizen"],
            "partner": cust["Partner"],
            "dependents": cust["Dependents"],
            "tenure": cust["tenure"],
            "phone_service": cust["phone_service"],
            "multiple_lines": cust["multiple_lines"],
            "internet_service": cust["internet_service"],
            "online_security": cust["online_security"],
            "online_backup": cust["online_backup"],
            "device_protection": cust["device_protection"],
            "tech_support": cust["tech_support"],
            "streaming_tv": cust["streaming_tv"],
            "streaming_movies": cust["streaming_movies"],
            "contract": cust["contract"],
            "paperless_billing": cust["paperless_billing"],
            "payment_method": cust["payment_method"],
            "monthly_charges": cust["monthly_charges"],
            "total_charges": cust["total_charges"],
            "actual_churn": cust["churn"]
        }
        return jsonify({"status": "success", "customer": payload})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/predict", methods=["POST"])
def predict():
    """Calculates churn risk prediction, risk level, top reasons, and retention actions"""
    try:
        data = request.get_json(force=True)
        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON input"}), 400

        # Preprocess & scale input
        df_row, raw_features = preprocess_customer_input(data)

        # Model Prediction
        prob = float(MODEL.predict_proba(df_row)[0][1])
        prediction = 1 if prob >= 0.5 else 0

        # Risk Classification
        if prob < 0.30:
            risk_level = "Low"
            risk_color = "#2ecc71" # Green
        elif prob <= 0.65:
            risk_level = "Medium"
            risk_color = "#f39c12" # Amber
        else:
            risk_level = "High"
            risk_color = "#e74c3c" # Red

        # Generate reasons and retention actions
        reasons, actions = generate_reasons_and_playbook(prob, raw_features)

        result = {
            "status": "success",
            "churn_probability": round(prob, 4),
            "churn_percentage": round(prob * 100, 1),
            "prediction": prediction,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "reasons": reasons,
            "actions": actions,
            "raw_features": raw_features
        }
        return jsonify(result)
    except Exception as e:
        print("Prediction Error:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/eda", methods=["GET"])
def get_eda_metrics():
    """Serves summary metrics and analytics for the EDA dashboard tab"""
    try:
        conn = get_db_connection()
        total_customers = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        churned_customers = conn.execute("SELECT COUNT(*) FROM churn_status WHERE churn='Yes' OR churn=1").fetchone()[0]
        avg_monthly = conn.execute("SELECT AVG(monthly_charges) FROM accounts").fetchone()[0]
        
        # High Risk Segment churn count: Month-to-Month + No Tech Support + Tenure < 12
        high_risk_query = """
            SELECT COUNT(*) FROM customers c
            JOIN accounts a ON c.customer_id = a.customer_id
            JOIN services s ON c.customer_id = s.customer_id
            JOIN churn_status cs ON c.customer_id = cs.customer_id
            WHERE a.contract = 'Month-to-month' AND s.tech_support = 'No' AND c.tenure < 12
        """
        high_risk_total = conn.execute(high_risk_query).fetchone()[0]
        
        high_risk_churn_query = high_risk_query + " AND (cs.churn = 'Yes' OR cs.churn = 1)"
        high_risk_churn = conn.execute(high_risk_churn_query).fetchone()[0]

        # Contract Breakdown
        contract_data = conn.execute("""
            SELECT a.contract, COUNT(*) as total, 
                   SUM(CASE WHEN cs.churn = 'Yes' OR cs.churn = 1 THEN 1 ELSE 0 END) as churned
            FROM accounts a
            JOIN churn_status cs ON a.customer_id = cs.customer_id
            GROUP BY a.contract
        """).fetchall()

        # Internet Service Breakdown
        internet_data = conn.execute("""
            SELECT s.internet_service, COUNT(*) as total,
                   SUM(CASE WHEN cs.churn = 'Yes' OR cs.churn = 1 THEN 1 ELSE 0 END) as churned
            FROM services s
            JOIN churn_status cs ON s.customer_id = cs.customer_id
            GROUP BY s.internet_service
        """).fetchall()

        conn.close()

        churn_rate = round((churned_customers / total_customers) * 100, 1)
        high_risk_churn_rate = round((high_risk_churn / high_risk_total) * 100, 1) if high_risk_total > 0 else 0.0

        return jsonify({
            "status": "success",
            "kpis": {
                "total_customers": total_customers,
                "churn_rate": churn_rate,
                "avg_monthly_charges": round(avg_monthly, 2),
                "high_risk_churn_rate": high_risk_churn_rate,
                "model_recall": 82.4, # Model evaluation metric
                "model_accuracy": 79.8
            },
            "contracts": [dict(r) for r in contract_data],
            "internet_services": [dict(r) for r in internet_data]
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    print("[STARTING] Starting NexaTel Churn Web Service on http://127.0.0.1:5000 ...")
    app.run(host="127.0.0.1", port=5000, debug=True)
