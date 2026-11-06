#!/usr/bin/env python
"""
SmartEdu Analytics - Phase 3: MapReduce Analytics
Job 4: Course Performance Analysis (Reducer)
Description:
    Aggregates performance metrics across all 17 university courses:
    - Calculates average grade, total enrolled units, and approval pass rate % per course.
    - Sorts and ranks courses to identify the Highest and Lowest performing academic programs.
"""

import sys

def main():
    course_data = {}

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split("\t")
        if len(parts) != 2:
            continue
            
        course_id, val_str = parts
        vals = val_str.split(",")
        if len(vals) != 4:
            continue
            
        try:
            grade = float(vals[0])
            enrolled = float(vals[1])
            approved = float(vals[2])
            cnt = int(vals[3])
        except ValueError:
            continue

        if course_id not in course_data:
            course_data[course_id] = {
                "sum_grade": 0.0,
                "sum_enrolled": 0.0,
                "sum_approved": 0.0,
                "count": 0
            }
            
        course_data[course_id]["sum_grade"] += grade
        course_data[course_id]["sum_enrolled"] += enrolled
        course_data[course_id]["sum_approved"] += approved
        course_data[course_id]["count"] += cnt

    # Process metrics
    results = []
    for cid, d in course_data.items():
        cnt = d["count"]
        if cnt == 0:
            continue
        avg_grade = d["sum_grade"] / cnt
        avg_enrolled = d["sum_enrolled"] / cnt
        avg_approved = d["sum_approved"] / cnt
        pass_rate = (d["sum_approved"] / d["sum_enrolled"] * 100.0) if d["sum_enrolled"] > 0 else 0.0
        results.append({
            "course_id": cid,
            "students": cnt,
            "avg_grade": avg_grade,
            "avg_enrolled": avg_enrolled,
            "avg_approved": avg_approved,
            "pass_rate": pass_rate
        })

    # Sort courses by average grade descending
    results.sort(key=lambda x: x["avg_grade"], reverse=True)

    print("=== COURSE PERFORMANCE RANKINGS ===")
    print("rank\tcourse_id\tstudent_count\tavg_annual_grade\tavg_units_enrolled\tavg_units_approved\tunit_pass_rate_pct")
    for rank, r in enumerate(results, start=1):
        print("{0}\tCourse_{1}\t{2}\t{3:.2f}\t{4:.2f}\t{5:.2f}\t{6:.2f}%".format(
            rank, r['course_id'], r['students'], r['avg_grade'], r['avg_enrolled'], r['avg_approved'], r['pass_rate']))

    print("\n=== TOP 3 HIGHEST PERFORMING COURSES ===")
    for rank, r in enumerate(results[:3], start=1):
        print("Top {0}: Course_{1} - Avg Grade: {2:.2f}/20 (Pass Rate: {3:.2f}%, Students: {4})".format(
            rank, r['course_id'], r['avg_grade'], r['pass_rate'], r['students']))

    print("\n=== TOP 3 LOWEST PERFORMING COURSES ===")
    for rank, r in enumerate(reversed(results[-3:]), start=1):
        print("Bottom {0}: Course_{1} - Avg Grade: {2:.2f}/20 (Pass Rate: {3:.2f}%, Students: {4})".format(
            rank, r['course_id'], r['avg_grade'], r['pass_rate'], r['students']))

if __name__ == "__main__":
    main()
