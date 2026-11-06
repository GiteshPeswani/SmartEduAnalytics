"""
SmartEdu Analytics - Phase 1: Data Collection & Ingestion
Script: load_dataset.py
Description:
    Downloads the verified UCI Machine Learning Repository dataset:
    "Predict Students' Dropout and Academic Success" (UCI ID: 697, CC BY 4.0).
    Saves the original unmodified raw dataset into 'dataset/raw/raw_student_data.csv'.
"""

import os
import sys
import io
import zipfile
import urllib.request
import pandas as pd

# Define paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "dataset", "raw")
RAW_DATA_PATH = os.path.join(RAW_DATA_DIR, "raw_student_data.csv")

UCI_URL = "https://archive.ics.uci.edu/static/public/697/predict+students+dropout+and+academic+success.zip"

def download_and_extract_dataset(force_download=False):
    """
    Downloads and extracts the dataset from UCI Machine Learning Repository.
    Preserves raw data without alterations.
    """
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    
    if os.path.exists(RAW_DATA_PATH) and not force_download:
        print(f"[INFO] Raw dataset already exists at: {RAW_DATA_PATH}")
        df = pd.read_csv(RAW_DATA_PATH, sep=";", encoding="utf-8-sig")
        print(f"[INFO] Loaded existing raw dataset: {df.shape[0]} rows, {df.shape[1]} columns.")
        return df

    print(f"[INFO] Downloading official UCI Dataset from: {UCI_URL}")
    req = urllib.request.Request(
        UCI_URL,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            zip_bytes = response.read()
            print(f"[SUCCESS] Download completed ({len(zip_bytes) / 1024:.2f} KB received).")
            
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            extracted_filename = "data.csv"
            if extracted_filename not in z.namelist():
                raise FileNotFoundError(f"'{extracted_filename}' not found in downloaded zip archive.")
            
            with z.open(extracted_filename) as f:
                # Read raw bytes and save verbatim to ensure provenance
                content = f.read()
                with open(RAW_DATA_PATH, "wb") as out_file:
                    out_file.write(content)
                    
        print(f"[SUCCESS] Raw dataset extracted and saved to: {RAW_DATA_PATH}")
        
        # Verify read
        df = pd.read_csv(RAW_DATA_PATH, sep=";", encoding="utf-8-sig")
        print(f"[METRICS] Total Records : {df.shape[0]:,}")
        print(f"[METRICS] Total Features: {df.shape[1]}")
        print(f"[METRICS] Target Classes: {dict(df['Target'].value_counts())}")
        return df

    except Exception as e:
        print(f"[ERROR] Failed to download or save dataset: {str(e)}", file=sys.stderr)
        raise

if __name__ == "__main__":
    print("=" * 70)
    print(" SmartEdu Analytics - Task 1: Dataset Collection & Ingestion")
    print("=" * 70)
    download_and_extract_dataset()
    print("=" * 70)
