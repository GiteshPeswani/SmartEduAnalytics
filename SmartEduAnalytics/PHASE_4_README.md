# SmartEdu Analytics – Phase 4: Apache Hive Data Warehousing & Analytics

## Overview
Phase 4 implements enterprise data warehousing, relational schema modeling, and distributed HiveQL querying over the student academic records stored in HDFS. It uses **Apache Hive 1.1.0-cdh5.13.0** inside the **Cloudera QuickStart VM**.

---

## File Inventory for Phase 4

```
SmartEduAnalytics/
│
├── hive/
│   ├── hive_schema.hql                     # DDL: Database, external tables, dimension table & ORC managed table
│   └── hive_analytics.hql                  # DQL: 14 Analytical queries, window functions, and HDFS exports
│
├── scripts/
│   └── phase4/
│       ├── create_hive_database.sh         # Shell script: Initializes database and validates tables
│       ├── run_hive_analytics.sh           # Shell script: Executes all 14 analytics queries & exports to HDFS
│       └── run_local_hive_simulation.py    # Local simulation script with exact query tables & chart export
│
├── dataset/
│   └── analytics/
│       └── hive/                           # Output directory populated by INSERT OVERWRITE DIRECTORY
│           ├── summary_metrics/
│           ├── course_performance/
│           └── dropout_risk_analysis/
│
├── visualizations/
│   └── phase4/                             # 5 High-resolution Hive analytical charts (.png)
│       ├── hive_query3_course_performance.png
│       ├── hive_query5_performance_classification_tiers.png
│       ├── hive_query8_age_displacement_performance.png
│       ├── hive_query9_financial_risk_heatmap.png
│       └── hive_query10_attrition_metrics_comparison.png
│
├── reports/
│   └── phase4_report.md                    # Comprehensive Phase 4 Technical Report
│
└── PHASE_4_README.md                       # This execution guide
```

---

## Environment & Compatibility
- **Platform:** Cloudera QuickStart VM 5.13.0
- **Hadoop:** 2.6.0-cdh5.13.0
- **Hive:** 1.1.0-cdh5.13.0
- **Metastore:** MySQL (Embedded / Local in Cloudera VM)
- **HDFS Location:** `/smartedu/processed/preprocessed/` and `/smartedu/analytics/hive/`

---

## Step-by-Step Execution in Cloudera VM

### 1. Transfer Scripts & Files to Cloudera VM
If you mounted the Windows shared folder at `/media/sf_SmartEduAnalytics`:
```bash
cp -r /media/sf_SmartEduAnalytics/hive /home/cloudera/SmartEduAnalytics/
cp -r /media/sf_SmartEduAnalytics/scripts/phase4 /home/cloudera/SmartEduAnalytics/scripts/
cd /home/cloudera/SmartEduAnalytics

# Convert line endings and make executable
sed -i -e 's/\r$//' scripts/phase4/*.sh hive/*.hql
chmod +x scripts/phase4/*.sh
```

### 2. Initialize the Hive Database & Tables
```bash
./scripts/phase4/create_hive_database.sh
```
*What this does:*
- Creates HDFS directory `/smartedu/processed/preprocessed/` and copies dataset.
- Executes `hive/hive_schema.hql`.
- Creates database `smartedu`.
- Maps external table `students_ext` (handling CSV headers using `skip.header.line.count=1`).
- Populates course dimension table `course_dim` (17 university degree programs).
- Loads managed table `student_analytics` (ORC with Snappy compression).

### 3. Run the Analytical Queries & Export to HDFS
```bash
./scripts/phase4/run_hive_analytics.sh
```
*What this does:*
- Executes all 14 HiveQL queries in `hive/hive_analytics.hql`.
- Computes cohort metrics, course averages, attendance percentages, demographic breakdowns, and dropout correlations.
- Exports result datasets directly into HDFS at `/smartedu/analytics/hive/`.

---

## Interactive Hive CLI Execution
You can also run Hive queries interactively in the terminal:
```bash
hive
```
```sql
USE smartedu;

-- 1. Check student count
SELECT COUNT(*) FROM student_analytics;

-- 2. View top courses by grade
SELECT s.course_id, c.course_name, ROUND(AVG(s.annual_grade_avg), 2) AS avg_grade
FROM student_analytics s
JOIN course_dim c ON s.course_id = c.course_id
GROUP BY s.course_id, c.course_name
ORDER BY avg_grade DESC
LIMIT 5;

-- 3. Quit Hive
QUIT;
```
