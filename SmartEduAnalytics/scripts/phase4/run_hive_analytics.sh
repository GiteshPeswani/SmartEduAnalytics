#!/bin/bash
# ==============================================================================
# SmartEdu Analytics - Phase 4: Apache Hive Data Warehousing
# Script: run_hive_analytics.sh
# Target Environment: Cloudera QuickStart VM 5.13.0 (Hive 1.1.0-cdh5.13.0)
# Description:
#   Orchestrates execution of all 14 HiveQL analytical and aggregation queries,
#   storing final query outputs into HDFS at /smartedu/analytics/hive/.
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
echo -e "${BOLD}${BLUE} SmartEdu Analytics - Phase 4: HiveQL Analytical Engine Execution${NC}"
echo -e "${BOLD}${BLUE} Target Cluster: Cloudera QuickStart VM (Hive 1.1.0-cdh5.13.0)${NC}"
echo -e "${BOLD}${BLUE}==============================================================================${NC}"

# Locate hive_analytics.hql
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
ANALYTICS_HQL="${PROJECT_ROOT}/hive/hive_analytics.hql"

if [ ! -f "$ANALYTICS_HQL" ]; then
    ANALYTICS_HQL="/home/cloudera/SmartEduAnalytics/hive/hive_analytics.hql"
fi

if [ ! -f "$ANALYTICS_HQL" ]; then
    echo -e "${RED}[ERROR] Cannot find hive_analytics.hql at expected path.${NC}"
    exit 1
fi

# Step 1: Ensure HDFS analytics directory structure
HDFS_HIVE_OUT="/smartedu/analytics/hive"
echo -e "\n${BOLD}[STEP 1] Initializing Target HDFS Analytics Directory (${HDFS_HIVE_OUT})...${NC}"
hdfs dfs -mkdir -p "$HDFS_HIVE_OUT"
hdfs dfs -chmod -R 775 "$HDFS_HIVE_OUT"
echo -e "${GREEN}[OK] HDFS directory verified.${NC}"

# Step 2: Execute Hive Analytics
echo -e "\n${BOLD}[STEP 2] Executing Analytical HiveQL Script (${ANALYTICS_HQL})...${NC}"
echo -e "Executing queries 1 to 14 (aggregations, rankings, window functions, and HDFS exports)..."
hive -f "$ANALYTICS_HQL"

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Hive analytics execution encountered an error. Check logs.${NC}"
    exit 1
fi

# Step 3: Verify HDFS Outputs
echo -e "\n${BOLD}[STEP 3] Verifying Generated HDFS Analytics Datasets (${HDFS_HIVE_OUT})...${NC}"
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"
hdfs dfs -ls -R "$HDFS_HIVE_OUT"
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"

# Step 4: Preview Sample HDFS Results
echo -e "\n${BOLD}[STEP 4] Previewing Exported Summary Metrics from HDFS:${NC}"
SUMMARY_FILE=$(hdfs dfs -ls "$HDFS_HIVE_OUT/summary_metrics" | grep -v "Found" | awk '{print $8}' | head -n 1)
if [ -n "$SUMMARY_FILE" ]; then
    echo -e "Path: $SUMMARY_FILE"
    echo -e "Columns: Total | AvgAdm | AvgSem1 | AvgSem2 | AvgAnnual | Dropouts | Graduates | Enrolled"
    hdfs dfs -cat "$SUMMARY_FILE" | sed 's/^/  [HDFS] /'
fi

echo -e "\n${BOLD}${GREEN}==============================================================================${NC}"
echo -e "${BOLD}${GREEN} [SUCCESS] All HiveQL analytics queries executed and stored in HDFS.${NC}"
echo -e "${BOLD}${GREEN}==============================================================================${NC}\n"
