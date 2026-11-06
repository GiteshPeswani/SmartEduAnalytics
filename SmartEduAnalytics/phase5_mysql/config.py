"""
SmartEdu Analytics - Phase 5: MySQL Configuration & Database Connection Manager
File: config.py
"""

import os
import sys

# MySQL Database Configuration
# Defaults can be overridden via environment variables
MYSQL_CONFIG = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "port": int(os.environ.get("MYSQL_PORT", 3306)),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),  # Default root password
    "database": os.environ.get("MYSQL_DATABASE", "smartedu"),
    "raise_on_warnings": True,
    "autocommit": True
}

# Project File Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CSV_DATA_PATH = os.path.join(PROJECT_ROOT, "dataset", "processed", "preprocessed_student_data.csv")
SQL_SCHEMA_PATH = os.path.join(SCRIPT_DIR, "schema.sql")
SQLITE_FALLBACK_DB = os.path.join(SCRIPT_DIR, "smartedu_local.db")

def get_mysql_connection():
    """
    Attempts connection to MySQL Server using mysql-connector-python.
    Returns (connection, is_sqlite_fallback)
    """
    try:
        import mysql.connector
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn, False
    except Exception as e:
        # Graceful SQLite fallback for local verification when MySQL service is offline
        import sqlite3
        conn = sqlite3.connect(SQLITE_FALLBACK_DB)
        conn.row_factory = sqlite3.Row
        return conn, True

def get_connection_info():
    conn, is_fallback = get_mysql_connection()
    if is_fallback:
        return f"SQLite Local Engine (Fallback: {SQLITE_FALLBACK_DB})"
    else:
        return f"MySQL Server 8.0 @ {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']} [Database: {MYSQL_CONFIG['database']}]"
