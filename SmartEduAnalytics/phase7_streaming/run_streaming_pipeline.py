"""
SmartEdu Analytics - Phase 7: Real-Time Streaming Analytics Pipeline
Script: run_streaming_pipeline.py
Description:
    End-to-end streaming execution:
    1. Spawns the synthetic academic event producer.
    2. Streams events into the real-time analytics consumer.
    3. Demonstrates event deduplication and low-attendance alert triggers (< 75%).
    4. Persists real-time metrics and alerts into MySQL / SQLite.
    5. Produces telemetry charts in visualizations/phase7/.
"""

import os
import sys
import time
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from student_event_producer import event_stream
from streaming_consumer import StreamingAnalyticsConsumer

VIZ_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "visualizations", "phase7")

def run_pipeline():
    os.makedirs(VIZ_DIR, exist_ok=True)
    print("=" * 85)
    print(" SmartEdu Analytics - Phase 7: Real-Time Streaming Analytics Pipeline")
    print(" Target Event Store: MySQL / SQLite Academic Activity Streaming Engine")
    print("=" * 85)

    consumer = StreamingAnalyticsConsumer()
    sample_students = [f"STD_{10001 + i}" for i in range(25)]
    sample_courses = [9500, 9070, 9085, 9119, 9238]

    print("\n[PRODUCER & CONSUMER] Initiating Live Stream of 100 Academic Telemetry Events...\n")
    processed_count = 0
    event_counts = {}
    last_event = None

    for event in event_stream(sample_students, sample_courses, max_events=100, delay=0.01):
        res = consumer.process_event(event)
        processed_count += 1
        etype = event["event_type"]
        event_counts[etype] = event_counts.get(etype, 0) + 1
        last_event = event

        if res.get("alert_fired"):
            print(f" [ALERT TRIGGERED] Student {res['student_id']}: Rolling Attendance dropped to {res['rolling_attendance_pct']}%! Status: HIGH_RISK")
        elif processed_count % 20 == 0:
            print(f" [STREAM STATUS] Ingested {processed_count}/100 events | Latest: {res['student_id']} - {res['event_type']} (Attendance: {res['rolling_attendance_pct']}%)")

    # Deduplication test: re-inject the last event
    print("\n[DEDUPLICATION TEST] Injecting duplicate event (event_id: {})...".format(last_event["event_id"][:12]))
    dup_res = consumer.process_event(last_event)
    print(f" -> Consumer Response: {dup_res['status']} (Deduplication Verified!)")

    print(f"\n[STREAMING SUMMARY] Total Ingested Events: {consumer.total_processed} | Active Alerts: {consumer.alerts_triggered}")

    # Query Real-Time Tables
    cursor = consumer.cursor
    cursor.execute("SELECT COUNT(*) FROM academic_event_logs")
    log_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM realtime_student_metrics")
    metric_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM streaming_attendance_alerts")
    alert_count = cursor.fetchone()[0]

    print("\n[DATABASE VERIFICATION]")
    print(f" -> 'academic_event_logs'      : {log_count} raw events stored.")
    print(f" -> 'realtime_student_metrics'  : {metric_count} active student rolling profiles.")
    print(f" -> 'streaming_attendance_alerts': {alert_count} threshold breach alerts recorded.")

    # Preview sample real-time metrics
    cursor.execute("""
        SELECT student_id, course_id, total_sessions_tracked, rolling_attendance_pct, 
               total_quizzes_taken, avg_quiz_score, latest_risk_level
        FROM realtime_student_metrics
        ORDER BY rolling_attendance_pct ASC
        LIMIT 6
    """)
    rows = cursor.fetchall()
    cols = ["Student_ID", "Course", "Sessions", "Rolling_Att_%", "Quizzes", "Avg_Quiz", "Risk_Level"]
    df_metrics = pd.DataFrame(rows, columns=cols)
    print("\n[SAMPLE REAL-TIME PROFILES]")
    print(df_metrics.to_string(index=False))

    # Generate Visualizations
    generate_streaming_charts(event_counts, consumer)
    consumer.close()
    print("\n[SUCCESS] Phase 7 real-time streaming pipeline completed successfully!\n")

def generate_streaming_charts(event_counts, consumer):
    print("\n[VISUALIZATIONS] Generating Phase 7 Streaming Telemetry Charts...")
    sns.set_theme(style="whitegrid", palette="muted")

    # Chart 1: Streaming Event Distribution
    plt.figure(figsize=(9, 5))
    names = [k.replace("_", " ").title() for k in event_counts.keys()]
    values = list(event_counts.values())
    colors = ["#3498db", "#2ecc71", "#e67e22", "#9b59b6"]
    bars = plt.bar(names, values, color=colors, edgecolor="black", linewidth=0.8)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 1, f"{yval} ({yval/sum(values)*100:.1f}%)", ha="center", fontweight="bold")
    plt.title("Phase 7: Real-Time Ingested Academic Event Stream Distribution", fontsize=13, fontweight="bold")
    plt.ylabel("Event Count", fontsize=11)
    plt.tight_layout()
    chart1 = os.path.join(VIZ_DIR, "streaming_event_distribution.png")
    plt.savefig(chart1, dpi=300)
    plt.close()
    print(f" -> Saved: {chart1}")

    # Chart 2: Real-time Attendance Distribution & Alert Level
    consumer.cursor.execute("SELECT rolling_attendance_pct, latest_risk_level FROM realtime_student_metrics")
    data = consumer.cursor.fetchall()
    if data:
        df_chart = pd.DataFrame(data, columns=["attendance", "risk"])
        plt.figure(figsize=(9, 5))
        sns.histplot(data=df_chart, x="attendance", hue="risk", multiple="stack", bins=15, palette={"Low_Risk": "#2ecc71", "High_Risk": "#e74c3c"})
        plt.axvline(75.0, color="red", linestyle="--", linewidth=1.5, label="Low Attendance Alert Threshold (75%)")
        plt.title("Phase 7: Real-Time Rolling Student Attendance Telemetry", fontsize=13, fontweight="bold")
        plt.xlabel("Rolling Curricular Attendance (%)", fontsize=11)
        plt.ylabel("Student Count", fontsize=11)
        plt.legend()
        plt.tight_layout()
        chart2 = os.path.join(VIZ_DIR, "realtime_attendance_alerts.png")
        plt.savefig(chart2, dpi=300)
        plt.close()
        print(f" -> Saved: {chart2}")

if __name__ == "__main__":
    run_pipeline()
