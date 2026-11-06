# SmartEdu Analytics – Phase 5: MySQL Database Integration

## Overview
Phase 5 integrates MySQL Server (8.0+) with the SmartEdu Analytics big data project. It establishes the relational database layer that stores student demographic baselines, course performance indicators, attendance metrics, and historical analytical outputs imported from Phase 3 (MapReduce) and Phase 4 (Apache Hive).

---

## Relational Schema Structure

- **`students`**: Demographic baseline, admission marks, and ground-truth administrative outcomes (`is_dropout`, `target_outcome`).
- **`performance_analytics`**: Semester 1 and 2 grades, units enrolled/approved/failed, and performance classification tiers.
- **`attendance_analytics`**: Daytime vs. Evening attendance mode, unattended unit counts, participation rates, and `< 75%` low-attendance alert flags.
- **`risk_indicators`**: Academic risk score, risk level (`Low_Risk`, `Moderate_Risk`, `High_Risk`), and financial factors (`tuition_fees_up_to_date`, `is_debtor`, `scholarship_holder`).
- **`hive_results`**: Historical course performance rankings and approval pass rates imported from Phase 4 Hive / Phase 3 MapReduce.
- **`v_high_risk_students`**: Analytical View surfacing at-risk students for proactive intervention.
- **`v_course_summary`**: Analytical View aggregating degree program graduation and dropout rates.

---

## Step-by-Step Execution Guide

### 1. Configure Database Credentials
Edit `config.py` or set environment variables:
```bash
export MYSQL_HOST="localhost"
export MYSQL_PORT=3306
export MYSQL_USER="root"
export MYSQL_PASSWORD="your_password"
export MYSQL_DATABASE="smartedu"
```
*(Note: If MySQL server is not running locally, the system automatically falls back to an embedded SQLite engine `smartedu_local.db` for demonstration and verification without interruption).*

### 2. Ingest Dataset & Historical Phase 3/4 Results
```bash
python import_data.py
```
*Output: 4,424 records populated in `students`, `performance_analytics`, `attendance_analytics`, `risk_indicators`, and 17 course records in `hive_results`.*

### 3. Test Relational CRUD Operations
```bash
python student_crud.py
```
*Demonstrates Create, Read, Update, and Delete operations with foreign-key cascade integrity.*

### 4. Execute Relational SQL Analytics
```bash
python run_mysql_analytics.py
```
*Executes all 7 analytical SQL queries demonstrating multi-table JOINs, GROUP BY, HAVING, subqueries, and Views.*

---

## File Manifest
- `schema.sql`: Complete DDL schema script for MySQL 8.0+.
- `config.py`: Database connection manager and configuration.
- `import_data.py`: Batch data ingestion and historical Hive result integration.
- `student_crud.py`: Modular CRUD interface.
- `mysql_analytics.sql`: Pure SQL analytics queries.
- `run_mysql_analytics.py`: Python-driven SQL analytics executor.
