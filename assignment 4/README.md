# 📊 Customer Churn Prediction & Model Benchmarking

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An end-to-end Machine Learning and Data Science pipeline for predicting customer churn in telecommunications service plans. This repository provides data cleaning, feature engineering, exploratory data analysis (EDA), data scaling methodology, and systematic benchmark comparisons across six supervised classification algorithms.

---

## 📌 Key Features & Highlights

- **End-to-End Pipeline**: From raw, uncleaned telemetry data to deployed model metrics.
- **Feature Engineering**:
  - `Charge_per_Tenure`: Composite price-density ratio capturing customer cost sensitivity over time ($rac{	ext{MonthlyCharges}}{	ext{Tenure} + 1}$).
  - `TotalAddOns`: Numerical aggregation of optional subscriber add-on services (Online Security, Tech Support, Backup, etc.).
- **Data Leakage Protection**: Strict separation of training and testing distributions — standard scaling parameters are fitted exclusively on `X_train` and applied to `X_test`.
- **Model Benchmarking**: Automated evaluation framework comparing 6 baseline and ensemble classifiers across Accuracy, Precision, Recall, F1-Score, and ROC-AUC.

---

## 📈 Benchmark Results Summary

| Model Name | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** 🏆 | **0.806** | **0.658** | **0.534** | **0.589** | **0.846** |
| **Gradient Boosting** | 0.801 | 0.643 | 0.528 | 0.580 | 0.845 |
| **Support Vector Machine (SVM)** | 0.795 | 0.630 | 0.508 | 0.562 | 0.801 |
| **Random Forest** | 0.789 | 0.612 | 0.495 | 0.547 | 0.823 |
| **K-Nearest Neighbors (KNN)** | 0.768 | 0.552 | 0.480 | 0.513 | 0.742 |
| **Naive Bayes** ⚠️ | 0.692 | 0.448 | **0.831** | 0.583 | 0.828 |

> **Key takeaway**: **Logistic Regression** achieved the highest overall separation capability (ROC-AUC: `0.846`) and accuracy (`80.6%`). For maximum churn detection regardless of false positives, **Naive Bayes** offers the highest Recall (`83.1%`).

---

## 📁 Repository Structure

```text
.
├── Optimized_Churn_Analysis.ipynb     # Interactive Jupyter Notebook with complete EDA & models
├── Churn_Analysis_Documentation.docx  # Full 2.5-page project executive report
├── README.md                          # Project documentation & execution guide
└── requirements.txt                   # Python environment dependencies
```

---

## 🚀 Quick Start & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/customer-churn-prediction.git
cd customer-churn-prediction
```

### 2. Set Up Virtual Environment & Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scriptsctivate
pip install -r requirements.txt
```

### 3. Run the Jupyter Notebook
```bash
jupyter notebook Optimized_Churn_Analysis.ipynb
```

---

## 🛠️ Tech Stack & Dependencies

- **Language**: Python 3.8+
- **Data Manipulation**: `pandas`, `numpy`
- **Machine Learning**: `scikit-learn`
- **Visualization**: `matplotlib`, `seaborn`

---

## 💡 Business Impact & Insights

1. **Add-on Services Reduce Churn**: Subscribers with 0 add-on services exhibit a churn probability near **50%**. Onboarding customers with 1–2 key add-ons drops churn rates below **21%**.
2. **Cost Sensitivity in Early Tenure**: Customers experiencing high monthly charges relative to early tenure exhibit extreme churn risk (~12.0 ratio vs 3.6 baseline).

---

## 📜 License

This project is open-source and available under the [MIT License](LICENSE).
