# SmartEdu Analytics - HDFS Ingestion Command Reference Guide
**Cluster Target:** Cloudera QuickStart VM 5.13.0 (Hadoop 2.6.0-cdh5.13.0)  
**HDFS NameNode URI:** `hdfs://quickstart.cloudera:8020` / `hdfs://localhost:8020`  
**Web UI:** `http://localhost:50070` (NameNode) | `http://localhost:8088` (YARN)

---

## 1. Transferring Phase 1 Files from Windows into Cloudera VM

### Method A: VirtualBox Shared Folder (Recommended)
1. Open VirtualBox Manager with Cloudera VM selected.
2. Go to **Settings > Shared Folders**.
3. Add a new Shared Folder:
   - **Folder Path:** `D:\bdampr\SmartEduAnalytics`
   - **Folder Name:** `SmartEduAnalytics`
   - Check **Auto-mount** and **Make Permanent**.
4. In Cloudera VM terminal (as `cloudera` user):
   ```bash
   sudo usermod -aG vboxsf cloudera
   sudo mkdir -p /media/sf_SmartEduAnalytics
   sudo mount -t vboxsf SmartEduAnalytics /media/sf_SmartEduAnalytics
   ls -la /media/sf_SmartEduAnalytics
   ```
5. Copy files into Cloudera home:
   ```bash
   mkdir -p /home/cloudera/SmartEduAnalytics
   cp -r /media/sf_SmartEduAnalytics/* /home/cloudera/SmartEduAnalytics/
   cd /home/cloudera/SmartEduAnalytics
   chmod +x scripts/phase2/*.sh
   ```

### Method B: Secure Copy (`scp`) via SSH
From Windows PowerShell (assuming NAT port forward on port 2222 or host-only IP `192.168.56.101`):
```powershell
# Using default Cloudera VM credentials: cloudera / cloudera
ssh -p 2222 cloudera@localhost "mkdir -p ~/SmartEduAnalytics/dataset/raw ~/SmartEduAnalytics/dataset/processed ~/SmartEduAnalytics/reports ~/SmartEduAnalytics/scripts/phase2"

# Transfer datasets
scp -P 2222 d:\bdampr\SmartEduAnalytics\dataset\raw\raw_student_data.csv cloudera@localhost:~/SmartEduAnalytics/dataset/raw/
scp -P 2222 d:\bdampr\SmartEduAnalytics\dataset\processed\*.csv cloudera@localhost:~/SmartEduAnalytics/dataset/processed/
scp -P 2222 d:\bdampr\SmartEduAnalytics\reports\dataset_summary.txt cloudera@localhost:~/SmartEduAnalytics/reports/
scp -P 2222 d:\bdampr\SmartEduAnalytics\scripts\phase2\*.sh cloudera@localhost:~/SmartEduAnalytics/scripts/phase2/
```

---

## 2. Command-by-Command Manual Reference

### Task 1: HDFS Cluster Health Check
```bash
# 1. Check Hadoop CLI version
hadoop version

# 2. Check active Java Daemons
jps
# Expected: NameNode, DataNode, SecondaryNameNode, ResourceManager, NodeManager

# 3. Check NameNode SafeMode status
hdfs dfsadmin -safemode get

# 4. If SafeMode is active, force leave:
hdfs dfsadmin -safemode leave

# 5. Cluster health and storage capacity report
hdfs dfsadmin -report
```

### Task 2: HDFS Directory Creation
```bash
# Create base and functional directories
hdfs dfs -mkdir -p /smartedu/raw
hdfs dfs -mkdir -p /smartedu/processed
hdfs dfs -mkdir -p /smartedu/analytics
hdfs dfs -mkdir -p /smartedu/reports

# Set permissions for multi-user access
hdfs dfs -chmod -R 775 /smartedu

# Verify creation
hdfs dfs -ls -R /smartedu
```

### Task 3: Ingestion of Phase 1 Datasets
```bash
cd /home/cloudera/SmartEduAnalytics

# Ingest raw dataset
hdfs dfs -put dataset/raw/raw_student_data.csv /smartedu/raw/

# Ingest cleaned and preprocessed datasets
hdfs dfs -put dataset/processed/cleaned_student_data.csv /smartedu/processed/
hdfs dfs -put dataset/processed/preprocessed_student_data.csv /smartedu/processed/
hdfs dfs -put dataset/processed/train_data.csv /smartedu/processed/
hdfs dfs -put dataset/processed/test_data.csv /smartedu/processed/

# Ingest summary report
hdfs dfs -put reports/dataset_summary.txt /smartedu/reports/
```

### Task 4: HDFS Storage Verification
```bash
# List all files and permissions
hdfs dfs -ls -R /smartedu

# Check human-readable disk space usage
hdfs dfs -du -h /smartedu/

# Count files, directories, and total byte size
hdfs dfs -count /smartedu/processed
```

### Task 5: Data Integrity & Record Count Comparison
```bash
# Check record counts (excluding CSV header):
# Local vs HDFS Cleaned Dataset
echo "Local records: $(tail -n +2 dataset/processed/cleaned_student_data.csv | wc -l)"
echo "HDFS records:  $(hdfs dfs -cat /smartedu/processed/cleaned_student_data.csv | tail -n +2 | wc -l)"

# Check exact byte sizes:
echo "Local size: $(stat -c%s dataset/processed/cleaned_student_data.csv) bytes"
echo "HDFS size:  $(hdfs dfs -stat "%b" /smartedu/processed/cleaned_student_data.csv) bytes"

# Stream first 5 rows from HDFS
hdfs dfs -cat /smartedu/processed/cleaned_student_data.csv | head -n 5
```

### Task 6: HDFS Read, Write & Download Demonstration
```bash
# 1. Download file back from HDFS to local temp
mkdir -p /tmp/verify
hdfs dfs -get /smartedu/processed/cleaned_student_data.csv /tmp/verify/cleaned_downloaded.csv

# 2. Cryptographic checksum validation
md5sum dataset/processed/cleaned_student_data.csv
md5sum /tmp/verify/cleaned_downloaded.csv

# 3. Clean up temporary test files
rm -rf /tmp/verify
```

### Task 7: HDFS Block & FSCK Diagnostics
```bash
# Check file blocks, replicas, and DataNode rack/host locations
hdfs fsck /smartedu/processed/ -files -blocks -locations
```

---

## 3. Automation Scripts Execution

All 5 automation scripts are located in `scripts/phase2/`:

```bash
cd /home/cloudera/SmartEduAnalytics

# Convert potential Windows CRLF to Linux LF
sed -i -e 's/\r$//' scripts/phase2/*.sh
chmod +x scripts/phase2/*.sh

# Step 1: Health Check
./scripts/phase2/hdfs_health_check.sh

# Step 2: Create HDFS Directories
./scripts/phase2/create_hdfs_directories.sh

# Step 3: Ingest Datasets
./scripts/phase2/upload_dataset_to_hdfs.sh

# Step 4: Verify HDFS Storage & Block Diagnostics
./scripts/phase2/verify_hdfs_data.sh

# Step 5: Verify Read, Write & Download Roundtrip
./scripts/phase2/download_from_hdfs.sh
```
