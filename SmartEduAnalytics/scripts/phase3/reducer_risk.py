#!/usr/bin/env python
"""
SmartEdu Analytics - Phase 3: MapReduce Analytics
Job 5: Dropout Risk & Institutional Outcome Analysis (Reducer)
Description:
    Aggregates student records by:
    1. Administrative Outcome (Graduate, Dropout, Enrolled):
       - Average Sem 1 and Sem 2 grades
       - Average failed units
       - Tuition up-to-date %
       - Debtor %
       - Scholarship %
    2. Heuristic Academic Risk Tiers (Low_Risk, Moderate_Risk, High_Risk):
       - Cross-tabulation of heuristic risk level vs actual dropout outcome.
    3. Documentation of heuristic vs ML boundaries.
"""

import sys

def main():
    outcome_stats = {}
    risk_stats = {}

    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split("\t")
        if len(parts) != 2:
            continue
            
        group_key, val_str = parts
        vals = val_str.split(",")
        if len(vals) != 8:
            continue
            
        try:
            s1 = float(vals[0])
            s2 = float(vals[1])
            failed = float(vals[2])
            tuition = float(vals[3])
            debtor = float(vals[4])
            scholar = float(vals[5])
            cross_tag = vals[6].strip()
            cnt = int(vals[7])
        except ValueError:
            continue

        target_dict = outcome_stats if group_key.startswith("OUTCOME_") else risk_stats
        
        if group_key not in target_dict:
            target_dict[group_key] = {
                "sum_s1": 0.0,
                "sum_s2": 0.0,
                "sum_failed": 0.0,
                "sum_tuition": 0.0,
                "sum_debtor": 0.0,
                "sum_scholar": 0.0,
                "count": 0,
                "cross_tags": {}
            }
            
        d = target_dict[group_key]
        d["sum_s1"] += s1
        d["sum_s2"] += s2
        d["sum_failed"] += failed
        d["sum_tuition"] += tuition
        d["sum_debtor"] += debtor
        d["sum_scholar"] += scholar
        d["count"] += cnt
        d["cross_tags"][cross_tag] = d["cross_tags"].get(cross_tag, 0) + cnt

    # Section 1: Breakdown by Administrative Target Outcome
    print("=== PART 1: ADMINISTRATIVE INSTITUTIONAL OUTCOMES ===")
    print("outcome_status\tstudent_count\tpct_of_cohort\tavg_sem1_grade\tavg_sem2_grade\tavg_failed_units\ttuition_current_pct\tdebtor_pct\tscholarship_pct")
    total_cohort = sum(d["count"] for d in outcome_stats.values())
    
    for k, d in sorted(outcome_stats.items()):
        name = k.replace("OUTCOME_", "")
        cnt = d["count"]
        pct = (cnt / total_cohort * 100.0) if total_cohort > 0 else 0.0
        avg_s1 = d["sum_s1"] / cnt
        avg_s2 = d["sum_s2"] / cnt
        avg_failed = d["sum_failed"] / cnt
        tuition_pct = (d["sum_tuition"] / cnt) * 100.0
        debtor_pct = (d["sum_debtor"] / cnt) * 100.0
        scholar_pct = (d["sum_scholar"] / cnt) * 100.0
        print("{0}\t{1}\t{2:.2f}%\t{3:.2f}\t{4:.2f}\t{5:.2f}\t{6:.2f}%\t{7:.2f}%\t{8:.2f}%".format(
            name, cnt, pct, avg_s1, avg_s2, avg_failed, tuition_pct, debtor_pct, scholar_pct))

    # Section 2: Heuristic Academic Risk Tiers vs Ground Truth Outcomes
    print("\n=== PART 2: HEURISTIC ACADEMIC RISK LEVEL VS ACTUAL OUTCOME ===")
    print("risk_tier\ttotal_students\tgraduates\tdropouts\tenrolled\tactual_dropout_rate")
    for k, d in sorted(risk_stats.items()):
        tier_name = k.replace("RISK_", "")
        cnt = d["count"]
        grads = d["cross_tags"].get("Graduate", 0)
        drops = d["cross_tags"].get("Dropout", 0)
        enrs = d["cross_tags"].get("Enrolled", 0)
        drop_rate = (drops / cnt * 100.0) if cnt > 0 else 0.0
        print("{0}\t{1}\t{2}\t{3}\t{4}\t{5:.2f}%".format(
            tier_name, cnt, grads, drops, enrs, drop_rate))

    print("\nNOTE: Heuristic academic risk tiers are rule-based progression indicators derived from credit completion deficits and grade thresholds.")
    print("They provide early warning diagnostics and are distinct from future machine learning predictive models.")

if __name__ == "__main__":
    main()
