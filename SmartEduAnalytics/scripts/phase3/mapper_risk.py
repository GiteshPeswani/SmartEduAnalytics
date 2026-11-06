#!/usr/bin/env python
"""
SmartEdu Analytics - Phase 3: MapReduce Analytics
Job 5: Dropout Risk & Institutional Outcome Analysis (Mapper)
Description:
    Processes student attrition and academic struggle metrics:
    - target_outcome (Graduate, Dropout, Enrolled)
    - academic_risk_level (Low_Risk, Moderate_Risk, High_Risk)
    - sem1_grade, sem2_grade
    - total_units_failed
    - tuition_fees_up_to_date
    - is_debtor
    - scholarship_holder
    Emits key-value records for both administrative outcome and heuristic risk level.
"""

import sys
import csv

def main():
    reader = csv.reader(sys.stdin)
    
    for row in reader:
        if not row or len(row) < 46:
            continue
            
        if row[0].strip().lower() == "student_id":
            continue
            
        try:
            target = row[37].strip()
            risk_level = row[44].strip()
            s1_grade = float(row[26].strip())
            s2_grade = float(row[32].strip())
            failed_units = float(row[42].strip())
            tuition_ok = float(row[17].strip())
            debtor = float(row[16].strip())
            scholarship = float(row[19].strip())
            
            # Key 1: Grouped by administrative target outcome
            print("OUTCOME_{0}\t{1:.2f},{2:.2f},{3:.1f},{4},{5},{6},{7},1".format(
                target, s1_grade, s2_grade, failed_units, tuition_ok, debtor, scholarship, risk_level))
            
            # Key 2: Grouped by heuristic academic risk level
            print("RISK_{0}\t{1:.2f},{2:.2f},{3:.1f},{4},{5},{6},{7},1".format(
                risk_level, s1_grade, s2_grade, failed_units, tuition_ok, debtor, scholarship, target))
        except (ValueError, IndexError):
            continue

if __name__ == "__main__":
    main()
