#!/bin/bash
# ==============================================================================
# SmartEdu Analytics - Phase 3: MapReduce Analytics Pipeline
# Script: run_all_jobs.sh
# Target Environment: Cloudera QuickStart VM 5.13.0 (Hadoop 2.6.0-cdh5.13.0)
# Description:
#   Orchestrates all 5 distributed Hadoop MapReduce analytics jobs via Hadoop Streaming:
#     1. Job 1: Average Student Performance
#     2. Job 2: Attendance & Curricular Participation Analysis
#     3. Job 3: Student Performance Classification
#     4. Job 4: Course Performance Analysis & Program Rankings
#     5. Job 5: Dropout Risk & Institutional Outcome Analysis
# ==============================================================================

set -u

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

FORCE_CLEAN=false
if [ "${1:-}" == "-f" ] || [ "${1:-}" == "--force" ]; then
    FORCE_CLEAN=true
fi

echo -e "${BOLD}${BLUE}==============================================================================${NC}"
echo -e "${BOLD}${BLUE} SmartEdu Analytics - Phase 3: Hadoop MapReduce Analytics Engine${NC}"
echo -e "${BOLD}${BLUE} Target Cluster: Cloudera QuickStart VM (Hadoop 2.6.0-cdh5.13.0)${NC}"
echo -e "${BOLD}${BLUE}==============================================================================${NC}"

# Step 1: Detect Hadoop Streaming JAR
echo -e "\n${BOLD}[STEP 1] Locating Hadoop Streaming JAR...${NC}"
POSSIBLE_JARS=(
    "/usr/lib/hadoop-mapreduce/hadoop-streaming.jar"
    "/usr/lib/hadoop-mapreduce/hadoop-streaming-2.6.0-cdh5.13.0.jar"
    "/usr/lib/hadoop-yarn/hadoop-streaming.jar"
    "$(find /usr/lib -name 'hadoop-streaming*.jar' 2>/dev/null | head -n 1)"
)

STREAMING_JAR=""
for jar in "${POSSIBLE_JARS[@]}"; do
    if [ -n "$jar" ] && [ -f "$jar" ]; then
        STREAMING_JAR="$jar"
        break
    fi
done

if [ -z "$STREAMING_JAR" ]; then
    echo -e "${RED}[ERROR] Could not find hadoop-streaming.jar in standard CDH library paths.${NC}"
    echo -e "${YELLOW}Please verify CDH installation or export STREAMING_JAR manually.${NC}"
    exit 1
fi
echo -e "${GREEN}[OK] Using Hadoop Streaming JAR:${NC} $STREAMING_JAR"

# Step 2: Verify Input Dataset in HDFS
HDFS_INPUT="/smartedu/processed/preprocessed_student_data.csv"
echo -e "\n${BOLD}[STEP 2] Verifying Input Dataset in HDFS (${HDFS_INPUT})...${NC}"
if ! hdfs dfs -test -e "$HDFS_INPUT"; then
    echo -e "${RED}[ERROR] Input dataset missing in HDFS: $HDFS_INPUT${NC}"
    echo -e "${YELLOW}Run Phase 2 upload script: ./scripts/phase2/upload_dataset_to_hdfs.sh${NC}"
    exit 1
fi
INPUT_BYTES=$(hdfs dfs -stat "%b" "$HDFS_INPUT")
echo -e "${GREEN}[OK] Input dataset verified (${INPUT_BYTES} bytes).${NC}"

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define Jobs Manifest: "JOB_NAME|MAPPER|REDUCER|OUTPUT_DIR"
JOBS_MANIFEST=(
    "Job 1: Average Student Performance|mapper_average.py|reducer_average.py|/smartedu/analytics/mapreduce/average_performance"
    "Job 2: Attendance & Participation Analysis|mapper_attendance.py|reducer_attendance.py|/smartedu/analytics/mapreduce/attendance_analysis"
    "Job 3: Performance Classification|mapper_classification.py|reducer_classification.py|/smartedu/analytics/mapreduce/performance_classification"
    "Job 4: Course Performance Analysis|mapper_course.py|reducer_course.py|/smartedu/analytics/mapreduce/course_analysis"
    "Job 5: Dropout Risk & Outcome Analysis|mapper_risk.py|reducer_risk.py|/smartedu/analytics/mapreduce/dropout_risk_analysis"
)

TOTAL_JOBS=${#JOBS_MANIFEST[@]}
COMPLETED_JOBS=0

echo -e "\n${BOLD}[STEP 3] Launching ${TOTAL_JOBS} MapReduce Analytics Jobs...${NC}\n"

for job_def in "${JOBS_MANIFEST[@]}"; do
    IFS='|' read -r job_name mapper reducer output_dir <<< "$job_def"
    
    echo -e "${BOLD}${CYAN}------------------------------------------------------------------------------${NC}"
    echo -e "${BOLD}${CYAN}>>> Executing: ${job_name}${NC}"
    echo -e " -> Mapper  : ${mapper}"
    echo -e " -> Reducer : ${reducer}"
    echo -e " -> Output  : ${output_dir}"
    
    # Check local scripts
    mapper_path="${SCRIPT_DIR}/${mapper}"
    reducer_path="${SCRIPT_DIR}/${reducer}"
    
    if [ ! -f "$mapper_path" ] || [ ! -f "$reducer_path" ]; then
        echo -e "${RED}[ERROR] Missing mapper or reducer script in ${SCRIPT_DIR}${NC}"
        continue
    fi
    chmod +x "$mapper_path" "$reducer_path"
    
    # Handle existing output directory safely
    if hdfs dfs -test -d "$output_dir"; then
        if [ "$FORCE_CLEAN" = true ]; then
            echo -e "${YELLOW}[NOTICE] Output directory exists. Removing previous output (-f enabled)...${NC}"
            hdfs dfs -rm -r -skipTrash "$output_dir"
        else
            echo -e "${YELLOW}[WARNING] Output directory '$output_dir' already exists.${NC}"
            echo -e "${YELLOW}Archiving existing directory to avoid data loss...${NC}"
            hdfs dfs -mv "$output_dir" "${output_dir}_backup_$(date +%s)"
        fi
    fi
    
    # Submit MapReduce Job to YARN via Hadoop Streaming
    echo -e "Submitting job to YARN..."
    hadoop jar "$STREAMING_JAR" \
        -D mapreduce.job.name="SmartEdu_${mapper%.*}" \
        -D mapreduce.job.reduces=1 \
        -file "${mapper_path}" \
        -file "${reducer_path}" \
        -mapper "python ${mapper}" \
        -reducer "python ${reducer}" \
        -input "$HDFS_INPUT" \
        -output "$output_dir"
        
    JOB_EXIT_CODE=$?
    if [ $JOB_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}[JOB SUCCESS] ${job_name} finished successfully!${NC}"
        COMPLETED_JOBS=$((COMPLETED_JOBS + 1))
        
        # Display sample output preview
        echo -e "Output Preview (First 5 lines):"
        hdfs dfs -cat "${output_dir}/part-00000" | head -n 5 | sed 's/^/  [HDFS] /'
    else
        echo -e "${RED}[JOB FAILED] ${job_name} exited with error code ${JOB_EXIT_CODE}.${NC}"
    fi
    echo ""
done

echo -e "${BOLD}${BLUE}==============================================================================${NC}"
echo -e "${BOLD}${BLUE} Execution Complete: ${COMPLETED_JOBS}/${TOTAL_JOBS} MapReduce jobs succeeded.${NC}"
echo -e "${BOLD}${BLUE}==============================================================================${NC}\n"

if [ "$COMPLETED_JOBS" -eq "$TOTAL_JOBS" ]; then
    exit 0
else
    exit 1
fi
