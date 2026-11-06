"""
SmartEdu Analytics - Phase 4: Local HiveQL Analytical Engine Simulation
Script: run_local_hive_simulation.py
Description:
    Simulates the exact Apache Hive 1.1.0 data warehouse queries locally on the
    verified Phase 1 & 2 dataset (preprocessed_student_data.csv).
    1. Executes Queries 1 through 10 + Advanced Aggregations.
    2. Writes analytical output datasets into dataset/analytics/hive/.
    3. Produces publication-quality visualizations in visualizations/phase4/.
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATASET_PATH = os.path.join(PROJECT_ROOT, "dataset", "processed", "preprocessed_student_data.csv")
HIVE_OUT_DIR = os.path.join(PROJECT_ROOT, "dataset", "analytics", "hive")
VIZ_DIR = os.path.join(PROJECT_ROOT, "visualizations", "phase4")

COURSE_MAP = {
    33: ('Biofuel Production Technologies', 'Agricultural & Bioengineering'),
    171: ('Animation and Multimedia Design', 'Arts & Multimedia'),
    8014: ('Social Service (Daytime)', 'Social Sciences'),
    9003: ('Agronomy', 'Agricultural & Bioengineering'),
    9070: ('Communication Design', 'Arts & Multimedia'),
    9085: ('Veterinary Nursing', 'Veterinary & Animal Care'),
    9119: ('Informatics Engineering', 'Computer Science & Technology'),
    9130: ('Equiniculture', 'Veterinary & Animal Care'),
    9147: ('Management', 'Business & Economics'),
    9238: ('Social Service (Evening)', 'Social Sciences'),
    9254: ('Tourism', 'Hospitality & Tourism'),
    9500: ('Nursing', 'Health & Nursing Sciences'),
    9556: ('Oral Hygiene', 'Health & Nursing Sciences'),
    9670: ('Advertising and Marketing Management', 'Business & Economics'),
    9773: ('Journalism and Communication', 'Social Sciences'),
    9853: ('Basic Education', 'Education & Teaching'),
    9991: ('Management (Evening)', 'Business & Economics')
}

def setup_dirs():
    os.makedirs(HIVE_OUT_DIR, exist_ok=True)
    os.makedirs(VIZ_DIR, exist_ok=True)

def run_analytics(df):
    setup_dirs()
    print("=" * 85)
    print(" SmartEdu Analytics - Phase 4: Apache HiveQL Analytical Engine Simulation")
    print(f" Loaded Dataset: {df.shape[0]:,} rows, {df.shape[1]} columns")
    print("=" * 85)

    # --------------------------------------------------------------------------
    # Query 1: Total Cohort & Gender Breakdown
    # --------------------------------------------------------------------------
    print("\n[HIVE QUERY 1] Total Number of Students & Gender Breakdown:")
    total = len(df)
    males = (df["gender"] == 1).sum()
    females = (df["gender"] == 0).sum()
    print(f" -> Total Students : {total:,}")
    print(f" -> Male Students  : {males:,} ({males/total*100:.2f}%)")
    print(f" -> Female Students: {females:,} ({females/total*100:.2f}%)")

    # --------------------------------------------------------------------------
    # Query 2: Overall Academic Performance Summary
    # --------------------------------------------------------------------------
    print("\n[HIVE QUERY 2] Overall Academic Grade Statistics:")
    q2 = pd.DataFrame({
        "Metric": ["Admission Grade", "Previous Qual Grade", "1st Sem Grade", "2nd Sem Grade", "Annual Grade Avg"],
        "Mean": [df["admission_grade"].mean(), df["previous_qualification_grade"].mean(), df["sem1_grade"].mean(), df["sem2_grade"].mean(), df["annual_grade_avg"].mean()],
        "StdDev": [df["admission_grade"].std(), df["previous_qualification_grade"].std(), df["sem1_grade"].std(), df["sem2_grade"].std(), df["annual_grade_avg"].std()],
        "Min": [df["admission_grade"].min(), df["previous_qualification_grade"].min(), df["sem1_grade"].min(), df["sem2_grade"].min(), df["annual_grade_avg"].min()],
        "Max": [df["admission_grade"].max(), df["previous_qualification_grade"].max(), df["sem1_grade"].max(), df["sem2_grade"].max(), df["annual_grade_avg"].max()]
    }).round(2)
    print(q2.to_string(index=False))

    # --------------------------------------------------------------------------
    # Query 3: Course-Wise Performance (Joined with Dimension Data)
    # --------------------------------------------------------------------------
    print("\n[HIVE QUERY 3] Course-Wise Academic Performance (Top 5 & Bottom 5):")
    course_list = []
    for cid, group in df.groupby("course_id"):
        cname, cdept = COURSE_MAP.get(cid, (f"Course {cid}", "General"))
        tot_enr = group["sem1_units_enrolled"].sum() + group["sem2_units_enrolled"].sum()
        tot_app = group["sem1_units_approved"].sum() + group["sem2_units_approved"].sum()
        pass_rate = (tot_app / tot_enr * 100.0) if tot_enr > 0 else 0.0
        course_list.append({
            "course_id": cid,
            "course_name": cname,
            "department": cdept,
            "students": len(group),
            "avg_admission": group["admission_grade"].mean(),
            "avg_annual_grade": group["annual_grade_avg"].mean(),
            "unit_pass_rate_pct": pass_rate
        })
    q3_df = pd.DataFrame(course_list).sort_values("avg_annual_grade", ascending=False).round(2)
    print(q3_df[["course_id", "course_name", "students", "avg_annual_grade", "unit_pass_rate_pct"]].head(5).to_string(index=False))
    print("...")
    print(q3_df[["course_id", "course_name", "students", "avg_annual_grade", "unit_pass_rate_pct"]].tail(5).to_string(index=False))

    # --------------------------------------------------------------------------
    # Query 4: Attendance Mode & Curricular Participation
    # --------------------------------------------------------------------------
    print("\n[HIVE QUERY 4] Attendance Mode & Curricular Participation:")
    total_enr = df["sem1_units_enrolled"] + df["sem2_units_enrolled"]
    total_unatt = df["sem1_units_without_eval"] + df["sem2_units_without_eval"]
    part_pct = (1.0 - (total_unatt / np.maximum(total_enr, 1))) * 100.0
    df_att = df.copy()
    df_att["participation_pct"] = part_pct.clip(0, 100)
    df_att["mode_name"] = df["daytime_evening_attendance"].map({1: "Daytime", 0: "Evening"})
    
    q4_df = df_att.groupby("mode_name").agg(
        students=("student_id", "count"),
        avg_participation=("participation_pct", "mean"),
        below_75_count=("participation_pct", lambda x: (x < 75.0).sum())
    ).reset_index()
    q4_df["pct_of_cohort"] = (q4_df["students"] / total * 100.0).round(2)
    q4_df["avg_participation"] = q4_df["avg_participation"].round(2)
    print(q4_df.to_string(index=False))

    # --------------------------------------------------------------------------
    # Query 5: Academic Performance Classification Tiers
    # --------------------------------------------------------------------------
    print("\n[HIVE QUERY 5] Performance Classification Tiers:")
    def assign_tier(g):
        if g >= 14.0:
            return "Excellent (>=14.0)"
        elif g >= 12.0:
            return "Good (12.0-13.9)"
        elif g >= 10.0:
            return "Average (10.0-11.9)"
        else:
            return "Needs Improvement (<10.0)"
            
    df_att["perf_tier"] = df["annual_grade_avg"].apply(assign_tier)
    q5_df = df_att.groupby("perf_tier").agg(
        students=("student_id", "count"),
        mean_grade=("annual_grade_avg", "mean"),
        dropouts=("target_outcome", lambda x: (x == "Dropout").sum())
    ).reset_index()
    q5_df["percentage"] = (q5_df["students"] / total * 100.0).round(2)
    q5_df["dropout_rate"] = (q5_df["dropouts"] / q5_df["students"] * 100.0).round(2)
    q5_df["mean_grade"] = q5_df["mean_grade"].round(2)
    print(q5_df.to_string(index=False))

    # --------------------------------------------------------------------------
    # Query 7: Top 10 High-Performing Students
    # --------------------------------------------------------------------------
    print("\n[HIVE QUERY 7] Top 10 High-Performing Students (Window Function Simulation):")
    top10 = df.sort_values("annual_grade_avg", ascending=False).head(10).copy()
    top10["rank"] = range(1, 11)
    top10["course_name"] = top10["course_id"].map(lambda x: COURSE_MAP.get(x, ("Unknown", ""))[0])
    print(top10[["rank", "student_id", "course_name", "admission_grade", "sem1_grade", "sem2_grade", "annual_grade_avg", "target_outcome"]].to_string(index=False))

    # --------------------------------------------------------------------------
    # Query 9: Socioeconomic & Financial Factors Impact
    # --------------------------------------------------------------------------
    print("\n[HIVE QUERY 9] Socioeconomic & Financial Impact on Attrition:")
    q9_df = df.groupby(["tuition_fees_up_to_date", "is_debtor", "scholarship_holder"]).agg(
        students=("student_id", "count"),
        avg_grade=("annual_grade_avg", "mean"),
        dropouts=("target_outcome", lambda x: (x == "Dropout").sum())
    ).reset_index()
    q9_df["dropout_rate_pct"] = (q9_df["dropouts"] / q9_df["students"] * 100.0).round(2)
    q9_df["avg_grade"] = q9_df["avg_grade"].round(2)
    q9_df["tuition_fees_up_to_date"] = q9_df["tuition_fees_up_to_date"].map({1: "Current", 0: "Arrears"})
    q9_df["is_debtor"] = q9_df["is_debtor"].map({1: "Has Debt", 0: "No Debt"})
    q9_df["scholarship_holder"] = q9_df["scholarship_holder"].map({1: "Scholarship", 0: "No Scholarship"})
    print(q9_df.sort_values("dropout_rate_pct", ascending=False).to_string(index=False))

    # --------------------------------------------------------------------------
    # Query 10: Ground-Truth Dropout Analysis
    # --------------------------------------------------------------------------
    print("\n[HIVE QUERY 10] Ground-Truth Dropout Outcome Characteristics:")
    q10_df = df.groupby("target_outcome").agg(
        students=("student_id", "count"),
        avg_sem1_grade=("sem1_grade", "mean"),
        avg_sem2_grade=("sem2_grade", "mean"),
        avg_annual_grade=("annual_grade_avg", "mean"),
        avg_failed_units=("total_units_failed", "mean"),
        tuition_current_pct=("tuition_fees_up_to_date", lambda x: (x == 1).mean() * 100.0),
        debtor_pct=("is_debtor", lambda x: (x == 1).mean() * 100.0),
        scholarship_pct=("scholarship_holder", lambda x: (x == 1).mean() * 100.0)
    ).reset_index().round(2)
    q10_df["pct_of_cohort"] = (q10_df["students"] / total * 100.0).round(2)
    print(q10_df.to_string(index=False))

    # --------------------------------------------------------------------------
    # Export Outputs into HDFS Analytics Subdirectory (dataset/analytics/hive/)
    # --------------------------------------------------------------------------
    print("\n[EXPORT] Storing Hive Analytical Output Tables...")
    
    # 1. Summary Metrics
    dir1 = os.path.join(HIVE_OUT_DIR, "summary_metrics")
    os.makedirs(dir1, exist_ok=True)
    with open(os.path.join(dir1, "part-m-00000"), "w", encoding="utf-8") as f:
        f.write(f"{total}\t{df['admission_grade'].mean():.2f}\t{df['sem1_grade'].mean():.2f}\t{df['sem2_grade'].mean():.2f}\t{df['annual_grade_avg'].mean():.2f}\t{(df['target_outcome']=='Dropout').sum()}\t{(df['target_outcome']=='Graduate').sum()}\t{(df['target_outcome']=='Enrolled').sum()}\n")

    # 2. Course Performance
    dir2 = os.path.join(HIVE_OUT_DIR, "course_performance")
    os.makedirs(dir2, exist_ok=True)
    q3_df.to_csv(os.path.join(dir2, "part-m-00000"), sep="\t", index=False)

    # 3. Dropout Risk Analysis
    dir3 = os.path.join(HIVE_OUT_DIR, "dropout_risk_analysis")
    os.makedirs(dir3, exist_ok=True)
    q10_df.to_csv(os.path.join(dir3, "part-m-00000"), sep="\t", index=False)

    print(" -> Successfully exported all analytical output partitions.")

def generate_visualizations(df):
    print("\n[VISUALIZATIONS] Generating Phase 4 Hive Analytical Charts...")
    sns.set_theme(style="whitegrid", palette="muted")

    # Chart 1: Course-Wise Performance by Department (Query 3)
    plt.figure(figsize=(14, 6))
    df_temp = df.copy()
    df_temp["course_name"] = df["course_id"].map(lambda x: COURSE_MAP.get(x, (f"Course {x}", ""))[0])
    course_order = df_temp.groupby("course_name")["annual_grade_avg"].mean().sort_values(ascending=False).index
    
    ax = sns.barplot(
        x="course_name",
        y="annual_grade_avg",
        data=df_temp,
        order=course_order,
        palette="viridis",
        ci=None
    )
    plt.axhline(10.0, color="red", linestyle="--", label="Passing Threshold (10.0/20)")
    plt.title("Hive Query 3: Academic Performance Across Degree Programs", fontsize=14, fontweight="bold")
    plt.ylabel("Average Annual Grade (0-20 Scale)", fontsize=11)
    plt.xlabel("Degree Program", fontsize=11)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.legend()
    plt.tight_layout()
    chart1_path = os.path.join(VIZ_DIR, "hive_query3_course_performance.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f" -> Saved: {chart1_path}")

    # Chart 2: Performance Classification Tiers & Dropout Share (Query 5)
    def assign_tier(g):
        if g >= 14.0:
            return "Excellent (>=14.0)"
        elif g >= 12.0:
            return "Good (12.0-13.9)"
        elif g >= 10.0:
            return "Average (10.0-11.9)"
        else:
            return "Needs Improvement (<10.0)"
    df_temp["tier"] = df["annual_grade_avg"].apply(assign_tier)
    tier_order = ["Excellent (>=14.0)", "Good (12.0-13.9)", "Average (10.0-11.9)", "Needs Improvement (<10.0)"]
    
    plt.figure(figsize=(11, 5))
    cross_tier = pd.crosstab(df_temp["tier"], df_temp["target_outcome"], normalize="index").reindex(tier_order) * 100.0
    cross_tier[["Graduate", "Enrolled", "Dropout"]].plot(
        kind="bar",
        stacked=True,
        color=["#2ecc71", "#f39c12", "#e74c3c"],
        figsize=(11, 5)
    )
    plt.title("Hive Query 5: Academic Performance Tier vs Institutional Outcome", fontsize=13, fontweight="bold")
    plt.xlabel("Performance Tier", fontsize=11)
    plt.ylabel("Proportion of Students (%)", fontsize=11)
    plt.xticks(rotation=0)
    plt.legend(title="Outcome", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    chart2_path = os.path.join(VIZ_DIR, "hive_query5_performance_classification_tiers.png")
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f" -> Saved: {chart2_path}")

    # Chart 3: Demographic Profiling - Age Brackets & Displacement (Query 8)
    def age_bracket(a):
        if a < 20:
            return "Under 20"
        elif a <= 24:
            return "20-24"
        elif a <= 29:
            return "25-29"
        else:
            return "30+"
    df_temp["age_bracket"] = df["age_at_enrollment"].apply(age_bracket)
    df_temp["displaced_label"] = df["is_displaced"].map({1: "Displaced (Living away)", 0: "Living at home"})
    
    plt.figure(figsize=(10, 5))
    sns.barplot(
        x="age_bracket",
        y="annual_grade_avg",
        hue="displaced_label",
        data=df_temp,
        palette=["#3498db", "#9b59b6"],
        ci=None
    )
    plt.title("Hive Query 8: Academic Performance by Age Bracket and Displacement Status", fontsize=13, fontweight="bold")
    plt.ylabel("Average Annual Grade (0-20)", fontsize=11)
    plt.xlabel("Age Bracket at University Enrollment", fontsize=11)
    plt.legend(title="Displacement")
    plt.tight_layout()
    chart3_path = os.path.join(VIZ_DIR, "hive_query8_age_displacement_performance.png")
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    print(f" -> Saved: {chart3_path}")

    # Chart 4: Financial Risk Factors (Query 9)
    plt.figure(figsize=(10, 5))
    fin_cross = df.groupby(["tuition_fees_up_to_date", "is_debtor"])["target_outcome"].apply(
        lambda x: (x == "Dropout").mean() * 100.0
    ).reset_index()
    fin_cross["tuition_label"] = fin_cross["tuition_fees_up_to_date"].map({1: "Tuition Current", 0: "Tuition In Arrears"})
    fin_cross["debtor_label"] = fin_cross["is_debtor"].map({1: "Has Outstanding Debt", 0: "No Debt"})
    
    pivot = fin_cross.pivot(index="tuition_label", columns="debtor_label", values="target_outcome")
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="Reds", cbar=True, annot_kws={"size": 12, "weight": "bold"})
    plt.title("Hive Query 9: Dropout Rate Heatmap (%) by Financial Status", fontsize=13, fontweight="bold")
    plt.ylabel("Tuition Fee Status", fontsize=11)
    plt.xlabel("Student Debt Status", fontsize=11)
    plt.tight_layout()
    chart4_path = os.path.join(VIZ_DIR, "hive_query9_financial_risk_heatmap.png")
    plt.savefig(chart4_path, dpi=300)
    plt.close()
    print(f" -> Saved: {chart4_path}")

    # Chart 5: Ground-Truth Outcome Academic Comparison (Query 10)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    outcome_palette = {"Graduate": "#2ecc71", "Dropout": "#e74c3c", "Enrolled": "#f39c12"}
    
    sns.boxplot(x="target_outcome", y="annual_grade_avg", data=df, ax=axes[0], palette=outcome_palette)
    axes[0].set_title("Annual Grade Average by Target Outcome", fontsize=12, fontweight="bold")
    axes[0].set_ylabel("Grade Average (0-20)")
    
    sns.barplot(x="target_outcome", y="total_units_failed", data=df, ax=axes[1], palette=outcome_palette, ci=None)
    axes[1].set_title("Average Cumulative Failed Units by Target Outcome", fontsize=12, fontweight="bold")
    axes[1].set_ylabel("Failed Units (Mean)")
    plt.tight_layout()
    chart5_path = os.path.join(VIZ_DIR, "hive_query10_attrition_metrics_comparison.png")
    plt.savefig(chart5_path, dpi=300)
    plt.close()
    print(f" -> Saved: {chart5_path}")

def main():
    if not os.path.exists(DATASET_PATH):
        print(f"[ERROR] Dataset missing: {DATASET_PATH}")
        sys.exit(1)
        
    df = pd.read_csv(DATASET_PATH)
    run_analytics(df)
    generate_visualizations(df)
    print("\n[SUCCESS] Phase 4 Hive simulation, exports, and visualizations completed successfully!\n")

if __name__ == "__main__":
    main()
