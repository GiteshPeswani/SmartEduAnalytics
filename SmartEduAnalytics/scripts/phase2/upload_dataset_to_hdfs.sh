#!/bin/bash
# ==============================================================================
# SmartEdu Analytics - Phase 2: Hadoop HDFS Data Storage & Ingestion
# Script: upload_dataset_to_hdfs.sh
# Target Environment: Cloudera QuickStart VM 5.13.0 (Hadoop 2.6.0-cdh5.13.0)
# Description:
#   Ingests Phase 1 CSV datasets and summary reports into HDFS:
#     - raw_student_data.csv            -> /smartedu/raw/
#     - cleaned_student_data.csv        -> /smartedu/processed/
#     - preprocessed_student_data.csv   -> /smartedu/processed/
#     - train_data.csv                  -> /smartedu/processed/
#     - test_data.csv                   -> /smartedu/processed/
#     - dataset_summary.txt             -> /smartedu/reports/
#   Handles existing files defensively; allows -f/--force to overwrite.
# ==============================================================================

set -u

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Determine Local Base Directory
# Can be passed as 1st argument or environment variable LOCAL_PROJECT_DIR
LOCAL_BASE="${1:-${LOCAL_PROJECT_DIR:-$(pwd)}}"
FORCE_OVERWRITE=false

if [ "${2:-}" == "-f" ] || [ "${1:-}" == "-f" ]; then
    FORCE_OVERWRITE=true
fi

echo -e "${BOLD}${BLUE}==============================================================================${NC}"
echo -e "${BOLD}${BLUE} SmartEdu Analytics - Task 3: Ingestion of Phase 1 Datasets into HDFS${NC}"
echo -e "${BOLD}${BLUE} Local Source Directory: ${LOCAL_BASE}${NC}"
echo -e "${BOLD}${BLUE} Force Overwrite: ${FORCE_OVERWRITE}${NC}"
echo -e "${BOLD}${BLUE}==============================================================================${NC}"

# Verification of local paths
# Support both direct project root or relative subdirectories
if [ -d "${LOCAL_BASE}/dataset/raw" ]; then
    PROJECT_ROOT="${LOCAL_BASE}"
elif [ -d "$(pwd)/dataset/raw" ]; then
    PROJECT_ROOT="$(pwd)"
elif [ -d "/home/cloudera/SmartEduAnalytics/dataset/raw" ]; then
    PROJECT_ROOT="/home/cloudera/SmartEduAnalytics"
elif [ -d "/media/sf_SmartEduAnalytics/dataset/raw" ]; then
    PROJECT_ROOT="/media/sf_SmartEduAnalytics"
else
    echo -e "${RED}[ERROR] Unable to locate Phase 1 dataset directories in '${LOCAL_BASE}'.${NC}"
    echo -e "${YELLOW}Usage: ./upload_dataset_to_hdfs.sh [LOCAL_PROJECT_PATH] [-f]${NC}"
    echo -e "${YELLOW}Example: ./upload_dataset_to_hdfs.sh /home/cloudera/SmartEduAnalytics${NC}"
    exit 1
fi

echo -e "${GREEN}[OK] Confirmed local project directory:${NC} ${PROJECT_ROOT}"

# Ingestion Mapping Array: "LOCAL_REL_PATH|HDFS_TARGET_DIR|LABEL"
INGESTION_MANIFEST=(
    "dataset/raw/raw_student_data.csv|/smartedu/raw/|Raw Student Dataset (UCI 697)"
    "dataset/processed/cleaned_student_data.csv|/smartedu/processed/|Cleaned Dataset (snake_case + student_id)"
    "dataset/processed/preprocessed_student_data.csv|/smartedu/processed/|Preprocessed Dataset (Engineered Features)"
    "dataset/processed/train_data.csv|/smartedu/processed/|Training Split (80% Stratified)"
    "dataset/processed/test_data.csv|/smartedu/processed/|Testing Split (20% Stratified)"
    "reports/dataset_summary.txt|/smartedu/reports/|Phase 1 Dataset Profiling Summary"
)

TOTAL_FILES=${#INGESTION_MANIFEST[@]}
SUCCESSFUL_UPLOADS=0

echo -e "\n${BOLD}[STARTING INGESTION] Transferring ${TOTAL_FILES} files to HDFS...${NC}\n"

for entry in "${INGESTION_MANIFEST[@]}"; do
    IFS='|' read -r rel_path hdfs_dir label <<< "$entry"
    local_file="${PROJECT_ROOT}/${rel_path}"
    filename=$(basename "$local_file")
    hdfs_target="${hdfs_dir}${filename}"
    
    echo -e "${BOLD}------------------------------------------------------------------------------${NC}"
    echo -e "${BOLD}[FILE] ${label}${NC}"
    echo -e " -> Local Source : ${local_file}"
    echo -e " -> HDFS Target  : ${hdfs_target}"
    
    # 1. Check local file existence
    if [ ! -f "${local_file}" ]; then
        echo -e "${RED}[ERROR] Local file does not exist: ${local_file}${NC}"
        continue
    fi
    local_size=$(stat -c%s "${local_file}" 2>/dev/null || wc -c < "${local_file}")
    echo -e " -> Local Size   : ${local_size} bytes ($((local_size / 1024)) KB)"
    
    # 2. Check if already present in HDFS
    if hdfs dfs -test -e "${hdfs_target}"; then
        if [ "$FORCE_OVERWRITE" = true ]; then
            echo -e "${YELLOW}[NOTICE] File exists in HDFS. Overwriting (-f enabled)...${NC}"
            hdfs dfs -put -f "${local_file}" "${hdfs_target}"
        else
            echo -e "${YELLOW}[SKIP] File already exists in HDFS. Use -f to overwrite.${NC}"
            SUCCESSFUL_UPLOADS=$((SUCCESSFUL_UPLOADS + 1))
            continue
        fi
    else
        hdfs dfs -put "${local_file}" "${hdfs_target}"
    fi
    
    # 3. Verify upload exit code
    if [ $? -eq 0 ]; then
        hdfs_size=$(hdfs dfs -stat "%b" "${hdfs_target}")
        echo -e "${GREEN}[UPLOAD SUCCESS] Successfully ingested into HDFS.${NC}"
        echo -e " -> HDFS Size    : ${hdfs_size} bytes"
        SUCCESSFUL_UPLOADS=$((SUCCESSFUL_UPLOADS + 1))
    else
        echo -e "${RED}[FAILED] HDFS upload command failed for ${filename}.${NC}"
    fi
done

echo -e "\n${BOLD}${BLUE}==============================================================================${NC}"
echo -e "${BOLD}${BLUE} Ingestion Summary: ${SUCCESSFUL_UPLOADS}/${TOTAL_FILES} files verified in HDFS.${NC}"
echo -e "${BOLD}${BLUE}==============================================================================${NC}\n"

if [ "$SUCCESSFUL_UPLOADS" -eq "$TOTAL_FILES" ]; then
    exit 0
else
    exit 1
fi
