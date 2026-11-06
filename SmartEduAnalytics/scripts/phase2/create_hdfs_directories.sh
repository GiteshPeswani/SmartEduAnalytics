#!/bin/bash
# ==============================================================================
# SmartEdu Analytics - Phase 2: Hadoop HDFS Data Storage & Ingestion
# Script: create_hdfs_directories.sh
# Target Environment: Cloudera QuickStart VM 5.13.0 (Hadoop 2.6.0-cdh5.13.0)
# Description:
#   Constructs the organized multi-tier HDFS storage hierarchy for SmartEdu:
#     /smartedu/
#         ├── raw/         -> Immutable landing zone for original student datasets
#         ├── processed/   -> Storage for cleaned, encoded, and partitioned CSVs
#         ├── analytics/   -> Designated target for future MapReduce & Spark jobs
#         └── reports/     # Technical summaries and data audit documents
# ==============================================================================

set -u

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

BASE_HDFS="/smartedu"
SUBDIRS=("raw" "processed" "analytics" "reports")

echo -e "${BOLD}${BLUE}==============================================================================${NC}"
echo -e "${BOLD}${BLUE} SmartEdu Analytics - Task 2: HDFS Directory Hierarchy Creation${NC}"
echo -e "${BOLD}${BLUE} Base Path: ${BASE_HDFS}${NC}"
echo -e "${BOLD}${BLUE}==============================================================================${NC}"

# Step 1: Create base directory if not exists
echo -e "\n${BOLD}[STEP 1] Initializing Base Project Root (${BASE_HDFS})...${NC}"
if hdfs dfs -test -d "${BASE_HDFS}"; then
    echo -e "${YELLOW}[EXISTS] Base directory '${BASE_HDFS}' already exists.${NC}"
else
    hdfs dfs -mkdir -p "${BASE_HDFS}"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[CREATED] Successfully created root HDFS directory: ${BASE_HDFS}${NC}"
    else
        echo -e "${RED}[ERROR] Failed to create ${BASE_HDFS}. Check HDFS permissions.${NC}"
        exit 1
    fi
fi

# Step 2: Create subdirectories
echo -e "\n${BOLD}[STEP 2] Creating Multi-Tier Functional Directories...${NC}"
for dir in "${SUBDIRS[@]}"; do
    target_path="${BASE_HDFS}/${dir}"
    if hdfs dfs -test -d "${target_path}"; then
        echo -e "${YELLOW}[EXISTS] ${target_path} is already present.${NC}"
    else
        hdfs dfs -mkdir -p "${target_path}"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[CREATED] Created HDFS directory: ${target_path}${NC}"
        else
            echo -e "${RED}[ERROR] Failed to create: ${target_path}${NC}"
            exit 1
        fi
    fi
done

# Step 3: Grant appropriate HDFS user permissions
echo -e "\n${BOLD}[STEP 3] Setting Access Permissions (775)...${NC}"
hdfs dfs -chmod -R 775 "${BASE_HDFS}"
echo -e "${GREEN}[OK] Permissions applied recursively to ${BASE_HDFS}${NC}"

# Step 4: Verify directory structure
echo -e "\n${BOLD}[STEP 4] Verifying Created HDFS Structure (hdfs dfs -ls -R ${BASE_HDFS})...${NC}"
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"
hdfs dfs -ls -R "${BASE_HDFS}"
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"

echo -e "\n${BOLD}${GREEN}==============================================================================${NC}"
echo -e "${BOLD}${GREEN} [SUCCESS] All HDFS project directories successfully created and verified.${NC}"
echo -e "${BOLD}${GREEN}==============================================================================${NC}\n"
