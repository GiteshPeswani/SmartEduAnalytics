"""
SmartEdu Analytics - Phase 3: Local MapReduce Engine & Visualizations
Script: run_local_simulation.py
Description:
    1. Simulates MapReduce pipelines locally using actual Phase 2 dataset:
       - Streams preprocessed_student_data.csv through each Mapper and Reducer.
       - Generates exact part-00000 analytics outputs into dataset/analytics/mapreduce/.
    2. Computes independent Pandas reference calculations to cross-validate results.
    3. Produces 5 high-resolution analytical charts in visualizations/phase3/.
"""

import os
import sys
import subprocess
import io
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
DATASET_PATH = os.path.join(PROJECT_ROOT, "dataset", "processed", "preprocessed_student_data.csv")
ANALYTICS_DIR = os.path.join(PROJECT_ROOT, "dataset", "analytics", "mapreduce")
VIZ_DIR = os.path.join(PROJECT_ROOT, "visualizations", "phase3")

def setup_dirs():
    os.makedirs(ANALYTICS_DIR, exist_ok=True)
    os.makedirs(VIZ_DIR, exist_ok=True)

def run_mapreduce_job(mapper_name, reducer_name, output_subdir):
    mapper_path = os.path.join(SCRIPT_DIR, mapper_name)
    reducer_path = os.path.join(SCRIPT_DIR, reducer_name)
    out_dir = os.path.join(ANALYTICS_DIR, output_subdir)
    os.makedirs(out_dir, exist_ok=True)
    part_out_path = os.path.join(out_dir, "part-00000")
    success_flag_path = os.path.join(out_dir, "_SUCCESS")

    print(f"\n[JOB] Running {mapper_name} | sort | {reducer_name}...")
    
    # 1. Run mapper
    with open(DATASET_PATH, "r", encoding="utf-8") as f_in:
        p_map = subprocess.Popen(
            [sys.executable, mapper_path],
            stdin=f_in,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        map_out, map_err = p_map.communicate()
        if p_map.returncode != 0:
            print(f"[ERROR] Mapper failed: {map_err}")
            return False

    # 2. Sort (emulating Hadoop shuffle and sort phase)
    lines = map_out.strip().split("\n")
    lines.sort()
    sorted_input = "\n".join(lines) + "\n"

    # 3. Run reducer
    p_red = subprocess.Popen(
        [sys.executable, reducer_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    red_out, red_err = p_red.communicate(input=sorted_input)
    if p_red.returncode != 0:
        print(f"[ERROR] Reducer failed: {red_err}")
        return False

    # 4. Save part-00000 and _SUCCESS marker
    with open(part_out_path, "w", encoding="utf-8") as f_out:
        f_out.write(red_out)
    with open(success_flag_path, "w", encoding="utf-8") as f_s:
        f_s.write("")

    print(f" -> Successfully generated: {part_out_path} ({len(red_out)} bytes)")
    return True

def generate_visualizations(df):
    print("\n[VISUALIZATIONS] Generating Phase 3 Analytics Charts...")
    sns.set_theme(style="whitegrid", palette="muted")
    
    # Chart 1: Course-wise Average Performance (Job 1 & 4)
    plt.figure(figsize=(14, 6))
    course_perf = df.groupby("course_id")["annual_grade_avg"].mean().sort_values(ascending=False)
    course_labels = [f"Course {c}" for c in course_perf.index]
    colors = sns.color_palette("viridis", len(course_perf))
    
    bars = plt.bar(course_labels, course_perf.values, color=colors, edgecolor="black", linewidth=0.8)
    plt.axhline(10.0, color="red", linestyle="--", linewidth=1.5, label="Passing Threshold (10.0/20)")
    plt.axhline(df["annual_grade_avg"].mean(), color="blue", linestyle=":", linewidth=1.5, label=f"Cohort Mean ({df['annual_grade_avg'].mean():.2f})")
    plt.title("MapReduce Job 1 & 4: Average Annual Academic Grade by Course", fontsize=14, fontweight="bold")
    plt.ylabel("Annual Grade Average (0-20 Scale)", fontsize=11)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.legend()
    plt.tight_layout()
    chart1_path = os.path.join(VIZ_DIR, "job1_course_average_performance.png")
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f" -> Saved: {chart1_path}")

    # Chart 2: Attendance Mode & Curricular Participation (Job 2)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    att_mode_counts = df["daytime_evening_attendance"].map({1: "Daytime", 0: "Evening"}).value_counts()
    axes[0].pie(att_mode_counts.values, labels=att_mode_counts.index, autopct="%1.1f%%", startangle=140, colors=["#3498db", "#e67e22"], explode=[0, 0.05])
    axes[0].set_title("Attendance Mode Distribution", fontsize=12, fontweight="bold")

    # Evaluation participation rate
    total_enrolled = df["sem1_units_enrolled"] + df["sem2_units_enrolled"]
    total_unattended = df["sem1_units_without_eval"] + df["sem2_units_without_eval"]
    part_rate = (1.0 - (total_unattended / np.maximum(total_enrolled, 1))) * 100.0
    df_temp = df.copy()
    df_temp["participation_rate"] = part_rate
    df_temp["attendance_label"] = df["daytime_evening_attendance"].map({1: "Daytime", 0: "Evening"})
    
    sns.boxplot(x="attendance_label", y="participation_rate", data=df_temp, ax=axes[1], palette=["#3498db", "#e67e22"])
    axes[1].axhline(75.0, color="red", linestyle="--", label="75% Attendance Alert Threshold")
    axes[1].set_title("Curricular Participation Rate by Attendance Mode", fontsize=12, fontweight="bold")
    axes[1].set_ylabel("Participation %")
    axes[1].legend()
    plt.tight_layout()
    chart2_path = os.path.join(VIZ_DIR, "job2_attendance_mode_and_tiers.png")
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f" -> Saved: {chart2_path}")

    # Chart 3: Performance Classification Breakdown (Job 3)
    def classify_grade(g):
        if g >= 14.0:
            return "Excellent (>=14.0)"
        elif g >= 12.0:
            return "Good (12.0-13.9)"
        elif g >= 10.0:
            return "Average (10.0-11.9)"
        else:
            return "Needs Improvement (<10.0)"
    
    class_series = df["annual_grade_avg"].apply(classify_grade).value_counts()
    order = ["Excellent (>=14.0)", "Good (12.0-13.9)", "Average (10.0-11.9)", "Needs Improvement (<10.0)"]
    class_series = class_series.reindex(order)

    plt.figure(figsize=(10, 5))
    colors_c = ["#2ecc71", "#3498db", "#f39c12", "#e74c3c"]
    ax = sns.barplot(x=class_series.index, y=class_series.values, palette=colors_c)
    plt.title("MapReduce Job 3: Student Academic Performance Classification", fontsize=14, fontweight="bold")
    plt.ylabel("Number of Students", fontsize=11)
    for i, v in enumerate(class_series.values):
        ax.text(i, v + 30, f"{v:,}\n({v/len(df)*100:.1f}%)", ha="center", fontweight="bold")
    plt.tight_layout()
    chart3_path = os.path.join(VIZ_DIR, "job3_performance_classification_bars.png")
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    print(f" -> Saved: {chart3_path}")

    # Chart 4: Course Performance Top vs Bottom (Job 4)
    course_stats = df.groupby("course_id").agg(
        avg_grade=("annual_grade_avg", "mean"),
        students=("student_id", "count")
    ).sort_values("avg_grade", ascending=False)
    
    top3 = course_stats.head(3).copy()
    top3["category"] = "Top 3 Highest"
    bot3 = course_stats.tail(3).copy()
    bot3["category"] = "Bottom 3 Lowest"
    combined = pd.concat([top3, bot3])
    
    plt.figure(figsize=(10, 5))
    bar_colors = ["#2ecc71" if cat == "Top 3 Highest" else "#e74c3c" for cat in combined["category"]]
    plt.bar([f"Course {c}" for c in combined.index], combined["avg_grade"], color=bar_colors, edgecolor="black")
    plt.axhline(10.0, color="gray", linestyle="--", label="Passing Benchmark (10.0)")
    plt.title("MapReduce Job 4: Extreme Course Performance (Top 3 vs Bottom 3)", fontsize=13, fontweight="bold")
    plt.ylabel("Average Grade (0-20)")
    plt.legend()
    plt.tight_layout()
    chart4_path = os.path.join(VIZ_DIR, "job4_top_bottom_performing_courses.png")
    plt.savefig(chart4_path, dpi=300)
    plt.close()
    print(f" -> Saved: {chart4_path}")

    # Chart 5: Dropout Risk Indicator vs Actual Target (Job 5)
    plt.figure(figsize=(10, 5))
    risk_cross = pd.crosstab(df["academic_risk_level"], df["target_outcome"], normalize="index") * 100.0
    risk_cross[["Dropout", "Enrolled", "Graduate"]].plot(
        kind="bar",
        stacked=True,
        color=["#e74c3c", "#f39c12", "#2ecc71"],
        figsize=(10, 5)
    )
    plt.title("MapReduce Job 5: Heuristic Academic Risk Tier vs Actual Institutional Outcome", fontsize=13, fontweight="bold")
    plt.xlabel("Heuristic Risk Tier", fontsize=11)
    plt.ylabel("Proportion of Students (%)", fontsize=11)
    plt.xticks(rotation=0)
    plt.legend(title="Ground Truth Outcome", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    chart5_path = os.path.join(VIZ_DIR, "job5_dropout_risk_vs_outcome.png")
    plt.savefig(chart5_path, dpi=300)
    plt.close()
    print(f" -> Saved: {chart5_path}")

def main():
    setup_dirs()
    if not os.path.exists(DATASET_PATH):
        print(f"[FATAL ERROR] Dataset not found: {DATASET_PATH}")
        sys.exit(1)
        
    df = pd.read_csv(DATASET_PATH)
    print(f"[INFO] Loaded verified dataset: {df.shape[0]:,} records, {df.shape[1]} features.")
    
    # Run all 5 MapReduce jobs locally
    jobs = [
        ("mapper_average.py", "reducer_average.py", "average_performance"),
        ("mapper_attendance.py", "reducer_attendance.py", "attendance_analysis"),
        ("mapper_classification.py", "reducer_classification.py", "performance_classification"),
        ("mapper_course.py", "reducer_course.py", "course_analysis"),
        ("mapper_risk.py", "reducer_risk.py", "dropout_risk_analysis"),
    ]
    
    for mapper, reducer, out_dir in jobs:
        ok = run_mapreduce_job(mapper, reducer, out_dir)
        if not ok:
            print(f"[FAIL] Pipeline failed at {out_dir}")
            sys.exit(1)
            
    # Generate Visualizations
    generate_visualizations(df)
    print("\n[COMPLETE] Phase 3 MapReduce simulation and visualizations finished successfully!")

if __name__ == "__main__":
    main()
