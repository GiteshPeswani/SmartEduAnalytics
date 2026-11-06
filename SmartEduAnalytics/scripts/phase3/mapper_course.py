#!/usr/bin/env python
"""
SmartEdu Analytics - Phase 3: MapReduce Analytics
Job 4: Course Performance Analysis (Mapper)
Description:
    Analyzes academic performance by academic course/degree program:
    - course_id
    - annual_grade_avg
    - sem1_units_enrolled, sem1_units_approved
    - sem2_units_enrolled, sem2_units_approved
    Emits: course_id \t annual_grade,units_enrolled,units_approved,1
"""

import sys
import csv

def main():
    reader = csv.reader(sys.stdin)
    
    for row in reader:
        if not row or len(row) < 41:
            continue
            
        if row[0].strip().lower() == "student_id":
            continue
            
        try:
            course_id = row[4].strip()
            annual_grade = float(row[40].strip())
            
            s1_enrolled = float(row[23].strip())
            s1_approved = float(row[25].strip())
            s2_enrolled = float(row[29].strip())
            s2_approved = float(row[31].strip())
            
            total_enrolled = s1_enrolled + s2_enrolled
            total_approved = s1_approved + s2_approved
            
            print("{0}\t{1:.2f},{2:.1f},{3:.1f},1".format(course_id, annual_grade, total_enrolled, total_approved))
        except (ValueError, IndexError):
            continue

if __name__ == "__main__":
    main()
