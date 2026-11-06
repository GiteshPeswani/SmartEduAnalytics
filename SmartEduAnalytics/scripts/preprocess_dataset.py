"""
SmartEdu Analytics - Phase 1: Data Preprocessing & Risk Preparation
Script: preprocess_dataset.py
Description:
    Implements feature engineering, encoding, normalization, and train-test splitting:
    1. Feature Engineering:
       - 'sem1_approval_rate': sem1_units_approved / (sem1_units_enrolled + 1e-5)
       - 'sem2_approval_rate': sem2_units_approved / (sem2_units_enrolled + 1e-5)
       - 'annual_grade_avg': (sem1_grade + sem2_grade) / 2
       - 'grade_trajectory': sem2_grade - sem1_grade (measuring academic momentum)
       - 'academic_performance_risk_score': composite academic struggle score [0.0 - 1.0]
       - 'academic_risk_category': 'Low', 'Moderate', 'High'
    2. Target Classification & Dropout Outcome:
       - 'is_dropout': Binary ground-truth target (1 = Dropout, 0 = Graduate / Enrolled)
       - 'target_multi_class': Label-encoded multi-class outcome (0=Dropout, 1=Enrolled, 2=Graduate)
    3. Stratified Train-Test Split (80% Train, 20% Test):
       - Eliminates data leakage by fitting scalers strictly on training data
    4. Feature Scaling:
       - Applies StandardScaler to continuous numerical features
    5. Exports:
       - 'dataset/processed/preprocessed_student_data.csv' (Full preprocessed dataset)
       - 'dataset/processed/train_data.csv' (Train split)
       - 'dataset/processed/test_data.csv' (Test split)
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CLEANED_DATA_PATH = os.path.join(PROJECT_ROOT, "dataset", "processed", "cleaned_student_data.csv")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "dataset", "processed")

FULL_PREPROCESSED_PATH = os.path.join(PROCESSED_DIR, "preprocessed_student_data.csv")
TRAIN_PATH = os.path.join(PROCESSED_DIR, "train_data.csv")
TEST_PATH = os.path.join(PROCESSED_DIR, "test_data.csv")

def preprocess_pipeline():
    if not os.path.exists(CLEANED_DATA_PATH):
        raise FileNotFoundError(f"Cleaned data not found at {CLEANED_DATA_PATH}. Run clean_dataset.py first.")
        
    print("\n" + "=" * 80)
    print(" SmartEdu Analytics - Task 4 & 5: Preprocessing & Dropout Risk Preparation")
    print("=" * 80)
    
    df = pd.read_csv(CLEANED_DATA_PATH)
    print(f"[INFO] Loaded cleaned dataset: {df.shape[0]:,} rows, {df.shape[1]} columns")
    
    # --- Feature Engineering ---
    print("\n[FEATURE ENGINEERING] Constructing academic performance & progression indicators:")
    
    # 1. Approval Rates
    df['sem1_approval_rate'] = (df['sem1_units_approved'] / np.maximum(df['sem1_units_enrolled'], 1)).clip(0.0, 1.0)
    df['sem2_approval_rate'] = (df['sem2_units_approved'] / np.maximum(df['sem2_units_enrolled'], 1)).clip(0.0, 1.0)
    
    # 2. Grade Averages & Trajectory (Momentum)
    df['annual_grade_avg'] = (df['sem1_grade'] + df['sem2_grade']) / 2.0
    df['grade_trajectory'] = df['sem2_grade'] - df['sem1_grade']
    
    # 3. Academic Failure Count
    df['total_units_failed'] = (
        (df['sem1_units_enrolled'] - df['sem1_units_approved']).clip(lower=0) +
        (df['sem2_units_enrolled'] - df['sem2_units_approved']).clip(lower=0)
    )
    
    # 4. Derived Academic Performance Risk Score (0.0 to 1.0)
    # Note: Explicitly distinguished from official dropout status!
    # Derived composite formula based purely on academic non-completion and low grades:
    non_approval_factor = 1.0 - ((df['sem1_approval_rate'] + df['sem2_approval_rate']) / 2.0)
    low_grade_factor = (20.0 - df['annual_grade_avg']).clip(lower=0.0) / 20.0
    df['academic_risk_score'] = (0.6 * non_approval_factor + 0.4 * low_grade_factor).round(4)
    
    # Categorize risk score
    df['academic_risk_level'] = pd.cut(
        df['academic_risk_score'],
        bins=[-0.01, 0.35, 0.65, 1.0],
        labels=['Low_Risk', 'Moderate_Risk', 'High_Risk']
    )
    print(f" -> Generated 'academic_risk_score' and 'academic_risk_level'")
    print(df['academic_risk_level'].value_counts())
    
    # --- Target Preparation ---
    # Verified ground truth targets
    # Binary: Dropout (1) vs Non-Dropout (0: Graduate or Enrolled)
    df['is_dropout'] = (df['target_outcome'] == 'Dropout').astype(int)
    
    # Multi-class encoded: 0=Dropout, 1=Enrolled, 2=Graduate
    target_mapping = {'Dropout': 0, 'Enrolled': 1, 'Graduate': 2}
    df['target_multi_class'] = df['target_outcome'].map(target_mapping)
    
    print("\n[GROUND TRUTH TARGETS] Verified Target Distribution:")
    print(f" -> Binary 'is_dropout': {dict(df['is_dropout'].value_counts())} (1=Dropout, 0=Non-Dropout)")
    print(f" -> Multi-class: {dict(df['target_multi_class'].value_counts())}")
    
    # Save full preprocessed dataset before splitting
    df.to_csv(FULL_PREPROCESSED_PATH, index=False)
    print(f"\n[SAVED] Full preprocessed dataset saved to: {FULL_PREPROCESSED_PATH}")
    
    # --- Train-Test Split (80% Train, 20% Test) ---
    print("\n[SPLIT] Executing Stratified Train-Test Split (80% Train, 20% Test)...")
    train_df, test_df = train_test_split(
        df,
        test_size=0.20,
        random_state=42,
        stratify=df['target_outcome']
    )
    
    train_df = train_df.copy()
    test_df = test_df.copy()
    
    print(f" -> Training set : {len(train_df):,} records ({len(train_df)/len(df)*100:.1f}%)")
    print(f" -> Testing set  : {len(test_df):,} records ({len(test_df)/len(df)*100:.1f}%)")
    print(f" -> Train class balance: {dict(train_df['target_outcome'].value_counts())}")
    print(f" -> Test class balance : {dict(test_df['target_outcome'].value_counts())}")
    
    # --- Feature Scaling without Data Leakage ---
    numeric_features_to_scale = [
        'admission_grade',
        'previous_qualification_grade',
        'age_at_enrollment',
        'sem1_grade',
        'sem2_grade',
        'annual_grade_avg',
        'grade_trajectory',
        'unemployment_rate',
        'inflation_rate',
        'gdp'
    ]
    
    scaler = StandardScaler()
    # Fit scaler strictly on training split
    scaler.fit(train_df[numeric_features_to_scale])
    
    # Transform both splits and save scaled columns with prefix
    for col in numeric_features_to_scale:
        scaled_col_name = f"scaled_{col}"
        train_df[scaled_col_name] = scaler.transform(train_df[numeric_features_to_scale])[:, numeric_features_to_scale.index(col)]
        test_df[scaled_col_name] = scaler.transform(test_df[numeric_features_to_scale])[:, numeric_features_to_scale.index(col)]
        
    print(f"[SCALING] Standardized {len(numeric_features_to_scale)} numerical features (fitted on train split only).")
    
    # Save split datasets
    train_df.to_csv(TRAIN_PATH, index=False)
    test_df.to_csv(TEST_PATH, index=False)
    
    print(f"\n[SAVED] Training split exported to: {TRAIN_PATH}")
    print(f"[SAVED] Testing split exported to : {TEST_PATH}")
    print("=" * 80 + "\n")
    return df, train_df, test_df

if __name__ == "__main__":
    preprocess_pipeline()
