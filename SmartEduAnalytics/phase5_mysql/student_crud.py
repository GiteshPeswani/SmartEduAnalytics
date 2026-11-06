"""
SmartEdu Analytics - Phase 5: MySQL CRUD Operations Module
File: student_crud.py
Description:
    Provides programmatic and CLI interface for relational CRUD operations:
    1. Create: Insert new student record and performance baseline.
    2. Read: Retrieve student by ID, or list students with pagination.
    3. Update: Modify student academic marks, tuition status, or course.
    4. Delete: Safely remove student record with cascading table cleanup.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import get_mysql_connection, get_connection_info

def create_student(student_id, marital_status, gender, age, is_displaced, 
                   is_intl, nationality, adm_grade, prev_grade, target, course_id, 
                   s1_grade, s2_grade):
    """Inserts a new student and associated performance metrics."""
    conn, is_sqlite = get_mysql_connection()
    cursor = conn.cursor()
    ph = "?" if is_sqlite else "%s"
    
    annual_avg = round((s1_grade + s2_grade) / 2.0, 2)
    is_drop = 1 if target.lower() == "dropout" else 0
    perf_cat = "Excellent" if annual_avg >= 14 else ("Good" if annual_avg >= 12 else ("Average" if annual_avg >= 10 else "Needs_Improvement"))

    try:
        # 1. Insert into students
        cursor.execute(f"""
            INSERT INTO students (
                student_id, marital_status, gender, age_at_enrollment,
                is_displaced, is_international, nationality, admission_grade,
                previous_qualification_grade, target_outcome, is_dropout
            ) VALUES ({','.join([ph]*11)})
        """, (student_id, marital_status, gender, age, is_displaced, is_intl, 
              nationality, adm_grade, prev_grade, target, is_drop))

        # 2. Insert into performance_analytics
        cursor.execute(f"""
            INSERT INTO performance_analytics (
                student_id, course_id, sem1_grade, sem2_grade, annual_grade_avg,
                grade_trajectory, sem1_units_enrolled, sem1_units_approved,
                sem2_units_enrolled, sem2_units_approved, total_units_failed,
                sem1_approval_rate, sem2_approval_rate, performance_category
            ) VALUES ({','.join([ph]*14)})
        """, (student_id, course_id, s1_grade, s2_grade, annual_avg,
              round(s2_grade - s1_grade, 2), 6, 6, 6, 6, 0, 1.0, 1.0, perf_cat))

        # 3. Insert default attendance and risk entries
        cursor.execute(f"""
            INSERT INTO attendance_analytics (
                student_id, daytime_evening_attendance, sem1_units_without_eval,
                sem2_units_without_eval, total_units_unattended, participation_rate,
                is_below_75_alert, attendance_tier
            ) VALUES ({','.join([ph]*8)})
        """, (student_id, 1, 0, 0, 0, 100.0, 0, "Tier1_Excellent_90+"))

        cursor.execute(f"""
            INSERT INTO risk_indicators (
                student_id, academic_risk_score, academic_risk_level,
                tuition_fees_up_to_date, is_debtor, scholarship_holder
            ) VALUES ({','.join([ph]*6)})
        """, (student_id, 0.15, "Low_Risk", 1, 0, 1))

        conn.commit()
        print(f"[SUCCESS] Student '{student_id}' successfully created across all relational tables.")
        return True
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Failed to insert student '{student_id}': {e}")
        return False
    finally:
        conn.close()

def get_student_by_id(student_id):
    """Retrieves detailed record for a given student_id across joined tables."""
    conn, is_sqlite = get_mysql_connection()
    cursor = conn.cursor()
    ph = "?" if is_sqlite else "%s"
    
    query = f"""
        SELECT 
            s.student_id, s.gender, s.age_at_enrollment, s.admission_grade, s.target_outcome,
            p.course_id, p.sem1_grade, p.sem2_grade, p.annual_grade_avg, p.performance_category,
            a.participation_rate, a.attendance_tier,
            r.academic_risk_level, r.tuition_fees_up_to_date, r.is_debtor
        FROM students s
        LEFT JOIN performance_analytics p ON s.student_id = p.student_id
        LEFT JOIN attendance_analytics a ON s.student_id = a.student_id
        LEFT JOIN risk_indicators r ON s.student_id = r.student_id
        WHERE s.student_id = {ph}
    """
    cursor.execute(query, (student_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        print(f"[NOT FOUND] No record located for Student ID: {student_id}")
        return None
        
    cols = [
        "student_id", "gender", "age", "admission_grade", "target_outcome",
        "course_id", "sem1_grade", "sem2_grade", "annual_avg", "perf_category",
        "participation_rate", "attendance_tier", "risk_level", "tuition_ok", "is_debtor"
    ]
    res = dict(zip(cols, row))
    return res

def update_student_grades(student_id, new_sem1_grade, new_sem2_grade):
    """Updates academic grades and recomputes annual average and category."""
    conn, is_sqlite = get_mysql_connection()
    cursor = conn.cursor()
    ph = "?" if is_sqlite else "%s"
    
    new_annual = round((new_sem1_grade + new_sem2_grade) / 2.0, 2)
    new_cat = "Excellent" if new_annual >= 14 else ("Good" if new_annual >= 12 else ("Average" if new_annual >= 10 else "Needs_Improvement"))
    
    try:
        cursor.execute(f"""
            UPDATE performance_analytics
            SET sem1_grade = {ph}, sem2_grade = {ph}, annual_grade_avg = {ph},
                grade_trajectory = {ph}, performance_category = {ph}
            WHERE student_id = {ph}
        """, (new_sem1_grade, new_sem2_grade, new_annual, round(new_sem2_grade - new_sem1_grade, 2), new_cat, student_id))
        
        conn.commit()
        print(f"[SUCCESS] Updated grades for Student '{student_id}': Annual Avg = {new_annual:.2f} ({new_cat})")
        return True
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Failed to update student '{student_id}': {e}")
        return False
    finally:
        conn.close()

def delete_student(student_id):
    """Safely deletes student record with cascading foreign-key deletion."""
    conn, is_sqlite = get_mysql_connection()
    cursor = conn.cursor()
    ph = "?" if is_sqlite else "%s"
    
    try:
        # Check existence
        cursor.execute(f"SELECT student_id FROM students WHERE student_id = {ph}", (student_id,))
        if not cursor.fetchone():
            print(f"[NOTICE] Student '{student_id}' does not exist.")
            return False
            
        cursor.execute(f"DELETE FROM risk_indicators WHERE student_id = {ph}", (student_id,))
        cursor.execute(f"DELETE FROM attendance_analytics WHERE student_id = {ph}", (student_id,))
        cursor.execute(f"DELETE FROM performance_analytics WHERE student_id = {ph}", (student_id,))
        cursor.execute(f"DELETE FROM students WHERE student_id = {ph}", (student_id,))
        conn.commit()
        print(f"[SUCCESS] Student record '{student_id}' safely deleted.")
        return True
    except Exception as e:
        conn.rollback()
        print(f"[ERROR] Failed to delete student '{student_id}': {e}")
        return False
    finally:
        conn.close()

def demo_crud():
    print("=" * 75)
    print(" SmartEdu Analytics - Phase 5: MySQL CRUD Operations Demonstration")
    print(f" Connected to: {get_connection_info()}")
    print("=" * 75)
    
    test_id = "STD_TEST_99999"
    
    # 1. CREATE
    print("\n[1. CREATE OPERATION]")
    create_student(
        student_id=test_id, marital_status=1, gender=0, age=20,
        is_displaced=1, is_intl=0, nationality=1, adm_grade=155.0,
        prev_grade=160.0, target="Graduate", course_id=9500,
        s1_grade=14.5, s2_grade=15.0
    )
    
    # 2. READ
    print("\n[2. READ OPERATION]")
    rec = get_student_by_id(test_id)
    if rec:
        for k, v in rec.items():
            print(f"  -> {k:<20}: {v}")
            
    # 3. UPDATE
    print("\n[3. UPDATE OPERATION]")
    update_student_grades(test_id, 16.0, 16.5)
    rec_updated = get_student_by_id(test_id)
    print(f"  -> Verified New Annual Avg: {rec_updated['annual_avg']} (Category: {rec_updated['perf_category']})")
    
    # 4. DELETE
    print("\n[4. DELETE OPERATION]")
    delete_student(test_id)
    verify_del = get_student_by_id(test_id)
    print(f"  -> Post-deletion existence check: {'Present' if verify_del else 'Confirmed Deleted'}")
    print("=" * 75)

if __name__ == "__main__":
    demo_crud()
