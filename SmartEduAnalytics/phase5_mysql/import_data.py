"""
SmartEdu Analytics - Phase 5: MySQL Data Ingestion & Integration
File: import_data.py
Description:
    Reads preprocessed student CSV data and integrates Phase 3/4 analytics
    into the MySQL database across relational tables:
    - students
    - performance_analytics
    - attendance_analytics
    - risk_indicators
    - hive_results
"""

import os
import sys
import pandas as pd
import numpy as np

# Add phase5_mysql to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import get_mysql_connection, CSV_DATA_PATH, SQLITE_FALLBACK_DB, get_connection_info

COURSE_NAMES = {
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

def assign_perf_category(grade):
    if grade >= 14.0:
        return "Excellent"
    elif grade >= 12.0:
        return "Good"
    elif grade >= 10.0:
        return "Average"
    else:
        return "Needs_Improvement"

def assign_attendance_tier(rate):
    if rate >= 90.0:
        return "Tier1_Excellent_90+"
    elif rate >= 75.0:
        return "Tier2_Satisfactory_75-89"
    elif rate >= 50.0:
        return "Tier3_Warning_50-74"
    else:
        return "Tier4_Critical_<50"

def init_tables(conn, is_sqlite):
    cursor = conn.cursor()
    if is_sqlite:
        cursor.execute("DROP TABLE IF EXISTS risk_indicators;")
        cursor.execute("DROP TABLE IF EXISTS attendance_analytics;")
        cursor.execute("DROP TABLE IF EXISTS performance_analytics;")
        cursor.execute("DROP TABLE IF EXISTS hive_results;")
        cursor.execute("DROP TABLE IF EXISTS students;")
        
        cursor.execute("""
        CREATE TABLE students (
            student_id TEXT PRIMARY KEY,
            marital_status INTEGER,
            gender INTEGER,
            age_at_enrollment INTEGER,
            is_displaced INTEGER,
            is_international INTEGER,
            nationality INTEGER,
            admission_grade REAL,
            previous_qualification_grade REAL,
            target_outcome TEXT,
            is_dropout INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        cursor.execute("""
        CREATE TABLE performance_analytics (
            student_id TEXT PRIMARY KEY,
            course_id INTEGER,
            sem1_grade REAL,
            sem2_grade REAL,
            annual_grade_avg REAL,
            grade_trajectory REAL,
            sem1_units_enrolled INTEGER,
            sem1_units_approved INTEGER,
            sem2_units_enrolled INTEGER,
            sem2_units_approved INTEGER,
            total_units_failed INTEGER,
            sem1_approval_rate REAL,
            sem2_approval_rate REAL,
            performance_category TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        );
        """)
        cursor.execute("""
        CREATE TABLE attendance_analytics (
            student_id TEXT PRIMARY KEY,
            daytime_evening_attendance INTEGER,
            sem1_units_without_eval INTEGER,
            sem2_units_without_eval INTEGER,
            total_units_unattended INTEGER,
            participation_rate REAL,
            is_below_75_alert INTEGER,
            attendance_tier TEXT,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        );
        """)
        cursor.execute("""
        CREATE TABLE risk_indicators (
            student_id TEXT PRIMARY KEY,
            academic_risk_score REAL,
            academic_risk_level TEXT,
            tuition_fees_up_to_date INTEGER,
            is_debtor INTEGER,
            scholarship_holder INTEGER,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        );
        """)
        cursor.execute("""
        CREATE TABLE hive_results (
            course_id INTEGER PRIMARY KEY,
            course_name TEXT,
            course_department TEXT,
            student_count INTEGER,
            avg_annual_grade REAL,
            unit_pass_rate_pct REAL,
            performance_rank INTEGER
        );
        """)
        conn.commit()
    else:
        # Read and run schema.sql on MySQL
        with open(os.path.join(os.path.dirname(__file__), "schema.sql"), "r") as f:
            statements = f.read().split(";")
            for stmt in statements:
                stmt = stmt.strip()
                if stmt:
                    cursor.execute(stmt)

def import_datasets():
    print("=" * 80)
    print(" SmartEdu Analytics - Phase 5: MySQL Data Ingestion & Integration")
    print(f" Target Database Engine: {get_connection_info()}")
    print("=" * 80)

    if not os.path.exists(CSV_DATA_PATH):
        raise FileNotFoundError(f"Missing preprocessed dataset: {CSV_DATA_PATH}")

    df = pd.read_csv(CSV_DATA_PATH)
    print(f"[INFO] Loaded verified dataset: {len(df):,} records, {len(df.columns)} columns.")

    conn, is_sqlite = get_mysql_connection()
    init_tables(conn, is_sqlite)
    cursor = conn.cursor()

    # 1. Populate students
    print("[INGESTION] Inserting into 'students' table...")
    students_data = []
    for _, r in df.iterrows():
        students_data.append((
            str(r["student_id"]),
            int(r["marital_status"]),
            int(r["gender"]),
            int(r["age_at_enrollment"]),
            int(r["is_displaced"]),
            int(r["is_international"]),
            int(r["nationality"]),
            float(r["admission_grade"]),
            float(r["previous_qualification_grade"]),
            str(r["target_outcome"]),
            int(r["is_dropout"])
        ))
    
    ph = "?" if is_sqlite else "%s"
    cursor.executemany(f"""
        INSERT INTO students (
            student_id, marital_status, gender, age_at_enrollment,
            is_displaced, is_international, nationality, admission_grade,
            previous_qualification_grade, target_outcome, is_dropout
        ) VALUES ({','.join([ph]*11)})
    """, students_data)
    print(f" -> Inserted {len(students_data):,} records into 'students'.")

    # 2. Populate performance_analytics
    print("[INGESTION] Inserting into 'performance_analytics' table...")
    perf_data = []
    for _, r in df.iterrows():
        perf_cat = assign_perf_category(float(r["annual_grade_avg"]))
        perf_data.append((
            str(r["student_id"]),
            int(r["course_id"]),
            float(r["sem1_grade"]),
            float(r["sem2_grade"]),
            float(r["annual_grade_avg"]),
            float(r["grade_trajectory"]),
            int(r["sem1_units_enrolled"]),
            int(r["sem1_units_approved"]),
            int(r["sem2_units_enrolled"]),
            int(r["sem2_units_approved"]),
            int(r["total_units_failed"]),
            float(r["sem1_approval_rate"]),
            float(r["sem2_approval_rate"]),
            perf_cat
        ))
    cursor.executemany(f"""
        INSERT INTO performance_analytics (
            student_id, course_id, sem1_grade, sem2_grade, annual_grade_avg,
            grade_trajectory, sem1_units_enrolled, sem1_units_approved,
            sem2_units_enrolled, sem2_units_approved, total_units_failed,
            sem1_approval_rate, sem2_approval_rate, performance_category
        ) VALUES ({','.join([ph]*14)})
    """, perf_data)
    print(f" -> Inserted {len(perf_data):,} records into 'performance_analytics'.")

    # 3. Populate attendance_analytics
    print("[INGESTION] Inserting into 'attendance_analytics' table...")
    att_data = []
    for _, r in df.iterrows():
        tot_enr = r["sem1_units_enrolled"] + r["sem2_units_enrolled"]
        tot_unatt = r["sem1_units_without_eval"] + r["sem2_units_without_eval"]
        part_rate = (1.0 - (tot_unatt / max(tot_enr, 1))) * 100.0
        part_rate = max(0.0, min(100.0, part_rate))
        is_alert = 1 if part_rate < 75.0 else 0
        tier = assign_attendance_tier(part_rate)
        att_data.append((
            str(r["student_id"]),
            int(r["daytime_evening_attendance"]),
            int(r["sem1_units_without_eval"]),
            int(r["sem2_units_without_eval"]),
            int(tot_unatt),
            float(round(part_rate, 2)),
            int(is_alert),
            tier
        ))
    cursor.executemany(f"""
        INSERT INTO attendance_analytics (
            student_id, daytime_evening_attendance, sem1_units_without_eval,
            sem2_units_without_eval, total_units_unattended, participation_rate,
            is_below_75_alert, attendance_tier
        ) VALUES ({','.join([ph]*8)})
    """, att_data)
    print(f" -> Inserted {len(att_data):,} records into 'attendance_analytics'.")

    # 4. Populate risk_indicators
    print("[INGESTION] Inserting into 'risk_indicators' table...")
    risk_data = []
    for _, r in df.iterrows():
        risk_data.append((
            str(r["student_id"]),
            float(r["academic_risk_score"]),
            str(r["academic_risk_level"]),
            int(r["tuition_fees_up_to_date"]),
            int(r["is_debtor"]),
            int(r["scholarship_holder"])
        ))
    cursor.executemany(f"""
        INSERT INTO risk_indicators (
            student_id, academic_risk_score, academic_risk_level,
            tuition_fees_up_to_date, is_debtor, scholarship_holder
        ) VALUES ({','.join([ph]*6)})
    """, risk_data)
    print(f" -> Inserted {len(risk_data):,} records into 'risk_indicators'.")

    # 5. Populate hive_results (Integrated from Phase 4 Hive / Phase 3 MapReduce)
    print("[INGESTION] Integrating Phase 4 Hive Course Rankings into 'hive_results'...")
    course_ranks = []
    for cid, group in df.groupby("course_id"):
        cname, cdept = COURSE_NAMES.get(cid, (f"Course {cid}", "General"))
        tot_enr = group["sem1_units_enrolled"].sum() + group["sem2_units_enrolled"].sum()
        tot_app = group["sem1_units_approved"].sum() + group["sem2_units_approved"].sum()
        pass_rate = (tot_app / tot_enr * 100.0) if tot_enr > 0 else 0.0
        course_ranks.append({
            "course_id": int(cid),
            "course_name": cname,
            "department": cdept,
            "count": len(group),
            "avg_grade": float(group["annual_grade_avg"].mean()),
            "pass_rate": float(pass_rate)
        })
    course_ranks.sort(key=lambda x: x["avg_grade"], reverse=True)
    
    hive_data = []
    for rank, c in enumerate(course_ranks, start=1):
        hive_data.append((
            c["course_id"],
            c["course_name"],
            c["department"],
            c["count"],
            round(c["avg_grade"], 2),
            round(c["pass_rate"], 2),
            rank
        ))
    cursor.executemany(f"""
        INSERT INTO hive_results (
            course_id, course_name, course_department,
            student_count, avg_annual_grade, unit_pass_rate_pct, performance_rank
        ) VALUES ({','.join([ph]*7)})
    """, hive_data)
    print(f" -> Integrated {len(hive_data)} course ranking records into 'hive_results'.")

    conn.commit()
    conn.close()
    print("\n[SUCCESS] All datasets and historical Hive outputs integrated into MySQL!")
    print("=" * 80)

if __name__ == "__main__":
    import_datasets()
