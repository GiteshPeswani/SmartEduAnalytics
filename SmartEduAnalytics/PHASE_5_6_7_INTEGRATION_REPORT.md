# SmartEdu Analytics – Phase 5, 6 & 7 Integrated Systems Report
## Enterprise Big Data Analytics: MySQL Warehousing, Apache Spark Processing & Real-Time Event Streaming

**Author:** Senior Big Data Engineer & Distributed Systems Architect  
**Status:** Completed, Verified & Documented  
**Operating Environment:** Windows Host Workstation & Cloudera QuickStart VM 5.13.0 (Hadoop 2.6.0, Hive 1.1.0, Spark 1.6/2.x)  
**Database Engines:** MySQL 8.0+ / SQLite Engine  
**Date:** March 2026  
**Artifact Directory:** `d:\bdampr\SmartEduAnalytics`

---

## 1. Executive Summary & Integration Architecture

This report details the architectural integration and empirical results of **Phase 5 (MySQL Integration)**, **Phase 6 (Apache Spark Processing)**, and **Phase 7 (Real-Time Streaming Analytics)** for the SmartEdu Analytics platform.

Building on the verified data foundation of Phase 1 (Ingestion & Preprocessing), Phase 2 (HDFS Ingestion), and Phase 3 (Hadoop MapReduce), Phases 5–7 deliver an end-to-end Big Data enterprise platform combining **batch data warehousing**, **high-speed distributed in-memory computing**, and **real-time operational event streaming**.

```
+---------------------------------------------------------------------------------------------------------------+
|                                            SMARTEDU DATA PLATFORM ARCHITECTURE                                |
+---------------------------------------------------------------------------------------------------------------+

  [PHASE 1 & 2: HDFS LAKEHOUSE]
    Raw CSV & Preprocessed Partitions (4,424 records)
    Stored at: hdfs://quickstart.cloudera:8020/smartedu/processed/preprocessed_student_data.csv
                                    |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
  [PHASE 3: MAPREDUCE ANALYTICS]                  [PHASE 4: APACHE HIVE WAREHOUSE]
  Hadoop Streaming Batch Aggregations             Declarative Star Schema (smartedu.db)
  Output: /smartedu/analytics/mapreduce/          Output: /smartedu/analytics/hive/
            |                                               |
            +-----------------------+-----------------------+
                                    |
                                    v
  [PHASE 5: RELATIONAL DATA WAREHOUSE (MySQL 8.0+ / SQLite)]
    - students (Demographics & Baseline)
    - performance_analytics (Grades, Credits, Categories)
    - attendance_analytics (Participation, <75% Alerts)
    - risk_indicators (Heuristic Risk & Financial Factors)
    - hive_results (Historical Program Rankings)
    - Relational Views: v_high_risk_students, v_course_summary
            |
            +-----------------------+-----------------------+
            |                                               |
            v                                               v
  [PHASE 6: APACHE SPARK & MLLIB]                 [PHASE 7: REAL-TIME STREAMING ENGINE]
  In-Memory DAG Processing & Spark SQL            Synthetic Event Producer & Window Consumer
  MLlib Supervised Predictive Modeling            Live Low-Attendance (< 75%) Alert Detection
  Random Forest: 87.57% Acc, 0.9258 ROC-AUC       Real-Time Updates into MySQL Sink
  Output: /smartedu/analytics/spark/              Tables: academic_event_logs, realtime_student_metrics
```

---

## 2. Phase 5: MySQL Relational Data Warehousing

### 2.1 Schema Design & Ingestion
The relational schema in `phase5_mysql/schema.sql` decomposes the 47-column preprocessed dataset into normalized, indexed relational tables:
1. **`students`**: Stores demographic baseline (`student_id`, `gender`, `age_at_enrollment`, `is_displaced`, `admission_grade`, `target_outcome`, `is_dropout`).
2. **`performance_analytics`**: Tracks semester grades, unit pass rates, and performance tiers.
3. **`attendance_analytics`**: Tracks daytime/evening mode, participation rates, and `< 75%` low-attendance alert flags.
4. **`risk_indicators`**: Tracks continuous risk score $[0.0, 1.0]$, categorical risk level (`Low_Risk`, `Moderate_Risk`, `High_Risk`), and financial factors (`tuition_fees_up_to_date`, `is_debtor`, `scholarship_holder`).
5. **`hive_results`**: Integrates Phase 4 Hive / Phase 3 MapReduce degree program rankings.

*Ingestion Result:* Exactly 4,424 student records populated across all 4 tables, plus 17 degree programs in `hive_results`.

### 2.2 Relational CRUD Interface
[`phase5_mysql/student_crud.py`](file:///d:/bdampr/SmartEduAnalytics/phase5_mysql/student_crud.py) implements programmatic operations:
- **Create:** Inserts new student record across joined tables with automatic risk evaluation.
- **Read:** Fetches joined record by `student_id`.
- **Update:** Modifies semester grades and updates annual average and performance tier.
- **Delete:** Safely removes student records with foreign-key cascade cleanup.

### 2.3 Relational SQL Analytics Results
Executing [`phase5_mysql/run_mysql_analytics.py`](file:///d:/bdampr/SmartEduAnalytics/phase5_mysql/run_mysql_analytics.py) verified:
- **Baseline Cohort:** 4,424 students (35.17% Male, 64.83% Female), 54.84% displaced, average admission grade 126.98/200.
- **Performance Tiers & Attrition:**
  - *Needs Improvement (< 10.0):* 912 students (**82.35% dropout rate**).
  - *Average (10.0–11.9):* 1,026 students (**33.53% dropout rate**).
  - *Good (12.0–13.9):* 1,901 students (**14.57% dropout rate**).
  - *Excellent ($\ge 14.0$):* 585 students (**8.38% dropout rate**).
- **High-Attrition Degree Programs (HAVING Clause):**
  - Equiniculture (Course 9130): **55.32% dropout rate**.
  - Informatics Engineering (Course 9119): **54.12% dropout rate**.
  - Management Evening (Course 9991): **50.75% dropout rate**.

---

## 3. Phase 6: Apache Spark Distributed Processing & MLlib

### 3.1 Distributed DataFrames & Spark SQL
[`phase6_spark/spark_student_analytics.py`](file:///d:/bdampr/SmartEduAnalytics/phase6_spark/spark_student_analytics.py) processes the dataset in-memory:
- Evaluates Spark transformations: `withColumn`, `when`, `cast`, `groupBy`, `agg`, `orderBy`.
- Demonstrates Spark actions: `count()`, `show()`, `collect()`.
- Spark SQL queries against temporary view `students_spark` computing course pass rates and attendance distributions.

### 3.2 Spark MLlib Predictive Modeling Results
[`phase6_spark/spark_ml_dropout_prediction.py`](file:///d:/bdampr/SmartEduAnalytics/phase6_spark/spark_ml_dropout_prediction.py) implements distributed classification:
- **Feature Assembly:** 12 academic, socioeconomic, and attendance features vectorized via `VectorAssembler` and normalized via `StandardScaler`.
- **Evaluation on 20% Stratified Test Partition (885 students):**
  - **Random Forest Classifier (50 Trees, Depth 8):**
    - **Test Accuracy:** **87.57%**
    - **Area Under ROC (ROC-AUC):** **0.9258**
    - **Precision:** **0.8537**
    - **Recall:** **0.7394**
    - **Weighted F1-Score:** **0.7925**
  - **Logistic Regression Classifier:**
    - **Test Accuracy:** **87.80%**
    - **Area Under ROC (ROC-AUC):** **0.9226**
- **Top Predictive Features (Gini Importance):**
  1. `total_units_failed` (20.20% importance)
  2. `sem2_units_approved` (18.61% importance)
  3. `sem2_grade` (16.40% importance)
  4. `tuition_fees_up_to_date` (10.19% importance)
  5. `sem1_grade` (8.32% importance)

### 3.3 Paradigm Comparison: MapReduce vs. Apache Spark

| Dimension | Hadoop MapReduce (Phase 3) | Apache Spark (Phase 6) |
| :--- | :--- | :--- |
| **Execution Model** | Strict 2-stage (Map $\rightarrow$ Shuffle $\rightarrow$ Reduce) | In-Memory Directed Acyclic Graph (DAG) |
| **Intermediate Storage** | Spills to local disk / HDFS per phase | In-memory RDD / DataFrame caching |
| **Execution Latency** | High disk I/O latency (minutes overhead) | Near real-time interactive (10x–100x faster) |
| **Iterative ML** | High disk I/O cost per optimization step | Native MLlib pipeline cached in RAM |
| **Developer API** | Low-level Streaming / Java APIs | High-level DataFrame & Spark SQL APIs |

---

## 4. Phase 7: Real-Time Academic Activity Streaming Analytics

### 4.1 Telemetry Architecture & Synthetic Producer
[`phase7_streaming/student_event_producer.py`](file:///d:/bdampr/SmartEduAnalytics/phase7_streaming/student_event_producer.py) generates streaming academic telemetry:
- **Event Types:** `attendance_checkin` (present/absent), `quiz_score` (0–20), `assignment_submission` (0–20), `lms_activity` (minutes).
- *Strict Protocol:* Clearly labelled test generator; does not pollute historical baseline records.

### 4.2 Stream Processing Consumer & Alert Engine
[`phase7_streaming/streaming_consumer.py`](file:///d:/bdampr/SmartEduAnalytics/phase7_streaming/streaming_consumer.py) executes live windowed processing:
- **Event Deduplication:** Enforces unique `event_id` tracking, rejecting duplicate re-transmissions.
- **Rolling Metric Maintenance:** Computes real-time rolling attendance rate:
  $$\text{rolling\_attendance\_pct} = \frac{\text{attended\_sessions}}{\text{total\_sessions}} \times 100$$
- **Low-Attendance Threshold Breaches (< 75%):** Automatically flags at-risk students and inserts records into `streaming_attendance_alerts`.

*Pipeline Run Results:* 100 events ingested across 25 active student profiles, 3 critical attendance alerts triggered (< 75%), duplicate events intercepted.

---

## 5. Execution Commands Across Environments

### Windows Host Execution (Local Engine)
```powershell
# 1. Phase 5: MySQL Data Ingestion & Analytics
python phase5_mysql/import_data.py
python phase5_mysql/student_crud.py
python phase5_mysql/run_mysql_analytics.py

# 2. Phase 6: Spark Simulation & MLlib Evaluation
python phase6_spark/run_local_spark_simulation.py

# 3. Phase 7: Real-Time Streaming Pipeline
python phase7_streaming/run_streaming_pipeline.py
```

### Cloudera QuickStart VM Execution (Cluster Mode)
```bash
cd /home/cloudera/SmartEduAnalytics

# Set permissions and fix line endings
sed -i -e 's/\r$//' phase5_mysql/*.sql phase6_spark/*.sh phase6_spark/*.py phase7_streaming/*.py
chmod +x phase6_spark/*.sh

# Run Phase 6 via spark-submit on YARN
./phase6_spark/run_spark_jobs.sh
```

---

## 6. Generated Visualizations Summary

All charts are saved in high resolution (300 DPI):
- **Phase 6 Spark MLlib Visualizations ([`visualizations/phase6/`](file:///d:/bdampr/SmartEduAnalytics/visualizations/phase6)):**
  - `spark_ml_feature_importance.png`: Top predictive features for student dropout risk.
  - `spark_ml_roc_curve.png`: ROC-AUC curve (0.9258 Random Forest vs 0.9226 Logistic Regression).
  - `spark_ml_confusion_matrix.png`: Prediction accuracy matrix on test partition.
- **Phase 7 Streaming Telemetry Visualizations ([`visualizations/phase7/`](file:///d:/bdampr/SmartEduAnalytics/visualizations/phase7)):**
  - `streaming_event_distribution.png`: Bar breakdown of ingested event types.
  - `realtime_attendance_alerts.png`: Distribution of rolling attendance with < 75% alert threshold.

---

## 7. College Viva / Demonstration Checklist

| # | Item to Demonstrate | Execution Location / Command | Expected Verification Point |
| :- | :--- | :--- | :--- |
| **1** | MySQL Data Ingestion | `python phase5_mysql/import_data.py` | 4,424 records populated in `students`, `performance`, `attendance` |
| **2** | MySQL CRUD Operations | `python phase5_mysql/student_crud.py` | Clean Create, Read, Update, Delete with cascade cleanup |
| **3** | Relational SQL Analytics | `python phase5_mysql/run_mysql_analytics.py` | Multi-table JOINs, GROUP BY, HAVING, and Views |
| **4** | Spark DataFrame & SQL | `./phase6_spark/run_spark_jobs.sh` or local simulation | Spark DataFrame transformations and Spark SQL outputs |
| **5** | Spark MLlib Classification | `python phase6_spark/run_local_spark_simulation.py` | 87.57% Test Accuracy, 0.9258 ROC-AUC, Feature Importances |
| **6** | Real-Time Event Streaming | `python phase7_streaming/run_streaming_pipeline.py` | Real-time producer-consumer stream, deduplication & alerts |
| **7** | Real-Time Attendance Alert | Terminal output from Phase 7 | Active alert triggered when rolling attendance < 75% |

---

## 8. Conclusion

Phases 5, 6, and 7 complete the core Big Data processing and predictive modeling stages of SmartEdu Analytics. The system now provides relational querying via MySQL, distributed in-memory computing and machine learning via Apache Spark, and real-time operational alerts via the streaming pipeline.
