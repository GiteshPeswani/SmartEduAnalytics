-- ==============================================================================
-- SmartEdu Analytics - Phase 4: Apache Hive Data Warehousing
-- Script: hive_schema.hql
-- Target Environment: Cloudera QuickStart VM 5.13.0 (Hive 1.1.0-cdh5.13.0)
-- Description:
--   1. Creates smartedu database.
--   2. Defines external table 'students_ext' mapping to HDFS CSV data.
--   3. Defines course dimension table 'course_dim' for relational joins.
--   4. Creates managed warehouse table 'student_analytics' for optimized queries.
-- ==============================================================================

-- 1. Create SmartEdu Database
CREATE DATABASE IF NOT EXISTS smartedu
COMMENT 'SmartEdu Student Analytics and Dropout Prediction Data Warehouse'
LOCATION '/user/hive/warehouse/smartedu.db';

USE smartedu;

-- 2. Drop existing tables if refreshing
DROP TABLE IF EXISTS students_ext;
DROP TABLE IF EXISTS course_dim;
DROP TABLE IF EXISTS student_analytics;

-- 3. External Table: Mapping directly to preprocessed student dataset in HDFS
-- Uses skip.header.line.count=1 to safely ignore CSV header row
CREATE EXTERNAL TABLE IF NOT EXISTS students_ext (
    student_id                      STRING      COMMENT 'Unique Student Identifier',
    marital_status                  INT         COMMENT '1=Single, 2=Married, 3=Widower, 4=Divorced, etc.',
    application_mode                INT         COMMENT 'Application method code',
    application_order               INT         COMMENT 'Preference order (0-9)',
    course_id                       INT         COMMENT 'Academic Degree Program ID',
    daytime_evening_attendance      INT         COMMENT '1=Daytime, 0=Evening',
    previous_qualification          INT         COMMENT 'Prior completed education code',
    previous_qualification_grade    DOUBLE      COMMENT 'High school completion grade (0-200)',
    nationality                     INT         COMMENT 'Country nationality code',
    mother_qualification            INT         COMMENT 'Maternal qualification code',
    father_qualification            INT         COMMENT 'Paternal qualification code',
    mother_occupation               INT         COMMENT 'Maternal occupation code',
    father_occupation               INT         COMMENT 'Paternal occupation code',
    admission_grade                 DOUBLE      COMMENT 'University entrance exam grade (0-200)',
    is_displaced                    INT         COMMENT '1=Lives away from home, 0=Lives at home',
    special_educational_needs       INT         COMMENT '1=Has documented special needs, 0=No',
    is_debtor                       INT         COMMENT '1=Has outstanding tuition debt, 0=No',
    tuition_fees_up_to_date         INT         COMMENT '1=Tuition payments current, 0=In arrears',
    gender                          INT         COMMENT '1=Male, 0=Female',
    scholarship_holder              INT         COMMENT '1=Scholarship recipient, 0=No',
    age_at_enrollment               INT         COMMENT 'Student age at enrollment',
    is_international                INT         COMMENT '1=International student, 0=Domestic',
    sem1_units_credited             INT         COMMENT 'Semester 1 credited units',
    sem1_units_enrolled             INT         COMMENT 'Semester 1 enrolled curricular units',
    sem1_units_evaluations          INT         COMMENT 'Semester 1 formal assessments taken',
    sem1_units_approved             INT         COMMENT 'Semester 1 approved curricular units',
    sem1_grade                      DOUBLE      COMMENT 'Semester 1 grade average (0-20 scale)',
    sem1_units_without_eval         INT         COMMENT 'Semester 1 unattended units without evaluation',
    sem2_units_credited             INT         COMMENT 'Semester 2 credited units',
    sem2_units_enrolled             INT         COMMENT 'Semester 2 enrolled curricular units',
    sem2_units_evaluations          INT         COMMENT 'Semester 2 formal assessments taken',
    sem2_units_approved             INT         COMMENT 'Semester 2 approved curricular units',
    sem2_grade                      DOUBLE      COMMENT 'Semester 2 grade average (0-20 scale)',
    sem2_units_without_eval         INT         COMMENT 'Semester 2 unattended units without evaluation',
    unemployment_rate               DOUBLE      COMMENT 'Regional unemployment rate (%)',
    inflation_rate                  DOUBLE      COMMENT 'Annual inflation rate (%)',
    gdp                             DOUBLE      COMMENT 'Annual GDP change rate (%)',
    target_outcome                  STRING      COMMENT 'Administrative Outcome: Graduate, Dropout, Enrolled',
    sem1_approval_rate              DOUBLE      COMMENT 'Sem 1 Approved / Enrolled ratio [0-1]',
    sem2_approval_rate              DOUBLE      COMMENT 'Sem 2 Approved / Enrolled ratio [0-1]',
    annual_grade_avg                DOUBLE      COMMENT 'Average of Sem 1 and Sem 2 grades (0-20)',
    grade_trajectory                DOUBLE      COMMENT 'Sem 2 grade minus Sem 1 grade',
    total_units_failed              INT         COMMENT 'Cumulative unapproved curricular units',
    academic_risk_score             DOUBLE      COMMENT 'Heuristic risk score [0.0 - 1.0]',
    academic_risk_level             STRING      COMMENT 'Heuristic tier: Low_Risk, Moderate_Risk, High_Risk',
    is_dropout                      INT         COMMENT 'Ground-truth binary target: 1=Dropout, 0=Non-Dropout',
    target_multi_class              INT         COMMENT 'Multi-class target: 0=Dropout, 1=Enrolled, 2=Graduate'
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/smartedu/processed/preprocessed/'
TBLPROPERTIES ("skip.header.line.count"="1");

-- 4. Dimension Table: Academic Degree Programs / Courses (for Relational Joins)
CREATE TABLE IF NOT EXISTS course_dim (
    course_id           INT,
    course_name         STRING,
    course_department   STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE;

-- Populate Dimension Table
INSERT INTO TABLE course_dim VALUES
    (33,   'Biofuel Production Technologies', 'Agricultural & Bioengineering'),
    (171,  'Animation and Multimedia Design', 'Arts & Multimedia'),
    (8014, 'Social Service (Daytime)', 'Social Sciences'),
    (9003, 'Agronomy', 'Agricultural & Bioengineering'),
    (9070, 'Communication Design', 'Arts & Multimedia'),
    (9085, 'Veterinary Nursing', 'Veterinary & Animal Care'),
    (9119, 'Informatics Engineering', 'Computer Science & Technology'),
    (9130, 'Equiniculture', 'Veterinary & Animal Care'),
    (9147, 'Management', 'Business & Economics'),
    (9238, 'Social Service (Evening)', 'Social Sciences'),
    (9254, 'Tourism', 'Hospitality & Tourism'),
    (9500, 'Nursing', 'Health & Nursing Sciences'),
    (9556, 'Oral Hygiene', 'Health & Nursing Sciences'),
    (9670, 'Advertising and Marketing Management', 'Business & Economics'),
    (9773, 'Journalism and Communication', 'Social Sciences'),
    (9853, 'Basic Education', 'Education & Teaching'),
    (9991, 'Management (Evening)', 'Business & Economics');

-- 5. Managed Table: Optimized Internal Data Warehouse Table
CREATE TABLE IF NOT EXISTS student_analytics (
    student_id                      STRING,
    course_id                       INT,
    daytime_evening_attendance      INT,
    admission_grade                 DOUBLE,
    sem1_grade                      DOUBLE,
    sem2_grade                      DOUBLE,
    annual_grade_avg                DOUBLE,
    sem1_units_enrolled             INT,
    sem1_units_approved             INT,
    sem2_units_enrolled             INT,
    sem2_units_approved             INT,
    total_units_failed              INT,
    sem1_units_without_eval         INT,
    sem2_units_without_eval         INT,
    is_debtor                       INT,
    tuition_fees_up_to_date         INT,
    scholarship_holder              INT,
    gender                          INT,
    age_at_enrollment               INT,
    is_displaced                    INT,
    is_international                INT,
    target_outcome                  STRING,
    academic_risk_score             DOUBLE,
    academic_risk_level             STRING,
    is_dropout                      INT
)
STORED AS ORC
TBLPROPERTIES ("orc.compress"="SNAPPY");

-- Load data from external table into managed ORC table
INSERT OVERWRITE TABLE student_analytics
SELECT 
    student_id,
    course_id,
    daytime_evening_attendance,
    admission_grade,
    sem1_grade,
    sem2_grade,
    annual_grade_avg,
    sem1_units_enrolled,
    sem1_units_approved,
    sem2_units_enrolled,
    sem2_units_approved,
    total_units_failed,
    sem1_units_without_eval,
    sem2_units_without_eval,
    is_debtor,
    tuition_fees_up_to_date,
    scholarship_holder,
    gender,
    age_at_enrollment,
    is_displaced,
    is_international,
    target_outcome,
    academic_risk_score,
    academic_risk_level,
    is_dropout
FROM students_ext;
