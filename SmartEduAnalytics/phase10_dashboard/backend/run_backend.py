"""
SmartEdu Analytics - Phase 10: Backend Server Runner
File: run_backend.py
"""

import uvicorn
import os

if __name__ == "__main__":
    print("=" * 80)
    print(" Starting SmartEdu Analytics REST API & Web Dashboard Server")
    print(" Listening on: http://127.0.0.1:8000")
    print(" API Documentation: http://127.0.0.1:8000/docs")
    print("=" * 80)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
