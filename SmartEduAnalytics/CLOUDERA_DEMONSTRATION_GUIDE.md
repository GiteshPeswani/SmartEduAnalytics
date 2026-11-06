# SmartEdu Analytics: Cloudera QuickStart VM Live Demonstration Guide

This guide provides step-by-step instructions to demonstrate **Phase 2 (HDFS)**, **Phase 3 (MapReduce)**, and **Phase 4 (Apache Hive)** directly inside your **Cloudera QuickStart VM (Hadoop 2.6.0-cdh5.13.0)**.

---

## 1. Cloudera Environment Overview
- **Virtual Machine**: Cloudera QuickStart VM 5.13.0 (CentOS 6.7 64-bit)
- **Hadoop Version**: 2.6.0-cdh5.13.0
- **Hive Version**: 1.1.0-cdh5.13.0
- **Default User**: `cloudera` (Password: `cloudera`)
- **Web Interfaces in VM**:
  - **HDFS NameNode UI**: `http://localhost:50070`
  - **YARN ResourceManager UI**: `http://localhost:8088`
  - **Hue Web Console**: `http://localhost:8888`

---

## 2. Step 1: Transfer Project Files to Cloudera VM

### Method A: Using VirtualBox Shared Folder (Recommended)
1. In VirtualBox, go to **Devices > Shared Folders > Shared Folders Settings...**
2. Add a shared folder pointing to `D:\bdampr\SmartEduAnalytics`, check **Auto-mount** and **Make Permanent**.
3. In Cloudera VM terminal:
   ```bash
   sudo mkdir -p /media/sf_SmartEduAnalytics
   sudo mount -t vboxsf SmartEduAnalytics /media/sf_SmartEduAnalytics
   cp -r /media/sf_SmartEduAnalytics ~/SmartEduAnalytics
   cd ~/SmartEduAnalytics
   ```

### Method B: Using SCP / WinSCP from Windows
In Windows PowerShell (with Cloudera VM Network set to Bridged or Host-Only, e.g., IP `192.168.56.101`):
```powershell
scp -r d:\bdampr\SmartEduAnalytics cloudera@192.168.56.101:/home/cloudera/
```

---

## 3. Step 2: One-Click Master Execution Inside Cloudera VM

Open the Cloudera terminal and run:
```bash
cd /home/cloudera/SmartEduAnalytics
chmod +x run_all_cloudera.sh
./run_all_cloudera.sh
```
*This automatically executes Phase 2 (HDFS upload & health check), Phase 3 (5 distributed MapReduce jobs), and Phase 4 (Hive warehouse creation & queries).*

---

## 4. Step 3: Demonstrating Phase 2 (Hadoop HDFS Storage)

In the Cloudera terminal, demonstrate these commands to your examiner:

### 1. Show HDFS Health & SafeMode:
```bash
hdfs dfsadmin -report
hdfs dfsadmin -safemode get
```

### 2. Inspect the SmartEdu HDFS Directory Hierarchy:
```bash
hdfs dfs -ls -R /smartedu
```
*Expected Output:*
```text
drwxr-xr-x   - cloudera cloudera          0 /smartedu/raw
-rw-r--r--   1 cloudera cloudera    1484223 /smartedu/raw/raw_student_data.csv
drwxr-xr-x   - cloudera cloudera          0 /smartedu/processed
-rw-r--r--   1 cloudera cloudera    1845129 /smartedu/processed/preprocessed_student_data.csv
-rw-r--r--   1 cloudera cloudera    1475102 /smartedu/processed/train_data.csv
-rw-r--r--   1 cloudera cloudera     370027 /smartedu/processed/test_data.csv
drwxr-xr-x   - cloudera cloudera          0 /smartedu/analytics
```

### 3. Verify Block Allocation and File Integrity:
```bash
hdfs fsck /smartedu/processed/preprocessed_student_data.csv -files -blocks -locations
```

### 4. Demonstrate HDFS Head Read:
```bash
hdfs dfs -cat /smartedu/processed/preprocessed_student_data.csv | head -n 5
```

### 5. Show NameNode Web UI:
Open Firefox inside Cloudera VM and go to **`http://localhost:50070`**:
- Click **Utilities > Browse the file system**
- Navigate to `/smartedu/processed/` to show the preprocessed dataset live in the Hadoop GUI!

---

## 5. Step 4: Demonstrating Phase 3 (Hadoop MapReduce Streaming)

### 1. Show MapReduce Streaming Python Scripts:
```bash
cat scripts/phase3/mapper_average.py
cat scripts/phase3/reducer_average.py
```

### 2. Run MapReduce Job 1 (Student Performance Average):
```bash
hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \
  -input /smartedu/processed/preprocessed_student_data.csv \
  -output /smartedu/analytics/mapreduce/job1_average \
  -mapper "python scripts/phase3/mapper_average.py" \
  -reducer "python scripts/phase3/reducer_average.py" \
  -file scripts/phase3/mapper_average.py \
  -file scripts/phase3/reducer_average.py
```

### 3. View MapReduce Output on HDFS:
```bash
hdfs dfs -cat /smartedu/analytics/mapreduce/job1_average/part-* | head -n 10
```

### 4. Show YARN ResourceManager UI:
Open Firefox inside Cloudera VM at **`http://localhost:8088`**:
- Show the completed MapReduce application status (`Application-Id`, `SUCCEEDED`, tracking URL).

---

## 6. Step 5: Demonstrating Phase 4 (Apache Hive Data Warehousing)

### 1. Launch Interactive Hive CLI:
```bash
hive
```

### 2. Run HiveQL Commands Live:
```sql
-- 1. Switch to project database
USE smartedu;

-- 2. Show tables
SHOW TABLES;

-- 3. Describe schema of students external table
DESCRIBE students_ext;

-- 4. Count total student records in Hive
SELECT COUNT(*) FROM students_ext;

-- 5. Query average GPA and dropout count by degree course
SELECT 
    course_id,
    COUNT(*) AS total_students,
    ROUND(AVG(annual_grade_avg), 2) AS avg_gpa,
    SUM(CASE WHEN is_dropout = 1 THEN 1 ELSE 0 END) AS dropouts
FROM students_ext
GROUP BY course_id
ORDER BY total_students DESC
LIMIT 10;

-- 6. Exit Hive
EXIT;
```

---

## 7. Viva / Evaluation Talking Points

1. **Why Hadoop 2.6.0 on Cloudera QuickStart VM?**
   - Cloudera QuickStart VM 5.13.0 provides an authentic, enterprise-grade CDH distribution with pre-configured HDFS, YARN, and Hive daemons running on CentOS.
2. **Why Hadoop Streaming for MapReduce?**
   - Hadoop Streaming enables Python mappers and reducers to process distributed HDFS splits via standard I/O pipes while letting the Hadoop YARN cluster manage parallel execution, failure recovery, and shuffle sorting.
3. **How does Hive connect to HDFS?**
   - The Hive table `students_ext` is an `EXTERNAL TABLE` pointing directly to `hdfs:///smartedu/processed/preprocessed/`, so HiveQL queries execute distributed MapReduce jobs on the underlying HDFS storage without copying the data.
4. **How does Cloudera connect to the final Web Dashboard?**
   - MapReduce and Hive aggregation results are extracted to `dataset/analytics/` and synced into MySQL/SQLite (Phase 5), powering the FastAPI REST backend and interactive frontend dashboard.
