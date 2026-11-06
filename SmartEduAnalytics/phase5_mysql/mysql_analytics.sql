-- ==============================================================================
-- SmartEdu Analytics - Phase 5: MySQL Relational Analytics Queries
-- Database: smartedu
-- Description:
--   Comprehensive SQL queries demonstrating:
--   1. Aggregate functions (COUNT, AVG, MIN, MAX)
--   2. Multi-table JOINs (students, performance, attendance, risk, hive_results)
--   3. GROUP BY and ORDER BY clauses
--   4. HAVING clauses for cohort filtering
--   5. Subqueries & analytical window functions / rankings
--   6. Relational Views querying
-- ==============================================================================

USE smartedu;

-- 1. Total Students and Core Baseline Demographics
SELECT 
    COUNT(*) AS total_students,
    ROUND(AVG(admission_grade), 2) AS avg_admission_grade,
    ROUND(MIN(admission_grade), 2) AS min_admission_grade,
    ROUND(MAX(admission_grade), 2) AS max_admission_grade,
    SUM(CASE WHEN gender = 1 THEN 1 ELSE 0 END) AS male_count,
    SUM(CASE WHEN gender = 0 THEN 1 ELSE 0 END) AS female_count,
    ROUND(SUM(CASE WHEN is_displaced = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS displaced_pct
FROM students;

-- 2. Average Academic Marks & Credit Failure Summary
SELECT 
    ROUND(AVG(sem1_grade), 2) AS avg_sem1_grade,
    ROUND(AVG(sem2_grade), 2) AS avg_sem2_grade,
    ROUND(AVG(annual_grade_avg), 2) AS avg_annual_grade,
    ROUND(AVG(total_units_failed), 2) AS avg_failed_units,
    ROUND(AVG(sem1_approval_rate) * 100, 2) AS avg_sem1_pass_rate_pct,
    ROUND(AVG(sem2_approval_rate) * 100, 2) AS avg_sem2_pass_rate_pct
FROM performance_analytics;

-- 3. Course-Wise Performance Analysis (INNER JOIN with hive_results)
SELECT 
    h.performance_rank,
    h.course_id,
    h.course_name,
    h.course_department,
    COUNT(p.student_id) AS enrolled_students,
    ROUND(AVG(p.annual_grade_avg), 2) AS mean_annual_grade,
    ROUND(AVG(p.total_units_failed), 2) AS mean_failed_units,
    ROUND(AVG(a.participation_rate), 2) AS mean_attendance_pct
FROM performance_analytics p
JOIN hive_results h ON p.course_id = h.course_id
JOIN attendance_analytics a ON p.student_id = a.student_id
GROUP BY h.performance_rank, h.course_id, h.course_name, h.course_department
ORDER BY h.performance_rank ASC;

-- 4. Attendance & Curricular Participation Analysis
SELECT 
    CASE WHEN daytime_evening_attendance = 1 THEN 'Daytime' ELSE 'Evening' END AS attendance_mode,
    attendance_tier,
    COUNT(*) AS student_count,
    ROUND(AVG(participation_rate), 2) AS avg_participation_pct,
    SUM(is_below_75_alert) AS low_attendance_alerts
FROM attendance_analytics
GROUP BY daytime_evening_attendance, attendance_tier
ORDER BY attendance_mode, avg_participation_pct DESC;

-- 5. Performance Category Distribution with Attrition Cross-Tabulation
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
ORDER BY category_avg_grade DESC;

-- 6. Low Attendance At-Risk Students (< 75% Participation Threshold)
SELECT 
    s.student_id,
    p.course_id,
    h.course_name,
    a.participation_rate,
    p.annual_grade_avg,
    r.academic_risk_level,
    s.target_outcome
FROM students s
JOIN attendance_analytics a ON s.student_id = a.student_id
JOIN performance_analytics p ON s.student_id = p.student_id
JOIN hive_results h ON p.course_id = h.course_id
JOIN risk_indicators r ON s.student_id = r.student_id
WHERE a.is_below_75_alert = 1
ORDER BY a.participation_rate ASC, p.annual_grade_avg ASC
LIMIT 15;

-- 7. Top 10 Highest-Performing Students (Subquery / Ordering)
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
LIMIT 10;

-- 8. Advanced: HAVING Clause Filtering High-Dropout Courses
SELECT 
    h.course_id,
    h.course_name,
    COUNT(s.student_id) AS student_count,
    ROUND(AVG(p.annual_grade_avg), 2) AS avg_course_grade,
    SUM(s.is_dropout) AS dropout_count,
    ROUND(SUM(s.is_dropout) * 100.0 / COUNT(s.student_id), 2) AS course_dropout_rate_pct
FROM hive_results h
JOIN performance_analytics p ON h.course_id = p.course_id
JOIN students s ON p.student_id = s.student_id
GROUP BY h.course_id, h.course_name
HAVING COUNT(s.student_id) >= 100 AND course_dropout_rate_pct >= 35.0
ORDER BY course_dropout_rate_pct DESC;

-- 9. Analytical View Query: High-Risk Students Roster
SELECT 
    academic_risk_level,
    COUNT(*) AS high_risk_count,
    ROUND(AVG(annual_grade_avg), 2) AS avg_annual_grade,
    ROUND(AVG(participation_rate), 2) AS avg_participation_rate,
    SUM(CASE WHEN target_outcome = 'Dropout' THEN 1 ELSE 0 END) AS actual_dropouts,
    ROUND(SUM(CASE WHEN target_outcome = 'Dropout' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS precision_rate_pct
FROM v_high_risk_students
GROUP BY academic_risk_level;
