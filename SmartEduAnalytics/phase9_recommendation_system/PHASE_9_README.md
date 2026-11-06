# Phase 9: Personalized Student Recommendation System

## 1. Overview
Phase 9 provides an automated, domain-aware educational recommendation and early intervention engine for SmartEdu Analytics. Leveraging the multidimensional student feature store from Phase 1 and the calibrated ML dropout predictions from Phase 8, it formulates targeted intervention plans across academic, financial, attendance, and faculty mentorship dimensions.

## 2. Recommendation Architecture & Rules
The engine applies a hybrid decision-tree rule matrix combined with machine learning risk tiers:
- **Academic Remedial & Tutoring**: Triggers when a student has $\ge 1$ failed units or cumulative annual grade $< 11.5/20$. Recommends mandatory peer tutoring, guided study halls, or subject-specific clinics.
- **Tuition & Financial Aid Advisory**: Triggers when tuition fee payments are overdue (`tuition_fees_up_to_date == 0`) or outstanding debt exists (`is_debtor == 1`). Recommends emergency micro-bursaries and installment plans.
- **Attendance & Schedule Advising**: Triggers for evening shift students who are struggling academically. Recommends asynchronous lecture access, commute accommodations, and workload rebalancing.
- **Faculty Mentorship & Retention Coaching**: Triggers for high/medium-risk students ($\text{Probability} \ge 0.35$) and those with declining grade trajectories ($\le -2.0$). Coordinates a binding Student Success Agreement (SSA).
- **Advanced Career & Research Enrichment**: Triggers for high achievers (GPA $\ge 14.0/20$ and 0 failed units). Recommends undergraduate research fellowships, honours societies, and corporate internships.

## 3. Prioritization Taxonomy
Each generated recommendation is assigned an urgency ranking:
1. `Critical`: Immediate action needed within 7 days (e.g. tuition hold, severe course failures, $>70\%$ dropout risk).
2. `High`: Action needed within 14 days (e.g. declining semester trajectory, single course failure).
3. `Medium`: Ongoing bi-weekly monitoring (e.g. evening shift fatigue, mature student integration).
4. `Low`: Long-term development and enrichment for top students.

## 4. Execution Workflow
```bash
# Generate recommendations and persist into MySQL / SQLite database
python mysql_integration.py
```

## 5. Artifacts
- Catalog: `dataset/analytics/recommendations/student_recommendations.csv`
- Database: Table `student_recommendations` with indexes on `student_id` and `priority`
