#!/bin/bash
# ==============================================================================
# SmartEdu Analytics - Phase 3: MapReduce Analytics Pipeline
# Script: validate_outputs.sh
# Target Environment: Cloudera QuickStart VM 5.13.0 (Hadoop 2.6.0-cdh5.13.0)
# Description:
#   Audits and validates the output directories produced by all 5 MapReduce jobs:
#   1. Checks presence of HDFS _SUCCESS marker flags.
#   2. Validates part-00000 file existence and non-zero byte size.
#   3. Previews content and counts emitted records.
# ==============================================================================

set -u

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

OUTPUT_DIRS=(
    "/smartedu/analytics/mapreduce/average_performance|Job 1: Average Student Performance"
    "/smartedu/analytics/mapreduce/attendance_analysis|Job 2: Attendance & Participation Analysis"
    "/smartedu/analytics/mapreduce/performance_classification|Job 3: Performance Classification"
    "/smartedu/analytics/mapreduce/course_analysis|Job 4: Course Performance Analysis"
    "/smartedu/analytics/mapreduce/dropout_risk_analysis|Job 5: Dropout Risk & Outcome Analysis"
)

echo -e "${BOLD}${BLUE}==============================================================================${NC}"
echo -e "${BOLD}${BLUE} SmartEdu Analytics - Phase 3: HDFS MapReduce Output Validation Audit${NC}"
echo -e "${BOLD}${BLUE}==============================================================================${NC}\n"

ALL_VALID=true

for item in "${OUTPUT_DIRS[@]}"; do
    IFS='|' read -r dir_path label <<< "$item"
    echo -e "${BOLD}Checking: ${label}${NC}"
    echo -e " -> Directory: ${dir_path}"
    
    # 1. Directory exists
    if ! hdfs dfs -test -d "$dir_path"; then
        echo -e "${RED}[FAILED] Output directory does not exist: ${dir_path}${NC}\n"
        ALL_VALID=false
        continue
    fi
    
    # 2. _SUCCESS marker exists
    if hdfs dfs -test -e "${dir_path}/_SUCCESS"; then
        echo -e " -> _SUCCESS Marker   : ${GREEN}[PASSED] Job committed successfully.${NC}"
    else
        echo -e " -> _SUCCESS Marker   : ${RED}[FAILED] Missing _SUCCESS flag.${NC}"
        ALL_VALID=false
    fi
    
    # 3. part-00000 exists and has data
    part_file="${dir_path}/part-00000"
    if hdfs dfs -test -e "$part_file"; then
        part_bytes=$(hdfs dfs -stat "%b" "$part_file")
        if [ "$part_bytes" -gt 0 ]; then
            lines=$(hdfs dfs -cat "$part_file" | wc -l)
            echo -e " -> Part File Status  : ${GREEN}[PASSED] Size: ${part_bytes} bytes (${lines} lines).${NC}"
            echo -e " -> Output Snippet:"
            hdfs dfs -cat "$part_file" | head -n 4 | sed 's/^/      /'
        else
            echo -e " -> Part File Status  : ${RED}[FAILED] File is empty (0 bytes).${NC}"
            ALL_VALID=false
        fi
    else
        echo -e " -> Part File Status  : ${RED}[FAILED] Missing part-00000 file.${NC}"
        ALL_VALID=false
    fi
    echo ""
done

echo -e "${BOLD}${BLUE}==============================================================================${NC}"
if [ "$ALL_VALID" = true ]; then
    echo -e "${BOLD}${GREEN} [AUDIT PASSED] All 5 MapReduce analytics outputs are verified and integral.${NC}"
else
    echo -e "${BOLD}${RED} [AUDIT WARNING] Discrepancies found in one or more jobs. Review details above.${NC}"
fi
echo -e "${BOLD}${BLUE}==============================================================================${NC}\n"
