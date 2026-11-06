"""
SmartEdu Analytics - Phase 10: Backend API Verification Suite
File: test_api.py
"""

import sys
import os
from fastapi.testclient import TestClient

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(SCRIPT_DIR)

from main import app

client = TestClient(app)

def test_endpoints():
    print("=" * 80)
    print(" SmartEdu Analytics - Phase 10: Backend API Verification Suite")
    print("=" * 80)

    # 1. Health check
    res = client.get("/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print(f" -> [PASS] /api/health: {res.json()}")

    # 2. Login
    res = client.post("/api/auth/login", json={"username": "admin", "password": "smartedu2026"})
    assert res.status_code == 200, f"Login failed: {res.text}"
    print(f" -> [PASS] /api/auth/login: Auth token received for {res.json()['user']['name']}")

    # 3. Dashboard Stats
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200, f"Stats failed: {res.text}"
    data = res.json()
    print(f" -> [PASS] /api/dashboard/stats: Total Students={data['total_students']}, Avg Grade={data['overall_avg_grade']}, High Risk={data['risk_tiers']['High Risk']}")

    # 4. Students Roster
    res = client.get("/api/students?page=1&page_size=5")
    assert res.status_code == 200, f"Students failed: {res.text}"
    std_data = res.json()
    print(f" -> [PASS] /api/students: Returned {len(std_data['data'])} records (Total: {std_data['total_records']})")
    first_sid = std_data['data'][0]['student_id']

    # 5. Student Detail
    res = client.get(f"/api/students/{first_sid}")
    assert res.status_code == 200, f"Student detail failed: {res.text}"
    detail = res.json()
    print(f" -> [PASS] /api/students/{first_sid}: Risk Tier={detail['risk_tier']}, Recommendations={len(detail['recommendations'])}")

    # 6. Performance Analytics
    res = client.get("/api/analytics/performance")
    assert res.status_code == 200, f"Performance failed: {res.text}"
    perf = res.json()
    print(f" -> [PASS] /api/analytics/performance: Loaded {len(perf['courses'])} courses")

    # 7. Risk Predictions
    res = client.get("/api/risk/predictions")
    assert res.status_code == 200, f"Risk predictions failed: {res.text}"
    risk = res.json()
    print(f" -> [PASS] /api/risk/predictions: Top at-risk count={len(risk['top_at_risk_students'])}, Models={len(risk['model_benchmarks'])}")

    # 8. Reports Export
    res = client.get("/api/reports/export")
    assert res.status_code == 200, f"Reports export failed: {res.text}"
    print(f" -> [PASS] /api/reports/export: CSV download stream verified ({len(res.content):,} bytes)")

    # 9. Frontend static file check
    res = client.get("/")
    assert res.status_code == 200, f"Frontend root failed: {res.text}"
    print(f" -> [PASS] / (Frontend Dashboard): Successfully served HTML ({len(res.content):,} bytes)")

    print("\n[VERIFICATION COMPLETE] All Phase 10 API endpoints and frontend routes passed successfully!")

if __name__ == "__main__":
    test_endpoints()
