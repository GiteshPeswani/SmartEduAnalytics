"""
SmartEdu Analytics - Phase 5: MySQL Analytics Runner
File: run_mysql_analytics.py
Description:
    Executes the suite of relational analytical queries against the smartedu database,
    demonstrating multi-table JOINs, aggregations, GROUP BY, HAVING, and Views.
"""

import os
import sys
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import get_mysql_connection, get_connection_info

def run_queries():
    print("=" * 85)
    print(" SmartEdu Analytics - Phase 5: MySQL Relational Analytics Engine")
    print(f" Engine: {get_connection_info()}")
    print("=" * 85)

    conn, is_sqlite = get_mysql_connection()

    queries = [
        ("Query 1: Total Cohort & Core Baseline Demographics", """
            SELECT 
                COUNT(*) AS total_students,
                ROUND(AVG(admission_grade), 2) AS avg_admission,
                ROUND(MIN(admission_grade), 2) AS min_admission,
                ROUND(MAX(admission_grade), 2) AS max_admission,
                SUM(CASE WHEN gender = 1 THEN 1 ELSE 0 END) AS male_count,
                SUM(CASE WHEN gender = 0 THEN 1 ELSE 0 END) AS female_count,
                ROUND(SUM(CASE WHEN is_displaced = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS displaced_pct
            FROM students
        """),
        ("Query 2: Overall Academic Marks & Credit Failure Summary", """
            SELECT 
                ROUND(AVG(sem1_grade), 2) AS avg_sem1_grade,
                ROUND(AVG(sem2_grade), 2) AS avg_sem2_grade,
                ROUND(AVG(annual_grade_avg), 2) AS avg_annual_grade,
                ROUND(AVG(total_units_failed), 2) AS avg_failed_units,
                ROUND(AVG(sem1_approval_rate) * 100, 2) AS avg_sem1_pass_pct,
                ROUND(AVG(sem2_approval_rate) * 100, 2) AS avg_sem2_pass_pct
            FROM performance_analytics
        """),
        ("Query 3: Course-Wise Performance Analysis (JOIN with hive_results)", """
            SELECT 
                h.performance_rank AS rank,
                h.course_id,
                h.course_name,
                COUNT(p.student_id) AS students,
                ROUND(AVG(p.annual_grade_avg), 2) AS avg_grade,
                ROUND(AVG(p.total_units_failed), 2) AS failed_units,
                ROUND(AVG(a.participation_rate), 2) AS attendance_pct
            FROM performance_analytics p
            JOIN hive_results h ON p.course_id = h.course_id
            JOIN attendance_analytics a ON p.student_id = a.student_id
            GROUP BY h.performance_rank, h.course_id, h.course_name
            ORDER BY h.performance_rank ASC
            LIMIT 8
        """),
        ("Query 4: Performance Classification Tiers & Attrition", """
            SELECT 
                p.performance_category,
                COUNT(*) AS total_students,
                ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM performance_analytics), 2) AS pct_of_cohort,
                ROUND(AVG(p.annual_grade_avg), 2) AS category_avg_grade,
                SUM(CASE WHEN s.target_outcome = 'Dropout' THEN 1 ELSE 0 END) AS dropouts,
                ROUND(SUM(CASE WHEN s.target_outcome = 'Dropout' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS dropout_rate_pct
            FROM performance_analytics p
            JOIN students s ON p.student_id = s.student_id
            GROUP BY p.performance_category
            ORDER BY category_avg_grade DESC
        """),
        ("Query 5: Low Attendance At-Risk Students (< 75% Participation)", """
            SELECT 
                s.student_id,
                p.course_id,
                a.participation_rate,
                p.annual_grade_avg,
                r.academic_risk_level,
                s.target_outcome
            FROM students s
            JOIN attendance_analytics a ON s.student_id = a.student_id
            JOIN performance_analytics p ON s.student_id = p.student_id
            JOIN risk_indicators r ON s.student_id = r.student_id
            WHERE a.is_below_75_alert = 1
            ORDER BY a.participation_rate ASC, p.annual_grade_avg ASC
            LIMIT 5
        """),
        ("Query 6: Top 5 Highest-Performing Students", """
            SELECT 
                s.student_id,
                h.course_name,
                s.admission_grade,
                p.sem1_grade,
                p.sem2_grade,
                p.annual_grade_avg,
                s.target_outcome
            FROM students s
            JOIN performance_analytics p ON s.student_id = p.student_id
            JOIN hive_results h ON p.course_id = h.course_id
            ORDER BY p.annual_grade_avg DESC
            LIMIT 5
        """),
        ("Query 7: High-Dropout Degree Programs (HAVING Clause)", """
            SELECT 
                h.course_id,
                h.course_name,
                COUNT(s.student_id) AS student_count,
                ROUND(AVG(p.annual_grade_avg), 2) AS avg_course_grade,
                SUM(s.is_dropout) AS dropout_count,
                ROUND(SUM(s.is_dropout) * 100.0 / COUNT(s.student_id), 2) AS dropout_rate_pct
            FROM hive_results h
            JOIN performance_analytics p ON h.course_id = p.course_id
            JOIN students s ON p.student_id = s.student_id
            GROUP BY h.course_id, h.course_name
            HAVING COUNT(s.student_id) >= 100 AND dropout_rate_pct >= 35.0
            ORDER BY dropout_rate_pct DESC
        """)
    ]

    for title, sql in queries:
        print(f"\n--- [{title}] ---")
        df_res = pd.read_sql_query(sql, conn)
        print(df_res.to_string(index=False))

    conn.close()
    print("\n" + "=" * 85)
    print(" [SUCCESS] All MySQL analytics queries executed successfully!")
    print("=" * 85 + "\n")

if __name__ == "__main__":
    run_queries()
