#!/usr/bin/env python
"""
SmartEdu Analytics - Phase 3: MapReduce Analytics
Job 3: Student Performance Classification (Mapper)
Description:
    Classifies each student into academic performance categories based on annual_grade_avg:
    - Excellent         : grade >= 14.0 (>= 70%)
    - Good              : 12.0 <= grade < 14.0 (60% - 70%)
    - Average           : 10.0 <= grade < 12.0 (50% - 60%)
    - Needs Improvement : grade < 10.0 (< 50% passing threshold)
    Emits student-level record and category summary counter:
    Emits:
      CATEGORY \t <category_name>,1
      STUDENT  \t student_id,course_id,annual_grade_avg,category,target_outcome
"""

import sys
import os
import csv

# Configurable thresholds via environment or defaults
THRESH_EXCELLENT = float(os.environ.get("THRESH_EXCELLENT", 14.0))
THRESH_GOOD = float(os.environ.get("THRESH_GOOD", 12.0))
THRESH_AVERAGE = float(os.environ.get("THRESH_AVERAGE", 10.0))

def classify_grade(grade):
    if grade >= THRESH_EXCELLENT:
        return "Excellent"
    elif grade >= THRESH_GOOD:
        return "Good"
    elif grade >= THRESH_AVERAGE:
        return "Average"
    else:
        return "Needs_Improvement"

def main():
    reader = csv.reader(sys.stdin)
    
    for row in reader:
        if not row or len(row) < 41:
            continue
            
        if row[0].strip().lower() == "student_id":
            continue
            
        try:
            student_id = row[0].strip()
            course_id = row[4].strip()
            annual_grade = float(row[40].strip())
            target_outcome = row[37].strip()
            
            category = classify_grade(annual_grade)
            
            # Emit category counter
            print("CAT_SUMMARY\t{0},1".format(category))
            # Emit student classification
            print("STUDENT_RECORD\t{0},{1},{2:.2f},{3},{4}".format(
                student_id, course_id, annual_grade, category, target_outcome))
        except (ValueError, IndexError):
            continue

if __name__ == "__main__":
    main()
