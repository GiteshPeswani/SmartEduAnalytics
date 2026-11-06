"""
SmartEdu Analytics - Phase 1: Exploratory Data Analysis (EDA)
Script: explore_dataset.py
Description:
    Performs comprehensive Exploratory Data Analysis on raw student data:
    - Dimensions, column data types, head and tail inspection
    - Missing values and duplicate detection
    - Summary descriptive statistics
    - Target distribution analysis
    - Generates and exports publication-ready visualizations to visualizations/
    - Writes detailed analytical summary to reports/dataset_summary.txt
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for script execution
import matplotlib.pyplot as plt
import seaborn as sns

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "dataset", "raw", "raw_student_data.csv")
VIZ_DIR = os.path.join(PROJECT_ROOT, "visualizations")
REPORT_PATH = os.path.join(PROJECT_ROOT, "reports", "dataset_summary.txt")

def setup_directories():
    os.makedirs(VIZ_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)

def load_data():
    if not os.path.exists(RAW_DATA_PATH):
        raise FileNotFoundError(f"Raw data file not found at {RAW_DATA_PATH}. Run load_dataset.py first.")
    # Dataset uses ';' as separator with UTF-8 encoding
    df = pd.read_csv(RAW_DATA_PATH, sep=";", encoding="utf-8-sig")
    return df

def generate_visualizations(df):
    """Generates and saves exploratory charts to visualizations/ directory."""
    print("\n[INFO] Generating analytical visualizations...")
    sns.set_theme(style="whitegrid", palette="muted")
    
    # 1. Target Distribution (Bar + Donut Chart)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    target_counts = df['Target'].value_counts()
    colors = ['#2ecc71', '#e74c3c', '#f39c12']
    
    sns.barplot(x=target_counts.index, y=target_counts.values, ax=axes[0], palette=colors)
    axes[0].set_title("Student Academic Outcome Counts (Target)", fontsize=13, fontweight='bold')
    axes[0].set_xlabel("Academic Status", fontsize=11)
    axes[0].set_ylabel("Number of Students", fontsize=11)
    for i, v in enumerate(target_counts.values):
        axes[0].text(i, v + 40, f"{v:,} ({v/len(df)*100:.1f}%)", ha='center', fontweight='bold')
        
    axes[1].pie(target_counts.values, labels=target_counts.index, autopct='%1.1f%%',
                startangle=140, colors=colors, wedgeprops={'edgecolor': 'white', 'linewidth': 2})
    axes[1].set_title("Student Outcome Proportions", fontsize=13, fontweight='bold')
    plt.tight_layout()
    chart1_path = os.path.join(VIZ_DIR, "target_distribution.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"  [SAVED] {chart1_path}")

    # 2. Academic Performance Distribution (Admission, Sem 1, Sem 2 Grades)
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    grade_cols = [
        ('Admission grade', 'Admission Grade (0-200 Scale)', '#3498db'),
        ('Curricular units 1st sem (grade)', '1st Semester Grade (0-20 Scale)', '#9b59b6'),
        ('Curricular units 2nd sem (grade)', '2nd Semester Grade (0-20 Scale)', '#1abc9c')
    ]
    for idx, (col, title, color) in enumerate(grade_cols):
        if col in df.columns:
            sns.histplot(df[col], kde=True, ax=axes[idx], color=color, bins=25)
            axes[idx].set_title(title, fontsize=12, fontweight='bold')
            axes[idx].set_xlabel("Grade", fontsize=10)
            axes[idx].set_ylabel("Frequency", fontsize=10)
    plt.tight_layout()
    chart2_path = os.path.join(VIZ_DIR, "academic_performance_dist.png")
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"  [SAVED] {chart2_path}")

    # 3. Curricular Units: Enrolled vs Approved by Outcome
    sem1_enrolled = 'Curricular units 1st sem (enrolled)'
    sem1_approved = 'Curricular units 1st sem (approved)'
    if sem1_enrolled in df.columns and sem1_approved in df.columns:
        plt.figure(figsize=(10, 6))
        sns.scatterplot(
            data=df,
            x=sem1_enrolled,
            y=sem1_approved,
            hue='Target',
            palette={'Graduate': '#2ecc71', 'Dropout': '#e74c3c', 'Enrolled': '#f39c12'},
            alpha=0.6,
            s=40
        )
        plt.title("Semester 1: Enrolled Units vs Approved Units by Academic Outcome", fontsize=13, fontweight='bold')
        plt.xlabel("Units Enrolled (1st Sem)", fontsize=11)
        plt.ylabel("Units Approved (1st Sem)", fontsize=11)
        plt.plot([0, 15], [0, 15], linestyle='--', color='gray', label='100% Approval Line')
        plt.legend(title='Outcome', loc='upper left')
        plt.tight_layout()
        chart3_path = os.path.join(VIZ_DIR, "curricular_evaluations_vs_approvals.png")
        plt.savefig(chart3_path, dpi=300)
        plt.close()
        print(f"  [SAVED] {chart3_path}")

    # 4. Attendance Impact (Daytime vs Evening Attendance)
    att_col = [c for c in df.columns if 'attendance' in c.lower()][0]
    plt.figure(figsize=(8, 5))
    att_ct = pd.crosstab(df[att_col], df['Target'], normalize='index') * 100
    att_ct.plot(kind='bar', stacked=True, color=['#e74c3c', '#f39c12', '#2ecc71'], figsize=(8, 5))
    plt.title("Academic Outcome Distribution by Attendance Mode", fontsize=13, fontweight='bold')
    plt.xlabel("Attendance Mode (1 = Daytime, 0 = Evening)", fontsize=11)
    plt.ylabel("Percentage (%)", fontsize=11)
    plt.legend(title='Outcome', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=0)
    plt.tight_layout()
    chart4_path = os.path.join(VIZ_DIR, "attendance_and_dropout.png")
    plt.savefig(chart4_path, dpi=300)
    plt.close()
    print(f"  [SAVED] {chart4_path}")

    # 5. Socioeconomic & Financial Factors (Tuition Up to Date & Debtor Status)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    if 'Tuition fees up to date' in df.columns:
        tuition_df = pd.crosstab(df['Tuition fees up to date'], df['Target'], normalize='index') * 100
        tuition_df.plot(kind='bar', stacked=True, ax=axes[0], color=['#e74c3c', '#f39c12', '#2ecc71'])
        axes[0].set_title("Tuition Fees Status vs Outcome", fontsize=12, fontweight='bold')
        axes[0].set_xlabel("Tuition Fees Up to Date (1=Yes, 0=No)", fontsize=10)
        axes[0].set_ylabel("Percentage (%)", fontsize=10)
        axes[0].tick_params(axis='x', rotation=0)

    if 'Debtor' in df.columns:
        debtor_df = pd.crosstab(df['Debtor'], df['Target'], normalize='index') * 100
        debtor_df.plot(kind='bar', stacked=True, ax=axes[1], color=['#e74c3c', '#f39c12', '#2ecc71'])
        axes[1].set_title("Debtor Status vs Outcome", fontsize=12, fontweight='bold')
        axes[1].set_xlabel("Debtor (1=Yes, 0=No)", fontsize=10)
        axes[1].set_ylabel("Percentage (%)", fontsize=10)
        axes[1].tick_params(axis='x', rotation=0)
    plt.tight_layout()
    chart5_path = os.path.join(VIZ_DIR, "socioeconomic_financial_impact.png")
    plt.savefig(chart5_path, dpi=300)
    plt.close()
    print(f"  [SAVED] {chart5_path}")

    # 6. Feature Correlation Heatmap (Key Numeric Variables)
    numeric_cols = [
        'Admission grade',
        'Previous qualification (grade)',
        'Age at enrollment',
        'Curricular units 1st sem (approved)',
        'Curricular units 1st sem (grade)',
        'Curricular units 2nd sem (approved)',
        'Curricular units 2nd sem (grade)',
        'Tuition fees up to date',
        'Debtor'
    ]
    avail_num_cols = [c for c in numeric_cols if c in df.columns]
    plt.figure(figsize=(10, 8))
    corr = df[avail_num_cols].corr()
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", cbar=True, square=True, linewidths=0.5)
    plt.title("Correlation Matrix of Key Academic & Financial Variables", fontsize=13, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    chart6_path = os.path.join(VIZ_DIR, "feature_correlation_heatmap.png")
    plt.savefig(chart6_path, dpi=300)
    plt.close()
    print(f"  [SAVED] {chart6_path}")

def run_exploration():
    setup_directories()
    df = load_data()
    
    print("\n" + "=" * 80)
    print(" SmartEdu Analytics - Task 2: Exploratory Data Analysis")
    print("=" * 80)
    
    # 1. Dataset Dimensions
    n_rows, n_cols = df.shape
    print(f"\n[DIMENSIONS] Rows (Instances): {n_rows:,} | Columns (Features): {n_cols}")
    
    # 2. First 10 Records
    print("\n[INSPECTION] First 10 Records:")
    print(df.head(10).to_string(max_cols=8))
    
    # 3. Last 10 Records
    print("\n[INSPECTION] Last 10 Records:")
    print(df.tail(10).to_string(max_cols=8))
    
    # 4. Column Names and Types
    print("\n[SCHEMA] Column Names, Types, and Non-Null Counts:")
    dtype_summary = pd.DataFrame({
        "Column": df.columns,
        "Dtype": df.dtypes.values,
        "Non-Null Count": df.notnull().sum().values,
        "Unique Values": [df[c].nunique() for c in df.columns]
    })
    print(dtype_summary.to_string(index=False))
    
    # 5. Missing Values Analysis
    missing_counts = df.isnull().sum()
    total_missing = missing_counts.sum()
    print(f"\n[DATA QUALITY] Total Missing Values in Raw Dataset: {total_missing}")
    if total_missing > 0:
        print(missing_counts[missing_counts > 0])
    else:
        print(" -> Verified: No missing/NaN values present in raw dataset.")
        
    # 6. Duplicate Records Analysis
    duplicate_rows = df.duplicated().sum()
    print(f"[DATA QUALITY] Duplicate Records in Raw Dataset: {duplicate_rows}")
    
    # 7. Descriptive Statistics
    print("\n[STATISTICS] Numerical Features Summary (Selected Key Metrics):")
    stats = df.describe().T[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
    print(stats.head(15).round(2).to_string())
    
    # 8. Target Outcome Analysis
    target_dist = df['Target'].value_counts()
    target_pct = df['Target'].value_counts(normalize=True) * 100
    print("\n[OUTCOME ANALYSIS] Target Variable Breakdown:")
    for cls_name in target_dist.index:
        print(f" - {cls_name:10s}: {target_dist[cls_name]:5d} students ({target_pct[cls_name]:5.2f}%)")
        
    # Generate Visualizations
    generate_visualizations(df)
    
    # Write summary report file
    with open(REPORT_PATH, "w", encoding="utf-8") as rep:
        rep.write("=" * 80 + "\n")
        rep.write("SmartEdu Analytics - Comprehensive Dataset Summary Report\n")
        rep.write("Dataset: Predict Students' Dropout and Academic Success (UCI ID: 697)\n")
        rep.write("=" * 80 + "\n\n")
        rep.write(f"Total Records: {n_rows:,}\n")
        rep.write(f"Total Columns: {n_cols}\n")
        rep.write(f"Missing Values: {total_missing}\n")
        rep.write(f"Duplicate Rows: {duplicate_rows}\n\n")
        rep.write("Target Variable Class Distribution:\n")
        for cls_name in target_dist.index:
            rep.write(f"  - {cls_name}: {target_dist[cls_name]} ({target_pct[cls_name]:.2f}%)\n")
        rep.write("\nSchema & Data Types:\n")
        rep.write(dtype_summary.to_string(index=False))
        rep.write("\n\nDescriptive Statistics:\n")
        rep.write(stats.round(2).to_string())
        rep.write("\n\n" + "=" * 80 + "\n")
        
    print(f"\n[SUCCESS] Dataset summary report saved to: {REPORT_PATH}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    run_exploration()
