#!/usr/bin/env python
"""
SmartEdu Analytics - Phase 3: MapReduce Analytics
Job 3: Student Performance Classification (Reducer)
Description:
    Aggregates student classifications:
    1. Computes total counts and proportions for each performance tier:
       (Excellent, Good, Average, Needs Improvement).
    2. Emits student-level classified roster for analytical querying.
"""

import sys

def main():
    cat_counts = {
        "Excellent": 0,
        "Good": 0,
        "Average": 0,
        "Needs_Improvement": 0
    }
    total_students = 0
    student_records = []

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split("\t")
        if len(parts) != 2:
            continue
            
        key_type, val_str = parts
        
        if key_type == "CAT_SUMMARY":
            cat_name, cnt = val_str.split(",")
            cat_name = cat_name.strip()
            cnt = int(cnt)
            if cat_name in cat_counts:
                cat_counts[cat_name] += cnt
            total_students += cnt
            
        elif key_type == "STUDENT_RECORD":
            student_records.append(val_str)

    # Output Section 1: Classification Summary Table
    print("=== STUDENT PERFORMANCE CLASSIFICATION SUMMARY ===")
    print("performance_category\tstudent_count\tpercentage_of_cohort")
    for cat in ["Excellent", "Good", "Average", "Needs_Improvement"]:
        cnt = cat_counts[cat]
        pct = (cnt / total_students * 100.0) if total_students > 0 else 0.0
        print("{0}\t{1}\t{2:.2f}%".format(cat, cnt, pct))
    print("TOTAL_COHORT\t{0}\t100.00%\n".format(total_students))

    # Output Section 2: Student-Level Classified Roster
    print("=== STUDENT-LEVEL CLASSIFIED ROSTER ===")
    print("student_id\tcourse_id\tannual_grade_avg\tperformance_category\ttarget_outcome")
    for rec in student_records:
        rec_parts = rec.split(",")
        if len(rec_parts) == 5:
            print("\t".join(rec_parts))

if __name__ == "__main__":
    main()
