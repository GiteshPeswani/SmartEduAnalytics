"""
SmartEdu Analytics - Phase 6: Local Apache Spark & MLlib Engine Simulation
Script: run_local_spark_simulation.py
Description:
    Simulates the exact Spark DataFrame transformations, Spark SQL queries,
    and Spark MLlib predictive modeling pipeline on the verified dataset:
    1. Spark DataFrame Transformations & SQL Aggregations.
    2. Spark MLlib Supervised Dropout Risk Modeling (Random Forest & Logistic Regression).
    3. Performance & Paradigm Comparison: Hadoop MapReduce vs. Apache Spark.
    4. Exports analytics datasets to dataset/analytics/spark/.
    5. Produces high-resolution analytical and ML evaluation figures.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score, precision_score, recall_score, roc_curve, confusion_matrix

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CSV_DATA_PATH = os.path.join(PROJECT_ROOT, "dataset", "processed", "preprocessed_student_data.csv")
SPARK_OUT_DIR = os.path.join(PROJECT_ROOT, "dataset", "analytics", "spark")
VIZ_DIR = os.path.join(PROJECT_ROOT, "visualizations", "phase6")

def setup_dirs():
    os.makedirs(SPARK_OUT_DIR, exist_ok=True)
    os.makedirs(VIZ_DIR, exist_ok=True)

def run_spark_simulation():
    setup_dirs()
    print("=" * 85)
    print(" SmartEdu Analytics - Phase 6: Apache Spark & MLlib Distributed Engine Simulation")
    print("=" * 85)

    if not os.path.exists(CSV_DATA_PATH):
        raise FileNotFoundError(f"Missing dataset: {CSV_DATA_PATH}")

    df = pd.read_csv(CSV_DATA_PATH)
    print(f"[SPARK ACTION] Loaded DataFrame: {df.shape[0]:,} rows, {df.shape[1]} columns.")

    # 1. Spark Transformations
    print("\n[SPARK TRANSFORMATIONS] Computing derived execution columns...")
    total_enr = df["sem1_units_enrolled"] + df["sem2_units_enrolled"]
    total_app = df["sem1_units_approved"] + df["sem2_units_approved"]
    total_unatt = df["sem1_units_without_eval"] + df["sem2_units_without_eval"]
    part_rate = (1.0 - (total_unatt / np.maximum(total_enr, 1))) * 100.0

    df["total_enrolled_units"] = total_enr
    df["total_approved_units"] = total_app
    df["participation_rate"] = part_rate.clip(0, 100).round(2)
    df["perf_tier"] = df["annual_grade_avg"].apply(
        lambda g: "Excellent" if g >= 14 else ("Good" if g >= 12 else ("Average" if g >= 10 else "Needs_Improvement"))
    )

    # 2. Spark SQL: Course Performance Aggregations
    print("\n[SPARK SQL] Aggregating Course Performance Table:")
    course_perf = df.groupby("course_id").agg(
        student_count=("student_id", "count"),
        avg_annual_grade=("annual_grade_avg", "mean"),
        total_enrolled=("total_enrolled_units", "sum"),
        total_approved=("total_approved_units", "sum"),
        dropouts=("is_dropout", "sum")
    ).reset_index()
    course_perf["pass_rate_pct"] = (course_perf["total_approved"] / course_perf["total_enrolled"] * 100.0).round(2)
    course_perf["dropout_rate_pct"] = (course_perf["dropouts"] / course_perf["student_count"] * 100.0).round(2)
    course_perf["avg_annual_grade"] = course_perf["avg_annual_grade"].round(2)
    course_perf = course_perf.sort_values("avg_annual_grade", ascending=False)
    print(course_perf[["course_id", "student_count", "avg_annual_grade", "pass_rate_pct", "dropout_rate_pct"]].head(8).to_string(index=False))

    # Export to dataset/analytics/spark/
    out_csv = os.path.join(SPARK_OUT_DIR, "course_performance.csv")
    course_perf.to_csv(out_csv, index=False)
    print(f" -> Exported course analytics dataset to: {out_csv}")

    # 3. Spark MLlib Machine Learning Pipeline Simulation
    print("\n[SPARK MLLIB] Constructing Supervised Machine Learning Pipeline...")
    feature_cols = [
        "admission_grade", "sem1_grade", "sem2_grade", "annual_grade_avg",
        "sem1_units_approved", "sem2_units_approved", "total_units_failed",
        "tuition_fees_up_to_date", "is_debtor", "scholarship_holder",
        "daytime_evening_attendance", "age_at_enrollment"
    ]
    print(f" -> VectorAssembler: Assembling {len(feature_cols)} features into feature vector.")

    X = df[feature_cols]
    y = df["is_dropout"]

    # Stratified Train-Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print(f" -> Training Partition: {len(X_train):,} samples | Testing Partition: {len(X_test):,} samples")

    # Model 1: Random Forest Classifier
    print("\n[SPARK MLLIB: MODEL 1] Fitting Random Forest Classifier (numTrees=50, maxDepth=8)...")
    rf = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42)
    rf.fit(X_train_scaled, y_train)
    rf_preds = rf.predict(X_test_scaled)
    rf_probs = rf.predict_proba(X_test_scaled)[:, 1]

    rf_acc = accuracy_score(y_test, rf_preds)
    rf_auc = roc_auc_score(y_test, rf_probs)
    rf_f1 = f1_score(y_test, rf_preds)
    rf_prec = precision_score(y_test, rf_preds)
    rf_rec = recall_score(y_test, rf_preds)

    print(" -> Test Accuracy           : {:.2f}%".format(rf_acc * 100))
    print(" -> Area Under ROC (ROC-AUC): {:.4f}".format(rf_auc))
    print(" -> Precision               : {:.4f}".format(rf_prec))
    print(" -> Recall                  : {:.4f}".format(rf_rec))
    print(" -> Weighted F1-Score       : {:.4f}".format(rf_f1))

    # Model 2: Logistic Regression Classifier
    print("\n[SPARK MLLIB: MODEL 2] Fitting Logistic Regression Classifier...")
    lr = LogisticRegression(max_iter=100, random_state=42)
    lr.fit(X_train_scaled, y_train)
    lr_preds = lr.predict(X_test_scaled)
    lr_probs = lr.predict_proba(X_test_scaled)[:, 1]

    lr_acc = accuracy_score(y_test, lr_preds)
    lr_auc = roc_auc_score(y_test, lr_probs)
    lr_f1 = f1_score(y_test, lr_preds)

    print(" -> Test Accuracy           : {:.2f}%".format(lr_acc * 100))
    print(" -> Area Under ROC (ROC-AUC): {:.4f}".format(lr_auc))
    print(" -> Weighted F1-Score       : {:.4f}".format(lr_f1))

    # Feature Importances
    importances = rf.feature_importances_
    feat_imp = pd.DataFrame({"Feature": feature_cols, "Importance": importances}).sort_values("Importance", ascending=False)
    print("\n[TOP PREDICTIVE FEATURES (RANDOM FOREST)]")
    print(feat_imp.head(6).to_string(index=False))

    # Export ML Metrics to dataset/analytics/spark/
    ml_metrics_df = pd.DataFrame([
        {"Model": "Random Forest Classifier", "Accuracy_Pct": round(rf_acc*100, 2), "ROC_AUC": round(rf_auc, 4), "F1_Score": round(rf_f1, 4), "Precision": round(rf_prec, 4), "Recall": round(rf_rec, 4)},
        {"Model": "Logistic Regression", "Accuracy_Pct": round(lr_acc*100, 2), "ROC_AUC": round(lr_auc, 4), "F1_Score": round(lr_f1, 4), "Precision": round(precision_score(y_test, lr_preds), 4), "Recall": round(recall_score(y_test, lr_preds), 4)}
    ])
    metrics_path = os.path.join(SPARK_OUT_DIR, "ml_evaluation_metrics.csv")
    ml_metrics_df.to_csv(metrics_path, index=False)
    print(f" -> Exported ML metrics to: {metrics_path}")

    # 4. MapReduce vs Spark Comparison Table
    print("\n[PARADIGM COMPARISON: HADOOP MAPREDUCE VS. APACHE SPARK]")
    comp_df = pd.DataFrame([
        {"Dimension": "Processing Model", "Hadoop MapReduce (Phase 3)": "Batch 2-stage (Map -> Shuffle -> Reduce)", "Apache Spark (Phase 6)": "In-Memory Directed Acyclic Graph (DAG)"},
        {"Dimension": "Intermediate Storage", "Hadoop MapReduce (Phase 3)": "Spills to local disk / HDFS per phase", "Apache Spark (Phase 6)": "In-memory RDD / DataFrame caching"},
        {"Dimension": "Execution Latency", "Hadoop MapReduce (Phase 3)": "Higher latency (seconds/minutes overhead)", "Apache Spark (Phase 6)": "Near interactive (10x - 100x faster)"},
        {"Dimension": "Iterative Machine Learning", "Hadoop MapReduce (Phase 3)": "Cumbersome (disk I/O per iteration)", "Apache Spark (Phase 6)": "Native MLlib optimized for gradient steps"},
        {"Dimension": "Developer API", "Hadoop MapReduce (Phase 3)": "Low-level Streaming / Java APIs", "Apache Spark (Phase 6)": "Declarative DataFrame & Spark SQL APIs"}
    ])
    print(comp_df.to_string(index=False))

    # 5. Visualizations
    generate_visualizations(df, y_test, rf_probs, lr_probs, rf_preds, feat_imp, comp_df)
    print("\n[SUCCESS] Phase 6 Spark processing and ML evaluation finished successfully!\n")

def generate_visualizations(df, y_test, rf_probs, lr_probs, rf_preds, feat_imp, comp_df):
    print("\n[VISUALIZATIONS] Generating Phase 6 Spark & MLlib Charts...")
    sns.set_theme(style="whitegrid", palette="muted")

    # Chart 1: Feature Importance (Random Forest)
    plt.figure(figsize=(10, 5))
    sns.barplot(x="Importance", y="Feature", data=feat_imp, palette="Blues_r")
    plt.title("Spark MLlib: Random Forest Predictive Feature Importances", fontsize=13, fontweight="bold")
    plt.xlabel("Gini Feature Importance", fontsize=11)
    plt.tight_layout()
    chart1 = os.path.join(VIZ_DIR, "spark_ml_feature_importance.png")
    plt.savefig(chart1, dpi=300)
    plt.close()
    print(f" -> Saved: {chart1}")

    # Chart 2: ROC Curve Comparison (Random Forest vs Logistic Regression)
    plt.figure(figsize=(8, 6))
    fpr_rf, tpr_rf, _ = roc_curve(y_test, rf_probs)
    fpr_lr, tpr_lr, _ = roc_curve(y_test, lr_probs)
    plt.plot(fpr_rf, tpr_rf, color="#2ecc71", linewidth=2.5, label=f"Random Forest (AUC = {roc_auc_score(y_test, rf_probs):.4f})")
    plt.plot(fpr_lr, tpr_lr, color="#3498db", linewidth=2.0, linestyle="--", label=f"Logistic Regression (AUC = {roc_auc_score(y_test, lr_probs):.4f})")
    plt.plot([0, 1], [0, 1], color="gray", linestyle=":")
    plt.title("Spark MLlib: Receiver Operating Characteristic (ROC) Curve", fontsize=13, fontweight="bold")
    plt.xlabel("False Positive Rate", fontsize=11)
    plt.ylabel("True Positive Rate (Recall)", fontsize=11)
    plt.legend(loc="lower right", fontsize=11)
    plt.tight_layout()
    chart2 = os.path.join(VIZ_DIR, "spark_ml_roc_curve.png")
    plt.savefig(chart2, dpi=300)
    plt.close()
    print(f" -> Saved: {chart2}")

    # Chart 3: Confusion Matrix
    plt.figure(figsize=(6, 5))
    cm = confusion_matrix(y_test, rf_preds)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=["Retained/Grad", "Dropout"], yticklabels=["Retained/Grad", "Dropout"])
    plt.title("Spark MLlib: Random Forest Confusion Matrix", fontsize=13, fontweight="bold")
    plt.xlabel("Predicted Label", fontsize=11)
    plt.ylabel("Actual Institutional Label", fontsize=11)
    plt.tight_layout()
    chart3 = os.path.join(VIZ_DIR, "spark_ml_confusion_matrix.png")
    plt.savefig(chart3, dpi=300)
    plt.close()
    print(f" -> Saved: {chart3}")

if __name__ == "__main__":
    run_spark_simulation()
