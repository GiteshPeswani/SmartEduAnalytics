-- ==============================================================================
-- SmartEdu Analytics - Phase 7: Real-Time Streaming Analytics Schema
-- Database: smartedu
-- Description:
--   Creates tables for ingesting streaming student academic activity events,
--   maintaining real-time rolling metrics, and recording low-attendance alerts.
-- ==============================================================================

USE smartedu;

-- 1. Raw Event Ingestion Log Table (Deduplication via unique event_id)
CREATE TABLE IF NOT EXISTS academic_event_logs (
    event_id VARCHAR(64) PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    course_id INT NOT NULL,
    event_type VARCHAR(30) NOT NULL COMMENT 'attendance_checkin, quiz_score, assignment_submission, lms_activity',
    event_value DECIMAL(5,2) DEFAULT NULL COMMENT 'Marks or attendance status (1=Present, 0=Absent)',
    event_metadata VARCHAR(255) DEFAULT NULL,
    event_timestamp TIMESTAMP NOT NULL,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_student_event (student_id),
    INDEX idx_event_type (event_type),
    INDEX idx_event_timestamp (event_timestamp)
) ENGINE=InnoDB;

-- 2. Real-Time Rolling Student Metrics Table
CREATE TABLE IF NOT EXISTS realtime_student_metrics (
    student_id VARCHAR(20) PRIMARY KEY,
    course_id INT NOT NULL,
    total_sessions_tracked INT DEFAULT 0,
    attended_sessions INT DEFAULT 0,
    unattended_sessions INT DEFAULT 0,
    rolling_attendance_pct DECIMAL(5,2) DEFAULT 100.00,
    total_quizzes_taken INT DEFAULT 0,
    avg_quiz_score DECIMAL(5,2) DEFAULT 0.00,
    total_assignments_submitted INT DEFAULT 0,
    avg_assignment_score DECIMAL(5,2) DEFAULT 0.00,
    latest_risk_level VARCHAR(20) DEFAULT 'Low_Risk',
    last_event_timestamp TIMESTAMP NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_rolling_attendance (rolling_attendance_pct),
    INDEX idx_latest_risk (latest_risk_level)
) ENGINE=InnoDB;

-- 3. Streaming Low-Attendance & Performance Alert Table
CREATE TABLE IF NOT EXISTS streaming_attendance_alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    course_id INT NOT NULL,
    alert_type VARCHAR(40) NOT NULL COMMENT 'LOW_ATTENDANCE_CRITICAL, QUIZ_SCORE_FAIL',
    current_value DECIMAL(5,2) NOT NULL,
    threshold_value DECIMAL(5,2) NOT NULL,
    alert_message VARCHAR(255) NOT NULL,
    alert_status VARCHAR(20) DEFAULT 'ACTIVE' COMMENT 'ACTIVE, ACKNOWLEDGED, RESOLVED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_alert_student (student_id),
    INDEX idx_alert_status (alert_status)
) ENGINE=InnoDB;
