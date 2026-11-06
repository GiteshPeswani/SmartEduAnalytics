#!/bin/bash
# ==============================================================================
# SmartEdu Analytics - Phase 4: Apache Hive Data Warehousing
# Script: create_hive_database.sh
# Target Environment: Cloudera QuickStart VM 5.13.0 (Hive 1.1.0-cdh5.13.0)
# Description:
#   1. Validates Hive service and CLI availability.
#   2. Prepares dedicated HDFS directory for external table mapping.
#   3. Executes hive_schema.hql to construct the smartedu database,
--     external table students_ext, course_dim dimension table, and
--     managed student_analytics ORC warehouse table.
#   4. Verifies database catalog and table row counts.
# ==============================================================================

set -u

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}==============================================================================${NC}"
echo -e "${BOLD}${BLUE} SmartEdu Analytics - Phase 4: Hive Data Warehouse Initialization${NC}"
echo -e "${BOLD}${BLUE} Target Cluster: Cloudera QuickStart VM (Hive 1.1.0-cdh5.13.0)${NC}"
echo -e "${BOLD}${BLUE}==============================================================================${NC}"

# Step 1: Check Hive CLI
echo -e "\n${BOLD}[STEP 1] Checking Hive CLI Availability...${NC}"
if ! command -v hive &> /dev/null; then
    echo -e "${RED}[ERROR] 'hive' command not found in system PATH.${NC}"
    echo -e "${YELLOW}Please ensure Cloudera Hive binary (/usr/bin/hive) is accessible.${NC}"
    exit 1
fi
HIVE_VERSION=$(hive --version 2>&1 | head -n 1)
echo -e "${GREEN}[OK] Hive CLI detected:${NC} $HIVE_VERSION"

# Step 2: Prepare Dedicated HDFS Directory for External Table
HDFS_SRC_FILE="/smartedu/processed/preprocessed_student_data.csv"
HDFS_TABLE_DIR="/smartedu/processed/preprocessed"

echo -e "\n${BOLD}[STEP 2] Configuring Dedicated HDFS Directory for Hive External Table...${NC}"
if ! hdfs dfs -test -e "$HDFS_SRC_FILE"; then
    echo -e "${RED}[ERROR] Required dataset missing in HDFS: $HDFS_SRC_FILE${NC}"
    echo -e "${YELLOW}Please complete Phase 2 ingestion first: ./scripts/phase2/upload_dataset_to_hdfs.sh${NC}"
    exit 1
fi

hdfs dfs -mkdir -p "$HDFS_TABLE_DIR"
if ! hdfs dfs -test -e "${HDFS_TABLE_DIR}/preprocessed_student_data.csv"; then
    echo -e "Copying dataset into dedicated external table directory..."
    hdfs dfs -cp "$HDFS_SRC_FILE" "${HDFS_TABLE_DIR}/"
fi
echo -e "${GREEN}[OK] Dedicated directory verified:${NC} ${HDFS_TABLE_DIR}"

# Step 3: Execute Schema DDL Script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
SCHEMA_HQL="${PROJECT_ROOT}/hive/hive_schema.hql"

if [ ! -f "$SCHEMA_HQL" ]; then
    SCHEMA_HQL="/home/cloudera/SmartEduAnalytics/hive/hive_schema.hql"
fi

if [ ! -f "$SCHEMA_HQL" ]; then
    echo -e "${RED}[ERROR] Cannot find hive_schema.hql at expected path.${NC}"
    exit 1
fi

echo -e "\n${BOLD}[STEP 3] Executing Hive DDL Schema Script (${SCHEMA_HQL})...${NC}"
echo -e "This will create database 'smartedu', external table 'students_ext', 'course_dim', and populate 'student_analytics'..."
hive -f "$SCHEMA_HQL"

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Hive DDL execution failed. Review Hive logs above.${NC}"
    exit 1
fi

# Step 4: Verification of Database & Tables
echo -e "\n${BOLD}[STEP 4] Verifying SmartEdu Hive Catalog...${NC}"
echo -e "${CYAN}Listing tables in database 'smartedu':${NC}"
hive -e "USE smartedu; SHOW TABLES;"

echo -e "\n${CYAN}Verifying student record count in managed table 'student_analytics':${NC}"
hive -e "USE smartedu; SELECT COUNT(*) AS student_count FROM student_analytics;"

echo -e "\n${BOLD}${GREEN}==============================================================================${NC}"
echo -e "${BOLD}${GREEN} [SUCCESS] Hive Data Warehouse initialized successfully! Ready for analytics.${NC}"
echo -e "${BOLD}${GREEN}==============================================================================${NC}\n"
