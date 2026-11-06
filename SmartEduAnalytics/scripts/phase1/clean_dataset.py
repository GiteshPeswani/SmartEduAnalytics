"""
SmartEdu Analytics - Phase 1: Data Cleaning & Standardization
Script: clean_dataset.py
Description:
    Cleans and standardizes raw student data:
    1. Audits missing values, NaNs, and duplicates defensively.
    2. Strips formatting anomalies (e.g. trailing tabs in column headers).
    3. Standardizes column names into clean snake_case suitable for Big Data frameworks (Hive, HDFS, Spark).
    4. Generates an explicit unique primary key 'student_id' (STD_10001, STD_10002, ...) for distributed partitioning.
    5. Validates domain ranges:
       - Semester grades: [0.0, 20.0]
       - Admission & previous qualification grades: [0.0, 200.0]
       - Age at enrollment: >= 16
       - Binary indicator flags (tuition, debtor, scholarship, etc.): {0, 1}
    6. Saves cleaned dataset to 'dataset/processed/cleaned_student_data.csv'.
    7. Preserves original raw dataset intact.
"""

import os
import sys
import pandas as pd
import numpy as np

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "dataset", "raw", "raw_student_data.csv")
PROCESSED_DIR = os.path.join(PROJECT_ROOT, "dataset", "processed")
CLEANED_DATA_PATH = os.path.join(PROCESSED_DIR, "cleaned_student_data.csv")

# Standardized column mapping dictionary
COLUMN_RENAME_MAP = {
    'Marital status': 'marital_status',
    'Application mode': 'application_mode',
    'Application order': 'application_order',
    'Course': 'course_id',
    'Daytime/evening attendance\t': 'daytime_evening_attendance',
    'Daytime/evening attendance': 'daytime_evening_attendance',
    'Previous qualification': 'previous_qualification',
    'Previous qualification (grade)': 'previous_qualification_grade',
    'Nacionality': 'nationality',
    "Mother's qualification": 'mother_qualification',
    "Father's qualification": 'father_qualification',
    "Mother's occupation": 'mother_occupation',
    "Father's occupation": 'father_occupation',
    'Admission grade': 'admission_grade',
    'Displaced': 'is_displaced',
    'Educational special needs': 'special_educational_needs',
    'Debtor': 'is_debtor',
    'Tuition fees up to date': 'tuition_fees_up_to_date',
    'Gender': 'gender',
    'Scholarship holder': 'scholarship_holder',
    'Age at enrollment': 'age_at_enrollment',
    'International': 'is_international',
    'Curricular units 1st sem (credited)': 'sem1_units_credited',
    'Curricular units 1st sem (enrolled)': 'sem1_units_enrolled',
    'Curricular units 1st sem (evaluations)': 'sem1_units_evaluations',
    'Curricular units 1st sem (approved)': 'sem1_units_approved',
    'Curricular units 1st sem (grade)': 'sem1_grade',
    'Curricular units 1st sem (without evaluations)': 'sem1_units_without_eval',
    'Curricular units 2nd sem (credited)': 'sem2_units_credited',
    'Curricular units 2nd sem (enrolled)': 'sem2_units_enrolled',
    'Curricular units 2nd sem (evaluations)': 'sem2_units_evaluations',
    'Curricular units 2nd sem (approved)': 'sem2_units_approved',
    'Curricular units 2nd sem (grade)': 'sem2_grade',
    'Curricular units 2nd sem (without evaluations)': 'sem2_units_without_eval',
    'Unemployment rate': 'unemployment_rate',
    'Inflation rate': 'inflation_rate',
    'GDP': 'gdp',
    'Target': 'target_outcome'
}

def clean_data():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw data file not found: {RAW_DATA_PATH}. Run load_dataset.py first.")
        
    print("\n" + "=" * 80)
    print(" SmartEdu Analytics - Task 3: Data Cleaning & Standardization")
    print("=" * 80)
    
    # Step 1: Load raw data
    print(f"[INFO] Reading raw dataset from: {RAW_DATA_PATH}")
    df_raw = pd.read_csv(RAW_DATA_PATH, sep=";", encoding="utf-8-sig")
    initial_shape = df_raw.shape
    print(f" -> Raw dimensions: {initial_shape[0]:,} rows, {initial_shape[1]} columns")
    
    # Step 2: Strip column whitespace / special characters and apply rename map
    df = df_raw.copy()
    cleaned_col_names = {}
    for col in df.columns:
        stripped = col.strip()
        cleaned_col_names[col] = COLUMN_RENAME_MAP.get(col, COLUMN_RENAME_MAP.get(stripped, stripped.lower().replace(" ", "_").replace("'", "").replace("(", "").replace(")", "")))
    
    df.rename(columns=cleaned_col_names, inplace=True)
    print(f"[CLEANING] Standardized {len(df.columns)} column names into clean Big-Data friendly snake_case.")
    
    # Step 3: Add explicit Unique Student Identifier
    # Essential for HDFS sharding, MapReduce key-value indexing, Hive primary keys, and Spark joins
    df.insert(0, 'student_id', [f"STD_{10001 + i}" for i in range(len(df))])
    print(f"[FEATURE] Generated unique student primary key 'student_id' (e.g. STD_10001 to STD_{10000 + len(df)}).")
    
    # Step 4: Missing Value Audit and Handling
    missing_sum = df.isnull().sum().sum()
    print(f"[AUDIT] Total Missing / NaN Values: {missing_sum}")
    if missing_sum > 0:
        print("[ACTION] Imputing missing numerical values with median and categorical with mode.")
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                if df[col].dtype in ['float64', 'int64']:
                    df[col] = df[col].fillna(df[col].median())
                else:
                    df[col] = df[col].fillna(df[col].mode()[0])
    else:
        print(" -> Verified: Dataset is complete with zero missing values.")
        
    # Step 5: Duplicate Records Check
    dup_subset = [c for c in df.columns if c != 'student_id']
    num_duplicates = df.duplicated(subset=dup_subset).sum()
    print(f"[AUDIT] Duplicate Records: {num_duplicates}")
    if num_duplicates > 0:
        df.drop_duplicates(subset=dup_subset, keep='first', inplace=True)
        print(f"[ACTION] Removed {num_duplicates} duplicate records.")
    else:
        print(" -> Verified: No duplicate rows found.")
        
    # Step 6: Domain Validation & Outlier Range Verification
    print("\n[VALIDATION] Performing Domain & Range Validation:")
    
    # Semester grades validation (0 to 20 scale)
    grade_cols = ['sem1_grade', 'sem2_grade']
    for gc in grade_cols:
        invalid_grades = df[(df[gc] < 0.0) | (df[gc] > 20.0)]
        print(f" -> '{gc}' range check [0, 20]: {len(invalid_grades)} invalid records detected.")
        if len(invalid_grades) > 0:
            df[gc] = df[gc].clip(lower=0.0, upper=20.0)
            
    # Admission & Previous Qualification grades validation (0 to 200 scale)
    entry_grades = ['admission_grade', 'previous_qualification_grade']
    for eg in entry_grades:
        invalid_entry = df[(df[eg] < 0.0) | (df[eg] > 200.0)]
        print(f" -> '{eg}' range check [0, 200]: {len(invalid_entry)} invalid records detected.")
        if len(invalid_entry) > 0:
            df[eg] = df[eg].clip(lower=0.0, upper=200.0)
            
    # Age validation
    invalid_age = df[df['age_at_enrollment'] < 16]
    print(f" -> 'age_at_enrollment' check (>= 16): {len(invalid_age)} invalid records detected.")
    
    # Binary flags validation {0, 1}
    binary_cols = ['daytime_evening_attendance', 'is_displaced', 'special_educational_needs',
                   'is_debtor', 'tuition_fees_up_to_date', 'gender', 'scholarship_holder', 'is_international']
    for bc in binary_cols:
        invalid_binary = df[~df[bc].isin([0, 1])]
        if len(invalid_binary) > 0:
            print(f" -> WARNING: Column '{bc}' contains non-binary values ({len(invalid_binary)} found).")
            
    # Target validation
    valid_targets = {'Dropout', 'Graduate', 'Enrolled'}
    target_check = set(df['target_outcome'].unique()) - valid_targets
    print(f" -> 'target_outcome' classes verified: {df['target_outcome'].unique().tolist()} (Unexpected: {target_check})")
    
    # Step 7: Export Cleaned Dataset
    df.to_csv(CLEANED_DATA_PATH, index=False)
    print(f"\n[SUCCESS] Cleaned dataset successfully exported to:")
    print(f" -> Path: {CLEANED_DATA_PATH}")
    print(f" -> Cleaned Shape: {df.shape[0]:,} rows, {df.shape[1]} columns")
    print(f" -> Original Raw Dataset preserved unmodified at: {RAW_DATA_PATH}")
    print("=" * 80 + "\n")
    return df

if __name__ == "__main__":
    clean_data()
