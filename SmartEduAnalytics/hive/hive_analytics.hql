-- ==============================================================================
-- SmartEdu Analytics - Phase 4: Apache Hive Data Warehousing
-- Script: hive_analytics.hql
-- Target Environment: Cloudera QuickStart VM 5.13.0 (Hive 1.1.0-cdh5.13.0)
-- Description:
--   Comprehensive HiveQL Analytical Queries:
--     1. Total Cohort Volume & Gender Distribution
--     2. Overall Academic Grade Profiling (Admission, Sem 1, Sem 2, Annual)
--     3. Course-Wise Average Performance (Joined with Dimension Table)
--     4. Attendance Mode & Curricular Participation Analysis
--     5. Performance Classification Tiers (Excellent, Good, Average, Needs Improvement)
--     6. At-Risk Students with Attendance/Participation < 75%
--     7. Top 10 High-Performing Students via Window Function (ROW_NUMBER)
--     8. Demographic Analysis: Age Brackets and Student Displacement
--     9. Socioeconomic & Financial Factors (Tuition, Debt, Scholarships)
--    10. Ground-Truth Dropout Analysis vs Heuristic Risk Matrix
--    11. Advanced: Course Rankings via DENSE_RANK() Window Function
--    12. Advanced: Severe Credit Failure Identification via HAVING Clause
--    13. Advanced: Multi-Table Relational JOIN Analysis
--    14. HDFS Result Storage (INSERT OVERWRITE DIRECTORY)
-- ==============================================================================

USE smartedu;

-- ------------------------------------------------------------------------------
-- Query 1: Total Number of Students & Gender Breakdown
-- ------------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_students,
    SUM(CASE WHEN gender = 1 THEN 1 ELSE 0 END) AS male_students,
    ROUND(SUM(CASE WHEN gender = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS male_percentage,
    SUM(CASE WHEN gender = 0 THEN 1 ELSE 0 END) AS female_students,
    ROUND(SUM(CASE WHEN gender = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS female_percentage
FROM student_analytics;

-- ------------------------------------------------------------------------------
-- Query 2: Overall Academic Performance Summary
-- ------------------------------------------------------------------------------
SELECT 
    COUNT(*) AS total_students,
    ROUND(AVG(admission_grade), 2) AS avg_admission_grade,
    ROUND(MIN(admission_grade), 2) AS min_admission_grade,
    ROUND(MAX(admission_grade), 2) AS max_admission_grade,
    ROUND(AVG(sem1_grade), 2) AS avg_sem1_grade,
    ROUND(AVG(sem2_grade), 2) AS avg_sem2_grade,
    ROUND(AVG(annual_grade_avg), 2) AS avg_annual_grade,
    ROUND(STDDEV(annual_grade_avg), 2) AS std_annual_grade
FROM student_analytics;

-- ------------------------------------------------------------------------------
-- Query 3: Course-Wise Average Performance & Units Pass Rate (Joined with course_dim)
-- ------------------------------------------------------------------------------
SELECT 
    s.course_id,
    c.course_name,
    c.course_department,
    COUNT(*) AS student_count,
    ROUND(AVG(s.admission_grade), 2) AS avg_admission,
    ROUND(AVG(s.sem1_grade), 2) AS avg_sem1_grade,
    ROUND(AVG(s.sem2_grade), 2) AS avg_sem2_grade,
    ROUND(AVG(s.annual_grade_avg), 2) AS avg_annual_grade,
    ROUND(SUM(s.sem1_units_approved + s.sem2_units_approved) * 100.0 / 
          SUM(s.sem1_units_enrolled + s.sem2_units_enrolled), 2) AS unit_pass_rate_pct
FROM student_analytics s
JOIN course_dim c ON s.course_id = c.course_id
GROUP BY s.course_id, c.course_name, c.course_department
ORDER BY avg_annual_grade DESC;

-- ------------------------------------------------------------------------------
-- Query 4: Attendance Mode & Curricular Participation Analysis
-- ------------------------------------------------------------------------------
SELECT 
    CASE WHEN daytime_evening_attendance = 1 THEN 'Daytime' ELSE 'Evening' END AS attendance_mode,
    COUNT(*) AS student_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM student_analytics), 2) AS pct_of_cohort,
    ROUND(AVG(100.0 * (1.0 - (sem1_units_without_eval + sem2_units_without_eval) / 
          NULLIF(sem1_units_enrolled + sem2_units_enrolled, 0))), 2) AS avg_participation_pct,
    SUM(CASE WHEN (1.0 - (sem1_units_without_eval + sem2_units_without_eval) / 
          NULLIF(sem1_units_enrolled + sem2_units_enrolled, 0)) < 0.75 THEN 1 ELSE 0 END) AS below_75_attendance_count
FROM student_analytics
GROUP BY daytime_evening_attendance;

-- ------------------------------------------------------------------------------
-- Query 5: Students Grouped by Academic Performance Categories
-- ------------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN annual_grade_avg >= 14.0 THEN 'Excellent (>=14.0)'
        WHEN annual_grade_avg >= 12.0 THEN 'Good (12.0-13.9)'
        WHEN annual_grade_avg >= 10.0 THEN 'Average (10.0-11.9)'
        ELSE 'Needs Improvement (<10.0)'
    END AS performance_category,
    COUNT(*) AS student_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM student_analytics), 2) AS percentage_of_cohort,
    ROUND(AVG(annual_grade_avg), 2) AS mean_category_grade,
    SUM(CASE WHEN target_outcome = 'Dropout' THEN 1 ELSE 0 END) AS actual_dropouts,
    ROUND(SUM(CASE WHEN target_outcome = 'Dropout' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS category_dropout_rate
FROM student_analytics
GROUP BY 
    CASE 
        WHEN annual_grade_avg >= 14.0 THEN 'Excellent (>=14.0)'
        WHEN annual_grade_avg >= 12.0 THEN 'Good (12.0-13.9)'
        WHEN annual_grade_avg >= 10.0 THEN 'Average (10.0-11.9)'
        ELSE 'Needs Improvement (<10.0)'
    END
ORDER BY mean_category_grade DESC;

-- ------------------------------------------------------------------------------
-- Query 6: Students with Low Attendance / Participation (< 75%)
-- ------------------------------------------------------------------------------
SELECT 
    s.student_id,
    s.course_id,
    c.course_name,
    CASE WHEN s.daytime_evening_attendance = 1 THEN 'Daytime' ELSE 'Evening' END AS attendance_mode,
    ROUND(100.0 * (1.0 - (s.sem1_units_without_eval + s.sem2_units_without_eval) / 
          NULLIF(s.sem1_units_enrolled + s.sem2_units_enrolled, 0)), 2) AS participation_pct,
    s.annual_grade_avg,
    s.target_outcome
FROM student_analytics s
JOIN course_dim c ON s.course_id = c.course_id
WHERE (1.0 - (s.sem1_units_without_eval + s.sem2_units_without_eval) / 
      NULLIF(s.sem1_units_enrolled + s.sem2_units_enrolled, 0)) < 0.75
ORDER BY participation_pct ASC, s.annual_grade_avg ASC
LIMIT 15;

-- ------------------------------------------------------------------------------
-- Query 7: Top 10 Highest-Performing Students (Window Function: ROW_NUMBER)
-- ------------------------------------------------------------------------------
SELECT 
    student_rank,
    student_id,
    course_name,
    admission_grade,
    sem1_grade,
    sem2_grade,
    annual_grade_avg,
    target_outcome
FROM (
    SELECT 
        ROW_NUMBER() OVER (ORDER BY s.annual_grade_avg DESC) AS student_rank,
        s.student_id,
        c.course_name,
        s.admission_grade,
        s.sem1_grade,
        s.sem2_grade,
        s.annual_grade_avg,
        s.target_outcome
    FROM student_analytics s
    JOIN course_dim c ON s.course_id = c.course_id
) ranked_students
WHERE student_rank <= 10;

-- ------------------------------------------------------------------------------
-- Query 8: Demographic Profiling: Age Brackets & Displacement
-- ------------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN age_at_enrollment < 20 THEN 'Under 20'
        WHEN age_at_enrollment BETWEEN 20 AND 24 THEN '20 - 24'
        WHEN age_at_enrollment BETWEEN 25 AND 29 THEN '25 - 29'
        ELSE '30 and Above'
    END AS age_bracket,
    CASE WHEN is_displaced = 1 THEN 'Displaced (Away from Home)' ELSE 'Non-Displaced (Home)' END AS displacement_status,
    COUNT(*) AS student_count,
    ROUND(AVG(annual_grade_avg), 2) AS avg_annual_grade,
    ROUND(SUM(CASE WHEN target_outcome = 'Dropout' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS dropout_rate_pct
FROM student_analytics
GROUP BY 
    CASE 
        WHEN age_at_enrollment < 20 THEN 'Under 20'
        WHEN age_at_enrollment BETWEEN 20 AND 24 THEN '20 - 24'
        WHEN age_at_enrollment BETWEEN 25 AND 29 THEN '25 - 29'
        ELSE '30 and Above'
    END,
    CASE WHEN is_displaced = 1 THEN 'Displaced (Away from Home)' ELSE 'Non-Displaced (Home)' END
ORDER BY age_bracket, displacement_status;

-- ------------------------------------------------------------------------------
-- Query 9: Socioeconomic & Financial Factors Impact on Student Attrition
-- ------------------------------------------------------------------------------
SELECT 
    CASE WHEN tuition_fees_up_to_date = 1 THEN 'Tuition Current' ELSE 'Tuition In Arrears' END AS tuition_status,
    CASE WHEN is_debtor = 1 THEN 'Has Student Debt' ELSE 'No Debt' END AS debtor_status,
    CASE WHEN scholarship_holder = 1 THEN 'Scholarship Recipient' ELSE 'No Scholarship' END AS scholarship_status,
    COUNT(*) AS student_count,
    ROUND(AVG(annual_grade_avg), 2) AS avg_grade,
    SUM(CASE WHEN target_outcome = 'Dropout' THEN 1 ELSE 0 END) AS dropout_count,
    ROUND(SUM(CASE WHEN target_outcome = 'Dropout' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS dropout_rate_pct
FROM student_analytics
GROUP BY tuition_fees_up_to_date, is_debtor, scholarship_holder
ORDER BY dropout_rate_pct DESC;

-- ------------------------------------------------------------------------------
-- Query 10: Ground-Truth Dropout Outcome vs Heuristic Risk Tier Analysis
-- ------------------------------------------------------------------------------
SELECT 
    target_outcome AS administrative_outcome,
    COUNT(*) AS student_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM student_analytics), 2) AS pct_of_cohort,
    ROUND(AVG(sem1_grade), 2) AS avg_sem1_grade,
    ROUND(AVG(sem2_grade), 2) AS avg_sem2_grade,
    ROUND(AVG(annual_grade_avg), 2) AS avg_annual_grade,
    ROUND(AVG(total_units_failed), 2) AS avg_failed_units,
    ROUND(SUM(CASE WHEN tuition_fees_up_to_date = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS tuition_current_pct,
    ROUND(SUM(CASE WHEN is_debtor = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS debtor_pct,
    ROUND(SUM(CASE WHEN scholarship_holder = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS scholarship_pct
FROM student_analytics
GROUP BY target_outcome
ORDER BY avg_annual_grade ASC;

-- ------------------------------------------------------------------------------
-- Query 11: Advanced Analytics - Dense Ranking of Courses by Grade
-- ------------------------------------------------------------------------------
SELECT 
    DENSE_RANK() OVER (ORDER BY AVG(s.annual_grade_avg) DESC) AS performance_rank,
    s.course_id,
    c.course_name,
    COUNT(*) AS total_students,
    ROUND(AVG(s.annual_grade_avg), 2) AS avg_annual_grade
FROM student_analytics s
JOIN course_dim c ON s.course_id = c.course_id
GROUP BY s.course_id, c.course_name;

-- ------------------------------------------------------------------------------
-- Query 12: Advanced Analytics - Severe Credit Failure Identification (HAVING)
-- ------------------------------------------------------------------------------
SELECT 
    c.course_name,
    COUNT(*) AS severe_struggle_students,
    ROUND(AVG(s.annual_grade_avg), 2) AS avg_grade_struggling,
    ROUND(AVG(s.total_units_failed), 2) AS avg_units_failed
FROM student_analytics s
JOIN course_dim c ON s.course_id = c.course_id
WHERE s.total_units_failed >= 4
GROUP BY c.course_name
HAVING COUNT(*) >= 25
ORDER BY severe_struggle_students DESC;

-- ------------------------------------------------------------------------------
-- Query 13: Export Analytical Results into HDFS Storage (/smartedu/analytics/hive/)
-- ------------------------------------------------------------------------------
-- 1. Store Summary Metrics
INSERT OVERWRITE DIRECTORY '/smartedu/analytics/hive/summary_metrics'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
SELECT 
    COUNT(*),
    ROUND(AVG(admission_grade), 2),
    ROUND(AVG(sem1_grade), 2),
    ROUND(AVG(sem2_grade), 2),
    ROUND(AVG(annual_grade_avg), 2),
    SUM(CASE WHEN target_outcome = 'Dropout' THEN 1 ELSE 0 END),
    SUM(CASE WHEN target_outcome = 'Graduate' THEN 1 ELSE 0 END),
    SUM(CASE WHEN target_outcome = 'Enrolled' THEN 1 ELSE 0 END)
FROM student_analytics;

-- 2. Store Course Performance
INSERT OVERWRITE DIRECTORY '/smartedu/analytics/hive/course_performance'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
SELECT 
    s.course_id,
    c.course_name,
    COUNT(*),
    ROUND(AVG(s.annual_grade_avg), 2),
    ROUND(SUM(s.sem1_units_approved + s.sem2_units_approved) * 100.0 / 
          SUM(s.sem1_units_enrolled + s.sem2_units_enrolled), 2)
FROM student_analytics s
JOIN course_dim c ON s.course_id = c.course_id
GROUP BY s.course_id, c.course_name;

-- 3. Store Dropout Risk Analysis
INSERT OVERWRITE DIRECTORY '/smartedu/analytics/hive/dropout_risk_analysis'
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
SELECT 
    academic_risk_level,
    target_outcome,
    COUNT(*),
    ROUND(AVG(annual_grade_avg), 2),
    ROUND(AVG(total_units_failed), 2)
FROM student_analytics
GROUP BY academic_risk_level, target_outcome;
