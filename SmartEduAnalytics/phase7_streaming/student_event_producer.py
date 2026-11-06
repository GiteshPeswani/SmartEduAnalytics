"""
SmartEdu Analytics - Phase 7: Real-Time Academic Event Producer
Script: student_event_producer.py
Description:
    Simulates high-velocity incoming student activity streams.
    IMPORTANT: This is a clearly labelled synthetic test event generator
    for streaming pipeline validation only. It does NOT modify or pollute
    the historical student baseline records from Phases 1-4.
"""

import os
import sys
import time
import json
import uuid
import random
from datetime import datetime

EVENT_TYPES = [
    ("attendance_checkin", [1.0, 1.0, 1.0, 1.0, 0.0]),  # 80% attendance probability
    ("quiz_score", lambda: round(random.gauss(12.5, 3.5), 2)), # Normal distribution 0-20
    ("assignment_submission", lambda: round(random.uniform(8.0, 19.5), 2)),
    ("lms_activity", lambda: round(random.uniform(10.0, 120.0), 1)) # Minutes active
]

def generate_synthetic_event(student_ids, course_ids):
    """Generates a single structured academic activity telemetry event."""
    student_id = random.choice(student_ids)
    course_id = random.choice(course_ids)
    
    event_def = random.choice(EVENT_TYPES)
    event_type = event_def[0]
    
    if callable(event_def[1]):
        raw_val = event_def[1]()
    else:
        raw_val = random.choice(event_def[1])
        
    val = max(0.0, min(20.0 if "score" in event_type else 180.0, raw_val))
    
    metadata = {}
    if event_type == "attendance_checkin":
        metadata["status"] = "PRESENT" if val == 1.0 else "ABSENT"
        metadata["lecture_slot"] = f"Slot_{random.randint(1, 4)}"
    elif event_type == "quiz_score":
        metadata["quiz_title"] = f"Quiz_{random.randint(1, 8)}"
        metadata["max_marks"] = 20.0
    elif event_type == "assignment_submission":
        metadata["assignment_id"] = f"ASG_{random.randint(1, 5)}"
    else:
        metadata["session_device"] = random.choice(["Desktop", "Mobile", "Tablet"])
        
    event = {
        "event_id": str(uuid.uuid4()),
        "student_id": student_id,
        "course_id": course_id,
        "event_type": event_type,
        "event_value": float(val),
        "event_metadata": json.dumps(metadata),
        "event_timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "is_test_event": True
    }
    return event

def event_stream(student_ids, course_ids, max_events=100, delay=0.05):
    """Generator yielding streaming academic events."""
    print(f"[PRODUCER] Initialized Streaming Event Producer for {len(student_ids)} student IDs.")
    print(f"[PRODUCER] Emitting {max_events} telemetry events (Interval: {delay}s)...")
    
    for i in range(max_events):
        ev = generate_synthetic_event(student_ids, course_ids)
        yield ev
        time.sleep(delay)

if __name__ == "__main__":
    sample_students = [f"STD_{10001 + i}" for i in range(25)]
    sample_courses = [9500, 9070, 9085, 9119, 9238]
    for ev in event_stream(sample_students, sample_courses, max_events=5, delay=0.1):
        print(json.dumps(ev, indent=2))
