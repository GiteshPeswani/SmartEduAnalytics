"""
SmartEdu Analytics - Phase 9: Personalized Student Recommendation Engine
File: recommendation_engine.py
Description:
    Synthesizes academic, behavioral, financial, and machine learning risk inputs
    to generate prioritized, actionable educational recommendations.
"""

import os
import sys
import pandas as pd
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(SCRIPT_DIR)

from recommendation_rules import (
    evaluate_academic_rules,
    evaluate_financial_rules,
    evaluate_attendance_and_lifestyle_rules,
    evaluate_risk_tier_rules
)
from student_analysis import StudentProfiler

PRIORITY_WEIGHTS = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1
}

class RecommendationEngine:
    def __init__(self):
        self.profiler = StudentProfiler()

    def generate_for_student(self, student_id: str):
        """
        Generates prioritized recommendations for a single student.
        """
        profile = self.profiler.get_student_profile(student_id)
        if not profile:
            return []

        raw_recs = []
        raw_recs.extend(evaluate_academic_rules(profile))
        raw_recs.extend(evaluate_financial_rules(profile))
        raw_recs.extend(evaluate_attendance_and_lifestyle_rules(profile))
        raw_recs.extend(evaluate_risk_tier_rules(profile))

        # Deduplicate recommendations by text
        seen_texts = set()
        deduped = []
        for r in raw_recs:
            if r["recommendation_text"] not in seen_texts:
                seen_texts.add(r["recommendation_text"])
                r["student_id"] = str(student_id)
                r["status"] = "Pending"
                r["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                deduped.append(r)

        # Sort by priority
        deduped.sort(key=lambda x: PRIORITY_WEIGHTS.get(x["priority"], 0), reverse=True)
        return deduped

    def generate_all(self):
        """
        Generates recommendations for all students across the institution.
        """
        all_recommendations = []
        print("[ENGINE] Generating personalized intervention pathways across cohort...")

        for profile in self.profiler.get_all_profiles():
            sid = str(profile["student_id"])
            recs = self.generate_for_student(sid)
            all_recommendations.extend(recs)

        df_recs = pd.DataFrame(all_recommendations)
        print(f"[ENGINE GENERATED] Total {len(df_recs):,} personalized action items across {len(self.profiler.df_merged):,} students.")
        return df_recs

if __name__ == "__main__":
    engine = RecommendationEngine()
    test_recs = engine.generate_for_student("STD_10001")
    print("\n--- SAMPLE INTERVENTION PLAN FOR STD_10001 ---")
    for r in test_recs:
        print(f"[{r['priority'].upper()}] ({r['category']}): {r['recommendation_text']}")
        print(f"   -> Action Plan: {r['action_plan']}")
