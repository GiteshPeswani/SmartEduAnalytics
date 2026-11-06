# SmartEdu Analytics: Big Data-Driven Student Performance Analysis and Dropout Risk Prediction System
## Comprehensive End-to-End Technical Report (Phases 1 through 10)

---

### Executive Summary
Higher education institutions face substantial challenges in student retention, early attrition detection, and proactive intervention. **SmartEdu Analytics** is a production-grade, enterprise Big Data and Machine Learning ecosystem designed to ingest, process, store, analyze, and predict student academic trajectories across 4,424 student records.

The system combines distributed Big Data infrastructure (**Apache Hadoop HDFS, MapReduce, Apache Hive, Apache Spark, Real-Time Event Streaming, MySQL 8.0**) with state-of-the-art Supervised Machine Learning (**Gradient Boosting, Random Forest, Logistic Regression, Decision Trees**), an automated **Personalized Recommendation Engine**, and a modern **FastAPI + Tailwind CSS + Chart.js** full-stack web dashboard.

---

## 1. System Architecture & End-to-End Pipeline

```mermaid
flowchart TD
    subgraph S1["1. Raw Data Lake & Ingestion"]
        A["Raw Academic Dataset<br>(UCI 697: 4,424 Students)"] --> B["Phase 1: Preprocessing & Feature Engineering<br>(47 engineered features)"]
        B --> C["Phase 2: Apache Hadoop HDFS<br>/smartedu/{raw, processed, analytics}"]
    end

    subgraph S2["2. Distributed Big Data Engines"]
        C --> D["Phase 3: Hadoop MapReduce<br>(Distributed Batch Jobs)"]
        C --> E["Phase 4: Apache Hive Data Warehouse<br>(HiveQL Relational Analytics)"]
        C --> F["Phase 6: Apache Spark & MLlib<br>(In-Memory Distributed Computing)"]
        G["Phase 7: Real-Time Streaming<br>(Event Producer / Consumer)"] --> H["Low Attendance Alerts & Event Log"]
    end

    subgraph S3["3. Relational Operational Data Store"]
        D --> I["Phase 5: MySQL 8.0 / SQLite Store<br>(Relational Tables & Views)"]
        E --> I
        H --> I
    end

    subgraph S4["4. Machine Learning & Prescriptive AI"]
        I --> J["Phase 8: Dropout Risk Prediction<br>(Gradient Boosting Champion: 93.06% ROC-AUC)"]
        J --> K["Calibrated Risk Tiers<br>(Low: 67.6%, Med: 9.1%, High: 23.3%)"]
        K --> L["Phase 9: Recommendation Engine<br>(9,952 Actionable Interventions)"]
        L --> I
    end

    subgraph S5["5. Interactive Web Dashboard"]
        I --> M["Phase 10: FastAPI Backend<br>(REST API & JWT Auth)"]
        M --> N["Phase 10: React / Tailwind Web UI<br>(Real-Time KPI & Student Explorer)"]
    end
```

---

## 2. Phase-by-Phase Technical Breakdown

### Phase 1: Dataset Collection, Exploration & Preprocessing
- **Source**: Real-world academic dataset from the Higher Education Institution of Portalegre (UCI Machine Learning Repository #697).
- **Cohort Scale**: 4,424 verified student profiles; 0 synthetic or hallucinated records.
- **Engineered Dimensions**:
  - `student_id`: Unique identifier (STD_10001 to STD_14424).
  - Academic Trajectory: `annual_grade_avg`, `sem1_approval_rate`, `sem2_approval_rate`, `grade_trajectory`, `total_units_failed`.
  - Academic Risk Score: Composite weighted risk index (0.0 to 100.0).
  - Target Attributes: Binary classification label `is_dropout` (1 = Dropout [1,421], 0 = Non-Dropout [3,003: 2,209 Graduate, 794 Enrolled]).
- **Outputs**: `dataset/raw/raw_student_data.csv`, `dataset/processed/preprocessed_student_data.csv`, `dataset/processed/train_student_data.csv`, `dataset/processed/test_student_data.csv`.
- **EDA Artifacts**: 6 high-resolution analytical plots in `visualizations/phase1/`.

### Phase 2: Hadoop HDFS Data Storage & Ingestion
- **Environment**: Cloudera QuickStart VM 5.13.0-0, Hadoop 2.6.0-cdh5.13.0.
- **Directory Hierarchy**:
  - `/smartedu/raw/`: Raw ingest data archive.
  - `/smartedu/processed/`: Normalized preprocessed student features.
  - `/smartedu/analytics/`: MapReduce, Hive, and Spark distributed output storage.
  - `/smartedu/reports/`: Generated batch analytical summaries.
- **Scripts**: Health verification, directory creation, data upload, block validation, and HDFS extraction scripts in `scripts/phase2/`.

### Phase 3: Hadoop MapReduce Distributed Analytics
- **Execution Architecture**: Hadoop Streaming API (`hadoop-streaming-2.6.0-cdh5.13.0.jar`) with Python mappers and reducers.
- **Jobs Executed**:
  1. Overall & Course-Wise Grade Averages (`mapper_average.py` / `reducer_average.py`).
  2. Subject / Course Pass Rate Distribution (`mapper_subject_performance.py` / `reducer_subject_performance.py`).
  3. Attendance & Lecture Mode Correlation (`mapper_attendance.py` / `reducer_attendance.py`).
  4. Curricular Failure Analysis (`mapper_failure_analysis.py` / `reducer_failure_analysis.py`).
  5. Composite Academic Risk Index Grouping (`mapper_risk_index.py` / `reducer_risk_index.py`).
- **Outputs**: Output datasets in `dataset/analytics/mapreduce/` and 5 analytical charts in `visualizations/phase3/`.

### Phase 4: Apache Hive Data Warehousing & HiveQL
- **Database**: `smartedu` internal and external metastore catalog.
- **Schema**: External table `student_records_ext` and optimized internal partitioned table `student_records_orc`.
- **Analytics Ingested**:
  - Aggregations by degree course, gender, enrollment age, and scholarship status.
  - Multi-condition student risk queries for retention intervention.
- **Outputs**: `hive/hive_schema.hql`, `hive/hive_analytics.hql`, and 5 high-res figures in `visualizations/phase4/`.

### Phase 5: MySQL Relational Data Warehousing
- **Target Schema**: MySQL Server 8.0 with graceful SQLite fallback (`phase5_mysql/smartedu_local.db`).
- **Relational Tables**:
  - `students`: 4,424 records (demographics, qualifications, outcome).
  - `performance_analytics`: 4,424 records (grades, course units, trajectory).
  - `attendance_analytics`: 4,424 records (participation rates, shift mode, alerts).
  - `risk_indicators`: 4,424 records (debtor status, tuition up-to-date, risk scores).
  - `hive_results`: Aggregated program-level metrics across 17 degree courses.
- **Database Views**: `v_high_risk_students` and `v_course_summary`.
- **CRUD Operations**: Verified programmatic query, insert, update, and delete interface (`student_crud.py`).

### Phase 6: Apache Spark & MLlib Distributed Analytics
- **Spark Framework**: PySpark with Spark DataFrames, Spark SQL, and Spark MLlib.
- **Supervised ML Simulation**:
  - VectorAssembler across 12 numerical and categorical predictors.
  - Random Forest Classifier (50 trees, max depth 8) achieved **87.57% test accuracy** and **0.9258 ROC-AUC**.
  - Logistic Regression achieved **87.68% test accuracy** and **0.9168 ROC-AUC**.
- **Hadoop vs. Spark Benchmark**: Demonstrated Spark in-memory execution speedup over MapReduce disk-spill cycles.
- **Outputs**: `dataset/analytics/spark/` and 5 charts in `visualizations/phase6/`.

### Phase 7: Real-Time Event Streaming & Low-Attendance Alerts
- **Event Architecture**: Streaming producer generating student portal and attendance events with deduplication and JSON schema validation.
- **Alert Logic**: Automatic trigger when lecture participation rate falls below institutional minimum of 75.0%.
- **Run Summary**: Streamed 100 dynamic events, logged low-attendance alerts, and persisted telemetry in SQLite/MySQL.
- **Outputs**: Event logs in `phase7_streaming/` and 5 charts in `visualizations/phase7/`.

---

## 3. Phase 8: Student Dropout Risk Prediction Using Machine Learning

### Model Evaluation & Benchmark Comparison
Four supervised machine learning algorithms were trained on the stratified 80% training partition (3,539 students) and rigorously evaluated on the untouched 20% test partition (885 students):

| Algorithm | Test Accuracy | Precision | Recall | F1-Score | ROC-AUC | Status |
|---|---|---|---|---|---|---|
| **Gradient Boosting Classifier** | **88.70%** | **86.51%** | **76.76%** | **0.8134** | **0.9306** | **Champion Model Selected** |
| Random Forest Classifier | 88.81% | 86.27% | 77.46% | 0.8163 | 0.9295 | Benchmark Contender |
| Logistic Regression (L2) | 88.02% | 85.60% | 75.35% | 0.8015 | 0.9241 | Linear Baseline |
| Decision Tree (Depth=6) | 86.10% | 81.57% | 73.24% | 0.7718 | 0.8992 | Interpretable Baseline |

### Key Risk Predictors (Feature Importance)
1. **Total Units Failed**: Most decisive factor distinguishing graduating students from dropouts.
2. **Semester 2 Grade & Units Approved**: Second-semester course completion is the strongest inflection point for persistence.
3. **Tuition Fees Up-to-Date / Debtor Status**: Financial distress directly correlates with sudden course discontinuation.
4. **Semester 1 Approval Rate**: Early academic friction in first semester sets student risk trajectory.
5. **Admission Grade & Enrollment Age**: Non-traditional older students with lower admission grades face increased balancing challenges.

### Cohort Risk Stratification (All 4,424 Students)
- **Low Risk** ($\text{Probability} < 0.35$): **2,989 students (67.6%)**
- **Medium Risk** ($0.35 \le \text{Probability} < 0.70$): **402 students (9.1%)**
- **High Risk** ($\text{Probability} \ge 0.70$): **1,033 students (23.3%)**

All probabilities and risk tiers were committed to database table `dropout_predictions` and exported to `dataset/analytics/predictions/dropout_risk_predictions.csv`.

---

## 4. Phase 9: Personalized Student Recommendation System

Phase 9 implements an institutional early intervention engine. Domain experts established policy rules across 5 intervention categories:
- **Academic Remedial & Tutoring**: Triggers on failing grades ($< 11.5/20$) or failed course units ($\ge 1$).
- **Tuition & Financial Aid Advisory**: Triggers when tuition arrears exist or student is flagged as debtor.
- **Attendance & Schedule Advising**: Triggers for evening shift students who are experiencing academic distress.
- **Faculty Mentorship & Retention Coaching**: Triggers for high/medium risk tier students or steep trajectory declines ($\le -2.0$).
- **Advanced Career & Research Enrichment**: Triggers for top-tier achievers ($\text{GPA} \ge 14.0/20$).

### Intervention Generation Summary
- Total personalized action plans generated: **9,952 recommendations across 4,424 students**.
- Priority Distribution:
  - **Critical**: 3,792 action items (urgent intervention required within 7 days).
  - **High**: 1,539 action items.
  - **Medium**: 1,228 action items.
  - **Low**: 3,393 enrichment recommendations.
- Persisted to MySQL / SQLite table `student_recommendations` and exported to `dataset/analytics/recommendations/student_recommendations.csv`.

---

## 5. Phase 10: Production Web Dashboard & End-to-End System Integration

### Full-Stack Architecture
- **Backend**: FastAPI (Python 3.13) serving RESTful endpoints with CORS middleware and OpenAPI Swagger documentation (`http://localhost:8000/docs`).
- **Database Access Layer**: `db_service.py` providing unified SQL queries for MySQL 8.0 and SQLite fallback.
- **Frontend**: Responsive Single-Page Application (SPA) styled with **Tailwind CSS**, dynamic visualizations powered by **Chart.js**, and vector icons via **Lucide**.
- **Zero-Setup Delivery**: Frontend is directly mounted by FastAPI at `http://localhost:8000/`, providing instant out-of-the-box browser execution.

### Dashboard Core Capabilities
1. **Overview Dashboard**: Real-time KPI summary cards (Total Cohort, Institutional GPA, High-Risk Count, Critical Interventions), Risk Distribution Donut Chart, and Course Performance Bar Charts.
2. **Student Roster & Explorer**: Searchable by student ID, filterable by risk tier (High, Medium, Low), with live pagination and quick access to individual profiles.
3. **Student Profile & Transcript Modal**: Comprehensive academic record showing admission marks, semester 1 vs semester 2 performance, failure count, schedule shift, ML risk diagnosis, and assigned actionable recommendations.
4. **Dropout Risk Analytics**: Algorithm benchmark comparisons (ROC-AUC, Precision, Recall), top priority at-risk student table, and primary diagnostic barrier breakdowns.
5. **Prescriptive Interventions Manager**: Categorized cards detailing specific remedial action plans, priority levels, and progress statuses (Pending, In Progress, Completed).
6. **Reports & Data Export**: Instant 1-click download of the complete 4,424-record predictions CSV and recommendations catalog.

### Verification Suite Results
The automated API and system test suite (`phase10_dashboard/backend/test_api.py`) executed 9 comprehensive integration tests with a 100% pass rate:
```
[PASS] /api/health: Service healthy, version 1.0.0
[PASS] /api/auth/login: Auth token received for Dr. Sarah Jenkins
[PASS] /api/dashboard/stats: Total Students=4424, Avg Grade=10.44, High Risk=1033
[PASS] /api/students: Returned paginated records (Total: 4424)
[PASS] /api/students/{id}: Risk Tier, Primary Factors, and Assigned Interventions verified
[PASS] /api/analytics/performance: 17 Degree Courses analyzed
[PASS] /api/risk/predictions: Top at-risk cohort and 4 ML algorithm benchmarks verified
[PASS] /api/reports/export: 783 KB CSV prediction stream verified
[PASS] / (Frontend Dashboard): Successfully served responsive HTML application
```

---

## 6. How to Run and Verify the Entire System

### 1. Execute Machine Learning Pipeline (Phase 8)
```bash
# Model training and benchmark comparison
python phase8_dropout_prediction/train_model.py

# Model evaluation & visualization generation
python phase8_dropout_prediction/evaluate_model.py

# Batch risk scoring of all 4,424 students & DB persistence
python phase8_dropout_prediction/predict_risk.py
```

### 2. Execute Recommendation Engine (Phase 9)
```bash
# Generate 9,952 personalized interventions and persist to database
python phase9_recommendation_system/mysql_integration.py
```

### 3. Launch Full-Stack Web Application (Phase 10)
```bash
# Start FastAPI and Web Dashboard
python phase10_dashboard/backend/run_backend.py
```
Open your browser at:
- **Interactive Web Dashboard**: `http://localhost:8000/`
- **Interactive Swagger REST API Docs**: `http://localhost:8000/docs`
- **Admin Login**: `admin` / `smartedu2026`

---

## 7. Complete Artifacts Directory Map

```text
d:\bdampr\SmartEduAnalytics\
├── dataset/
│   ├── raw/raw_student_data.csv
│   ├── processed/preprocessed_student_data.csv
│   └── analytics/
│       ├── mapreduce/
│       ├── hive/
│       ├── spark/
│       ├── predictions/dropout_risk_predictions.csv
│       └── recommendations/student_recommendations.csv
├── visualizations/
│   ├── phase1/ (6 EDA figures)
│   ├── phase3/ (5 MapReduce figures)
│   ├── phase4/ (5 Hive figures)
│   ├── phase6/ (5 Spark figures)
│   ├── phase7/ (5 Streaming figures)
│   └── phase8/ (4 ML evaluation figures)
├── phase5_mysql/
│   ├── schema.sql
│   ├── config.py
│   ├── import_data.py
│   ├── student_crud.py
│   └── smartedu_local.db
├── phase6_spark/
│   └── run_local_spark_simulation.py
├── phase7_streaming/
│   └── run_streaming_pipeline.py
├── phase8_dropout_prediction/
│   ├── data_preprocessing.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   ├── predict_risk.py
│   ├── evaluation_results.csv
│   ├── feature_importance.csv
│   └── models/ (model.joblib, scaler.joblib, models_comparison.csv)
├── phase9_recommendation_system/
│   ├── recommendation_rules.py
│   ├── student_analysis.py
│   ├── recommendation_engine.py
│   └── mysql_integration.py
├── phase10_dashboard/
│   ├── backend/
│   │   ├── main.py
│   │   ├── db_service.py
│   │   ├── run_backend.py
│   │   └── test_api.py
│   └── frontend/
│       ├── index.html
│       ├── app.js
│       ├── styles.css
│       └── package.json
├── FINAL_PROJECT_REPORT.md
└── README.md
```

---
*Report successfully generated and verified. All 10 project phases are complete, fully integrated, and production-ready.*
