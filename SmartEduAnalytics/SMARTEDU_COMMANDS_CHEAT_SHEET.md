# SmartEdu Analytics: Live Commands Cheatsheet (For 3 Presenters)
## Big Data Analytics (BDA) Lab Practical Demonstration

---

## ⚡ 0. ONE-TIME INITIAL CLOUDERA VM SETUP (Run Once Before Presentation)
**Environment:** Cloudera QuickStart VM 5.13.0 Terminal
```bash
cd ~
wget -O smartedu.tar.gz http://192.168.56.1:8889/smartedu.tar.gz || wget -O smartedu.tar.gz http://10.0.2.2:8889/smartedu.tar.gz
tar -xzvf smartedu.tar.gz -C ~
cd ~/SmartEduAnalytics
chmod +x scripts/phase2/*.sh scripts/phase3/*.sh scripts/phase3/*.py scripts/phase4/*.sh run_all_cloudera.sh
```

---

## 👨‍💻 SPEAKER 1 COMMANDS: HDFS Storage & Health Inspection
**Environment:** Cloudera QuickStart VM 5.13.0 Terminal

### 1. Navigate to Project Directory:
```bash
cd /home/cloudera/SmartEduAnalytics
```

### 2. Ingest Dataset into HDFS:
```bash
bash scripts/phase2/upload_dataset_to_hdfs.sh . -f
```

### 3. List All HDFS Directories & Files:
```bash
hdfs dfs -ls -R /smartedu
```

### 4. Verify HDFS Health & 128 MB Block Allocation:
```bash
hdfs fsck /smartedu/processed/preprocessed_student_data.csv -files -blocks
```

### 5. Preview First 5 Rows of HDFS Preprocessed Data:
```bash
hdfs dfs -cat /smartedu/processed/preprocessed_student_data.csv | head -n 5
```

### 6. NameNode Web UI:
- Open Firefox in Cloudera VM:
- URL: **`http://localhost:50070`** ➡️ *Utilities > Browse the file system > `/smartedu/processed/`*

---

## ⚙️ SPEAKER 2 COMMANDS: MapReduce Streaming & Apache Hive
**Environment:** Cloudera QuickStart VM (Hadoop 2.6.0, YARN, Hive 1.1.0) Terminal

### 1. Execute Distributed MapReduce Job (Fail-Safe: Auto-cleans previous output):
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

### 2. View YARN ResourceManager UI:
- Open Firefox in Cloudera VM:
- URL: **`http://localhost:8088`** ➡️ *Show State: `SUCCEEDED`, FinalStatus: `SUCCESS`*

### 3. Read MapReduce Output Partitions from HDFS:
```bash
hdfs dfs -cat /smartedu/analytics/mapreduce/demo_avg_job/part-* | head -n 10
```

### 4. Initialize Hive Data Warehouse Schema (Creates database & tables):
```bash
bash scripts/phase4/create_hive_database.sh
```

### 5. Interactive Apache Hive CLI Queries (HiveQL):
```bash
hive
```
Inside Hive prompt:
```sql
USE smartedu;

SHOW TABLES;

DESCRIBE students_ext;

SELECT course_id, COUNT(*) AS total_students, ROUND(AVG(annual_grade_avg), 2) AS avg_gpa
FROM students_ext
GROUP BY course_id
ORDER BY total_students DESC
LIMIT 5;

exit;
```

---

## 🖥️ SPEAKER 3 COMMANDS: Web Dashboard & System Integration
**Environment:** Windows Host PowerShell & Web Browser

### 1. Launch FastAPI Server & Web Application:
```powershell
cd d:\bdampr\SmartEduAnalytics
d:\bdampr\.venv\Scripts\python.exe run_all.py --server-only
```

### 2. Open Interactive Web Dashboard:
- Browser URL: **`http://127.0.0.1:8000/`**
- Default Admin Login: `admin` / `smartedu2026`

### 3. Walkthrough Sequence in Dashboard:
1. **Overview Tab**: Point to **4,424** Total Students, **10.44** GPA, **1,033** High Risk (23.3%), Doughnut chart, and Course Pass Rate bars.
2. **Student Roster Tab**: Type `STD_11688` in the search box ➡️ Click **Profile** button ➡️ Show Semester 1 vs 2 grade drop, failed units, and 5 assigned personalized interventions.
3. **Dropout Risk ML Tab**: Point to **Gradient Boosting** champion benchmark (**93.06% ROC-AUC**, **88.70% Accuracy**).
4. **Top Header**: Click **Export Predictions CSV** to download the complete 4,424-record scored dataset.

### 4. Automated Backend API Verification Suite (Optional for Examiner):
```powershell
d:\bdampr\.venv\Scripts\python.exe phase10_dashboard\backend\test_api.py
```
