"""
Test suite for NexaTel Churn Prediction Backend & API Endpoints
Phase 7 — Verification & Edge Case Testing
"""

import unittest
import json
from app import app


class TestNexaTelChurnApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_01_index_page(self):
        """Test homepage rendering"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'NexaTel', response.data)

    def test_02_customers_api(self):
        """Test customer database lookup endpoint"""
        response = self.app.get('/api/customers')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertTrue(len(data['customers']) > 0)
        print(f"[OK] Customer lookup returned {len(data['customers'])} customers.")

    def test_03_customer_details_api(self):
        """Test fetching a specific customer profile from DB"""
        customer_id = '7590-VHVEG'
        response = self.app.get(f'/api/customer/{customer_id}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['customer']['customer_id'], customer_id)
        print(f"[OK] Loaded customer details for {customer_id}: contract={data['customer']['contract']}, tenure={data['customer']['tenure']}m")

    def test_04_predict_high_risk_customer(self):
        """Test prediction for high-risk customer profile (Month-to-month, Fiber optic, No Tech Support)"""
        payload = {
            "gender": "Female",
            "senior_citizen": 0,
            "partner": "No",
            "dependents": "No",
            "tenure": 2,
            "contract": "Month-to-month",
            "monthly_charges": 89.50,
            "total_charges": 179.00,
            "payment_method": "Electronic check",
            "paperless_billing": "Yes",
            "phone_service": "Yes",
            "multiple_lines": "No",
            "internet_service": "Fiber optic",
            "online_security": "No",
            "online_backup": "No",
            "device_protection": "No",
            "tech_support": "No",
            "streaming_tv": "No",
            "streaming_movies": "No"
        }
        response = self.app.post('/predict', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('churn_probability', data)
        self.assertIn('risk_level', data)
        self.assertIn('reasons', data)
        self.assertIn('actions', data)
        print(f"[OK] High Risk Customer Test: Probability={data['churn_percentage']}%, Risk Level={data['risk_level']}")

    def test_05_predict_low_risk_customer(self):
        """Test prediction for low-risk loyal customer profile (Two year contract, DSL, Tech Support, Tenure 60m)"""
        payload = {
            "gender": "Male",
            "senior_citizen": 0,
            "partner": "Yes",
            "dependents": "Yes",
            "tenure": 60,
            "contract": "Two year",
            "monthly_charges": 45.00,
            "total_charges": 2700.00,
            "payment_method": "Bank transfer (automatic)",
            "paperless_billing": "No",
            "phone_service": "Yes",
            "multiple_lines": "Yes",
            "internet_service": "DSL",
            "online_security": "Yes",
            "online_backup": "Yes",
            "device_protection": "Yes",
            "tech_support": "Yes",
            "streaming_tv": "No",
            "streaming_movies": "No"
        }
        response = self.app.post('/predict', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['risk_level'], 'Low')
        print(f"[OK] Low Risk Customer Test: Probability={data['churn_percentage']}%, Risk Level={data['risk_level']}")

    def test_06_edge_case_tenure_zero(self):
        """Edge Case: Brand new customer with tenure = 0 and blank/zero total charges"""
        payload = {
            "gender": "Female",
            "senior_citizen": 0,
            "partner": "No",
            "dependents": "No",
            "tenure": 0,
            "contract": "Month-to-month",
            "monthly_charges": 20.00,
            "total_charges": 0.0,
            "payment_method": "Mailed check",
            "paperless_billing": "No",
            "phone_service": "Yes",
            "multiple_lines": "No",
            "internet_service": "No",
            "online_security": "No internet service",
            "online_backup": "No internet service",
            "device_protection": "No internet service",
            "tech_support": "No internet service",
            "streaming_tv": "No internet service",
            "streaming_movies": "No internet service"
        }
        response = self.app.post('/predict', data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        print(f"[OK] Tenure = 0 Edge Case Test: Probability={data['churn_percentage']}%, Risk Level={data['risk_level']}")

    def test_07_eda_metrics_api(self):
        """Test EDA metrics dashboard endpoint"""
        response = self.app.get('/api/eda')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['kpis']['total_customers'], 7043)
        print(f"[OK] EDA API Test: Total Customers={data['kpis']['total_customers']}, Churn Rate={data['kpis']['churn_rate']}%")


if __name__ == '__main__':
    unittest.main()
