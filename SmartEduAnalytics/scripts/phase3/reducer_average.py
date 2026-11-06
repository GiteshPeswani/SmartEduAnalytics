#!/usr/bin/env python
"""
SmartEdu Analytics - Phase 3: MapReduce Analytics
Job 1: Average Student Performance (Reducer)
Description:
    Aggregates academic metrics per course_id and overall cohort:
    Calculates:
    - Average admission grade
    - Average previous qualification grade
    - Average 1st semester score
    - Average 2nd semester score
    - Overall average annual performance
    Emits formatted tab-delimited records.
"""

import sys

def main():
    current_key = None
    sum_adm = 0.0
    sum_prev = 0.0
    sum_sem1 = 0.0
    sum_sem2 = 0.0
    sum_annual = 0.0
    total_count = 0

    # Print header for downstream CSV processing
    print("category_or_course\tstudent_count\tavg_admission_grade\tavg_prev_qual_grade\tavg_sem1_grade\tavg_sem2_grade\tavg_annual_grade")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        parts = line.split("\t")
        if len(parts) != 2:
            continue
        
        key, val_str = parts
        vals = val_str.split(",")
        if len(vals) != 6:
            continue
        
        try:
            adm = float(vals[0])
            prev = float(vals[1])
            s1 = float(vals[2])
            s2 = float(vals[3])
            ann = float(vals[4])
            cnt = int(vals[5])
        except ValueError:
            continue

        if current_key == key:
            sum_adm += adm
            sum_prev += prev
            sum_sem1 += s1
            sum_sem2 += s2
            sum_annual += ann
            total_count += cnt
        else:
            if current_key:
                emit_result(current_key, total_count, sum_adm, sum_prev, sum_sem1, sum_sem2, sum_annual)
            current_key = key
            sum_adm = adm
            sum_prev = prev
            sum_sem1 = s1
            sum_sem2 = s2
            sum_annual = ann
            total_count = cnt

    if current_key:
        emit_result(current_key, total_count, sum_adm, sum_prev, sum_sem1, sum_sem2, sum_annual)

def emit_result(key, count, sum_adm, sum_prev, sum_sem1, sum_sem2, sum_annual):
    if count == 0:
        return
    avg_adm = sum_adm / count
    avg_prev = sum_prev / count
    avg_s1 = sum_sem1 / count
    avg_s2 = sum_sem2 / count
    avg_ann = sum_annual / count
    label = "OVERALL_COHORT" if key == "__ALL__" else ("Course_" + str(key))
    print("{0}\t{1}\t{2:.2f}\t{3:.2f}\t{4:.2f}\t{5:.2f}\t{6:.2f}".format(
        label, count, avg_adm, avg_prev, avg_s1, avg_s2, avg_ann))

if __name__ == "__main__":
    main()
