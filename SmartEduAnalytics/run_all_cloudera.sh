#!/bin/bash
# ==============================================================================
# SmartEdu Analytics - Master Cloudera QuickStart VM Demonstration Runner
# Script: run_all_cloudera.sh
# Target: Cloudera QuickStart VM 5.13.0 (Hadoop 2.6.0, HDFS, YARN, Hive 1.1.0)
# ==============================================================================

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}==============================================================================${NC}"
echo -e "${BOLD}${BLUE}   SmartEdu Analytics: Cloudera QuickStart VM End-to-End Execution            ${NC}"
echo -e "${BOLD}${BLUE}   HDFS + MapReduce Streaming + Apache Hive Data Warehouse Demonstration      ${NC}"
echo -e "${BOLD}${BLUE}==============================================================================${NC}"

# Find project directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo -e "${CYAN}Project Root:${NC} $PROJECT_ROOT"

# Ensure execution permissions on all scripts
chmod +x "$PROJECT_ROOT"/scripts/phase2/*.sh
chmod +x "$PROJECT_ROOT"/scripts/phase3/*.sh
chmod +x "$PROJECT_ROOT"/scripts/phase3/*.py
chmod +x "$PROJECT_ROOT"/scripts/phase4/*.sh

# ==============================================================================
# PHASE 2: HDFS STORAGE & INGESTION
# ==============================================================================
echo -e "\n${BOLD}${YELLOW}>>> STEP 1: Checking HDFS Cluster Health & Service Status...${NC}"
bash "$PROJECT_ROOT/scripts/phase2/hdfs_health_check.sh"

echo -e "\n${BOLD}${YELLOW}>>> STEP 2: Creating Organized HDFS Directory Structure (/smartedu)...${NC}"
bash "$PROJECT_ROOT/scripts/phase2/create_hdfs_directories.sh"

echo -e "\n${BOLD}${YELLOW}>>> STEP 3: Uploading Preprocessed Datasets to HDFS...${NC}"
bash "$PROJECT_ROOT/scripts/phase2/upload_dataset_to_hdfs.sh" "$PROJECT_ROOT" -f

echo -e "\n${BOLD}${YELLOW}>>> STEP 4: Verifying HDFS Stored Files & Block Allocation...${NC}"
bash "$PROJECT_ROOT/scripts/phase2/verify_hdfs_data.sh"

# ==============================================================================
# PHASE 3: MAPREDUCE ANALYTICS
# ==============================================================================
echo -e "\n${BOLD}${YELLOW}>>> STEP 5: Executing Distributed Hadoop MapReduce Streaming Jobs...${NC}"
bash "$PROJECT_ROOT/scripts/phase3/run_all_jobs.sh" -f

echo -e "\n${BOLD}${YELLOW}>>> STEP 6: Validating MapReduce Output Datasets...${NC}"
bash "$PROJECT_ROOT/scripts/phase3/validate_outputs.sh"

# ==============================================================================
# PHASE 4: APACHE HIVE DATA WAREHOUSE
# ==============================================================================
echo -e "\n${BOLD}${YELLOW}>>> STEP 7: Creating Apache Hive Database & Schema (smartedu)...${NC}"
bash "$PROJECT_ROOT/scripts/phase4/create_hive_database.sh"

echo -e "\n${BOLD}${YELLOW}>>> STEP 8: Running HiveQL Aggregation & Analytical Queries...${NC}"
bash "$PROJECT_ROOT/scripts/phase4/run_hive_analytics.sh"

echo -e "\n${BOLD}${GREEN}==============================================================================${NC}"
echo -e "${BOLD}${GREEN} [SUCCESS] All Cloudera Big Data Demonstrations Completed!                  ${NC}"
echo -e "${BOLD}${GREEN} 1. HDFS Ingestion: Verified in /smartedu/                                    ${NC}"
echo -e "${BOLD}${GREEN} 2. MapReduce Jobs: 5 Distributed Jobs Completed via Hadoop Streaming         ${NC}"
echo -e "${BOLD}${GREEN} 3. Hive Analytics: smartedu Database & Analytics Tables Ready                ${NC}"
echo -e "${BOLD}${GREEN}==============================================================================${NC}"
