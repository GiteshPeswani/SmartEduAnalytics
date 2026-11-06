-- ==============================================================================
-- SmartEdu Analytics - Phase 5: MySQL Database Schema
-- Database: smartedu
-- MySQL Server: 8.0+ / 5.7+ Compatible
-- Description:
--   Creates relational database schema for student demographic records,
--   academic performance metrics, attendance diagnostics, and integrated
--   Hadoop MapReduce / Hive analytical outputs.
-- ==============================================================================

-- 1. Create Database
CREATE DATABASE IF NOT EXISTS smartedu 
DEFAULT CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE smartedu;

-- 2. Drop existing tables if re-initializing (in reverse foreign-key order)
DROP TABLE IF EXISTS risk_indicators;
DROP TABLE IF EXISTS attendance_analytics;
DROP TABLE IF EXISTS performance_analytics;
DROP TABLE IF EXISTS hive_results;
DROP TABLE IF EXISTS students;

-- 3. Core Students Table (Demographic & Ground-Truth Attrition Baseline)
CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(20) PRIMARY KEY,
    marital_status INT NOT NULL,
    gender TINYINT NOT NULL COMMENT '1=Male, 0=Female',
    age_at_enrollment INT NOT NULL,
    is_displaced TINYINT NOT NULL COMMENT '1=Away from home, 0=Living at home',
    is_international TINYINT NOT NULL COMMENT '1=International, 0=Domestic',
    nationality INT NOT NULL,
    admission_grade DECIMAL(6,2) NOT NULL COMMENT '0-200 Scale',
    previous_qualification_grade DECIMAL(6,2) NOT NULL COMMENT '0-200 Scale',
    target_outcome VARCHAR(20) NOT NULL COMMENT 'Graduate, Dropout, Enrolled',
    is_dropout TINYINT NOT NULL COMMENT '1=Dropout, 0=Non-Dropout',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_target_outcome (target_outcome),
    INDEX idx_admission_grade (admission_grade)
) ENGINE=InnoDB;

-- 4. Academic Performance Analytics Table
CREATE TABLE IF NOT EXISTS performance_analytics (
    student_id VARCHAR(20) PRIMARY KEY,
    course_id INT NOT NULL,
    sem1_grade DECIMAL(5,2) NOT NULL,
    sem2_grade DECIMAL(5,2) NOT NULL,
    annual_grade_avg DECIMAL(5,2) NOT NULL,
    grade_trajectory DECIMAL(5,2) NOT NULL COMMENT 'sem2_grade - sem1_grade',
    sem1_units_enrolled INT NOT NULL,
    sem1_units_approved INT NOT NULL,
    sem2_units_enrolled INT NOT NULL,
    sem2_units_approved INT NOT NULL,
    total_units_failed INT NOT NULL,
    sem1_approval_rate DECIMAL(5,4) NOT NULL,
    sem2_approval_rate DECIMAL(5,4) NOT NULL,
    performance_category VARCHAR(25) NOT NULL COMMENT 'Excellent, Good, Average, Needs Improvement',
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    INDEX idx_course_id (course_id),
    INDEX idx_annual_grade (annual_grade_avg),
    INDEX idx_perf_category (performance_category)
) ENGINE=InnoDB;

-- 5. Attendance & Curricular Participation Table
CREATE TABLE IF NOT EXISTS attendance_analytics (
    student_id VARCHAR(20) PRIMARY KEY,
    daytime_evening_attendance TINYINT NOT NULL COMMENT '1=Daytime, 0=Evening',
    sem1_units_without_eval INT NOT NULL,
    sem2_units_without_eval INT NOT NULL,
    total_units_unattended INT NOT NULL,
    participation_rate DECIMAL(5,2) NOT NULL COMMENT 'Percentage [0-100]',
    is_below_75_alert TINYINT NOT NULL COMMENT '1=Under 75% Alert, 0=Satisfactory',
    attendance_tier VARCHAR(30) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    INDEX idx_attendance_mode (daytime_evening_attendance),
    INDEX idx_below_75 (is_below_75_alert)
) ENGINE=InnoDB;

-- 6. Risk Indicators & Socioeconomic Factors Table
CREATE TABLE IF NOT EXISTS risk_indicators (
    student_id VARCHAR(20) PRIMARY KEY,
    academic_risk_score DECIMAL(5,4) NOT NULL COMMENT 'Diagnostic score [0.0 - 1.0]',
    academic_risk_level VARCHAR(20) NOT NULL COMMENT 'Low_Risk, Moderate_Risk, High_Risk',
    tuition_fees_up_to_date TINYINT NOT NULL COMMENT '1=Current, 0=Arrears',
    is_debtor TINYINT NOT NULL COMMENT '1=Has Debt, 0=No Debt',
    scholarship_holder TINYINT NOT NULL COMMENT '1=Scholarship, 0=No',
    FOREIGN KEY (student_id) REFERENCES students(student_id) ON DELETE CASCADE,
    INDEX idx_risk_level (academic_risk_level),
    INDEX idx_tuition_fees (tuition_fees_up_to_date),
    INDEX idx_debtor (is_debtor)
) ENGINE=InnoDB;

-- 7. Integrated Hadoop Hive / MapReduce Aggregated Results Table
CREATE TABLE IF NOT EXISTS hive_results (
    course_id INT PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    course_department VARCHAR(100) NOT NULL,
    student_count INT NOT NULL,
    avg_annual_grade DECIMAL(5,2) NOT NULL,
    unit_pass_rate_pct DECIMAL(5,2) NOT NULL,
    performance_rank INT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_perf_rank (performance_rank)
) ENGINE=InnoDB;

-- 8. Analytical Views
-- View 1: High-Risk Students for Academic Advising
CREATE OR REPLACE VIEW v_high_risk_students AS
SELECT 
    s.student_id,
    p.course_id,
    s.gender,
    s.age_at_enrollment,
    p.annual_grade_avg,
    p.total_units_failed,
    a.participation_rate,
    r.academic_risk_score,
    r.academic_risk_level,
    r.tuition_fees_up_to_date,
    r.is_debtor,
    s.target_outcome
FROM students s
JOIN performance_analytics p ON s.student_id = p.student_id
JOIN attendance_analytics a ON s.student_id = a.student_id
JOIN risk_indicators r ON s.student_id = r.student_id
WHERE r.academic_risk_level = 'High_Risk' OR p.annual_grade_avg < 10.0;

-- View 2: Course Summary Roster
CREATE OR REPLACE VIEW v_course_summary AS
SELECT 
    h.course_id,
    h.course_name,
    h.course_department,
    h.student_count,
    h.avg_annual_grade,
    h.unit_pass_rate_pct,
    COUNT(CASE WHEN s.target_outcome = 'Dropout' THEN 1 END) AS dropout_count,
    ROUND(COUNT(CASE WHEN s.target_outcome = 'Dropout' THEN 1 END) * 100.0 / h.student_count, 2) AS dropout_rate_pct
FROM hive_results h
JOIN performance_analytics p ON h.course_id = p.course_id
JOIN students s ON p.student_id = s.student_id
GROUP BY h.course_id, h.course_name, h.course_department, h.student_count, h.avg_annual_grade, h.unit_pass_rate_pct;
