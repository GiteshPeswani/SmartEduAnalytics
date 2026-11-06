"""
SmartEdu Analytics - Master End-to-End Project Runner
File: run_all.py
Description:
    Orchestrates and executes the complete 10-phase SmartEdu Analytics pipeline:
    1. Preprocessing & Feature Engineering (Phase 1)
    2. Relational Database Ingestion & Storage (Phase 5)
    3. Apache Spark Analytics Simulation (Phase 6)
    4. Real-Time Streaming & Alerts Simulation (Phase 7)
    5. Machine Learning Dropout Prediction Pipeline (Phase 8)
    6. Personalized Student Recommendation Generation (Phase 9)
    7. Backend API Verification Test Suite (Phase 10)
    8. Web Application Server Launch (Phase 10)
"""

import os
import sys
import subprocess
import time
import webbrowser

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(os.path.dirname(PROJECT_ROOT), ".venv", "Scripts", "python.exe")
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

def print_banner(text):
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)

def run_step(step_name, command_args):
    print(f"\n[RUNNING] {step_name}...")
    start_time = time.time()
    result = subprocess.run([VENV_PYTHON] + command_args, cwd=PROJECT_ROOT)
    elapsed = time.time() - start_time
    if result.returncode != 0:
        print(f"[ERROR] {step_name} failed with exit code {result.returncode}!")
        return False
    print(f"[SUCCESS] {step_name} completed in {elapsed:.2f} seconds.")
    return True

def run_pipeline():
    print_banner("SmartEdu Analytics: Complete 10-Phase Pipeline Execution")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Python Interpreter: {VENV_PYTHON}")

    steps = [
        ("Phase 1: Data Cleaning & Standardization", 
         [os.path.join(PROJECT_ROOT, "scripts", "phase1", "clean_dataset.py")]),

        ("Phase 1: Dataset Preprocessing & Feature Engineering", 
         [os.path.join(PROJECT_ROOT, "scripts", "phase1", "preprocess_dataset.py")]),

        ("Phase 5: MySQL / SQLite Relational Database Ingestion", 
         [os.path.join(PROJECT_ROOT, "phase5_mysql", "import_data.py")]),

        ("Phase 6: Apache Spark & MLlib Distributed Simulation", 
         [os.path.join(PROJECT_ROOT, "phase6_spark", "run_local_spark_simulation.py")]),

        ("Phase 7: Real-Time Attendance Event Streaming & Alert Simulation", 
         [os.path.join(PROJECT_ROOT, "phase7_streaming", "run_streaming_pipeline.py")]),

        ("Phase 8: Machine Learning Model Training (Champion: Gradient Boosting)", 
         [os.path.join(PROJECT_ROOT, "phase8_dropout_prediction", "train_model.py")]),

        ("Phase 8: Model Evaluation & Metric Visualizations", 
         [os.path.join(PROJECT_ROOT, "phase8_dropout_prediction", "evaluate_model.py")]),

        ("Phase 8: Batch Scoring & Risk Tier Classification (4,424 Students)", 
         [os.path.join(PROJECT_ROOT, "phase8_dropout_prediction", "predict_risk.py")]),

        ("Phase 9: Personalized Student Recommendation Generation", 
         [os.path.join(PROJECT_ROOT, "phase9_recommendation_system", "mysql_integration.py")]),

        ("Phase 10: Backend REST API Verification Suite", 
         [os.path.join(PROJECT_ROOT, "phase10_dashboard", "backend", "test_api.py")])
    ]

    for name, args in steps:
        if not run_step(name, args):
            print(f"\n[PIPELINE ABORTED] Encountered failure at: {name}")
            return False

    print_banner("All Pipeline Stages Completed Successfully!")
    return True

def start_server():
    print_banner("Starting Phase 10 Production Web Dashboard & REST API Server")
    server_script = os.path.join(PROJECT_ROOT, "phase10_dashboard", "backend", "run_backend.py")
    
    print("Launching server at: http://127.0.0.1:8000")
    print("Opening web browser in 2 seconds...")
    print("Press CTRL+C anytime in this window to stop the server.\n")

    # Open browser
    time.sleep(1.5)
    try:
        webbrowser.open("http://127.0.0.1:8000/")
    except Exception:
        pass

    subprocess.run([VENV_PYTHON, server_script], cwd=os.path.dirname(server_script))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SmartEdu Analytics Master Orchestrator")
    parser.add_argument("--server-only", action="store_true", help="Launch the web dashboard directly without re-running data pipeline")
    parser.add_argument("--pipeline-only", action="store_true", help="Run data and ML pipeline only without starting server")
    args = parser.parse_args()

    if args.server_only:
        start_server()
    elif args.pipeline_only:
        run_pipeline()
    else:
        success = run_pipeline()
        if success:
            start_server()
