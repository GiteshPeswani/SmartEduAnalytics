"""
SmartEdu Analytics - Phase 10: Backend Database Service Layer
File: db_service.py
Description:
    Provides high-performance query abstraction across MySQL and SQLite fallback
    for KPI metrics, student rosters, risk diagnostics, and intervention tracking.
"""

import os
import sys
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE10_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(PHASE10_DIR)
sys.path.append(os.path.join(PROJECT_ROOT, "phase5_mysql"))

from config import get_mysql_connection

class DatabaseService:
    @staticmethod
    def get_kpi_overview():
        """
        Calculates aggregate dashboard metrics.
        """
        conn, is_fallback = get_mysql_connection()
        cursor = conn.cursor()

        # Total Students
        cursor.execute("SELECT COUNT(*) FROM students;")
        total_students = cursor.fetchone()[0]

        # Average Marks
        cursor.execute("SELECT AVG(annual_grade_avg) FROM performance_analytics;")
        avg_grade = cursor.fetchone()[0] or 0.0

        # Dropout Count
        cursor.execute("SELECT COUNT(*) FROM students WHERE is_dropout = 1;")
        dropout_count = cursor.fetchone()[0]

        # Risk Tier Counts
        cursor.execute("SELECT risk_tier, COUNT(*) FROM dropout_predictions GROUP BY risk_tier;")
        tier_rows = cursor.fetchall()
        tier_counts = {r[0]: r[1] for r in tier_rows}

        # Recommendations Priority Counts
        cursor.execute("SELECT priority, COUNT(*) FROM student_recommendations GROUP BY priority;")
        rec_rows = cursor.fetchall()
        rec_counts = {r[0]: r[1] for r in rec_rows}

        cursor.close()
        conn.close()

        retention_rate = ((total_students - dropout_count) / max(total_students, 1)) * 100.0

        return {
            "total_students": total_students,
            "overall_avg_grade": round(avg_grade, 2),
            "retention_rate_pct": round(retention_rate, 2),
            "dropout_rate_pct": round(100.0 - retention_rate, 2),
            "risk_tiers": {
                "High Risk": tier_counts.get("High Risk", 0),
                "Medium Risk": tier_counts.get("Medium Risk", 0),
                "Low Risk": tier_counts.get("Low Risk", 0)
            },
            "recommendations": {
                "Critical": rec_counts.get("Critical", 0),
                "High": rec_counts.get("High", 0),
                "Medium": rec_counts.get("Medium", 0),
                "Low": rec_counts.get("Low", 0)
            }
        }

    @staticmethod
    def get_students_list(page: int = 1, page_size: int = 15, search: str = "", risk_filter: str = ""):
        """
        Returns paginated, searchable, filterable student roster.
        """
        conn, is_fallback = get_mysql_connection()
        offset = (page - 1) * page_size

        query = """
        SELECT 
            s.student_id,
            s.gender,
            s.age_at_enrollment,
            p.course_id,
            p.annual_grade_avg,
            p.sem1_grade,
            p.sem2_grade,
            p.total_units_failed,
            a.participation_rate,
            a.attendance_tier,
            dp.dropout_probability,
            dp.risk_tier,
            s.target_outcome
        FROM students s
        LEFT JOIN performance_analytics p ON s.student_id = p.student_id
        LEFT JOIN attendance_analytics a ON s.student_id = a.student_id
        LEFT JOIN dropout_predictions dp ON s.student_id = dp.student_id
        WHERE 1=1
        """
        params = []

        if search:
            query += " AND s.student_id LIKE ?" if is_fallback else " AND s.student_id LIKE %s"
            params.append(f"%{search}%")

        if risk_filter and risk_filter != "ALL":
            query += " AND dp.risk_tier = ?" if is_fallback else " AND dp.risk_tier = %s"
            params.append(risk_filter)

        # Count total matches
        count_query = f"SELECT COUNT(*) FROM ({query}) as cnt_tbl;"
        cursor = conn.cursor()
        cursor.execute(count_query, params)
        total_records = cursor.fetchone()[0]

        # Add ordering and pagination
        query += " ORDER BY dp.dropout_probability DESC, s.student_id ASC"
        query += f" LIMIT {page_size} OFFSET {offset};"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        records = []
        for r in rows:
            records.append({
                "student_id": r[0],
                "gender": "Male" if r[1] == 1 else "Female",
                "age_at_enrollment": r[2],
                "course_id": r[3],
                "annual_grade_avg": round(r[4], 2) if r[4] is not None else 0.0,
                "sem1_grade": round(r[5], 2) if r[5] is not None else 0.0,
                "sem2_grade": round(r[6], 2) if r[6] is not None else 0.0,
                "total_units_failed": r[7] if r[7] is not None else 0,
                "attendance_rate": round(r[8], 2) if r[8] is not None else 0.0,
                "attendance_tier": r[9] or "Unknown",
                "dropout_probability": round(r[10], 4) if r[10] is not None else 0.0,
                "risk_tier": r[11] or "Low Risk",
                "target_outcome": r[12]
            })

        return {
            "page": page,
            "page_size": page_size,
            "total_records": total_records,
            "total_pages": (total_records + page_size - 1) // page_size,
            "data": records
        }

    @staticmethod
    def get_student_detail(student_id: str):
        """
        Returns in-depth profile, risk diagnostics, and recommendations for a single student.
        """
        conn, is_fallback = get_mysql_connection()
        cursor = conn.cursor()

        q_std = """
        SELECT 
            s.student_id, s.gender, s.age_at_enrollment, s.marital_status, s.is_displaced,
            s.admission_grade, s.target_outcome, s.is_dropout,
            p.course_id, p.annual_grade_avg, p.sem1_grade, p.sem2_grade, p.grade_trajectory,
            p.sem1_units_enrolled, p.sem1_units_approved, p.sem2_units_enrolled, p.sem2_units_approved, p.total_units_failed,
            a.participation_rate, a.attendance_tier, a.daytime_evening_attendance,
            dp.dropout_probability, dp.risk_tier, dp.model_name, dp.primary_risk_factors
        FROM students s
        LEFT JOIN performance_analytics p ON s.student_id = p.student_id
        LEFT JOIN attendance_analytics a ON s.student_id = a.student_id
        LEFT JOIN dropout_predictions dp ON s.student_id = dp.student_id
        WHERE s.student_id = ?
        """ if is_fallback else """
        SELECT 
            s.student_id, s.gender, s.age_at_enrollment, s.marital_status, s.is_displaced,
            s.admission_grade, s.target_outcome, s.is_dropout,
            p.course_id, p.annual_grade_avg, p.sem1_grade, p.sem2_grade, p.grade_trajectory,
            p.sem1_units_enrolled, p.sem1_units_approved, p.sem2_units_enrolled, p.sem2_units_approved, p.total_units_failed,
            a.participation_rate, a.attendance_tier, a.daytime_evening_attendance,
            dp.dropout_probability, dp.risk_tier, dp.model_name, dp.primary_risk_factors
        FROM students s
        LEFT JOIN performance_analytics p ON s.student_id = p.student_id
        LEFT JOIN attendance_analytics a ON s.student_id = a.student_id
        LEFT JOIN dropout_predictions dp ON s.student_id = dp.student_id
        WHERE s.student_id = %s
        """

        cursor.execute(q_std, (student_id,))
        row = cursor.fetchone()

        if not row:
            cursor.close()
            conn.close()
            return None

        # Fetch recommendations
        q_rec = ("SELECT id, category, priority, recommendation_text, action_plan, status "
                 "FROM student_recommendations WHERE student_id = ? ORDER BY id ASC;") if is_fallback else \
                ("SELECT id, category, priority, recommendation_text, action_plan, status "
                 "FROM student_recommendations WHERE student_id = %s ORDER BY id ASC;")
        cursor.execute(q_rec, (student_id,))
        recs = [
            {
                "id": r[0],
                "category": r[1],
                "priority": r[2],
                "recommendation_text": r[3],
                "action_plan": r[4],
                "status": r[5]
            }
            for r in cursor.fetchall()
        ]

        cursor.close()
        conn.close()

        return {
            "student_id": row[0],
            "gender": "Male" if row[1] == 1 else "Female",
            "age_at_enrollment": row[2],
            "marital_status": row[3],
            "is_displaced": bool(row[4]),
            "admission_grade": row[5],
            "target_outcome": row[6],
            "is_dropout": bool(row[7]),
            "course_id": row[8],
            "annual_grade_avg": round(row[9], 2) if row[9] is not None else 0.0,
            "sem1_grade": round(row[10], 2) if row[10] is not None else 0.0,
            "sem2_grade": round(row[11], 2) if row[11] is not None else 0.0,
            "grade_trajectory": round(row[12], 2) if row[12] is not None else 0.0,
            "sem1_units_enrolled": row[13],
            "sem1_units_approved": row[14],
            "sem2_units_enrolled": row[15],
            "sem2_units_approved": row[16],
            "total_units_failed": row[17],
            "attendance_rate": round(row[18], 2) if row[18] is not None else 0.0,
            "attendance_tier": row[19] or "Unknown",
            "schedule": "Daytime" if row[20] == 1 else "Evening",
            "dropout_probability": round(row[21], 4) if row[21] is not None else 0.0,
            "risk_tier": row[22] or "Low Risk",
            "model_name": row[23] or "Gradient Boosting",
            "primary_risk_factors": row[24] or "",
            "recommendations": recs
        }

    @staticmethod
    def get_analytics_performance():
        """
        Returns course-level performance and trajectory statistics for charting.
        """
        conn, is_fallback = get_mysql_connection()
        query = """
        SELECT 
            p.course_id,
            COUNT(s.student_id) as student_count,
            AVG(p.annual_grade_avg) as avg_grade,
            SUM(CASE WHEN s.is_dropout = 1 THEN 1 ELSE 0 END) as dropout_count
        FROM performance_analytics p
        JOIN students s ON p.student_id = s.student_id
        GROUP BY p.course_id
        ORDER BY student_count DESC;
        """
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        course_names = {
            33: 'Biofuel Production Tech',
            171: 'Animation & Multimedia Design',
            8014: 'Social Service (Daytime)',
            9003: 'Agronomy',
            9070: 'Communication Design',
            9085: 'Veterinary Nursing',
            9119: 'Informatics Engineering',
            9130: 'Equiniculture',
            9147: 'Management',
            9238: 'Social Service (Evening)',
            9254: 'Tourism',
            9500: 'Nursing',
            9556: 'Oral Hygiene',
            9670: 'Advertising & Marketing',
            9773: 'Journalism & Communication',
            9853: 'Basic Education',
            9991: 'Management (Evening)'
        }

        courses = []
        for r in rows:
            cid = r[0]
            cnt = r[1]
            avg_g = round(r[2], 2) if r[2] else 0.0
            drop_cnt = r[3]
            drop_rate = round((drop_cnt / cnt) * 100.0, 2)
            courses.append({
                "course_id": cid,
                "course_name": course_names.get(cid, f"Course #{cid}"),
                "student_count": cnt,
                "avg_grade": avg_g,
                "dropout_count": drop_cnt,
                "dropout_rate_pct": drop_rate
            })

        return {"courses": courses}

    @staticmethod
    def update_recommendation_status(rec_id: int, status: str):
        conn, is_fallback = get_mysql_connection()
        cursor = conn.cursor()
        q = "UPDATE student_recommendations SET status = ? WHERE id = ?;" if is_fallback else \
            "UPDATE student_recommendations SET status = %s WHERE id = %s;"
        cursor.execute(q, (status, rec_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
