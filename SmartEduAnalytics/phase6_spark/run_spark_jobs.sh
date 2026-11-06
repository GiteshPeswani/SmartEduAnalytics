#!/bin/bash
# ==============================================================================
# SmartEdu Analytics - Phase 6: Apache Spark Distributed Processing
# Script: run_spark_jobs.sh
# Target Environment: Cloudera QuickStart VM 5.13.0 (Spark 1.6 / 2.x)
# Description:
#   Submits Spark DataFrame analytics and MLlib predictive modeling jobs
#   to YARN / Spark standalone using spark-submit.
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
echo -e "${BOLD}${BLUE} SmartEdu Analytics - Phase 6: Apache Spark Distributed Processing${NC}"
echo -e "${BOLD}${BLUE} Target Cluster: Cloudera QuickStart VM (CDH 5.13.0)${NC}"
echo -e "${BOLD}${BLUE}==============================================================================${NC}"

# Check spark-submit
echo -e "\n${BOLD}[STEP 1] Checking spark-submit Command...${NC}"
if ! command -v spark-submit &> /dev/null; then
    echo -e "${RED}[ERROR] 'spark-submit' command not found in system PATH.${NC}"
    echo -e "${YELLOW}Please ensure /usr/bin/spark-submit is accessible in your Cloudera VM.${NC}"
    exit 1
fi
SPARK_VER=$(spark-submit --version 2>&1 | grep -i "version" | head -n 1)
echo -e "${GREEN}[OK] Detected Spark:${NC} $SPARK_VER"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Run Job 1: Spark DataFrame & Spark SQL Analytics
echo -e "\n${BOLD}[STEP 2] Submitting Spark DataFrame & SQL Analytics Job...${NC}"
spark-submit \
    --master local[*] \
    --name "SmartEdu_Spark_Analytics" \
    "${SCRIPT_DIR}/spark_student_analytics.py"

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Spark analytics job failed.${NC}"
    exit 1
fi

# Run Job 2: Spark MLlib Machine Learning Pipeline
echo -e "\n${BOLD}[STEP 3] Submitting Spark MLlib Machine Learning Pipeline...${NC}"
spark-submit \
    --master local[*] \
    --name "SmartEdu_Spark_ML_Pipeline" \
    "${SCRIPT_DIR}/spark_ml_dropout_prediction.py"

if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Spark MLlib job failed.${NC}"
    exit 1
fi

# Verify HDFS Output
echo -e "\n${BOLD}[STEP 4] Verifying Generated HDFS Spark Outputs (/smartedu/analytics/spark/)...${NC}"
hdfs dfs -ls -R /smartedu/analytics/spark/

echo -e "\n${BOLD}${GREEN}==============================================================================${NC}"
echo -e "${BOLD}${GREEN} [SUCCESS] All Phase 6 Apache Spark processing jobs completed successfully!${NC}"
echo -e "${BOLD}${GREEN}==============================================================================${NC}\n"
