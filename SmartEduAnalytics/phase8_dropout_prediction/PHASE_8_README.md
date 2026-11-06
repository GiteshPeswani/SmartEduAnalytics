# Phase 8: Student Dropout Risk Prediction Using Machine Learning

## 1. Overview
Phase 8 develops, benchmarks, and deploys supervised machine learning models to identify students who are at risk of academic attrition before course completion. It integrates directly with the preprocessed dataset from Phase 1 and persists scored probabilities and risk tiers into the central MySQL/SQLite database established in Phase 5.

## 2. Machine Learning Architecture
- **Features (21 predictors)**:
  - Academic Performance: `admission_grade`, `sem1_grade`, `sem2_grade`, `annual_grade_avg`, `sem1_approval_rate`, `sem2_approval_rate`, `grade_trajectory`.
  - Academic Load & Progress: `sem1_units_enrolled`, `sem1_units_approved`, `sem1_units_evaluations`, `sem2_units_enrolled`, `sem2_units_approved`, `sem2_units_evaluations`, `total_units_failed`.
  - Financial & Socio-demographic Factors: `tuition_fees_up_to_date`, `is_debtor`, `scholarship_holder`, `daytime_evening_attendance`, `age_at_enrollment`, `gender`, `is_displaced`.
- **Target Label**: `is_dropout` (0 = Enrolled/Graduated, 1 = Dropped Out).
- **Split Strategy**: Stratified 80/20 train/test split (3,539 training samples, 885 testing samples).
- **Algorithms Evaluated**:
  1. Logistic Regression (L2 regularization, max_iter=1000)
  2. Decision Tree Classifier (max_depth=6)
  3. Random Forest Classifier (n_estimators=100, max_depth=10, min_samples_split=5)
  4. Gradient Boosting Classifier (n_estimators=100, learning_rate=0.08, max_depth=4)

## 3. Risk Tier Calibration
Scored probabilities are categorized into clear, actionable institutional intervention tiers:
- **Low Risk** ($\text{Probability} < 0.35$): Student making sound academic progress.
- **Medium Risk** ($0.35 \le \text{Probability} < 0.70$): Emerging academic friction; requires proactive monitoring.
- **High Risk** ($\text{Probability} \ge 0.70$): Urgent intervention required (academic counseling, financial aid review).

## 4. Execution Workflow
Run the pipeline in order:
```bash
# Step 1: Preprocess data & fit feature scaler
python data_preprocessing.py

# Step 2: Train all models, benchmark, and save champion model
python train_model.py

# Step 3: Evaluate champion model & generate high-res visualizations
python evaluate_model.py

# Step 4: Batch score all 4,424 students & persist to MySQL database
python predict_risk.py
```

## 5. Generated Artifacts
- Models: `models/model.joblib`, `models/scaler.joblib`, `models/model_meta.joblib`, `models/models_comparison.csv`
- Evaluation: `evaluation_results.csv`, `feature_importance.csv`
- Predictions: `dataset/analytics/predictions/dropout_risk_predictions.csv`
- Visualizations:
  - `visualizations/phase8/confusion_matrix_best_model.png`
  - `visualizations/phase8/feature_importance.png`
  - `visualizations/phase8/model_metrics_comparison_barchart.png`
  - `visualizations/phase8/roc_pr_curves_best_model.png`
