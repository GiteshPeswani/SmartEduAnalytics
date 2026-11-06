"""
SmartEdu Analytics - Phase 7: Real-Time Streaming Analytics Consumer
Script: streaming_consumer.py
Description:
    Consumes streaming academic activity events, executes real-time windowed
    aggregations, updates rolling attendance metrics, triggers low-attendance
    alerts (< 75%), and records persistent telemetry into MySQL / SQLite.
"""

import os
import sys
import json
from datetime import datetime

# Import database manager from phase5_mysql
PHASE5_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "phase5_mysql")
sys.path.append(PHASE5_DIR)
from config import get_mysql_connection

class StreamingAnalyticsConsumer:
    def __init__(self):
        self.conn, self.is_sqlite = get_mysql_connection()
        self.cursor = self.conn.cursor()
        self._init_streaming_tables()
        self.processed_event_ids = set()
        self.total_processed = 0
        self.alerts_triggered = 0

    def _init_streaming_tables(self):
        """Ensures streaming tables exist in target database."""
        if self.is_sqlite:
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS academic_event_logs (
                event_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                course_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                event_value REAL,
                event_metadata TEXT,
                event_timestamp TIMESTAMP,
                ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS realtime_student_metrics (
                student_id TEXT PRIMARY KEY,
                course_id INTEGER NOT NULL,
                total_sessions_tracked INTEGER DEFAULT 0,
                attended_sessions INTEGER DEFAULT 0,
                unattended_sessions INTEGER DEFAULT 0,
                rolling_attendance_pct REAL DEFAULT 100.0,
                total_quizzes_taken INTEGER DEFAULT 0,
                avg_quiz_score REAL DEFAULT 0.0,
                total_assignments_submitted INTEGER DEFAULT 0,
                avg_assignment_score REAL DEFAULT 0.0,
                latest_risk_level TEXT DEFAULT 'Low_Risk',
                last_event_timestamp TIMESTAMP
            );
            """)
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS streaming_attendance_alerts (
                alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course_id INTEGER NOT NULL,
                alert_type TEXT NOT NULL,
                current_value REAL NOT NULL,
                threshold_value REAL NOT NULL,
                alert_message TEXT NOT NULL,
                alert_status TEXT DEFAULT 'ACTIVE',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            self.conn.commit()

    def process_event(self, event):
        """Processes a single incoming streaming event with deduplication and alert checks."""
        event_id = event["event_id"]
        
        # Deduplication check
        if event_id in self.processed_event_ids:
            return {"status": "SKIPPED_DUPLICATE", "event_id": event_id}
            
        student_id = event["student_id"]
        course_id = event["course_id"]
        event_type = event["event_type"]
        val = event["event_value"]
        timestamp = event["event_timestamp"]
        ph = "?" if self.is_sqlite else "%s"

        # 1. Log Raw Event
        self.cursor.execute(f"""
            INSERT INTO academic_event_logs (
                event_id, student_id, course_id, event_type, event_value, event_metadata, event_timestamp
            ) VALUES ({','.join([ph]*7)})
        """, (event_id, student_id, course_id, event_type, val, event.get("event_metadata", "{}"), timestamp))

        # 2. Fetch or initialize student metrics
        self.cursor.execute(f"SELECT * FROM realtime_student_metrics WHERE student_id = {ph}", (student_id,))
        record = self.cursor.fetchone()
        
        if not record:
            self.cursor.execute(f"""
                INSERT INTO realtime_student_metrics (
                    student_id, course_id, total_sessions_tracked, attended_sessions,
                    unattended_sessions, rolling_attendance_pct, total_quizzes_taken,
                    avg_quiz_score, total_assignments_submitted, avg_assignment_score,
                    latest_risk_level, last_event_timestamp
                ) VALUES ({','.join([ph]*12)})
            """, (student_id, course_id, 0, 0, 0, 100.0, 0, 0.0, 0, 0.0, "Low_Risk", timestamp))
            self.cursor.execute(f"SELECT * FROM realtime_student_metrics WHERE student_id = {ph}", (student_id,))
            record = self.cursor.fetchone()

        # Update rolling state
        tot_sess = record[2]
        att_sess = record[3]
        unatt_sess = record[4]
        quizzes = record[6]
        avg_quiz = record[7]
        asgs = record[8]
        avg_asg = record[9]

        alert_fired = False
        if event_type == "attendance_checkin":
            tot_sess += 1
            if val == 1.0:
                att_sess += 1
            else:
                unatt_sess += 1
            rolling_att = round((att_sess / tot_sess) * 100.0, 2)
            
            # Check for < 75% threshold breach
            if tot_sess >= 3 and rolling_att < 75.0:
                msg = f"Alert: Rolling attendance for {student_id} dropped to {rolling_att:.1f}% (Threshold: 75.0%)"
                self.cursor.execute(f"""
                    INSERT INTO streaming_attendance_alerts (
                        student_id, course_id, alert_type, current_value, threshold_value, alert_message
                    ) VALUES ({','.join([ph]*6)})
                """, (student_id, course_id, "LOW_ATTENDANCE_CRITICAL", rolling_att, 75.0, msg))
                alert_fired = True
                self.alerts_triggered += 1
                
        elif event_type == "quiz_score":
            avg_quiz = round(((avg_quiz * quizzes) + val) / (quizzes + 1), 2)
            quizzes += 1
            rolling_att = record[5]
        elif event_type == "assignment_submission":
            avg_asg = round(((avg_asg * asgs) + val) / (asgs + 1), 2)
            asgs += 1
            rolling_att = record[5]
        else:
            rolling_att = record[5]

        # Dynamic risk assessment
        risk_level = "High_Risk" if rolling_att < 75.0 or (quizzes > 0 and avg_quiz < 10.0) else "Low_Risk"

        # Update database record
        self.cursor.execute(f"""
            UPDATE realtime_student_metrics
            SET total_sessions_tracked = {ph}, attended_sessions = {ph}, unattended_sessions = {ph},
                rolling_attendance_pct = {ph}, total_quizzes_taken = {ph}, avg_quiz_score = {ph},
                total_assignments_submitted = {ph}, avg_assignment_score = {ph},
                latest_risk_level = {ph}, last_event_timestamp = {ph}
            WHERE student_id = {ph}
        """, (tot_sess, att_sess, unatt_sess, rolling_att, quizzes, avg_quiz, asgs, avg_asg, risk_level, timestamp, student_id))

        self.conn.commit()
        self.processed_event_ids.add(event_id)
        self.total_processed += 1

        return {
            "status": "PROCESSED",
            "student_id": student_id,
            "event_type": event_type,
            "rolling_attendance_pct": rolling_att,
            "alert_fired": alert_fired,
            "latest_risk": risk_level
        }

    def close(self):
        self.conn.close()
