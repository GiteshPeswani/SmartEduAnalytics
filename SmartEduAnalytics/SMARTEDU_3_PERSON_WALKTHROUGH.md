# SmartEdu Analytics: 3-Person Project Walkthrough Guide
## Big Data Analytics (BDA) Practical Demonstration Script

**Document Path**: `SmartEdu_3_Person_Walkthrough_Guide.pdf` & `SMARTEDU_3_PERSON_WALKTHROUGH.md`  
**Dataset Scale**: 4,424 verified student records (UCI Machine Learning Repository #697)  
**Target Environments**: Cloudera QuickStart VM 5.13.0 (Hadoop 2.6.0, YARN, Hive 1.1.0) & Windows Host (FastAPI, Tailwind CSS, Chart.js)

---

## Team Division Overview

| Presenter | Core Focus Area | Platform / Terminal | Key Artifacts Demonstrated |
|---|---|---|---|
| **Speaker 1** | Project Intro, Data Preprocessing & HDFS Storage | Cloudera VM Terminal & Port 50070 | UCI 697 dataset, `/smartedu/` HDFS hierarchy, block inspection |
| **Speaker 2** | Distributed Processing & Data Warehousing | Cloudera VM Terminal, Port 8088 & Hive | Hadoop Streaming MapReduce Job, HiveQL queries, External Tables |
| **Speaker 3** | ML Modeling, Recommendations & Web Dashboard | Windows Host (FastAPI Port 8000) | Gradient Boosting ML (93.06% AUC), Risk Tiers, Roster, Modal, CSV |

---

# PART 1: SPEAKER 1 - Project Intro & HDFS Storage

### 1.1 Project Introduction
> **What to Say:**  
> *"Good morning Ma'am. Our project is SmartEdu Analytics: A Big Data-Driven Student Performance Analysis and Dropout Risk Prediction System. Higher education institutions face high attrition rates. Our objective is to ingest a verified dataset of 4,424 students, store it across distributed HDFS, process parallel aggregations via MapReduce and Hive on Cloudera QuickStart, and finally predict attrition risks using machine learning. I will demonstrate the Data Preprocessing and HDFS Storage layer."*

### 1.2 Navigate to Project in Cloudera Terminal
Open Cloudera QuickStart VM Terminal and type:
```bash
cd /home/cloudera/SmartEduAnalytics
```

### 1.3 Demonstrate Distributed HDFS File System (Phase 2)
> **What to Say:**  
> *"Ma'am, our cleaned dataset has been transferred to Hadoop Distributed File System (HDFS). We created an organized namespace partitioned into `/smartedu/raw` for raw data archives, `/smartedu/processed` for sanitized feature vectors, and `/smartedu/analytics` for job outputs. Let us inspect the files directly inside HDFS."*

**Command to Type:**
```bash
hdfs dfs -ls -R /smartedu
```
- **What to Point Out on Screen**: Show `raw_student_data.csv` (1.48 MB) and `preprocessed_student_data.csv` (1.84 MB) stored in HDFS.

### 1.4 Demonstrate HDFS Health & Block Allocation
**Command to Type:**
```bash
hdfs fsck /smartedu/processed/preprocessed_student_data.csv -files -blocks
```
> **What to Say:**  
> *"As you can see, HDFS reports filesystem status as HEALTHY. The preprocessed dataset is partitioned into Hadoop default 128 MB blocks with a replication factor of 1 on this cluster."*

### 1.5 NameNode Web UI Demonstration
Open Firefox browser inside Cloudera VM and navigate to: **`http://localhost:50070`**
> **What to Say:**  
> *"Here is the HDFS NameNode Web Interface. By clicking on Utilities -> Browse the file system and opening `/smartedu/processed`, we can visually verify the uploaded files. I will now hand over to Speaker 2 to demonstrate distributed processing via MapReduce and Hive."*

---

# PART 2: SPEAKER 2 - Distributed MapReduce & Apache Hive

### 2.1 Distributed Hadoop MapReduce Streaming (Phase 3)
> **What to Say:**  
> *"Thank you Speaker 1. Now I will demonstrate distributed computing using Hadoop MapReduce on YARN. Instead of Java compilation, we implemented 5 MapReduce streaming jobs using Python mappers and reducers. The Hadoop Streaming utility handles parallel data piping, sorting, and shuffling automatically. I will now execute Job 1 to calculate overall and course-level student academic averages."*

**Command to Type:**
```bash
hdfs dfs -rm -r -f /smartedu/analytics/mapreduce/demo_avg_job 2>/dev/null

hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
  -input /smartedu/processed/preprocessed_student_data.csv \
  -output /smartedu/analytics/mapreduce/demo_avg_job \
  -mapper "python mapper_average.py" \
  -reducer "python reducer_average.py" \
  -file scripts/phase3/mapper_average.py \
  -file scripts/phase3/reducer_average.py
```
- **What to Point Out on Screen**: Point to the terminal output showing `Map 0% -> Map 100% -> Reduce 100%`.

### 2.2 YARN Web Interface & Output Verification
Open Firefox in Cloudera VM at: **`http://localhost:8088`**
> **What to Say:**  
> *"In the YARN ResourceManager UI at port 8088, we see our application has been allocated containers and completed with state SUCCEEDED. Let us now examine the generated output partitions on HDFS."*

**Command to Type:**
```bash
hdfs dfs -cat /smartedu/analytics/mapreduce/demo_avg_job/part-* | head -n 8
```
- **What to Point Out on Screen**: Point to the tab-delimited output displaying course performance and cumulative average marks (11.53/20).

### 2.3 Apache Hive Data Warehousing (Phase 4)
> **What to Say:**  
> *"Next, I will demonstrate Phase 4: Apache Hive Data Warehousing. We first initialize the Hive Data Warehouse catalog and external tables mapped directly to our HDFS CSV files, then query it using standard HiveQL without moving underlying data blocks."*

**1. Initialize Hive Warehouse:**
```bash
bash scripts/phase4/create_hive_database.sh
```

**2. Interactive Hive CLI Query (HiveQL):**
```sql
hive
USE smartedu;
SHOW TABLES;
SELECT course_id, COUNT(*) AS student_count, ROUND(AVG(annual_grade_avg), 2) AS avg_gpa
FROM students_ext
GROUP BY course_id
ORDER BY student_count DESC
LIMIT 5;
exit;
```
> **What to Say:**  
> *"The Hive query parsed the table, executed a background MapReduce aggregation, and returned the top courses by enrollment. I will now hand over to Speaker 3 to present our Machine Learning Dropout Risk Prediction model and the production Web Application Dashboard."*

---

# PART 3: SPEAKER 3 - Machine Learning, Recommendations & Web UI

### 3.1 Machine Learning Dropout Risk Prediction (Phase 8)
> **What to Say:**  
> *"Thank you Speaker 2. While Hadoop and Hive provide distributed batch analytics, our objective is proactive intervention. In Phase 8, we engineered 21 academic and socio-economic predictors and benchmarked 4 algorithms on an 80/20 stratified split of 4,424 students. Gradient Boosting achieved champion performance with 93.06% ROC-AUC and 88.70% accuracy, outperforming Random Forest, Logistic Regression, and Decision Trees. Feature importance reveals that accumulated failed course units, semester 2 grades, and tuition payment are the top 3 attrition drivers."*

### 3.2 Personalized Recommendation Engine (Phase 9)
> **What to Say:**  
> *"In Phase 9, we built an automated intervention engine mapping student distress signals to actionable remediation. It generated 9,952 prioritized action items: 3,792 Critical items for urgent peer tutoring and financial holds, 1,539 High priority trajectory recovery sessions, and 3,393 enrichment recommendations for high-achieving scholars. All predictions and recommendations are persisted in relational tables."*

### 3.3 Production Web Dashboard Live Demonstration (Phase 10)
Switch to the browser on the Windows host at: **`http://127.0.0.1:8000/`**
> **What to Say:**  
> *"Here is our production full-stack application built with FastAPI, Tailwind CSS, and Chart.js.*
> 
> *1. **Overview Tab**: We see live KPI cards for all 4,424 enrolled students, overall GPA 10.44/20, and 1,033 students flagged in the High-Risk tier (23.3%). Below are interactive Doughnut and Course Pass-Rate charts.*
> 
> *2. **Student Roster Tab**: Let us switch to the Student Directory. It features server-side pagination and real-time filtering.*
> 
> *3. **Search Demonstration**: I will search for student 'STD_11688'. Notice their high risk probability of 91.2%. Clicking 'Profile' opens their complete academic transcript, semester 1 vs semester 2 drop, and 5 assigned interventions.*
> 
> *4. **Export Report**: Clicking 'Export Predictions CSV' initiates an instant download of all 4,424 scored records.*
> 
> *This completes our end-to-end Big Data & AI pipeline from Hadoop HDFS to real-time administrative intelligence."*

---

## 🎯 Quick Viva Answers (Reference for All 3 Presenters)

| Question | 1-Sentence Answer |
|---|---|
| **Why use HDFS over local disk?** | HDFS provides distributed storage with automatic block replication and fault tolerance across nodes. |
| **Why MapReduce Streaming?** | Hadoop Streaming allows standard Unix I/O with Python scripts while YARN handles parallel cluster distribution. |
| **Why External Table in Hive?** | External tables decouple data from schema so dropping the table preserves underlying HDFS files safely. |
| **Why Gradient Boosting for ML?** | It achieved highest ROC-AUC (93.06%) by sequentially correcting weak learner residuals and handling class imbalance. |
