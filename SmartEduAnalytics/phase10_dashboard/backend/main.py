"""
SmartEdu Analytics - Phase 10: Production FastAPI Application
File: main.py
Description:
    Core backend server providing RESTful endpoints for dashboard KPI metrics,
    student roster querying, ML risk predictions, recommendations, and CSV reports.
"""

import os
import sys
from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import io
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PHASE10_DIR = os.path.dirname(SCRIPT_DIR)
PROJECT_ROOT = os.path.dirname(PHASE10_DIR)
FRONTEND_DIR = os.path.join(PHASE10_DIR, "frontend")

sys.path.append(SCRIPT_DIR)
from db_service import DatabaseService

app = FastAPI(
    title="SmartEdu Analytics REST API",
    description="Big Data & ML-Driven Student Retention and Dropout Risk Prediction Platform",
    version="1.0.0"
)

# Enable CORS for cross-origin frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data Models
class LoginRequest(BaseModel):
    username: str
    password: str

class StatusUpdateRequest(BaseModel):
    status: str

# Endpoints
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "SmartEdu Analytics Backend API",
        "version": "1.0.0"
    }

@app.post("/api/auth/login")
def login(creds: LoginRequest):
    # Standard administrative credentials for academic personnel
    if creds.username == "admin" and creds.password == "smartedu2026":
        return {
            "success": True,
            "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.smartedu_admin_session",
            "user": {
                "username": "admin",
                "role": "Academic Dean / System Administrator",
                "name": "Dr. Sarah Jenkins"
            }
        }
    raise HTTPException(status_code=401, detail="Invalid administrator credentials.")

@app.get("/api/dashboard/stats")
def get_dashboard_stats():
    return DatabaseService.get_kpi_overview()

@app.get("/api/students")
def get_students(
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    search: str = Query("", description="Search by student_id"),
    risk_filter: str = Query("", description="Filter by risk tier (High Risk, Medium Risk, Low Risk, or ALL)")
):
    return DatabaseService.get_students_list(page=page, page_size=page_size, search=search, risk_filter=risk_filter)

@app.get("/api/students/{student_id}")
def get_student_profile(student_id: str):
    profile = DatabaseService.get_student_detail(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Student record '{student_id}' not found.")
    return profile

@app.get("/api/analytics/performance")
def get_performance_analytics():
    return DatabaseService.get_analytics_performance()

@app.get("/api/analytics/attendance")
def get_attendance_analytics():
    # Return daytime vs evening attendance risk correlation
    return {
        "attendance_modes": [
            {"mode": "Daytime Schedule", "count": 3915, "pct": 88.5, "avg_dropout_rate": 28.4},
            {"mode": "Evening Schedule", "count": 509, "pct": 11.5, "avg_dropout_rate": 60.7}
        ],
        "attendance_tiers": [
            {"tier": "Tier 1: Excellent (>=90%)", "avg_grade": 13.8, "dropout_pct": 12.1},
            {"tier": "Tier 2: Satisfactory (75-89%)", "avg_grade": 11.9, "dropout_pct": 28.5},
            {"tier": "Tier 3: Warning (50-74%)", "avg_grade": 9.4, "dropout_pct": 54.3},
            {"tier": "Tier 4: Critical (<50%)", "avg_grade": 4.2, "dropout_pct": 89.6}
        ]
    }

@app.get("/api/risk/predictions")
def get_risk_predictions():
    # Top 10 high-risk students and model benchmarks
    top_risk = DatabaseService.get_students_list(page=1, page_size=10, risk_filter="High Risk")
    comp_csv = os.path.join(PROJECT_ROOT, "phase8_dropout_prediction", "models", "models_comparison.csv")
    benchmarks = []
    if os.path.exists(comp_csv):
        df_bench = pd.read_csv(comp_csv)
        benchmarks = df_bench.to_dict(orient="records")

    return {
        "top_at_risk_students": top_risk["data"],
        "model_benchmarks": benchmarks
    }

@app.get("/api/risk/{student_id}")
def get_student_risk(student_id: str):
    profile = DatabaseService.get_student_detail(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found.")
    return {
        "student_id": profile["student_id"],
        "dropout_probability": profile["dropout_probability"],
        "risk_tier": profile["risk_tier"],
        "model_name": profile["model_name"],
        "primary_risk_factors": profile["primary_risk_factors"]
    }

@app.get("/api/recommendations/{student_id}")
def get_student_recommendations(student_id: str):
    profile = DatabaseService.get_student_detail(student_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Student not found.")
    return {
        "student_id": student_id,
        "recommendations": profile["recommendations"]
    }

@app.post("/api/recommendations/{rec_id}/status")
def update_rec_status(rec_id: int, payload: StatusUpdateRequest):
    success = DatabaseService.update_recommendation_status(rec_id, payload.status)
    return {"success": success, "rec_id": rec_id, "updated_status": payload.status}

@app.get("/api/reports/export")
def export_predictions_report():
    csv_path = os.path.join(PROJECT_ROOT, "dataset", "analytics", "predictions", "dropout_risk_predictions.csv")
    if not os.path.exists(csv_path):
        raise HTTPException(status_code=404, detail="Predictions dataset not found.")
    
    return FileResponse(
        csv_path,
        media_type="text/csv",
        filename="smartedu_dropout_risk_predictions.csv"
    )

# Mount frontend directory for SPA web UI
if os.path.exists(FRONTEND_DIR):
    @app.get("/app.js")
    def serve_app_js():
        return FileResponse(os.path.join(FRONTEND_DIR, "app.js"), media_type="application/javascript")

    @app.get("/styles.css")
    def serve_styles_css():
        return FileResponse(os.path.join(FRONTEND_DIR, "styles.css"), media_type="text/css")

    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_frontend():
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Frontend UI directory located, index.html building."}
