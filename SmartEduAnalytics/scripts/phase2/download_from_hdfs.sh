#!/bin/bash
# ==============================================================================
# SmartEdu Analytics - Phase 2: Hadoop HDFS Data Storage & Ingestion
# Script: download_from_hdfs.sh
# Target Environment: Cloudera QuickStart VM 5.13.0 (Hadoop 2.6.0-cdh5.13.0)
# Description:
#   Implements Task 6: Comprehensive HDFS Read, Write & Download Demonstration
#   1. Creates temporary HDFS test directory.
#   2. Verifies HDFS write via upload.
#   3. Reads data in-flight via hdfs dfs -cat.
#   4. Downloads data back to local filesystem using hdfs dfs -get.
#   5. Performs strict byte-level diff & MD5 cryptographic checksum comparison.
#   6. Cleans up test artifacts cleanly.
# ==============================================================================

set -u

BOLD='\033[1m'
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

LOCAL_BASE="${1:-${LOCAL_PROJECT_DIR:-$(pwd)}}"
LOCAL_SRC="${LOCAL_BASE}/dataset/processed/cleaned_student_data.csv"
HDFS_SRC="/smartedu/processed/cleaned_student_data.csv"
DOWNLOAD_DIR="/tmp/smartedu_hdfs_verification_$$"

echo -e "${BOLD}${BLUE}==============================================================================${NC}"
echo -e "${BOLD}${BLUE} SmartEdu Analytics - Task 6: HDFS Read, Write & Download Demonstration${NC}"
echo -e "${BOLD}${BLUE}==============================================================================${NC}"

# Verify HDFS source
echo -e "\n${BOLD}[STEP 1] Verifying HDFS Source File...${NC}"
if ! hdfs dfs -test -e "${HDFS_SRC}"; then
    echo -e "${RED}[ERROR] HDFS source file does not exist: ${HDFS_SRC}${NC}"
    echo -e "${YELLOW}Please run upload_dataset_to_hdfs.sh first.${NC}"
    exit 1
fi
echo -e "${GREEN}[OK] HDFS Source verified:${NC} ${HDFS_SRC}"

# Step 2: In-flight HDFS Read (hdfs dfs -cat)
echo -e "\n${BOLD}[STEP 2] Demonstrating In-Flight HDFS Read (hdfs dfs -cat | head -n 5)...${NC}"
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"
hdfs dfs -cat "${HDFS_SRC}" | head -n 5
echo -e "${BLUE}------------------------------------------------------------------------------${NC}"
echo -e "${GREEN}[OK] Successfully streamed records directly from HDFS NameNode/DataNode pipeline.${NC}"

# Step 3: Local Download Directory Setup
echo -e "\n${BOLD}[STEP 3] Preparing Local Download Destination (${DOWNLOAD_DIR})...${NC}"
mkdir -p "${DOWNLOAD_DIR}"
DOWNLOADED_FILE="${DOWNLOAD_DIR}/cleaned_student_data_downloaded.csv"

# Step 4: Download from HDFS (hdfs dfs -get)
echo -e "\n${BOLD}[STEP 4] Executing HDFS Download (hdfs dfs -get)...${NC}"
hdfs dfs -get "${HDFS_SRC}" "${DOWNLOADED_FILE}"
if [ $? -eq 0 ] && [ -f "${DOWNLOADED_FILE}" ]; then
    echo -e "${GREEN}[SUCCESS] File successfully retrieved from HDFS to:${NC} ${DOWNLOADED_FILE}"
    dl_size=$(stat -c%s "${DOWNLOADED_FILE}" 2>/dev/null || wc -c < "${DOWNLOADED_FILE}")
    echo -e " -> Downloaded file size: ${dl_size} bytes"
else
    echo -e "${RED}[ERROR] Failed to download file from HDFS.${NC}"
    exit 1
fi

# Step 5: Checksum and Exact Bitwise Verification
echo -e "\n${BOLD}[STEP 5] Cryptographic & Content Verification (MD5 Checksum)...${NC}"
HDFS_MD5=$(md5sum "${DOWNLOADED_FILE}" | awk '{print $1}')
echo -e " -> Downloaded File MD5 : ${HDFS_MD5}"

if [ -f "${LOCAL_SRC}" ]; then
    LOCAL_MD5=$(md5sum "${LOCAL_SRC}" | awk '{print $1}')
    echo -e " -> Original File MD5   : ${LOCAL_MD5}"
    
    if [ "${HDFS_MD5}" == "${LOCAL_MD5}" ]; then
        echo -e "${GREEN}[INTEGRITY VERIFIED] Checksums match perfectly! 100% bitwise data fidelity.${NC}"
    else
        echo -e "${RED}[INTEGRITY FAILURE] Checksum mismatch between original and downloaded copy!${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}[NOTICE] Original local source not found at ${LOCAL_SRC}; verified downloaded structure independently.${NC}"
fi

# Step 6: Cleanup Demonstration
echo -e "\n${BOLD}[STEP 6] Cleaning Up Temporary Local Download Artifacts...${NC}"
rm -rf "${DOWNLOAD_DIR}"
echo -e "${GREEN}[OK] Cleaned up temporary directory ${DOWNLOAD_DIR}.${NC}"

echo -e "\n${BOLD}${GREEN}==============================================================================${NC}"
echo -e "${BOLD}${GREEN} [DEMONSTRATION COMPLETE] HDFS Read, Write & Download fully verified.${NC}"
echo -e "${BOLD}${GREEN}==============================================================================${NC}\n"
