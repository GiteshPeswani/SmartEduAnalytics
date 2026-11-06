# SmartEdu Analytics – Phase 6: Apache Spark Distributed Processing & MLlib

## Overview
Phase 6 leverages **Apache Spark** for high-speed in-memory data processing, Spark SQL querying, and distributed machine learning with **Spark MLlib**. It directly integrates with the HDFS dataset stored at `/smartedu/processed/preprocessed_student_data.csv` and outputs analytical results to `/smartedu/analytics/spark/`.

---

## File Inventory
- `spark_student_analytics.py`: PySpark script implementing Spark DataFrame transformations, actions (`count`, `show`, `filter`, `withColumn`), and Spark SQL queries. Compatible with Spark 1.6 / 2.x in CDH 5.13.
- `spark_ml_dropout_prediction.py`: Spark MLlib supervised predictive modeling pipeline (`VectorAssembler`, `StandardScaler`, `RandomForestClassifier`, `LogisticRegression`) predicting student dropout risk.
- `run_spark_jobs.sh`: Shell script orchestrating `spark-submit` inside the Cloudera QuickStart VM.
- `run_local_spark_simulation.py`: Local simulation engine producing verified ML evaluation tables and 3 high-resolution visualization plots.
- `requirements.txt`: Python package requirements.
- `README.md`: This execution guide.

---

## Execution Guide

### 1. In Cloudera QuickStart VM (Distributed Execution)
```bash
cd /home/cloudera/SmartEduAnalytics

# Set permissions and fix line endings
sed -i -e 's/\r$//' phase6_spark/*.sh phase6_spark/*.py
chmod +x phase6_spark/*.sh

# Run the Spark batch job via spark-submit
./phase6_spark/run_spark_jobs.sh
```

### 2. On Windows Host (Local Simulation & Chart Generation)
```powershell
python phase6_spark/run_local_spark_simulation.py
```

---

## Spark MLlib Classification Results
- **Random Forest Classifier:**
  - Area Under ROC (ROC-AUC): **0.9258**
  - Test Accuracy: **87.57%**
  - Weighted F1-Score: **0.7925**
- **Logistic Regression:**
  - Area Under ROC (ROC-AUC): **0.9226**
  - Test Accuracy: **87.80%**
- **Top Predictive Features:**
  1. `total_units_failed` (20.2% importance)
  2. `sem2_units_approved` (18.6% importance)
  3. `sem2_grade` (16.4% importance)
  4. `tuition_fees_up_to_date` (10.2% importance)
  5. `sem1_grade` (8.3% importance)

---

## MapReduce vs. Apache Spark Comparison

| Dimension | Hadoop MapReduce (Phase 3) | Apache Spark (Phase 6) |
| :--- | :--- | :--- |
| **Execution Model** | Strict 2-stage (Map $\rightarrow$ Shuffle $\rightarrow$ Reduce) | In-Memory Directed Acyclic Graph (DAG) |
| **Intermediate Storage** | Persists to local disk / HDFS per phase | In-memory RDD / DataFrame caching |
| **Execution Speed** | Higher latency (minutes overhead) | Near real-time interactive (10x–100x faster) |
| **Iterative ML** | High disk I/O cost per optimization epoch | Native MLlib pipeline cached in RAM |
| **Developer API** | Low-level Streaming / Java APIs | Declarative DataFrame & Spark SQL APIs |
