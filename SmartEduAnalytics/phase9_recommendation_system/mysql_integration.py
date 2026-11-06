"""
SmartEdu Analytics - Phase 9: Recommendation Database Integration
File: mysql_integration.py
Description:
    Persists rule-based and machine-learning driven student recommendations
    into the MySQL database / SQLite engine and exports comprehensive CSV reports.
"""

import os
import sys
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.append(os.path.join(PROJECT_ROOT, "phase5_mysql"))
sys.path.append(SCRIPT_DIR)

from config import get_mysql_connection
from recommendation_engine import RecommendationEngine

RECOMMENDATIONS_OUT_DIR = os.path.join(PROJECT_ROOT, "dataset", "analytics", "recommendations")

def persist_recommendations_pipeline():
    print("=" * 80)
    print(" SmartEdu Analytics - Phase 9: Recommendation Generation & DB Ingestion")
    print("=" * 80)

    os.makedirs(RECOMMENDATIONS_OUT_DIR, exist_ok=True)

    # 1. Generate recommendations
    engine = RecommendationEngine()
    df_recs = engine.generate_all()

    # 2. Export CSV
    csv_path = os.path.join(RECOMMENDATIONS_OUT_DIR, "student_recommendations.csv")
    df_recs.to_csv(csv_path, index=False)
    print(f"[EXPORTED CSV] Saved recommendations catalog to: {csv_path}")

    # 3. Persist to Database
    conn, is_fallback = get_mysql_connection()
    cursor = conn.cursor()
    db_type = "SQLite Fallback" if is_fallback else "MySQL 8.0"
    print(f"[DATABASE INTEGRATION] Target engine: {db_type}")

    if is_fallback:
        cursor.execute("DROP TABLE IF EXISTS student_recommendations;")
        create_sql = """
        CREATE TABLE student_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            recommendation_text TEXT NOT NULL,
            action_plan TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TEXT
        );
        """
        cursor.execute(create_sql)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rec_student ON student_recommendations(student_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rec_priority ON student_recommendations(priority);")
        
        insert_sql = """
        INSERT INTO student_recommendations (student_id, category, priority, recommendation_text, action_plan, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
    else:
        cursor.execute("DROP TABLE IF EXISTS student_recommendations;")
        create_sql = """
        CREATE TABLE student_recommendations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id VARCHAR(50) NOT NULL,
            category VARCHAR(100) NOT NULL,
            priority VARCHAR(30) NOT NULL,
            recommendation_text TEXT NOT NULL,
            action_plan TEXT,
            status VARCHAR(30) DEFAULT 'Pending',
            created_at VARCHAR(30),
            INDEX (student_id),
            INDEX (priority)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(create_sql)

        insert_sql = """
        INSERT INTO student_recommendations (student_id, category, priority, recommendation_text, action_plan, status, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """

    records = [
        (
            str(row["student_id"]),
            str(row["category"]),
            str(row["priority"]),
            str(row["recommendation_text"]),
            str(row["action_plan"]),
            str(row.get("status", "Pending")),
            str(row["created_at"])
        )
        for _, row in df_recs.iterrows()
    ]

    cursor.executemany(insert_sql, records)
    conn.commit()
    cursor.close()
    conn.close()

    print(f"[DATABASE COMMITTED] Successfully inserted {len(records):,} recommendations into 'student_recommendations' table.")

    # 4. Summary Breakdown
    print("\n[RECOMMENDATION BREAKDOWN BY PRIORITY]:")
    print(df_recs["priority"].value_counts().to_string())

    print("\n[RECOMMENDATION BREAKDOWN BY CATEGORY]:")
    print(df_recs["category"].value_counts().to_string())

if __name__ == "__main__":
    persist_recommendations_pipeline()
