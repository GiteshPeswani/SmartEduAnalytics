# SmartEdu Analytics – Phase 7: Real-Time Academic Activity Streaming Engine

## Overview
Phase 7 implements real-time streaming analytics to capture, process, and evaluate incoming student telemetry in real time. It enables instant detection of attendance drops below the critical 75% threshold and continuously updates student performance risk indicators.

---

## File Inventory
- `schema_streaming.sql`: DDL schema for streaming event logs (`academic_event_logs`), rolling metrics (`realtime_student_metrics`), and threshold alerts (`streaming_attendance_alerts`).
- `student_event_producer.py`: High-velocity synthetic event stream generator. *Clearly labelled for testing only; does not contaminate historical baseline records.*
- `streaming_consumer.py`: Real-time streaming consumer performing event deduplication, windowed rolling attendance calculations, alert triggers (< 75%), and state persistence into MySQL / SQLite.
- `run_streaming_pipeline.py`: End-to-end streaming simulation runner and chart exporter.
- `requirements.txt`: Streaming dependencies.
- `README.md`: This execution guide.

---

## Architecture Flow

```
+------------------------------------+          +------------------------------------+
|       Synthetic Event Producer     |  Stream  |        Streaming Consumer          |
|    (Attendance, Quizzes, LMS)      |--------->| (Deduplication, Rolling Metrics,   |
|   100 events / 25 student cohort   |          |  Alert Threshold Check < 75%)      |
+------------------------------------+          +------------------------------------+
                                                                  |
                                                                  v
                                                +------------------------------------+
                                                |     MySQL / SQLite Event Sink      |
                                                |  - academic_event_logs             |
                                                |  - realtime_student_metrics        |
                                                |  - streaming_attendance_alerts     |
                                                +------------------------------------+
```

---

## Execution Guide

### Run End-to-End Streaming Simulation:
```powershell
python phase7_streaming/run_streaming_pipeline.py
```

*Expected Verification:*
1. Producer emits 100 structured telemetry events.
2. Consumer logs events, updates rolling attendance, and triggers active alerts for students dropping below 75% attendance.
3. Deduplication engine intercepts and skips re-injected duplicate events.
4. Generates 2 charts in `visualizations/phase7/`.
