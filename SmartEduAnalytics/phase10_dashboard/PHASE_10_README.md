# Phase 10: Production Web Dashboard & End-to-End System Integration

## 1. Overview
Phase 10 delivers a full-stack, real-time analytics web dashboard that connects directly to the underlying Big Data data store (MySQL/SQLite) and Machine Learning inference pipelines. The application empowers academic administrators, department chairs, and faculty counselors to monitor cohort health, explore individual student profiles, inspect AI-driven dropout risks, and track targeted intervention plans.

## 2. Technology Architecture
- **Backend**:
  - Framework: FastAPI (Python 3.13)
  - ASGI Server: Uvicorn
  - Database Interface: Unified abstraction layer supporting MySQL Server 8.0 with graceful SQLite fallback
  - Data Serialization: Pydantic v2
  - Core Modules:
    - `main.py`: RESTful routing, CORS middleware, static file serving
    - `db_service.py`: High-performance analytical queries and pagination
    - `run_backend.py`: Production application startup script
- **Frontend**:
  - Modern Single-Page Application (SPA) architecture
  - Styling: Tailwind CSS
  - Charting Engine: Chart.js
  - Component Iconography: Lucide Icons
  - Zero-build immediate browser accessibility via FastAPI static hosting at `http://localhost:8000/`

## 3. Endpoints Documentation
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status check |
| `POST` | `/api/auth/login` | Administrator authentication |
| `GET` | `/api/dashboard/stats` | KPI aggregate metrics (total students, GPA, risk tiers) |
| `GET` | `/api/students` | Paginated, searchable student directory with risk filtering |
| `GET` | `/api/students/{id}` | In-depth student academic profile and transcript |
| `GET` | `/api/analytics/performance` | Program-wise GPA and attrition metrics |
| `GET` | `/api/analytics/attendance` | Shift comparison & attendance tier correlations |
| `GET` | `/api/risk/predictions` | Top priority at-risk students and ML model benchmarks |
| `GET` | `/api/risk/{id}` | Diagnostic risk factors and probability for single student |
| `GET` | `/api/recommendations/{id}` | Assigned personalized interventions |
| `POST` | `/api/recommendations/{id}/status`| Update intervention status (Pending/In Progress/Completed) |
| `GET` | `/api/reports/export` | Direct CSV export of all 4,424 student predictions |

## 4. How to Run the Dashboard

### Step 1: Launch the Backend & Frontend Server
Navigate to the backend directory and run:
```bash
# Using project venv
d:\bdampr\.venv\Scripts\python.exe d:\bdampr\SmartEduAnalytics\phase10_dashboard\backend\run_backend.py
```

### Step 2: Access the Application
Open your web browser and navigate to:
- **Interactive Web Dashboard**: `http://localhost:8000/`
- **Interactive Swagger API Docs**: `http://localhost:8000/docs`
- **Alternative ReDoc Docs**: `http://localhost:8000/redoc`

### Step 3: Default Administrative Credentials
- **Username**: `admin`
- **Password**: `smartedu2026`
