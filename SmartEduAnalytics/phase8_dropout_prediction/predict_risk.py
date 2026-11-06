"""
SmartEdu Analytics - Phase 8: Batch Dropout Risk Scoring & Database Persistence
File: predict_risk.py
Description:
    Loads champion machine learning model and scaler, computes calibrated
    dropout probabilities across all 4,424 enrolled students, assigns
    risk tiers (Low, Medium, High Risk), diagnoses primary risk drivers,
    exports predictions to CSV, and persists results into MySQL/SQLite table:
    dropout_predictions.
"""

import os
import sys
import joblib
import pandas as pd
import numpy as np
from datetime import datetime

# Reference config from Phase 5
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(os.path.join(PROJECT_ROOT, "phase5_mysql"))
from config import get_mysql_connection

from data_preprocessing import FEATURE_COLS, MODELS_DIR

PREDICTIONS_DIR = os.path.join(PROJECT_ROOT, "dataset", "analytics", "predictions")
DATA_PATH = os.path.join(PROJECT_ROOT, "dataset", "processed", "preprocessed_student_data.csv")

def identify_primary_risk_factors(row):
    """
    Evaluates key indicators to provide an interpretable diagnosis of
    student academic and socio-economic distress.
    """
    factors = []
    if row.get("annual_grade_avg", 0) < 10.0:
        factors.append("Critically low cumulative grade (<10.0/20)")
    elif row.get("annual_grade_avg", 0) < 12.0:
        factors.append("Sub-optimal academic marks (<12.0/20)")

    if row.get("sem1_approval_rate", 1.0) < 0.50:
        factors.append("High course failure rate in Sem 1 (<50% units approved)")
    if row.get("sem2_approval_rate", 1.0) < 0.50:
        factors.append("High course failure rate in Sem 2 (<50% units approved)")

    if row.get("total_units_failed", 0) >= 3:
        factors.append(f"Accumulated {int(row['total_units_failed'])} failed course units")

    if row.get("tuition_fees_up_to_date", 1) == 0 or row.get("is_debtor", 0) == 1:
        factors.append("Tuition fee arrears / outstanding financial debt")

    if row.get("grade_trajectory", 0) < -1.5:
        factors.append("Sharply declining semester grade trajectory")

    if row.get("daytime_evening_attendance", 1) == 0:
        factors.append("Evening shift schedule attendance challenge")

    if not factors:
        if row.get("admission_grade", 0) < 110.0:
            factors.append("Low incoming admission qualification score")
        else:
            factors.append("Satisfactory academic progress; minimal attrition risk factors")

    return "; ".join(factors[:3])

def run_risk_prediction_pipeline():
    print("=" * 80)
    print(" SmartEdu Analytics - Phase 8: Batch Student Dropout Risk Scoring")
    print("=" * 80)

    os.makedirs(PREDICTIONS_DIR, exist_ok=True)

    # 1. Load Model and Scaler
    model_path = os.path.join(MODELS_DIR, "model.joblib")
    scaler_path = os.path.join(MODELS_DIR, "scaler.joblib")
    meta_path = os.path.join(MODELS_DIR, "model_meta.joblib")

    if not os.path.exists(model_path) or not os.path.exists(scaler_path):
        raise FileNotFoundError("Trained model or scaler not found. Run train_model.py first.")

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
    meta = joblib.load(meta_path) if os.path.exists(meta_path) else {"best_model_name": type(model).__name__}
    model_name = meta.get("best_model_name", "Random Forest")

    print(f"[MODEL LOADED] {model_name}")

    # 2. Load Student Records
    df = pd.read_csv(DATA_PATH)
    print(f"[DATA LOADED] {len(df):,} student records loaded for risk scoring.")

    # 3. Transform and Predict
    X = df[FEATURE_COLS].copy()
    X_scaled = scaler.transform(X)

    probabilities = model.predict_proba(X_scaled)[:, 1]
    
    # Risk Tier assignment
    # Low Risk: < 0.35 | Medium Risk: 0.35 - 0.699 | High Risk: >= 0.70
    risk_tiers = []
    for prob in probabilities:
        if prob >= 0.70:
            risk_tiers.append("High Risk")
        elif prob >= 0.35:
            risk_tiers.append("Medium Risk")
        else:
            risk_tiers.append("Low Risk")

    df_preds = pd.DataFrame({
        "student_id": df["student_id"],
        "course_id": df["course_id"],
        "annual_grade_avg": df["annual_grade_avg"],
        "total_units_failed": df["total_units_failed"],
        "tuition_fees_up_to_date": df["tuition_fees_up_to_date"],
        "is_debtor": df["is_debtor"],
        "actual_is_dropout": df["is_dropout"],
        "dropout_probability": np.round(probabilities, 4),
        "risk_tier": risk_tiers,
        "model_name": model_name,
        "predicted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    # Add diagnostic factors
    print("[DIAGNOSTICS] Deriving primary academic and socio-economic risk factors...")
    primary_factors = []
    for idx, row in df.iterrows():
        primary_factors.append(identify_primary_risk_factors(row))
    df_preds["primary_risk_factors"] = primary_factors

    # Distribution summary
    tier_counts = df_preds["risk_tier"].value_counts()
    print("\n[RISK TIER DISTRIBUTION]:")
    for tier, count in tier_counts.items():
        pct = (count / len(df_preds)) * 100
        print(f" -> {tier:<12}: {count:>5,} students ({pct:>5.1f}%)")

    # Save to CSV
    csv_out = os.path.join(PREDICTIONS_DIR, "dropout_risk_predictions.csv")
    df_preds.to_csv(csv_out, index=False)
    print(f"\n[SAVED CSV] Exported predictions table to: {csv_out}")

    # 4. Persist to MySQL / SQLite Database
    persist_predictions_to_db(df_preds)

    return df_preds

def persist_predictions_to_db(df_preds):
    print("\n[DATABASE INTEGRATION] Persisting risk predictions to database...")
    conn, is_fallback = get_mysql_connection()
    cursor = conn.cursor()

    db_type = "SQLite Fallback" if is_fallback else "MySQL 8.0"
    print(f" -> Active connection: {db_type}")

    # Create table if not exists
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS dropout_predictions (
        student_id VARCHAR(50) PRIMARY KEY,
        dropout_probability DOUBLE,
        risk_tier VARCHAR(30),
        model_name VARCHAR(100),
        primary_risk_factors TEXT,
        predicted_at VARCHAR(30)
    );
    """
    cursor.execute(create_table_sql)

    # Insert or Replace records
    if is_fallback:
        insert_sql = """
        INSERT OR REPLACE INTO dropout_predictions 
        (student_id, dropout_probability, risk_tier, model_name, primary_risk_factors, predicted_at)
        VALUES (?, ?, ?, ?, ?, ?);
        """
    else:
        insert_sql = """
        INSERT INTO dropout_predictions 
        (student_id, dropout_probability, risk_tier, model_name, primary_risk_factors, predicted_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
            dropout_probability=VALUES(dropout_probability),
            risk_tier=VALUES(risk_tier),
            model_name=VALUES(model_name),
            primary_risk_factors=VALUES(primary_risk_factors),
            predicted_at=VALUES(predicted_at);
        """

    records = [
        (
            str(row["student_id"]),
            float(row["dropout_probability"]),
            str(row["risk_tier"]),
            str(row["model_name"]),
            str(row["primary_risk_factors"]),
            str(row["predicted_at"])
        )
        for _, row in df_preds.iterrows()
    ]

    cursor.executemany(insert_sql, records)
    conn.commit()
    cursor.close()
    conn.close()
    print(f" -> Successfully committed {len(records):,} student risk predictions into 'dropout_predictions' table.")

if __name__ == "__main__":
    run_risk_prediction_pipeline()
