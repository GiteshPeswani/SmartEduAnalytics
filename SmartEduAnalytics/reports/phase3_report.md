# SmartEdu Analytics: Big Data-Driven Student Performance Analysis and Dropout Risk Prediction System
## Phase 3 Technical Report: MapReduce-Based Student Performance Analytics

**Author:** Senior Hadoop Developer & Big Data Engineer  
**Status:** Completed, Verified & Documented  
**Target Cluster:** Cloudera QuickStart VM 5.13.0 (Hadoop 2.6.0-cdh5.13.0, YARN, HDFS)  
**Host Environment:** Windows Development Workstation (`d:\bdampr\SmartEduAnalytics`)  
**Date:** March 2026  
**Artifact Directory:** `d:\bdampr\SmartEduAnalytics`

---

## 1. Aim

The primary objective of Phase 3 is to implement, execute, and validate distributed Big Data analytics jobs using **Apache Hadoop MapReduce** (Hadoop Streaming with Python) against the preprocessed student academic dataset stored in HDFS. 

The analytical pipeline computes five distributed analytics objectives:
1. **Average Student Performance:** Multi-stage course and cohort grade averages.
2. **Attendance & Curricular Participation Analysis:** Attendance mode distributions and alert thresholds (< 75%).
3. **Student Performance Classification:** Tiered academic categorization (`Excellent`, `Good`, `Average`, `Needs Improvement`).
4. **Course Performance Rankings:** Program-level pass rates and identification of highest- and lowest-performing degrees.
5. **Dropout Risk & Institutional Outcome Analysis:** Empirical cross-tabulation of ground-truth attrition vs. early heuristic risk indicators.

---

## 2. Introduction to Hadoop MapReduce

**Apache Hadoop MapReduce** is a software framework and programming model for processing massive datasets concurrently across distributed clusters of commodity servers. MapReduce fundamentally operates on the paradigm of **Data Locality**—bringing the computational logic to the physical storage node where data blocks reside, rather than transmitting terabytes of raw data across network switches.

### Core Strengths of MapReduce:
- **Fault-Tolerant Parallelism:** Worker task failures (speculative or hardware errors) are automatically detected by the ApplicationMaster and restarted on alternative cluster nodes.
- **Linear Scalability:** Cluster throughput scales linearly by expanding DataNodes and NodeManagers.
- **Determinism:** Map and Reduce operations are pure functions of key-value pairs, ensuring idempotent, reproducible data aggregations.

---

## 3. MapReduce Architecture & Execution Flow

### High-Level Architecture Flowchart

```
+----------------------------------------------------------------------------------------------------+
|                                    HDFS Input Split (128 MB Block)                                 |
|                         /smartedu/processed/preprocessed_student_data.csv                          |
+----------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                              MAP PHASE: RecordReader (Line by Line)                                |
|                        (mapper_average.py / mapper_attendance.py / etc.)                           |
|       Parses CSV row -> Extracts grouping key -> Emits Intermediate Key-Value: <Key, MetricTuple> |
+----------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                SHUFFLE & SORT (Hadoop 2.6.0 Core)                                  |
|         Partitioning (HashPartitioner) -> In-memory Spill -> Merge Sort -> HTTP Fetch              |
|                             Groups all identical keys to the same Reducer                          |
+----------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                             REDUCE PHASE: Iterative Aggregation                                    |
|                      (reducer_average.py / reducer_attendance.py / etc.)                           |
|           Aggregates counts, sums, min/max -> Emits Final Key-Value: <Key, SummaryMetrics>         |
+----------------------------------------------------------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                                    HDFS Output Part Files                                          |
|                          /smartedu/analytics/mapreduce/<job_name>/part-00000                       |
|                          /smartedu/analytics/mapreduce/<job_name>/_SUCCESS                         |
+----------------------------------------------------------------------------------------------------+
```

### Component Roles in Hadoop 2.6.0 (YARN):
1. **ResourceManager:** Manages cluster compute resources, allocates containers, and schedules job submission.
2. **NodeManager:** Manages per-node container lifecycles, monitoring CPU and memory usage.
3. **ApplicationMaster (MRAppMaster):** Coordinates the execution of Map and Reduce tasks for the specific job instance.
4. **Hadoop Streaming:** Utility enabling Python mappers and reducers to read from standard input (`sys.stdin`) and write tab-delimited records to standard output (`sys.stdout`).

---

## 4. Mapper and Reducer Technical Specification

Each mapper and reducer script strictly adheres to Hadoop Streaming conventions and employs Python's standard `csv.reader` to prevent naive comma-splitting errors on quoted fields:

| Job | Mapper Script | Reducer Script | Emitted Intermediate Key | Emitted Values / Aggregation |
| :--- | :--- | :--- | :--- | :--- |
| **Job 1: Average Performance** | `mapper_average.py` | `reducer_average.py` | `course_id` / `__ALL__` | Admission, Previous, Sem1, Sem2, Annual grades, count |
| **Job 2: Attendance Analysis** | `mapper_attendance.py` | `reducer_attendance.py` | `Daytime` / `Evening` / `OVERALL` | Participation %, below 75 flag, tier name, count |
| **Job 3: Classification** | `mapper_classification.py` | `reducer_classification.py` | `CAT_SUMMARY` / `STUDENT_RECORD` | Student ID, Course, Grade, Tier, Outcome |
| **Job 4: Course Rankings** | `mapper_course.py` | `reducer_course.py` | `course_id` | Annual grade, units enrolled, units approved, count |
| **Job 5: Risk & Outcomes** | `mapper_risk.py` | `reducer_risk.py` | `OUTCOME_<status>` / `RISK_<tier>` | Grades, failed units, tuition, debtor, scholarship |

---

## 5. Input Dataset Description

- **Source Path:** `hdfs://quickstart.cloudera:8020/smartedu/processed/preprocessed_student_data.csv`
- **Total Records:** 4,424 student rows (plus 1 header row)
- **Features Used:**
  - `student_id` (Col 0)
  - `course_id` (Col 4)
  - `daytime_evening_attendance` (Col 5)
  - `previous_qualification_grade` (Col 7)
  - `admission_grade` (Col 13)
  - `is_debtor` (Col 16)
  - `tuition_fees_up_to_date` (Col 17)
  - `scholarship_holder` (Col 19)
  - `sem1_units_enrolled` (Col 23), `sem1_units_approved` (Col 25), `sem1_grade` (Col 26), `sem1_units_without_eval` (Col 27)
  - `sem2_units_enrolled` (Col 29), `sem2_units_approved` (Col 31), `sem2_grade` (Col 32), `sem2_units_without_eval` (Col 33)
  - `target_outcome` (Col 37)
  - `annual_grade_avg` (Col 40)
  - `total_units_failed` (Col 42)
  - `academic_risk_level` (Col 44)

---

## 6. Implementation Methodology

### 6.1 Safe Directory Management
The orchestration script `run_all_jobs.sh` inspects HDFS prior to job submission. If a destination directory exists, it is archived or cleanly refreshed using the `-f` flag, ensuring no job crashes due to `FileAlreadyExistsException`.

### 6.2 Data Leakage & Header Safeguards
- The mapper checks `if row[0].strip().lower() == "student_id"` to safely bypass the CSV header row.
- Zero records were fabricated; all calculations reflect exact cohort records.

---

## 7. The Five MapReduce Analytics Jobs & Actual Outputs

### Job 1: Average Student Performance
**HDFS Output Directory:** `/smartedu/analytics/mapreduce/average_performance/part-00000`

```text
category_or_course	student_count	avg_admission_grade	avg_prev_qual_grade	avg_sem1_grade	avg_sem2_grade	avg_annual_grade
Course_171	215	136.16	137.91	2.07	2.08	2.08
Course_33	12	118.56	128.11	9.64	8.99	9.32
Course_8014	215	122.18	129.32	10.57	9.80	10.18
Course_9003	210	132.76	136.16	10.38	9.48	9.93
Course_9070	226	128.89	132.00	12.08	11.20	11.64
Course_9085	337	131.17	135.27	11.86	11.16	11.51
Course_9119	170	126.40	132.08	8.57	8.79	8.68
Course_9130	141	132.41	136.45	10.08	9.68	9.88
Course_9147	380	122.83	130.58	10.12	9.70	9.91
Course_9238	355	125.58	131.91	11.24	11.12	11.18
Course_9254	252	121.57	127.84	10.46	9.93	10.19
Course_9500	766	127.26	135.02	12.46	12.35	12.41
Course_9556	86	123.09	131.66	10.33	9.77	10.05
Course_9670	268	121.46	128.33	11.33	10.68	11.01
Course_9773	331	127.96	132.24	11.69	11.04	11.37
Course_9853	192	123.16	130.84	11.47	10.57	11.02
Course_9991	268	130.24	131.69	9.10	9.22	9.16
OVERALL_COHORT	4424	126.98	132.61	10.64	10.23	10.44
```
*Analytical Finding:* The overall cohort average admission grade is 126.98/200, while the annual grade average is 10.44/20.

---

### Job 2: Attendance & Curricular Participation Analysis
**HDFS Output Directory:** `/smartedu/analytics/mapreduce/attendance_analysis/part-00000`

```text
attendance_mode	total_students	avg_attendance_pct	min_attendance_pct	max_attendance_pct	below_75_count	below_75_pct	excellent_90_plus	satisfactory_75_89	warning_50_74	critical_below_50
Daytime	3941	97.68	0.00	100.00	116	2.94%	3705	120	85	31
Evening	483	98.20	50.00	100.00	12	2.48%	464	7	12	0
OVERALL_COHORT	4424	97.74	0.00	100.00	128	2.89%	4169	127	97	31
```
*Analytical Finding:* The student cohort demonstrates an average participation rate of 97.74%. A total of **128 students (2.89%)** breach the critical `< 75%` attendance alert threshold, identifying them as candidates for immediate academic intervention.

---

### Job 3: Student Performance Classification
**HDFS Output Directory:** `/smartedu/analytics/mapreduce/performance_classification/part-00000`

```text
=== STUDENT PERFORMANCE CLASSIFICATION SUMMARY ===
performance_category	student_count	percentage_of_cohort
Excellent	585	13.22%
Good	1901	42.97%
Average	1026	23.19%
Needs_Improvement	912	20.61%
TOTAL_COHORT	4424	100.00%
```
*Configurable Thresholds Used:*
- **Excellent:** Grade $\ge 14.0$ (13.22%, 585 students)
- **Good:** $12.0 \le \text{Grade} < 14.0$ (42.97%, 1,901 students)
- **Average:** $10.0 \le \text{Grade} < 12.0$ (23.19%, 1,026 students)
- **Needs Improvement:** $\text{Grade} < 10.0$ (20.61%, 912 students)

---

### Job 4: Course Performance Analysis & Program Rankings
**HDFS Output Directory:** `/smartedu/analytics/mapreduce/course_analysis/part-00000`

```text
=== TOP 3 HIGHEST PERFORMING COURSES ===
Top 1: Course_9500 - Avg Grade: 12.41/20 (Pass Rate: 82.44%, Students: 766)
Top 2: Course_9070 - Avg Grade: 11.64/20 (Pass Rate: 81.12%, Students: 226)
Top 3: Course_9085 - Avg Grade: 11.51/20 (Pass Rate: 71.92%, Students: 337)

=== TOP 3 LOWEST PERFORMING COURSES ===
Bottom 1: Course_171 - Avg Grade: 2.08/20 (Pass Rate: 89.74%, Students: 215)
Bottom 2: Course_9119 - Avg Grade: 8.68/20 (Pass Rate: 44.39%, Students: 170)
Bottom 3: Course_9991 - Avg Grade: 9.16/20 (Pass Rate: 63.28%, Students: 268)
```
*Analytical Finding:* Course 9500 (Nursing) represents the highest academic performer (12.41/20, 82.44% unit pass rate across 766 students). Course 9119 exhibits severe credit completion deficits with only a 44.39% unit pass rate.

---

### Job 5: Dropout Risk & Institutional Outcome Analysis
**HDFS Output Directory:** `/smartedu/analytics/mapreduce/dropout_risk_analysis/part-00000`

```text
=== PART 1: ADMINISTRATIVE INSTITUTIONAL OUTCOMES ===
outcome_status	student_count	pct_of_cohort	avg_sem1_grade	avg_sem2_grade	avg_failed_units	tuition_current_pct	debtor_pct	scholarship_pct
Dropout	1421	32.12%	7.26	5.90	7.11	67.84%	21.96%	9.43%
Enrolled	794	17.95%	11.13	11.12	3.53	94.71%	11.34%	16.37%
Graduate	2209	49.93%	12.64	12.70	0.89	98.69%	4.57%	37.80%

=== PART 2: HEURISTIC ACADEMIC RISK LEVEL VS ACTUAL OUTCOME ===
risk_tier	total_students	graduates	dropouts	enrolled	actual_dropout_rate
High_Risk	896	75	733	88	81.81%
Moderate_Risk	665	40	381	244	57.29%
Low_Risk	2863	2094	307	462	10.72%
```

#### Ground Truth vs. Heuristic Clarification:
The heuristic rule-based risk indicator correctly isolated **733 out of 896 High-Risk students as confirmed dropouts (81.81% precision)**, validating that early-stage credit deficits and grade drops correlate heavily with university non-completion.

---

## 8. Exact Execution Commands for Cloudera QuickStart VM

Inside your Cloudera Linux VM (`cloudera@quickstart`):

```bash
# 1. Navigate to project root
cd /home/cloudera/SmartEduAnalytics

# 2. Convert line endings and make executable
sed -i -e 's/\r$//' scripts/phase3/*.sh scripts/phase3/*.py
chmod +x scripts/phase3/*.sh scripts/phase3/*.py

# 3. Execute all 5 MapReduce Jobs in batch
./scripts/phase3/run_all_jobs.sh -f

# 4. Run output validation audit
./scripts/phase3/validate_outputs.sh
```

---

## 9. Visualizations Generated

Five high-resolution visual charts have been exported to [`visualizations/phase3/`](file:///d:/bdampr/SmartEduAnalytics/visualizations/phase3):
1. `job1_course_average_performance.png`: Bar chart of mean grades across all 17 university courses.
2. `job2_attendance_mode_and_tiers.png`: Pie distribution of attendance mode and boxplot of participation rates.
3. `job3_performance_classification_bars.png`: Cohort distribution across Excellent, Good, Average, and Needs Improvement.
4. `job4_top_bottom_performing_courses.png`: Comparative analysis of the Top 3 vs. Bottom 3 courses.
5. `job5_dropout_risk_vs_outcome.png`: Stacked bar chart showing actual attrition rate across heuristic risk tiers.

---

## 10. Screenshots Checklist for College Viva / Project Demonstration

| # | Item to Document / Screenshot | Command / Location | Expected Verification Point |
| :- | :--- | :--- | :--- |
| **1** | MapReduce Submission Log | `./scripts/phase3/run_all_jobs.sh` | YARN MapReduce application ID, Map 100%, Reduce 100% |
| **2** | YARN Resource Manager UI | In browser: `http://localhost:8088/cluster/apps` | 5 completed MapReduce applications in `SUCCEEDED` state |
| **3** | Output Verification Audit | `./scripts/phase3/validate_outputs.sh` | All 5 output directories verified with `_SUCCESS` flags |
| **4** | Average Performance Output | `hdfs dfs -cat /smartedu/analytics/mapreduce/average_performance/part-00000` | Course-wise and cohort averages |
| **5** | Attendance Output | `hdfs dfs -cat /smartedu/analytics/mapreduce/attendance_analysis/part-00000` | Attendance mode stats and `< 75%` count |
| **6** | Classification Summary | `hdfs dfs -cat /smartedu/analytics/mapreduce/performance_classification/part-00000 \| head -n 10` | 585 Excellent, 1,901 Good, 1,026 Average, 912 Needs Improvement |
| **7** | Risk & Outcome Output | `hdfs dfs -cat /smartedu/analytics/mapreduce/dropout_risk_analysis/part-00000` | Administrative outcomes vs heuristic risk tiers |

---

## 11. Conclusion & Handoff Instructions for Phase 4 (Apache Hive)

Phase 3 is complete and verified. The five distributed MapReduce analytics jobs have been implemented, tested, and validated against the actual Phase 2 dataset.

### Handoff Instructions for Phase 4: Apache Hive Data Warehousing
In Phase 4, we will transition from low-level MapReduce to high-level declarative SQL querying using **Apache Hive 1.1.0**:
1. **Database Creation:** `CREATE DATABASE IF NOT EXISTS smartedu_dw;`
2. **External Hive Tables:**
   - Map external Hive tables directly over `/smartedu/processed/cleaned_student_data.csv` and `/smartedu/processed/preprocessed_student_data.csv`.
   - Map tables over Phase 3 MapReduce output directories (`/smartedu/analytics/mapreduce/...`).
3. **Partitioning & Bucketing:**
   - Partition student records by `course_id` or `daytime_evening_attendance`.
   - Bucket by `student_id` to optimize distributed joins.
4. **Analytical HiveQL Queries:**
   - Multi-dimensional rollups and windowing functions (`OVER()`, `RANK()`, `NTILE()`).
   - Socioeconomic correlation queries and attrition risk reports.
