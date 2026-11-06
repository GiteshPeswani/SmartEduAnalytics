#!/usr/bin/env python
"""
SmartEdu Analytics - Phase 3: MapReduce Analytics
Job 1: Average Student Performance (Mapper)
Description:
    Reads preprocessed student records from standard input.
    Extracts course_id (key) and academic score metrics:
    - admission_grade
    - previous_qualification_grade
    - sem1_grade
    - sem2_grade
    - annual_grade_avg
    Emits: course_id \t admission_grade,prev_grade,sem1_grade,sem2_grade,annual_avg,count
"""

import sys
import csv

def main():
    # csv.reader handles quoted fields and commas safely
    reader = csv.reader(sys.stdin)
    
    for row in reader:
        if not row or len(row) < 41:
            continue
        
        # Skip header
        if row[0].strip().lower() == "student_id":
            continue
        
        try:
            course_id = row[4].strip()
            prev_grade = float(row[7].strip())
            admission_grade = float(row[13].strip())
            sem1_grade = float(row[26].strip())
            sem2_grade = float(row[32].strip())
            annual_avg = float(row[40].strip())
            
            # Emit per-course metrics
            print("{0}\t{1:.2f},{2:.2f},{3:.2f},{4:.2f},{5:.2f},1".format(
                course_id, admission_grade, prev_grade, sem1_grade, sem2_grade, annual_avg))
            # Emit global accumulator with special key '__ALL__'
            print("__ALL__\t{0:.2f},{1:.2f},{2:.2f},{3:.2f},{4:.2f},1".format(
                admission_grade, prev_grade, sem1_grade, sem2_grade, annual_avg))
        except (ValueError, IndexError):
            # Skip malformed row
            continue

if __name__ == "__main__":
    main()
