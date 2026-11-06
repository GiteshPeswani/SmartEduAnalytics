#!/usr/bin/env python
"""
SmartEdu Analytics - Phase 3: MapReduce Analytics
Job 2: Attendance & Curricular Participation Analysis (Reducer)
Description:
    Aggregates attendance metrics per attendance mode (Daytime, Evening, OVERALL):
    - Average attendance / participation %
    - Minimum attendance %
    - Maximum attendance %
    - Total students below 75% attendance threshold
    - Attendance distribution across ranges (>=90%, 75-89%, 50-74%, <50%)
    Emits comprehensive statistical summaries.
"""

import sys

def main():
    current_key = None
    sum_rate = 0.0
    min_rate = 100.0
    max_rate = 0.0
    below_75_count = 0
    total_count = 0
    tier_counts = {
        "Tier1_Excellent_90+": 0,
        "Tier2_Satisfactory_75-89": 0,
        "Tier3_Warning_50-74": 0,
        "Tier4_Critical_<50": 0
    }

    print("attendance_mode\ttotal_students\tavg_attendance_pct\tmin_attendance_pct\tmax_attendance_pct\tbelow_75_count\tbelow_75_pct\texcellent_90_plus\tsatisfactory_75_89\twarning_50_74\tcritical_below_50")

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split("\t")
        if len(parts) != 2:
            continue
            
        key, val_str = parts
        vals = val_str.split(",")
        if len(vals) != 4:
            continue
            
        try:
            rate = float(vals[0])
            b75 = int(vals[1])
            tier = vals[2].strip()
            cnt = int(vals[3])
        except ValueError:
            continue

        if current_key == key:
            sum_rate += rate
            if rate < min_rate:
                min_rate = rate
            if rate > max_rate:
                max_rate = rate
            below_75_count += b75
            total_count += cnt
            if tier in tier_counts:
                tier_counts[tier] += 1
        else:
            if current_key:
                emit_attendance_summary(current_key, total_count, sum_rate, min_rate, max_rate, below_75_count, tier_counts)
            current_key = key
            sum_rate = rate
            min_rate = rate
            max_rate = rate
            below_75_count = b75
            total_count = cnt
            tier_counts = {
                "Tier1_Excellent_90+": 0,
                "Tier2_Satisfactory_75-89": 0,
                "Tier3_Warning_50-74": 0,
                "Tier4_Critical_<50": 0
            }
            if tier in tier_counts:
                tier_counts[tier] += 1

    if current_key:
        emit_attendance_summary(current_key, total_count, sum_rate, min_rate, max_rate, below_75_count, tier_counts)

def emit_attendance_summary(key, count, sum_r, min_r, max_r, b75_cnt, tiers):
    if count == 0:
        return
    avg_r = sum_r / count
    b75_pct = (b75_cnt / count) * 100.0
    t1 = tiers["Tier1_Excellent_90+"]
    t2 = tiers["Tier2_Satisfactory_75-89"]
    t3 = tiers["Tier3_Warning_50-74"]
    t4 = tiers["Tier4_Critical_<50"]
    print("{0}\t{1}\t{2:.2f}\t{3:.2f}\t{4:.2f}\t{5}\t{6:.2f}%\t{7}\t{8}\t{9}\t{10}".format(
        key, count, avg_r, min_r, max_r, b75_cnt, b75_pct, t1, t2, t3, t4))

if __name__ == "__main__":
    main()
