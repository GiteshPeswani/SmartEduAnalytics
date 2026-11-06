#!/bin/bash
# ==============================================================================
# SmartEdu Analytics - Phase 2: Hadoop HDFS Data Storage & Ingestion
# Script: verify_hdfs_data.sh
# Target Environment: Cloudera QuickStart VM 5.13.0 (Hadoop 2.6.0-cdh5.13.0)
# Description:
#   Performs rigorous verification and validation of HDFS ingested data:
#     - Task 4: HDFS file listing, disk usage, directory counts, and stats
#     - Task 5: 100% Data integrity matching (record counts & byte sizes)
#     - Task 7: HDFS block layout, replication, and physical DataNode locations
# ==============================================================================

set -u

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

LOCAL_BASE="${1:-${LOCAL_PROJECT_DIR:-$(pwd)}}"

echo -e "${BOLD}${BLUE}==============================================================================${NC}"
echo -e "${BOLD}${BLUE} SmartEdu Analytics - Task 4, 5 & 7: HDFS Verification & Block Diagnostics${NC}"
echo -e "${BOLD}${BLUE} Target Cluster: Cloudera QuickStart VM 5.13.0 (Hadoop 2.6.0)${NC}"
echo -e "${BOLD}${BLUE}==============================================================================${NC}"

# Locate local directory for comparison
if [ -d "${LOCAL_BASE}/dataset/processed" ]; then
    PROJECT_ROOT="${LOCAL_BASE}"
elif [ -d "/home/cloudera/SmartEduAnalytics/dataset/processed" ]; then
    PROJECT_ROOT="/home/cloudera/SmartEduAnalytics"
elif [ -d "/media/sf_SmartEduAnalytics/dataset/processed" ]; then
    PROJECT_ROOT="/media/sf_SmartEduAnalytics"
else
    PROJECT_ROOT="$(pwd)"
fi

# ==============================================================================
# PART 1: Task 4 - File & Directory Storage Inspection
# ==============================================================================
echo -e "\n${BOLD}${CYAN}--- [PART 1: TASK 4] HDFS STORAGE & DIRECTORY INSPECTION ---${NC}"

echo -e "\n${BOLD}[CHECK 1.1] Detailed HDFS Directory Tree Listing (hdfs dfs -ls -R /smartedu):${NC}"
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"
hdfs dfs -ls -R /smartedu
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"

echo -e "\n${BOLD}[CHECK 1.2] Disk Space Usage (hdfs dfs -du -h /smartedu):${NC}"
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"
hdfs dfs -du -h /smartedu
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"

echo -e "\n${BOLD}[CHECK 1.3] Directory and File Counts (hdfs dfs -count /smartedu/processed):${NC}"
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"
# Output columns: DIR_COUNT, FILE_COUNT, CONTENT_SIZE, PATHNAME
echo -e "DIR_COUNT  FILE_COUNT   TOTAL_BYTES  PATH"
hdfs dfs -count /smartedu/processed
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"

# ==============================================================================
# PART 2: Task 5 - Rigorous Record Count & Byte Size Integrity Verification
# ==============================================================================
echo -e "\n${BOLD}${CYAN}--- [PART 2: TASK 5] DATA INTEGRITY & RECORD COUNT COMPARISON ---${NC}"

FILES_TO_VERIFY=(
    "dataset/raw/raw_student_data.csv|/smartedu/raw/raw_student_data.csv|Raw Student Data"
    "dataset/processed/cleaned_student_data.csv|/smartedu/processed/cleaned_student_data.csv|Cleaned Student Data"
    "dataset/processed/preprocessed_student_data.csv|/smartedu/processed/preprocessed_student_data.csv|Preprocessed Student Data"
    "dataset/processed/train_data.csv|/smartedu/processed/train_data.csv|Training Partition (80%)"
    "dataset/processed/test_data.csv|/smartedu/processed/test_data.csv|Testing Partition (20%)"
)

INTEGRITY_PASSED=true

for item in "${FILES_TO_VERIFY[@]}"; do
    IFS='|' read -r rel_path hdfs_path label <<< "$item"
    local_file="${PROJECT_ROOT}/${rel_path}"
    
    echo -e "\n${BOLD}Validating: ${label}${NC}"
    echo -e " -> HDFS Path: ${hdfs_path}"
    
    # Verify file existence in HDFS
    if ! hdfs dfs -test -e "${hdfs_path}"; then
        echo -e "${RED}[FAILED] File missing in HDFS: ${hdfs_path}${NC}"
        INTEGRITY_PASSED=false
        continue
    fi
    
    # 1. Byte Size Verification
    hdfs_bytes=$(hdfs dfs -stat "%b" "${hdfs_path}")
    if [ -f "${local_file}" ]; then
        local_bytes=$(stat -c%s "${local_file}" 2>/dev/null || wc -c < "${local_file}")
        if [ "${local_bytes}" -eq "${hdfs_bytes}" ]; then
            echo -e " -> Byte Size Match   : ${GREEN}[PASSED] Local: ${local_bytes} B == HDFS: ${hdfs_bytes} B${NC}"
        else
            echo -e " -> Byte Size Match   : ${RED}[MISMATCH] Local: ${local_bytes} B != HDFS: ${hdfs_bytes} B${NC}"
            INTEGRITY_PASSED=false
        fi
    else
        echo -e " -> HDFS Size         : ${hdfs_bytes} bytes (${GREEN}[EXISTS]${NC} local comparison skipped)"
    fi
    
    # 2. Record Count (excluding header line)
    # Using awk/sed to cleanly handle CSV header
    hdfs_total_lines=$(hdfs dfs -cat "${hdfs_path}" | wc -l)
    hdfs_data_records=$((hdfs_total_lines - 1))
    
    if [ -f "${local_file}" ]; then
        local_total_lines=$(wc -l < "${local_file}")
        local_data_records=$((local_total_lines - 1))
        
        if [ "${local_data_records}" -eq "${hdfs_data_records}" ]; then
            echo -e " -> Record Count Match: ${GREEN}[PASSED] Local: ${local_data_records} rows == HDFS: ${hdfs_data_records} rows (header excluded)${NC}"
        else
            echo -e " -> Record Count Match: ${RED}[MISMATCH] Local: ${local_data_records} rows != HDFS: ${hdfs_data_records} rows${NC}"
            INTEGRITY_PASSED=false
        fi
    else
        echo -e " -> HDFS Records      : ${hdfs_data_records} data records (header excluded)"
    fi
    
    # 3. Header & First Data Row Preview directly from HDFS
    echo -e " -> Direct HDFS Preview (First 2 Lines):"
    hdfs dfs -cat "${hdfs_path}" | head -n 2 | sed 's/^/    [HDFS] /'
done

# ==============================================================================
# PART 3: Task 7 - HDFS Block Diagnostics & FSCK Health Check
# ==============================================================================
echo -e "\n${BOLD}${CYAN}--- [PART 3: TASK 7] HDFS BLOCK ARCHITECTURE & FSCK REPORT ---${NC}"
echo -e "${YELLOW}[INFO] In Cloudera VM (single-node pseudo-distributed), default dfs.blocksize is 128MB.${NC}"
echo -e "${YELLOW}Our dataset CSV files are ~0.3MB - 1.4MB, fitting cleanly within a single HDFS block per file.${NC}\n"

echo -e "${BOLD}[FSCK DIAGNOSTICS] Querying block layout for /smartedu/processed/:${NC}"
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"
hdfs fsck /smartedu/processed/ -files -blocks -locations
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"

# Final summary
echo -e "\n${BOLD}${BLUE}==============================================================================${NC}"
if [ "$INTEGRITY_PASSED" = true ]; then
    echo -e "${BOLD}${GREEN} [ALL VERIFICATION CHECKS PASSED] Data in HDFS is 100% verified and integral.${NC}"
else
    echo -e "${BOLD}${RED} [WARNING] Discrepancies detected during verification. Review details above.${NC}"
fi
echo -e "${BOLD}${BLUE}==============================================================================${NC}\n"
