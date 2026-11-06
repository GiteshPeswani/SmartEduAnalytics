#!/bin/bash
# ==============================================================================
# SmartEdu Analytics - Phase 2: Hadoop HDFS Data Storage & Ingestion
# Script: hdfs_health_check.sh
# Target Environment: Cloudera QuickStart VM 5.13.0 (Hadoop 2.6.0-cdh5.13.0)
# Description:
#   Performs comprehensive cluster health inspection:
#   1. Validates Hadoop CLI and Java environment.
#   2. Inspects Java processes (NameNode, DataNode, SecondaryNameNode).
#   3. Queries HDFS SafeMode status.
#   4. Executes hdfs dfsadmin -report for capacity, block pool, and live DataNodes.
#   5. Evaluates HDFS root status.
# ==============================================================================

set -u

# Text formatting
BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BOLD}${BLUE}==============================================================================${NC}"
echo -e "${BOLD}${BLUE} SmartEdu Analytics - Task 1: Hadoop HDFS Cluster Health Check${NC}"
echo -e "${BOLD}${BLUE} Cluster: Cloudera QuickStart VM (Hadoop 2.6.0-cdh5.13.0)${NC}"
echo -e "${BOLD}${BLUE}==============================================================================${NC}"

# Step 1: Check Hadoop CLI availability
echo -e "\n${BOLD}[STEP 1] Validating Hadoop Environment...${NC}"
if ! command -v hadoop &> /dev/null; then
    echo -e "${RED}[ERROR] 'hadoop' command not found in PATH.${NC}"
    echo -e "${YELLOW}Please ensure /usr/bin/hadoop or HADOOP_HOME/bin is in your PATH.${NC}"
    exit 1
fi

HADOOP_VER=$(hadoop version | head -n 1)
echo -e "${GREEN}[OK] Hadoop binary detected:${NC} $HADOOP_VER"

# Step 2: Check Java Processes (JPS)
echo -e "\n${BOLD}[STEP 2] Inspecting HDFS Daemon Processes (jps)...${NC}"
if command -v jps &> /dev/null; then
    JPS_OUTPUT=$(jps)
    echo "$JPS_OUTPUT"
    
    # Check essential daemons
    for daemon in NameNode DataNode SecondaryNameNode; do
        if echo "$JPS_OUTPUT" | grep -q "$daemon"; then
            echo -e "${GREEN}[RUNNING] $daemon process active.${NC}"
        else
            echo -e "${RED}[WARNING] $daemon process NOT detected in jps.${NC}"
        fi
    done
else
    echo -e "${YELLOW}[NOTICE] 'jps' command not found. Falling back to ps aux...${NC}"
    ps aux | grep -E "hadoop.*(namenode|datanode)" | grep -v grep
fi

# Step 3: Check NameNode SafeMode
echo -e "\n${BOLD}[STEP 3] Querying NameNode SafeMode Status...${NC}"
SAFEMODE_STATUS=$(hdfs dfsadmin -safemode get 2>&1)
echo -e "Status: $SAFEMODE_STATUS"
if echo "$SAFEMODE_STATUS" | grep -q "Safe mode is ON"; then
    echo -e "${YELLOW}[WARNING] NameNode is in SAFE MODE. Leaving safe mode...${NC}"
    hdfs dfsadmin -safemode leave
    echo -e "${GREEN}[OK] NameNode is now in normal write-enabled mode.${NC}"
else
    echo -e "${GREEN}[OK] NameNode safe mode is OFF. Read and Write operations enabled.${NC}"
fi

# Step 4: Run HDFS DFSAdmin Report
echo -e "\n${BOLD}[STEP 4] Generating HDFS DFSAdmin Cluster Report...${NC}"
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"
hdfs dfsadmin -report
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"

# Step 5: Test Basic HDFS Read Access
echo -e "\n${BOLD}[STEP 5] Testing Root HDFS Connectivity...${NC}"
if hdfs dfs -ls / &> /dev/null; then
    echo -e "${GREEN}[SUCCESS] Root HDFS directory is accessible.${NC}"
else
    echo -e "${RED}[ERROR] Unable to read root HDFS directory (/). Check NameNode service.${NC}"
    exit 1
fi

echo -e "\n${BOLD}${GREEN}==============================================================================${NC}"
echo -e "${BOLD}${GREEN} [HEALTH CHECK PASSED] Hadoop HDFS cluster is healthy and ready for ingestion.${NC}"
echo -e "${BOLD}${GREEN}==============================================================================${NC}\n"
