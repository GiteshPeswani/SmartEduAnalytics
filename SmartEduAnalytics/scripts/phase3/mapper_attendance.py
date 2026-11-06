#!/usr/bin/env python
"""
SmartEdu Analytics - Phase 3: MapReduce Analytics
Job 2: Attendance & Curricular Participation Analysis (Mapper)
Description:
    Processes attendance mode and curricular participation metrics:
    - daytime_evening_attendance (1=Daytime, 0=Evening)
    - sem1_units_enrolled, sem1_units_without_eval
    - sem2_units_enrolled, sem2_units_without_eval
    Calculates participation_rate = (1 - (unattended_units / enrolled_units)) * 100
    Evaluates < 75% alert threshold and categorical participation tiers.
    Emits: attendance_mode \t participation_rate,is_below_75,tier,count
"""

import sys
import csv

def main():
    reader = csv.reader(sys.stdin)
    
    for row in reader:
        if not row or len(row) < 34:
            continue
        
        if row[0].strip().lower() == "student_id":
            continue
            
        try:
            mode_code = row[5].strip()
            mode_label = "Daytime" if mode_code == "1" else "Evening"
            
            s1_enrolled = float(row[23].strip())
            s1_no_eval = float(row[27].strip())
            s2_enrolled = float(row[29].strip())
            s2_no_eval = float(row[33].strip())
            
            total_enrolled = s1_enrolled + s2_enrolled
            total_unattended = s1_no_eval + s2_no_eval
            
            if total_enrolled > 0:
                part_rate = (1.0 - (total_unattended / total_enrolled)) * 100.0
            else:
                part_rate = 100.0
            part_rate = max(0.0, min(100.0, part_rate))
            
            below_75 = 1 if part_rate < 75.0 else 0
            
            if part_rate >= 90.0:
                tier = "Tier1_Excellent_90+"
            elif part_rate >= 75.0:
                tier = "Tier2_Satisfactory_75-89"
            elif part_rate >= 50.0:
                tier = "Tier3_Warning_50-74"
            else:
                tier = "Tier4_Critical_<50"
                
            # Emit for specific attendance mode
            print("{0}\t{1:.2f},{2},{3},1".format(mode_label, part_rate, below_75, tier))
            # Emit for overall cohort
            print("OVERALL_COHORT\t{0:.2f},{1},{2},1".format(part_rate, below_75, tier))
        except (ValueError, IndexError):
            continue

if __name__ == "__main__":
    main()
