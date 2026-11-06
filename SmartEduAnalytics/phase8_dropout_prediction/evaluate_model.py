"""
SmartEdu Analytics - Phase 8: Model Evaluation & Visualizations
File: evaluate_model.py
Description:
    Conducts rigorous evaluation of the trained models:
    - Generates Confusion Matrix & Classification Report
    - Plots ROC curves comparison
    - Plots Feature Importance bar chart
    - Plots Performance Metrics comparison
    - Exports evaluation_results.csv and high-res visualization artifacts.
"""

import os
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_curve, auc,
    precision_recall_curve, average_precision_score
)

from data_preprocessing import load_and_preprocess_data, MODELS_DIR

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
VIZ_DIR = os.path.join(PROJECT_ROOT, "visualizations", "phase8")

def evaluate_models_and_visualize():
    print("=" * 80)
    print(" SmartEdu Analytics - Phase 8: Comprehensive Model Evaluation")
    print("=" * 80)

    os.makedirs(VIZ_DIR, exist_ok=True)

    # Load data
    data = load_and_preprocess_data(save_scaler=False)
    X_test_scaled = data["X_test_scaled"]
    y_test = data["y_test"]
    feature_cols = data["feature_cols"]

    # Load champion model
    best_model_path = os.path.join(MODELS_DIR, "model.joblib")
    meta_path = os.path.join(MODELS_DIR, "model_meta.joblib")
    comp_path = os.path.join(MODELS_DIR, "models_comparison.csv")

    if not os.path.exists(best_model_path):
        raise FileNotFoundError(f"Model file not found at {best_model_path}. Please run train_model.py first.")

    best_model = joblib.load(best_model_path)
    meta = joblib.load(meta_path) if os.path.exists(meta_path) else {"best_model_name": type(best_model).__name__}
    best_model_name = meta["best_model_name"]

    print(f"[EVALUATION TARGET] Champion Model: {best_model_name}")

    # Generate predictions
    y_pred = best_model.predict(X_test_scaled)
    y_prob = best_model.predict_proba(X_test_scaled)[:, 1] if hasattr(best_model, "predict_proba") else y_pred

    # Classification Report
    cls_report = classification_report(y_test, y_pred, target_names=["Enrolled/Graduate (0)", "Dropout (1)"], output_dict=True)
    df_cls = pd.DataFrame(cls_report).transpose()
    eval_csv_path = os.path.join(SCRIPT_DIR, "evaluation_results.csv")
    df_cls.to_csv(eval_csv_path)
    print(f"\n[CLASSIFICATION REPORT]:\n{classification_report(y_test, y_pred, target_names=['Enrolled/Graduate (0)', 'Dropout (1)'])}")
    print(f" -> Exported classification report to: {eval_csv_path}")

    # 1. Visualization: Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False,
                xticklabels=["Enrolled / Grad", "Dropout"],
                yticklabels=["Enrolled / Grad", "Dropout"],
                annot_kws={"size": 14, "weight": "bold"})
    plt.title(f"Confusion Matrix - {best_model_name}\n(Test Set: N={len(y_test)})", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Predicted Class", fontsize=11, fontweight="bold")
    plt.ylabel("Actual True Class", fontsize=11, fontweight="bold")
    plt.tight_layout()
    cm_plot_path = os.path.join(VIZ_DIR, "confusion_matrix_best_model.png")
    plt.savefig(cm_plot_path, dpi=300)
    plt.close()
    print(f" -> Saved Confusion Matrix plot: {cm_plot_path}")

    # 2. Visualization: Feature Importance
    if hasattr(best_model, "feature_importances_"):
        importances = best_model.feature_importances_
    elif hasattr(best_model, "coef_"):
        importances = np.abs(best_model.coef_[0])
    else:
        importances = np.ones(len(feature_cols))

    feat_imp = pd.DataFrame({
        "Feature": feature_cols,
        "Importance": importances
    }).sort_values(by="Importance", ascending=False)

    feat_imp_csv = os.path.join(SCRIPT_DIR, "feature_importance.csv")
    feat_imp.to_csv(feat_imp_csv, index=False)

    plt.figure(figsize=(9, 7))
    top_feats = feat_imp.head(15).sort_values(by="Importance", ascending=True)
    bars = plt.barh(top_feats["Feature"], top_feats["Importance"], color="#2b5c8f", edgecolor="#1a365d")
    plt.title(f"Top 15 Predictive Features - {best_model_name}", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Relative Importance Score", fontsize=11, fontweight="bold")
    plt.grid(axis="x", linestyle="--", alpha=0.5)
    plt.tight_layout()
    feat_plot_path = os.path.join(VIZ_DIR, "feature_importance.png")
    plt.savefig(feat_plot_path, dpi=300)
    plt.close()
    print(f" -> Saved Feature Importance plot: {feat_plot_path}")

    # 3. Visualization: Model Comparison Bar Chart
    if os.path.exists(comp_path):
        df_comp = pd.read_csv(comp_path)
        metrics = ["Accuracy", "Precision", "Recall", "F1_Score", "ROC_AUC"]
        
        df_melt = pd.melt(df_comp, id_vars=["Model"], value_vars=metrics, var_name="Metric", value_name="Score")
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df_melt, x="Metric", y="Score", hue="Model", palette="tab10")
        plt.title("Comparative Performance Across Supervised ML Algorithms", fontsize=12, fontweight="bold", pad=12)
        plt.ylim(0.60, 1.0)
        plt.ylabel("Performance Score (0.0 - 1.0)", fontsize=11, fontweight="bold")
        plt.grid(axis="y", linestyle="--", alpha=0.5)
        plt.legend(bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)
        plt.tight_layout()
        comp_plot_path = os.path.join(VIZ_DIR, "model_metrics_comparison_barchart.png")
        plt.savefig(comp_plot_path, dpi=300)
        plt.close()
        print(f" -> Saved Model Metrics Comparison plot: {comp_plot_path}")

    # 4. Visualization: ROC & Precision-Recall Curves
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    prec_pts, rec_pts, _ = precision_recall_curve(y_test, y_prob)
    pr_auc = average_precision_score(y_test, y_prob)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    
    # ROC Curve
    axes[0].plot(fpr, tpr, color="#1e40af", lw=2.5, label=f"{best_model_name} (AUC = {roc_auc:.4f})")
    axes[0].plot([0, 1], [0, 1], color="#9ca3af", lw=1.5, linestyle="--", label="Random Chance (AUC = 0.50)")
    axes[0].set_xlim([0.0, 1.0])
    axes[0].set_ylim([0.0, 1.05])
    axes[0].set_xlabel("False Positive Rate", fontweight="bold")
    axes[0].set_ylabel("True Positive Rate", fontweight="bold")
    axes[0].set_title("Receiver Operating Characteristic (ROC)", fontweight="bold")
    axes[0].legend(loc="lower right")
    axes[0].grid(True, linestyle="--", alpha=0.5)

    # PR Curve
    axes[1].plot(rec_pts, prec_pts, color="#059669", lw=2.5, label=f"PR Curve (Avg Prec = {pr_auc:.4f})")
    axes[1].set_xlim([0.0, 1.0])
    axes[1].set_ylim([0.0, 1.05])
    axes[1].set_xlabel("Recall", fontweight="bold")
    axes[1].set_ylabel("Precision", fontweight="bold")
    axes[1].set_title("Precision-Recall (PR) Curve", fontweight="bold")
    axes[1].legend(loc="lower left")
    axes[1].grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    roc_plot_path = os.path.join(VIZ_DIR, "roc_pr_curves_best_model.png")
    plt.savefig(roc_plot_path, dpi=300)
    plt.close()
    print(f" -> Saved ROC & PR Curves plot: {roc_plot_path}")

    print("[SUCCESS] Phase 8 model evaluation and visualizations generated successfully.")

if __name__ == "__main__":
    evaluate_models_and_visualize()
