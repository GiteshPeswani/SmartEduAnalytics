import os
import pandas as pd

base = r"d:\bdampr\SmartEduAnalytics"
files = {
    "raw_student_data.csv": os.path.join(base, "dataset", "raw", "raw_student_data.csv"),
    "cleaned_student_data.csv": os.path.join(base, "dataset", "processed", "cleaned_student_data.csv"),
    "preprocessed_student_data.csv": os.path.join(base, "dataset", "processed", "preprocessed_student_data.csv"),
    "train_data.csv": os.path.join(base, "dataset", "processed", "train_data.csv"),
    "test_data.csv": os.path.join(base, "dataset", "processed", "test_data.csv"),
    "dataset_summary.txt": os.path.join(base, "reports", "dataset_summary.txt")
}

for name, path in files.items():
    exists = os.path.exists(path)
    size = os.path.getsize(path) if exists else 0
    print(f"=== {name} ===")
    print(f"Path: {path}")
    print(f"Exists: {exists} | Size: {size:,} bytes ({size/1024:.2f} KB)")
    if exists and name.endswith(".csv"):
        with open(path, "r", encoding="utf-8-sig") as f:
            first_line = f.readline().strip()
            sep = ";" if ";" in first_line else ","
        df = pd.read_csv(path, sep=sep)
        print(f"Rows: {df.shape[0]:,} | Columns: {df.shape[1]} | Delimiter: '{sep}'")
        print(f"First 5 Columns: {list(df.columns[:5])}")
        print(f"Last 3 Columns: {list(df.columns[-3:])}")
    elif exists and name.endswith(".txt"):
        with open(path, "r", encoding="utf-8") as f:
            lines = [f.readline() for _ in range(5)]
            print("Preview:\n" + "".join(lines).strip())
    print("-" * 50)
