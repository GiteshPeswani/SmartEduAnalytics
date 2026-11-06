"""
SmartEdu Analytics - Phase 8: Student Dropout Risk Prediction
File: data_preprocessing.py
Description:
    Loads preprocessed student dataset, performs feature selection,
    applies stratified train-test splitting (80/20), standardizes continuous
    attributes, and prepares train/test feature sets for model training.
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_PATH = os.path.join(PROJECT_ROOT, "dataset", "processed", "preprocessed_student_data.csv")
MODELS_DIR = os.path.join(SCRIPT_DIR, "models")

# Carefully curated features with high predictive power for academic attrition
FEATURE_COLS = [
    "admission_grade",
    "sem1_grade",
    "sem2_grade",
    "annual_grade_avg",
    "sem1_approval_rate",
    "sem2_approval_rate",
    "grade_trajectory",
    "sem1_units_enrolled",
    "sem1_units_approved",
    "sem1_units_evaluations",
    "sem2_units_enrolled",
    "sem2_units_approved",
    "sem2_units_evaluations",
    "total_units_failed",
    "tuition_fees_up_to_date",
    "is_debtor",
    "scholarship_holder",
    "daytime_evening_attendance",
    "age_at_enrollment",
    "gender",
    "is_displaced"
]

TARGET_COL = "is_dropout"

def load_and_preprocess_data(save_scaler=True):
    """
    Loads preprocessed dataset, extracts selected features, splits into train/test,
    fits StandardScaler on train partition, and returns processed partitions.
    """
    os.makedirs(MODELS_DIR, exist_ok=True)
    
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Processed dataset not found at: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    print(f"[DATA PREPROCESSING] Loaded dataset: {df.shape[0]:,} rows, {df.shape[1]} columns.")
    
    # Verify missing values
    missing_count = df[FEATURE_COLS + [TARGET_COL]].isnull().sum().sum()
    if missing_count > 0:
        print(f"[WARN] Imputing {missing_count} missing values with median values.")
        df[FEATURE_COLS] = df[FEATURE_COLS].fillna(df[FEATURE_COLS].median())

    X = df[FEATURE_COLS].copy()
    y = df[TARGET_COL].astype(int)

    # Class balance check
    dropout_count = y.sum()
    non_dropout_count = len(y) - dropout_count
    print(f"[CLASS DISTRIBUTION] Non-Dropout (0): {non_dropout_count:,} ({non_dropout_count/len(y)*100:.1f}%) | "
          f"Dropout (1): {dropout_count:,} ({dropout_count/len(y)*100:.1f}%)")

    # Stratified Train-Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"[SPLIT] Train samples: {len(X_train):,} | Test samples: {len(X_test):,}")

    # Standard Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    if save_scaler:
        scaler_path = os.path.join(MODELS_DIR, "scaler.joblib")
        joblib.dump(scaler, scaler_path)
        print(f"[SAVED] Feature scaler saved to: {scaler_path}")

    return {
        "df_full": df,
        "feature_cols": FEATURE_COLS,
        "target_col": TARGET_COL,
        "X_train": X_train,
        "X_test": X_test,
        "X_train_scaled": X_train_scaled,
        "X_test_scaled": X_test_scaled,
        "y_train": y_train,
        "y_test": y_test,
        "scaler": scaler
    }

if __name__ == "__main__":
    data = load_and_preprocess_data()
    print("[SUCCESS] Data preprocessing completed successfully.")
