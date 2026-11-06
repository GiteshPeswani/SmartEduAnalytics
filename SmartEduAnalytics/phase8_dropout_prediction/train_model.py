"""
SmartEdu Analytics - Phase 8: Student Dropout Risk Prediction
File: train_model.py
Description:
    Trains four distinct supervised machine learning classifiers:
    1. Logistic Regression
    2. Decision Tree Classifier
    3. Random Forest Classifier
    4. Gradient Boosting Classifier
    Evaluates their performance on test data, selects the best model,
    and serializes the champion model using joblib.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from data_preprocessing import load_and_preprocess_data, MODELS_DIR

def train_and_evaluate_models():
    print("=" * 80)
    print(" SmartEdu Analytics - Phase 8: Model Training & Benchmark Comparison")
    print("=" * 80)

    data = load_and_preprocess_data(save_scaler=True)
    X_train_scaled = data["X_train_scaled"]
    X_test_scaled = data["X_test_scaled"]
    y_train = data["y_train"]
    y_test = data["y_test"]
    feature_cols = data["feature_cols"]

    # Candidate Models
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
        "Decision Tree": DecisionTreeClassifier(max_depth=6, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, max_depth=10, min_samples_split=5, random_state=42),
        "Gradient Boosting": GradientBoostingClassifier(n_estimators=100, learning_rate=0.08, max_depth=4, random_state=42)
    }

    results = []
    fitted_models = {}

    print("\n[TRAINING] Fitting candidate algorithms...")
    for name, model in models.items():
        print(f" -> Training {name}...")
        model.fit(X_train_scaled, y_train)
        fitted_models[name] = model

        # Predictions
        y_pred = model.predict(X_test_scaled)
        y_prob = model.predict_proba(X_test_scaled)[:, 1] if hasattr(model, "predict_proba") else y_pred

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_prob)

        results.append({
            "Model": name,
            "Accuracy": round(acc, 4),
            "Precision": round(prec, 4),
            "Recall": round(rec, 4),
            "F1_Score": round(f1, 4),
            "ROC_AUC": round(auc, 4)
        })

    df_results = pd.DataFrame(results).sort_values(by="ROC_AUC", ascending=False)
    print("\n" + "=" * 80)
    print(" MODEL PERFORMANCE COMPARISON (TEST PARTITION):")
    print("=" * 80)
    print(df_results.to_string(index=False))

    # Save benchmark table
    comp_path = os.path.join(MODELS_DIR, "models_comparison.csv")
    df_results.to_csv(comp_path, index=False)
    print(f"\n[SAVED] Benchmark summary saved to: {comp_path}")

    # Identify champion model (highest ROC-AUC and F1)
    best_model_name = df_results.iloc[0]["Model"]
    best_model = fitted_models[best_model_name]
    print(f"\n[CHAMPION MODEL SELECTED]: {best_model_name}")
    print(f" -> ROC-AUC: {df_results.iloc[0]['ROC_AUC']:.4f} | F1-Score: {df_results.iloc[0]['F1_Score']:.4f} | Accuracy: {df_results.iloc[0]['Accuracy']*100:.2f}%")

    # Save best model
    best_model_path = os.path.join(MODELS_DIR, "model.joblib")
    joblib.dump(best_model, best_model_path)
    print(f"[SAVED] Champion model saved to: {best_model_path}")

    # Also save metadata
    meta = {
        "best_model_name": best_model_name,
        "feature_cols": feature_cols,
        "metrics": df_results.iloc[0].to_dict()
    }
    joblib.dump(meta, os.path.join(MODELS_DIR, "model_meta.joblib"))

    return best_model, fitted_models, df_results, data

if __name__ == "__main__":
    train_and_evaluate_models()
