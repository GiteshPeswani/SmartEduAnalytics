"""
SmartEdu Analytics - Phase 9: Student Analytical Profiler
File: student_analysis.py
Description:
    Constructs holistic student profiles combining demographic, academic,
    financial, and machine learning risk prediction vectors.
"""

import os
import sys
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_PATH = os.path.join(PROJECT_ROOT, "dataset", "processed", "preprocessed_student_data.csv")
PRED_PATH = os.path.join(PROJECT_ROOT, "dataset", "analytics", "predictions", "dropout_risk_predictions.csv")

class StudentProfiler:
    def __init__(self):
        self.df_data = None
        self.df_preds = None
        self.df_merged = None
        self._load_datasets()

    def _load_datasets(self):
        if not os.path.exists(DATA_PATH):
            raise FileNotFoundError(f"Missing core student dataset: {DATA_PATH}")

        self.df_data = pd.read_csv(DATA_PATH)
        
        # If predictions exist, merge them
        if os.path.exists(PRED_PATH):
            self.df_preds = pd.read_csv(PRED_PATH)
            pred_cols = ["student_id", "dropout_probability", "risk_tier", "primary_risk_factors"]
            # Avoid duplicate cols
            self.df_merged = pd.merge(self.df_data, self.df_preds[pred_cols], on="student_id", how="left")
        else:
            self.df_merged = self.df_data.copy()
            self.df_merged["dropout_probability"] = 0.0
            self.df_merged["risk_tier"] = "Low Risk"
            self.df_merged["primary_risk_factors"] = "Pending ML Scoring"

    def get_student_profile(self, student_id):
        """
        Returns a rich analytical dictionary for a single student.
        """
        records = self.df_merged[self.df_merged["student_id"].astype(str) == str(student_id)]
        if records.empty:
            return None
        
        row = records.iloc[0].to_dict()
        profile = {
            "student_id": str(row["student_id"]),
            "course_id": int(row["course_id"]),
            "admission_grade": float(row.get("admission_grade", 0.0)),
            "sem1_grade": float(row.get("sem1_grade", 0.0)),
            "sem2_grade": float(row.get("sem2_grade", 0.0)),
            "annual_grade_avg": float(row.get("annual_grade_avg", 0.0)),
            "grade_trajectory": float(row.get("grade_trajectory", 0.0)),
            "sem1_approval_rate": float(row.get("sem1_approval_rate", 0.0)),
            "sem2_approval_rate": float(row.get("sem2_approval_rate", 0.0)),
            "sem1_units_enrolled": int(row.get("sem1_units_enrolled", 0)),
            "sem1_units_approved": int(row.get("sem1_units_approved", 0)),
            "sem2_units_enrolled": int(row.get("sem2_units_enrolled", 0)),
            "sem2_units_approved": int(row.get("sem2_units_approved", 0)),
            "total_units_failed": int(row.get("total_units_failed", 0)),
            "tuition_fees_up_to_date": int(row.get("tuition_fees_up_to_date", 1)),
            "is_debtor": int(row.get("is_debtor", 0)),
            "scholarship_holder": int(row.get("scholarship_holder", 0)),
            "daytime_evening_attendance": int(row.get("daytime_evening_attendance", 1)),
            "age_at_enrollment": int(row.get("age_at_enrollment", 20)),
            "gender": int(row.get("gender", 1)),
            "is_displaced": int(row.get("is_displaced", 0)),
            "target_outcome": str(row.get("target_outcome", "Unknown")),
            "is_dropout": int(row.get("is_dropout", 0)),
            "dropout_probability": float(row.get("dropout_probability", 0.0)),
            "risk_tier": str(row.get("risk_tier", "Low Risk")),
            "primary_risk_factors": str(row.get("primary_risk_factors", ""))
        }
        return profile

    def get_all_profiles(self):
        """
        Generator yielding profile dictionaries for all students.
        """
        for _, row in self.df_merged.iterrows():
            yield row.to_dict()

if __name__ == "__main__":
    profiler = StudentProfiler()
    sample = profiler.get_student_profile(1)
    print("[SAMPLE PROFILE for Student 1]:", sample)
