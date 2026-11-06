@echo off
TITLE SmartEdu Analytics - Full End-to-End Execution
echo ===============================================================================
echo            SmartEdu Analytics - Complete 10-Phase Pipeline
echo ===============================================================================
echo This script executes:
echo  1. Data Preprocessing & Feature Engineering (Phase 1)
echo  2. Relational Database Ingestion (Phase 5)
echo  3. Apache Spark Distributed Analytics Simulation (Phase 6)
echo  4. Real-Time Streaming & Alerts (Phase 7)
echo  5. Machine Learning Training, Evaluation & Predictions (Phase 8)
echo  6. Personalized Recommendations Generation (Phase 9)
echo  7. Backend API Test Suite (Phase 10)
echo  8. Production Web Dashboard Launch (Phase 10)
echo ===============================================================================
echo.

"d:\bdampr\.venv\Scripts\python.exe" "d:\bdampr\SmartEduAnalytics\run_all.py"

pause
