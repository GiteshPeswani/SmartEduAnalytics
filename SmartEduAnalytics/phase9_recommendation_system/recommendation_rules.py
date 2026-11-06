"""
SmartEdu Analytics - Phase 9: Personalized Student Recommendation System
File: recommendation_rules.py
Description:
    Domain rule catalog and policy mappings for academic interventions,
    attendance remediation, financial counseling, and performance enrichment.
"""

# Categorized Intervention Domains
CATEGORIES = {
    "ACADEMIC_REMEDIAL": "Academic Remedial & Tutoring",
    "ATTENDANCE_SUPPORT": "Attendance & Schedule Advising",
    "FINANCIAL_COUNSELING": "Tuition & Financial Aid Advisory",
    "FACULTY_MENTORSHIP": "Faculty Mentorship & Retention Coaching",
    "ADVANCED_ENRICHMENT": "Advanced Career & Research Enrichment"
}

PRIORITIES = {
    "CRITICAL": "Critical",
    "HIGH": "High",
    "MEDIUM": "Medium",
    "LOW": "Low"
}

def evaluate_academic_rules(student_profile):
    """
    Evaluates academic scores and course pass rates.
    """
    recs = []
    annual_grade = student_profile.get("annual_grade_avg", 0.0)
    failed_units = student_profile.get("total_units_failed", 0)
    sem1_approval = student_profile.get("sem1_approval_rate", 1.0)
    sem2_approval = student_profile.get("sem2_approval_rate", 1.0)
    trajectory = student_profile.get("grade_trajectory", 0.0)

    # 1. Critical Failure Intervention
    if failed_units >= 3 or (sem1_approval < 0.50 and sem2_approval < 0.50):
        recs.append({
            "category": CATEGORIES["ACADEMIC_REMEDIAL"],
            "priority": PRIORITIES["CRITICAL"],
            "recommendation_text": f"Enroll in Mandatory Intensive Peer Tutoring for {failed_units} failed curricular units.",
            "action_plan": "Schedule weekly 3-hour guided study halls with student department tutors and retake diagnostic assessments before midterm."
        })
    elif failed_units >= 1 or annual_grade < 11.5:
        recs.append({
            "category": CATEGORIES["ACADEMIC_REMEDIAL"],
            "priority": PRIORITIES["HIGH"],
            "recommendation_text": "Join Subject-Specific Remedial Workshop Series.",
            "action_plan": "Attend bi-weekly faculty office hours and access practice problem sets for underperforming modules."
        })

    # 2. Steep Trajectory Drop
    if trajectory <= -2.0:
        recs.append({
            "category": CATEGORIES["FACULTY_MENTORSHIP"],
            "priority": PRIORITIES["HIGH"],
            "recommendation_text": "Academic Trajectory Recovery Consultation with Department Head.",
            "action_plan": "Analyze causes behind grade drop from Sem 1 to Sem 2; adjust study load and workload allocation."
        })

    # 3. High Achiever Enrichment
    if annual_grade >= 14.0 and failed_units == 0:
        recs.append({
            "category": CATEGORIES["ADVANCED_ENRICHMENT"],
            "priority": PRIORITIES["LOW"],
            "recommendation_text": "Nomination for Undergraduate Research Fellowship & Academic Honours Society.",
            "action_plan": "Engage with faculty research labs, explore peer mentorship opportunities, and apply for competitive national grants."
        })

    return recs

def evaluate_financial_rules(student_profile):
    """
    Evaluates financial status: debt and tuition payment compliance.
    """
    recs = []
    fees_up_to_date = student_profile.get("tuition_fees_up_to_date", 1)
    is_debtor = student_profile.get("is_debtor", 0)

    if fees_up_to_date == 0 or is_debtor == 1:
        recs.append({
            "category": CATEGORIES["FINANCIAL_COUNSELING"],
            "priority": PRIORITIES["CRITICAL"],
            "recommendation_text": "Immediate Financial Aid & Tuition Payment Plan Consultation.",
            "action_plan": "Submit installment rescheduling request to Student Financial Services; evaluate emergency micro-scholarships and bursaries to eliminate academic administrative holds."
        })
    return recs

def evaluate_attendance_and_lifestyle_rules(student_profile):
    """
    Evaluates shift, attendance barriers, and lifestyle constraints.
    """
    recs = []
    evening_mode = student_profile.get("daytime_evening_attendance", 1) == 0
    age = student_profile.get("age_at_enrollment", 20)
    risk_tier = student_profile.get("risk_tier", "Low Risk")

    if evening_mode and risk_tier in ["High Risk", "Medium Risk"]:
        recs.append({
            "category": CATEGORIES["ATTENDANCE_SUPPORT"],
            "priority": PRIORITIES["MEDIUM"],
            "recommendation_text": "Evening Student Work-Study Rebalancing Counseling.",
            "action_plan": "Coordinate flexible digital lecture recordings, optimize evening commuting support, and negotiate blended learning accommodations."
        })

    if age >= 26 and risk_tier in ["High Risk", "Medium Risk"]:
        recs.append({
            "category": CATEGORIES["FACULTY_MENTORSHIP"],
            "priority": PRIORITIES["MEDIUM"],
            "recommendation_text": "Mature Student Academic Integration & Time-Management Coaching.",
            "action_plan": "Partner with non-traditional student network for peer study groups, professional workload management, and career transition mapping."
        })

    return recs

def evaluate_risk_tier_rules(student_profile):
    """
    Evaluates Phase 8 predicted risk tier.
    """
    recs = []
    risk_tier = student_profile.get("risk_tier", "Low Risk")
    dropout_prob = student_profile.get("dropout_probability", 0.0)

    if risk_tier == "High Risk" or dropout_prob >= 0.70:
        recs.append({
            "category": CATEGORIES["FACULTY_MENTORSHIP"],
            "priority": PRIORITIES["CRITICAL"],
            "recommendation_text": f"Urgent Comprehensive Multi-Disciplinary Case Review (Predicted Dropout Risk: {dropout_prob*100:.1f}%).",
            "action_plan": "Convening academic advisor, student welfare coordinator, and faculty lead to execute an individualized Student Success Agreement (SSA)."
        })
    elif risk_tier == "Medium Risk" or dropout_prob >= 0.35:
        recs.append({
            "category": CATEGORIES["FACULTY_MENTORSHIP"],
            "priority": PRIORITIES["MEDIUM"],
            "recommendation_text": f"Proactive Bi-Weekly Academic Advising Check-in (Dropout Risk: {dropout_prob*100:.1f}%).",
            "action_plan": "Monitor upcoming assignment submissions, evaluate course comprehension, and review mid-semester milestone targets."
        })
    elif not recs and risk_tier == "Low Risk":
        recs.append({
            "category": CATEGORIES["ADVANCED_ENRICHMENT"],
            "priority": PRIORITIES["LOW"],
            "recommendation_text": "Maintain Steady Academic Cadence & Explore Professional Internships.",
            "action_plan": "Continue current coursework study habits, attend department industry career days, and register for technical certifications."
        })

    return recs
