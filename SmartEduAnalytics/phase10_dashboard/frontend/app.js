/**
 * SmartEdu Analytics - Interactive Dashboard Controller
 * File: app.js
 */

const API_BASE = window.location.origin.includes('http') ? window.location.origin : 'http://127.0.0.1:8000';

let currentPage = 1;
let currentSearch = "";
let currentRiskFilter = "ALL";
let totalPages = 1;
let charts = {};

document.addEventListener('DOMContentLoaded', () => {
  refreshDashboard();
  loadStudentsData(1);
  loadPerformanceData();
  loadRiskPredictionsData();
  loadRecommendationsData();
});

// Tab Switcher
function switchTab(tabId) {
  document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.remove('bg-sky-600', 'text-white', 'shadow-sm');
    el.classList.add('text-slate-400');
  });

  const targetTab = document.getElementById(`tab-${tabId}`);
  const targetNav = document.getElementById(`nav-${tabId}`);
  if (targetTab) targetTab.classList.remove('hidden');
  if (targetNav) {
    targetNav.classList.remove('text-slate-400');
    targetNav.classList.add('bg-sky-600', 'text-white', 'shadow-sm');
  }

  // Header title update
  const titles = {
    'overview': ['Institutional Performance Overview', 'Real-time cohort insights across 4,424 student records'],
    'students': ['Student Directory & Academic Tracking', 'Searchable profiles and dynamic retention indicators'],
    'performance': ['Course Performance & Attendance Analytics', 'Curricular pass rates and shift impact comparisons'],
    'risk': ['Supervised ML Dropout Risk Modeling', 'Predictive diagnostic signals and early retention warnings'],
    'recommendations': ['Actionable Student Intervention Catalog', 'Prescriptive student success workflows and tutoring plans'],
    'reports': ['Pipeline Documentation & Data Exports', 'Verified artifacts from Phases 1 through 10']
  };
  if (titles[tabId]) {
    document.getElementById('page-title').innerText = titles[tabId][0];
    document.getElementById('page-subtitle').innerText = titles[tabId][1];
  }

  // Auto-refresh target tab content
  try {
    if (tabId === 'students') {
      loadStudentsData(currentPage);
    } else if (tabId === 'performance') {
      loadPerformanceData();
    } else if (tabId === 'risk') {
      loadRiskPredictionsData();
    } else if (tabId === 'recommendations') {
      loadRecommendationsData();
    }
    if (window.lucide) lucide.createIcons();
  } catch (e) {
    console.error("Tab activation error:", e);
  }
}

// 1. Dashboard Overview
async function refreshDashboard() {
  try {
    const res = await fetch(`${API_BASE}/api/dashboard/stats`);
    if (!res.ok) throw new Error("API call failed");
    const data = await res.json();

    document.getElementById('kpi-total-students').innerText = data.total_students.toLocaleString();
    document.getElementById('kpi-avg-grade').innerText = `${data.overall_avg_grade} / 20`;
    document.getElementById('kpi-high-risk').innerText = data.risk_tiers["High Risk"].toLocaleString();
    document.getElementById('kpi-critical-recs').innerText = data.recommendations["Critical"].toLocaleString();

    renderRiskDonut(data.risk_tiers);
  } catch (err) {
    console.warn("Using offline fallback data for overview KPIs", err);
    renderRiskDonut({ "Low Risk": 2989, "Medium Risk": 402, "High Risk": 1033 });
  }
}

function renderRiskDonut(riskData) {
  const ctx = document.getElementById('chart-risk-donut');
  if (!ctx) return;
  if (charts.riskDonut) charts.riskDonut.destroy();

  charts.riskDonut = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Low Risk', 'Medium Risk', 'High Risk'],
      datasets: [{
        data: [riskData['Low Risk'], riskData['Medium Risk'], riskData['High Risk']],
        backgroundColor: ['#10b981', '#f59e0b', '#f43f5e'],
        borderWidth: 2,
        borderColor: '#ffffff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: 'bottom' }
      },
      cutout: '68%'
    }
  });
}

// 2. Student Roster Loader
async function loadStudentsData(page = 1) {
  currentPage = page;
  const search = document.getElementById('student-search-input')?.value.trim() || "";
  const filter = document.getElementById('student-risk-filter')?.value || "ALL";

  try {
    const url = `${API_BASE}/api/students?page=${page}&page_size=15&search=${encodeURIComponent(search)}&risk_filter=${encodeURIComponent(filter)}`;
    const res = await fetch(url);
    const data = await res.json();

    totalPages = data.total_pages;
    document.getElementById('pagination-info').innerText = `Showing page ${data.page} of ${data.total_pages} (${data.total_records.toLocaleString()} total students)`;
    document.getElementById('current-page-num').innerText = data.page;
    document.getElementById('btn-prev-page').disabled = (data.page <= 1);
    document.getElementById('btn-next-page').disabled = (data.page >= data.total_pages);

    const tbody = document.getElementById('student-table-body');
    tbody.innerHTML = "";

    data.data.forEach(s => {
      const riskBadgeClass = s.risk_tier === "High Risk" 
        ? "bg-rose-100 text-rose-700 border-rose-200" 
        : (s.risk_tier === "Medium Risk" ? "bg-amber-100 text-amber-700 border-amber-200" : "bg-emerald-100 text-emerald-700 border-emerald-200");

      const tr = document.createElement('tr');
      tr.className = "hover:bg-slate-50 transition-colors";
      tr.innerHTML = `
        <td class="px-5 py-3.5 font-bold text-slate-800">${s.student_id}</td>
        <td class="px-4 py-3.5 text-slate-600">Course #${s.course_id}</td>
        <td class="px-4 py-3.5 font-semibold text-slate-700">${s.annual_grade_avg}</td>
        <td class="px-4 py-3.5 font-semibold ${s.total_units_failed > 0 ? 'text-rose-600' : 'text-slate-600'}">${s.total_units_failed}</td>
        <td class="px-4 py-3.5 text-slate-600">${s.attendance_rate}%</td>
        <td class="px-4 py-3.5 font-semibold">${(s.dropout_probability * 100).toFixed(1)}%</td>
        <td class="px-4 py-3.5">
          <span class="px-2.5 py-1 rounded-full text-xs font-bold border ${riskBadgeClass}">
            ${s.risk_tier}
          </span>
        </td>
        <td class="px-4 py-3.5 text-right">
          <button onclick="viewStudentModal('${s.student_id}')" class="px-2.5 py-1.5 text-xs font-semibold text-sky-600 hover:text-white hover:bg-sky-600 border border-sky-300 rounded-md transition-colors">
            Profile
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error("Failed to load student table:", err);
  }
}

function handleStudentSearch(event) {
  if (event.key === "Enter") {
    loadStudentsData(1);
  }
}

function prevStudentPage() {
  if (currentPage > 1) loadStudentsData(currentPage - 1);
}

function nextStudentPage() {
  if (currentPage < totalPages) loadStudentsData(currentPage + 1);
}

// 3. Performance & Course Charts
async function loadPerformanceData() {
  try {
    const res = await fetch(`${API_BASE}/api/analytics/performance`);
    const data = await res.json();
    const courses = data.courses.slice(0, 8); // Top 8 courses

    const ctx = document.getElementById('chart-course-bar');
    if (!ctx) return;
    if (charts.courseBar) charts.courseBar.destroy();

    charts.courseBar = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: courses.map(c => c.course_name),
        datasets: [
          {
            label: 'Avg Grade (/20)',
            data: courses.map(c => c.avg_grade),
            backgroundColor: '#0284c7'
          },
          {
            label: 'Dropout Rate (%)',
            data: courses.map(c => c.dropout_rate_pct),
            backgroundColor: '#f43f5e'
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, max: 25 }
        }
      }
    });

    // Attendance tier chart
    const attRes = await fetch(`${API_BASE}/api/analytics/attendance`);
    const attData = await attRes.json();

    const attCtx = document.getElementById('chart-attendance-bar');
    if (attCtx) {
      new Chart(attCtx, {
        type: 'bar',
        data: {
          labels: attData.attendance_tiers.map(t => t.tier),
          datasets: [{
            label: 'Dropout Rate (%)',
            data: attData.attendance_tiers.map(t => t.dropout_pct),
            backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      });
    }

    // Schedule Shift Comparison
    const schedCtx = document.getElementById('chart-schedule-pie');
    if (schedCtx) {
      new Chart(schedCtx, {
        type: 'pie',
        data: {
          labels: ['Daytime Cohort (88.5%)', 'Evening Cohort (11.5%)'],
          datasets: [{
            data: [3915, 509],
            backgroundColor: ['#0284c7', '#6366f1']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      });
    }
  } catch (err) {
    console.error("Failed loading performance data:", err);
  }
}

// 4. ML Benchmarks & Top Risk Table
async function loadRiskPredictionsData() {
  try {
    const res = await fetch(`${API_BASE}/api/risk/predictions`);
    const data = await res.json();

    // Benchmarks chart
    const mlCtx = document.getElementById('chart-ml-benchmarks');
    if (mlCtx && data.model_benchmarks && data.model_benchmarks.length > 0) {
      new Chart(mlCtx, {
        type: 'bar',
        data: {
          labels: data.model_benchmarks.map(m => m.Model),
          datasets: [
            {
              label: 'ROC-AUC',
              data: data.model_benchmarks.map(m => m.ROC_AUC),
              backgroundColor: '#4f46e5'
            },
            {
              label: 'Accuracy',
              data: data.model_benchmarks.map(m => m.Accuracy),
              backgroundColor: '#0284c7'
            },
            {
              label: 'F1-Score',
              data: data.model_benchmarks.map(m => m.F1_Score),
              backgroundColor: '#10b981'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: { min: 0.70, max: 1.0 }
          }
        }
      });
    }

    // Top at-risk table
    const topTbody = document.getElementById('top-risk-table-body');
    if (topTbody && data.top_at_risk_students) {
      topTbody.innerHTML = "";
      data.top_at_risk_students.forEach(s => {
        const tr = document.createElement('tr');
        tr.className = "hover:bg-slate-50";
        tr.innerHTML = `
          <td class="p-3 font-bold text-slate-800">${s.student_id}</td>
          <td class="p-3 font-bold text-rose-600">${(s.dropout_probability * 100).toFixed(1)}%</td>
          <td class="p-3 font-semibold text-slate-700">${s.annual_grade_avg}</td>
          <td class="p-3 font-semibold text-rose-600">${s.total_units_failed}</td>
          <td class="p-3 text-xs text-slate-500 max-w-xs truncate">${s.target_outcome || 'Academic failure & tuition debt'}</td>
          <td class="p-3 text-right">
            <button onclick="viewStudentModal('${s.student_id}')" class="px-2 py-1 text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200 rounded hover:bg-rose-100">
              Diagnose
            </button>
          </td>
        `;
        topTbody.appendChild(tr);
      });
    }
  } catch (err) {
    console.error("Failed loading risk predictions:", err);
  }
}

// 5. Interventions Catalog
async function loadRecommendationsData() {
  const container = document.getElementById('rec-cards-container');
  if (!container) return;

  const sampleCards = [
    { priority: 'Critical', category: 'Academic Remedial & Tutoring', title: 'Mandatory Intensive Peer Tutoring', desc: 'Weekly 3-hour guided study halls with student department tutors for failed curricular units.', badge: 'bg-rose-100 text-rose-800' },
    { priority: 'Critical', category: 'Tuition & Financial Aid Advisory', title: 'Emergency Financial Aid Restructuring', desc: 'Tuition installment rescheduling request and micro-scholarship consultation to avoid academic holds.', badge: 'bg-rose-100 text-rose-800' },
    { priority: 'High', category: 'Faculty Mentorship & Retention Coaching', title: 'Academic Trajectory Recovery Consultation', desc: '1-on-1 department advisor check-in for steep grade trajectory drop from Sem 1 to Sem 2.', badge: 'bg-amber-100 text-amber-800' },
    { priority: 'Medium', category: 'Attendance & Schedule Advising', title: 'Evening Shift Commute & Study Support', desc: 'Flexible digital lecture recordings and asynchronous study accommodations.', badge: 'bg-blue-100 text-blue-800' },
    { priority: 'Low', category: 'Advanced Career & Research Enrichment', title: 'Undergraduate Research Fellowship', desc: 'Honours society nomination, corporate internship tracks, and faculty lab assistantships.', badge: 'bg-emerald-100 text-emerald-800' }
  ];

  container.innerHTML = sampleCards.map(c => `
    <div class="border border-slate-200 rounded-xl p-5 hover:shadow-md transition-shadow bg-white flex flex-col justify-between">
      <div>
        <div class="flex items-center justify-between mb-3">
          <span class="px-2.5 py-0.5 rounded-full text-xs font-bold uppercase ${c.badge}">${c.priority}</span>
          <span class="text-xs text-slate-400 font-medium">${c.category}</span>
        </div>
        <h5 class="font-bold text-slate-800 text-sm">${c.title}</h5>
        <p class="text-xs text-slate-500 mt-2 leading-relaxed">${c.desc}</p>
      </div>
      <div class="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
        <span>Target: 7-14 Days</span>
        <span class="text-sky-600 font-semibold cursor-pointer hover:underline">Apply Policy &rarr;</span>
      </div>
    </div>
  `).join('');
}

// 6. Student Detail Modal
async function viewStudentModal(studentId) {
  try {
    const res = await fetch(`${API_BASE}/api/students/${studentId}`);
    if (!res.ok) throw new Error("Could not load student profile");
    const s = await res.json();

    document.getElementById('modal-student-id').innerText = `${s.student_id} - ${s.gender}, ${s.age_at_enrollment} yrs`;
    document.getElementById('modal-course-title').innerText = `Course #${s.course_id} | Schedule: ${s.schedule}`;

    const riskBadgeClass = s.risk_tier === "High Risk" ? "bg-rose-100 text-rose-700" : (s.risk_tier === "Medium Risk" ? "bg-amber-100 text-amber-700" : "bg-emerald-100 text-emerald-700");

    const content = `
      <!-- Top Metrics -->
      <div class="grid grid-cols-3 gap-4">
        <div class="p-3 bg-slate-50 rounded-lg text-center border border-slate-100">
          <p class="text-xs text-slate-400">Cumulative GPA</p>
          <p class="text-xl font-bold text-slate-800 mt-0.5">${s.annual_grade_avg} / 20</p>
        </div>
        <div class="p-3 bg-slate-50 rounded-lg text-center border border-slate-100">
          <p class="text-xs text-slate-400">Dropout Probability</p>
          <p class="text-xl font-bold text-rose-600 mt-0.5">${(s.dropout_probability * 100).toFixed(1)}%</p>
        </div>
        <div class="p-3 bg-slate-50 rounded-lg text-center border border-slate-100">
          <p class="text-xs text-slate-400">Retention Tier</p>
          <span class="inline-block mt-1 px-2.5 py-0.5 rounded-full text-xs font-bold ${riskBadgeClass}">
            ${s.risk_tier}
          </span>
        </div>
      </div>

      <!-- Academic Transcript Breakdown -->
      <div class="border border-slate-200 rounded-xl p-4 space-y-3">
        <h5 class="text-xs font-bold text-slate-700 uppercase tracking-wider">Curricular Performance</h5>
        <div class="grid grid-cols-2 gap-4 text-xs">
          <div>
            <p class="text-slate-500">Semester 1 Grade: <span class="font-bold text-slate-800">${s.sem1_grade}</span></p>
            <p class="text-slate-500 mt-1">Units Approved: <span class="font-bold text-slate-800">${s.sem1_units_approved} / ${s.sem1_units_enrolled}</span></p>
          </div>
          <div>
            <p class="text-slate-500">Semester 2 Grade: <span class="font-bold text-slate-800">${s.sem2_grade}</span></p>
            <p class="text-slate-500 mt-1">Units Approved: <span class="font-bold text-slate-800">${s.sem2_units_approved} / ${s.sem2_units_enrolled}</span></p>
          </div>
        </div>
        <div class="border-t border-slate-100 pt-2 text-xs text-slate-600">
          <p><span class="font-semibold text-slate-700">Diagnostic Factors:</span> ${s.primary_risk_factors || 'None identified'}</p>
        </div>
      </div>

      <!-- Prescribed Recommendations -->
      <div class="space-y-3">
        <h5 class="text-xs font-bold text-slate-700 uppercase tracking-wider">Assigned Interventions (${s.recommendations.length})</h5>
        <div class="space-y-2 max-h-48 overflow-y-auto pr-1">
          ${s.recommendations.map(r => `
            <div class="p-3 rounded-lg border border-slate-200 bg-slate-50 text-xs flex items-start justify-between gap-3">
              <div>
                <div class="flex items-center gap-2 mb-1">
                  <span class="font-bold text-sky-800">${r.category}</span>
                  <span class="text-slate-400">•</span>
                  <span class="font-semibold text-amber-700">${r.priority}</span>
                </div>
                <p class="font-medium text-slate-800">${r.recommendation_text}</p>
                <p class="text-slate-500 mt-1">${r.action_plan}</p>
              </div>
              <span class="px-2 py-0.5 rounded text-xs font-semibold ${r.status === 'Completed' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-700'}">
                ${r.status}
              </span>
            </div>
          `).join('')}
        </div>
      </div>
    `;

    document.getElementById('modal-body-content').innerHTML = content;
    document.getElementById('student-modal').classList.remove('hidden');
    document.getElementById('student-modal').classList.add('flex');
    lucide.createIcons();
  } catch (err) {
    console.error("Modal error:", err);
  }
}

function closeStudentModal() {
  document.getElementById('student-modal').classList.add('hidden');
  document.getElementById('student-modal').classList.remove('flex');
}
