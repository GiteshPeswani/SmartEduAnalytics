@echo off
TITLE SmartEdu Analytics - Web Dashboard Server
echo ===============================================================================
echo            SmartEdu Analytics - Big Data & AI Retention Platform
echo ===============================================================================
echo Starting FastAPI Backend and Web Dashboard...
echo URL: http://127.0.0.1:8000/
echo Swagger API Docs: http://127.0.0.1:8000/docs
echo.
echo Default Admin Login:
echo Username: admin
echo Password: smartedu2026
echo ===============================================================================

rem Open browser automatically after 2 seconds
start "" "http://127.0.0.1:8000/"

rem Run server using project virtual environment
"d:\bdampr\.venv\Scripts\python.exe" "d:\bdampr\SmartEduAnalytics\run_all.py" --server-only

pause
