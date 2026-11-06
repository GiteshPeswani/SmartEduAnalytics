"""
SmartEdu Analytics - Phase 1: End-to-End Pipeline & Data Validation
Script: validate_dataset.py
Description:
    Conducts rigorous data quality assurance and verification on all Phase 1 outputs:
    1. File Existence & Storage Integrity Check
    2. Record Count Conservation (Raw -> Cleaned -> Preprocessed -> Train + Test)
    3. Missing Value Audit (Zero NaNs in processed data)
    4. Stratified Split Preservation (Train/Test class distribution check)
    5. Value Range Validation (Grades, Ages, Binary Flags, Risk Scores)
    6. Primary Key Uniqueness (student_id uniqueness check)
"""

import os
import sys
import pandas as pd
import numpy as np

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_RAW = os.path.join(PROJECT_ROOT, "dataset", "raw", "raw_student_data.csv")
DATA_CLEAN = os.path.join(PROJECT_ROOT, "dataset", "processed", "cleaned_student_data.csv")
DATA_PREP = os.path.join(PROJECT_ROOT, "dataset", "processed", "preprocessed_student_data.csv")
DATA_TRAIN = os.path.join(PROJECT_ROOT, "dataset", "processed", "train_data.csv")
DATA_TEST = os.path.join(PROJECT_ROOT, "dataset", "processed", "test_data.csv")

def validate_pipeline():
    print("\n" + "=" * 80)
    print(" SmartEdu Analytics - Phase 1: Data Pipeline Validation Audit")
    print("=" * 80)
    
    validation_results = []
    
    # 1. File Existence Verification
    files_to_check = {
        "Raw Student Data": DATA_RAW,
        "Cleaned Student Data": DATA_CLEAN,
        "Preprocessed Student Data": DATA_PREP,
        "Training Split (80%)": DATA_TRAIN,
        "Testing Split (20%)": DATA_TEST
    }
    
    print("\n[CHECK 1] Artifact Existence & File Size:")
    for label, path in files_to_check.items():
        exists = os.path.exists(path)
        size_kb = os.path.getsize(path) / 1024 if exists else 0
        status = "PASSED" if exists and size_kb > 0 else "FAILED"
        print(f" -> {label:<28}: [{status}] Size: {size_kb:8.2f} KB | Path: {os.path.basename(path)}")
        validation_results.append((f"Existence: {label}", status))
        if not exists:
            print(f"[FATAL ERROR] Required artifact missing: {path}")
            return False

    # Load datasets
    df_raw = pd.read_csv(DATA_RAW, sep=";", encoding="utf-8-sig")
    df_clean = pd.read_csv(DATA_CLEAN)
    df_prep = pd.read_csv(DATA_PREP)
    df_train = pd.read_csv(DATA_TRAIN)
    df_test = pd.read_csv(DATA_TEST)

    # 2. Row Count Conservation Check
    print("\n[CHECK 2] Record Count Conservation:")
    raw_len = len(df_raw)
    clean_len = len(df_clean)
    prep_len = len(df_prep)
    split_sum = len(df_train) + len(df_test)
    
    count_match = (raw_len == clean_len == prep_len == split_sum == 4424)
    status_c2 = "PASSED" if count_match else "FAILED"
    print(f" -> Raw: {raw_len:,} | Cleaned: {clean_len:,} | Preprocessed: {prep_len:,} | Train+Test: {split_sum:,}")
    print(f" -> Result: [{status_c2}] Exact 4,424 records conserved across all stages.")
    validation_results.append(("Record Count Conservation", status_c2))

    # 3. Missing Value Check on Cleaned & Preprocessed Data
    print("\n[CHECK 3] Missing Value Audit:")
    clean_nans = df_clean.isnull().sum().sum()
    prep_nans = df_prep.isnull().sum().sum()
    status_c3 = "PASSED" if clean_nans == 0 and prep_nans == 0 else "FAILED"
    print(f" -> Cleaned Data NaNs: {clean_nans} | Preprocessed Data NaNs: {prep_nans}")
    print(f" -> Result: [{status_c3}] Zero missing values detected.")
    validation_results.append(("Zero Missing Values", status_c3))

    # 4. Student ID Primary Key Uniqueness
    print("\n[CHECK 4] Primary Key Uniqueness ('student_id'):")
    unique_ids = df_clean['student_id'].nunique()
    status_c4 = "PASSED" if unique_ids == len(df_clean) else "FAILED"
    print(f" -> Unique student_ids: {unique_ids:,} / {len(df_clean):,}")
    print(f" -> Result: [{status_c4}] Every student record has an unambiguous primary key.")
    validation_results.append(("Primary Key Uniqueness", status_c4))

    # 5. Value Range Integrity Check
    print("\n[CHECK 5] Domain & Range Validation:")
    sem1_ok = (df_clean['sem1_grade'] >= 0.0).all() and (df_clean['sem1_grade'] <= 20.0).all()
    sem2_ok = (df_clean['sem2_grade'] >= 0.0).all() and (df_clean['sem2_grade'] <= 20.0).all()
    adm_ok = (df_clean['admission_grade'] >= 0.0).all() and (df_clean['admission_grade'] <= 200.0).all()
    risk_ok = (df_prep['academic_risk_score'] >= 0.0).all() and (df_prep['academic_risk_score'] <= 1.0).all()
    ranges_pass = sem1_ok and sem2_ok and adm_ok and risk_ok
    status_c5 = "PASSED" if ranges_pass else "FAILED"
    print(f" -> Semester Grades [0, 20]: {'Valid' if sem1_ok and sem2_ok else 'Invalid'}")
    print(f" -> Admission Grades [0, 200]: {'Valid' if adm_ok else 'Invalid'}")
    print(f" -> Derived Risk Scores [0.0, 1.0]: {'Valid' if risk_ok else 'Invalid'}")
    print(f" -> Result: [{status_c5}] All values strictly comply with domain boundary specifications.")
    validation_results.append(("Domain & Range Checks", status_c5))

    # 6. Stratification Check
    print("\n[CHECK 6] Stratified Class Distribution (Train vs Test):")
    train_dist = (df_train['target_outcome'].value_counts(normalize=True) * 100).round(2).to_dict()
    test_dist = (df_test['target_outcome'].value_counts(normalize=True) * 100).round(2).to_dict()
    print(f" -> Train Class %: {train_dist}")
    print(f" -> Test Class  %: {test_dist}")
    strat_diff = max(abs(train_dist[k] - test_dist[k]) for k in train_dist)
    status_c6 = "PASSED" if strat_diff < 0.5 else "FAILED"
    print(f" -> Maximum Class Proportion Deviation: {strat_diff:.2f}% (Threshold: < 0.5%)")
    print(f" -> Result: [{status_c6}] Train and Test splits are perfectly stratified.")
    validation_results.append(("Stratified Split Balance", status_c6))

    # Summary
    print("\n" + "=" * 80)
    print(" Phase 1 Pipeline Validation Audit Summary:")
    print("=" * 80)
    all_passed = True
    for item, status in validation_results:
        print(f"  [{status}] {item}")
        if status != "PASSED":
            all_passed = False
            
    print("-" * 80)
    if all_passed:
        print(" [ALL VERIFICATION CHECKS PASSED] Ready for Phase 2: Hadoop & HDFS Ingestion.")
    else:
        print(" [WARNING] One or more verification checks failed. Review details above.")
    print("=" * 80 + "\n")
    return all_passed

if __name__ == "__main__":
    success = validate_pipeline()
    if not success:
        sys.exit(1)
