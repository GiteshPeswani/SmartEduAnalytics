"""
SmartEdu Analytics - PDF Walkthrough Generator for 3 Presenters
File: generate_pdf_walkthrough.py
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_PATH = r"d:\bdampr\SmartEduAnalytics\SmartEdu_3_Person_Walkthrough_Guide.pdf"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))
        # Header
        self.drawString(54, 750, "SmartEdu Analytics - 3-Person Technical Walkthrough Script")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        # Footer
        self.line(54, 45, 558, 45)
        self.setFont("Helvetica", 8)
        self.drawString(54, 32, "Subject: Big Data Analytics (BDA) | Academic Evaluation Script")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 32, page_str)
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=60,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#0284c7"),
        spaceAfter=14
    )
    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=12,
        spaceAfter=6
    )
    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#334155"),
        spaceAfter=5
    )
    speech_style = ParagraphStyle(
        'SpeechText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#0f172a")
    )
    code_style = ParagraphStyle(
        'CodeStyle',
        parent=styles['Normal'],
        fontName='Courier-Bold',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0284c7")
    )

    story = []

    # Title Banner
    story.append(Paragraph("SmartEdu Analytics: 3-Person Project Walkthrough Guide", title_style))
    story.append(Paragraph("Complete Practical Demonstration Script & Commands for Big Data Analytics (BDA) Evaluation", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=10))

    # Allocation Overview Table
    role_data = [
        [
            Paragraph("<b>Presenter</b>", body_style),
            Paragraph("<b>Core Focus Area</b>", body_style),
            Paragraph("<b>Platform / Environment</b>", body_style),
            Paragraph("<b>Key Deliverables</b>", body_style)
        ],
        [
            Paragraph("<b>Speaker 1</b>", body_style),
            Paragraph("Project Intro, Preprocessing & HDFS Storage", body_style),
            Paragraph("Cloudera VM (HDFS Terminal & Port 50070)", body_style),
            Paragraph("UCI 697 dataset, /smartedu/ HDFS directory, Block inspection", body_style)
        ],
        [
            Paragraph("<b>Speaker 2</b>", body_style),
            Paragraph("Distributed Computing & Data Warehousing", body_style),
            Paragraph("Cloudera VM (YARN Terminal, Port 8088 & Hive)", body_style),
            Paragraph("Hadoop Streaming MapReduce Job, HiveQL queries, External Tables", body_style)
        ],
        [
            Paragraph("<b>Speaker 3</b>", body_style),
            Paragraph("ML Modeling, Recommendations & Dashboard", body_style),
            Paragraph("Windows Host (FastAPI Port 8000 Web UI)", body_style),
            Paragraph("Gradient Boosting ML (93.06% AUC), Risk Tiers, Roster, Modal, CSV", body_style)
        ]
    ]
    t_roles = Table(role_data, colWidths=[65, 145, 130, 164])
    t_roles.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_roles)
    story.append(Spacer(1, 12))

    # =========================================================================
    # SPEAKER 1 SECTION
    # =========================================================================
    story.append(Paragraph("PART 1: SPEAKER 1 - Project Introduction & HDFS Storage", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceAfter=8))

    story.append(Paragraph("Step 1.1: Project Introduction & Problem Statement", h2_style))
    speech_1_1 = (
        "<b>What to Say:</b><br/>"
        "\"Good morning Ma'am. Our project is SmartEdu Analytics: A Big Data-Driven Student Performance "
        "Analysis and Dropout Risk Prediction System. Higher education institutions face high attrition rates. "
        "Our objective is to ingest a verified dataset of 4,424 students, store it across distributed HDFS, "
        "process parallel aggregations via MapReduce and Hive on Cloudera QuickStart, and finally predict attrition "
        "risks using machine learning. I will demonstrate the Data Preprocessing and HDFS Storage layer.\""
    )
    t_box1 = Table([[Paragraph(speech_1_1, speech_style)]], colWidths=[504])
    t_box1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#38bdf8")),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_box1)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Step 1.2: Navigate to Project in Cloudera Terminal", h2_style))
    story.append(Paragraph("<b>Terminal:</b> Open Cloudera QuickStart VM Terminal and enter:", body_style))
    c1 = "cd /home/cloudera/SmartEduAnalytics"
    t_c1 = Table([[Paragraph(c1, code_style)]], colWidths=[504])
    t_c1.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")), ('LEFTPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(t_c1)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Step 1.3: Demonstrate Distributed HDFS File System (Phase 2)", h2_style))
    speech_1_3 = (
        "<b>What to Say:</b><br/>"
        "\"Ma'am, our cleaned dataset has been transferred to Hadoop Distributed File System (HDFS). "
        "We created an organized namespace partitioned into /smartedu/raw for raw data archives, "
        "/smartedu/processed for sanitized feature vectors, and /smartedu/analytics for job outputs. "
        "Let us inspect the files directly inside HDFS.\""
    )
    t_box2 = Table([[Paragraph(speech_1_3, speech_style)]], colWidths=[504])
    t_box2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")), ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#38bdf8")), ('LEFTPADDING', (0,0), (-1,-1), 8), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6)]))
    story.append(t_box2)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Command to Type:</b>", body_style))
    c2 = "hdfs dfs -ls -R /smartedu"
    t_c2 = Table([[Paragraph(c2, code_style)]], colWidths=[504])
    t_c2.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")), ('LEFTPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(t_c2)
    story.append(Paragraph("<b>Expected Output to Highlight:</b> Point out <code>raw_student_data.csv</code> (1.48 MB) and <code>preprocessed_student_data.csv</code> (1.84 MB) stored in HDFS.", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Step 1.4: Demonstrate HDFS Health & Block Allocation", h2_style))
    story.append(Paragraph("<b>Command to Type:</b>", body_style))
    c3 = "hdfs fsck /smartedu/processed/preprocessed_student_data.csv -files -blocks"
    t_c3 = Table([[Paragraph(c3, code_style)]], colWidths=[504])
    t_c3.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")), ('LEFTPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(t_c3)
    speech_1_4 = (
        "<b>What to Say:</b><br/>"
        "\"As you can see, HDFS reports filesystem status as HEALTHY. The preprocessed dataset is partitioned "
        "into Hadoop default 128 MB blocks with a replication factor of 1 on this cluster.\""
    )
    t_box3 = Table([[Paragraph(speech_1_4, speech_style)]], colWidths=[504])
    t_box3.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")), ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#38bdf8")), ('LEFTPADDING', (0,0), (-1,-1), 8), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6)]))
    story.append(t_box3)
    story.append(Spacer(1, 4))

    story.append(Paragraph("Step 1.5: NameNode Web UI Demonstration", h2_style))
    story.append(Paragraph("Open Firefox browser inside Cloudera VM and navigate to: <b>http://localhost:50070</b>", body_style))
    speech_1_5 = (
        "<b>What to Say:</b><br/>"
        "\"Here is the HDFS NameNode Web Interface. By clicking on Utilities -> Browse the file system and opening "
        "/smartedu/processed, we can visually verify the uploaded files. I will now hand over to Speaker 2 to demonstrate "
        "distributed processing via MapReduce and Hive.\""
    )
    t_box4 = Table([[Paragraph(speech_1_5, speech_style)]], colWidths=[504])
    t_box4.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")), ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#38bdf8")), ('LEFTPADDING', (0,0), (-1,-1), 8), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6)]))
    story.append(t_box4)

    story.append(PageBreak())

    # =========================================================================
    # SPEAKER 2 SECTION
    # =========================================================================
    story.append(Paragraph("PART 2: SPEAKER 2 - Distributed MapReduce & Apache Hive", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceAfter=8))

    story.append(Paragraph("Step 2.1: Distributed Hadoop MapReduce Streaming (Phase 3)", h2_style))
    speech_2_1 = (
        "<b>What to Say:</b><br/>"
        "\"Thank you Speaker 1. Now I will demonstrate distributed computing using Hadoop MapReduce on YARN. "
        "Instead of Java compilation, we implemented 5 MapReduce streaming jobs using Python mappers and reducers. "
        "The Hadoop Streaming utility handles parallel data piping, sorting, and shuffling automatically. "
        "I will now execute Job 1 to calculate overall and course-level student academic averages.\""
    )
    t_box5 = Table([[Paragraph(speech_2_1, speech_style)]], colWidths=[504])
    t_box5.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")), ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#6366f1")), ('LEFTPADDING', (0,0), (-1,-1), 8), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6)]))
    story.append(t_box5)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Command to Type:</b>", body_style))
    c4 = (
        "hdfs dfs -rm -r -f /smartedu/analytics/mapreduce/demo_avg_job 2>/dev/null\n"
        "hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \\\n"
        "  -input /smartedu/processed/preprocessed_student_data.csv \\\n"
        "  -output /smartedu/analytics/mapreduce/demo_avg_job \\\n"
        "  -mapper \"python mapper_average.py\" \\\n"
        "  -reducer \"python reducer_average.py\" \\\n"
        "  -file scripts/phase3/mapper_average.py \\\n"
        "  -file scripts/phase3/reducer_average.py"
    )
    t_c4 = Table([[Paragraph(c4.replace('\n', '<br/>'), code_style)]], colWidths=[504])
    t_c4.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")), ('LEFTPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(t_c4)
    story.append(Paragraph("<b>Execution Progress to Point Out:</b> Show terminal displaying <code>Map 0% -> Map 100% -> Reduce 100%</code>.", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Step 2.2: YARN Web Interface Verification", h2_style))
    story.append(Paragraph("Open Firefox in Cloudera VM at: <b>http://localhost:8088</b>", body_style))
    speech_2_2 = (
        "<b>What to Say:</b><br/>"
        "\"In the YARN ResourceManager UI at port 8088, we see our application has been allocated containers "
        "and completed with state SUCCEEDED. Let us now examine the generated output partitions on HDFS.\""
    )
    t_box6 = Table([[Paragraph(speech_2_2, speech_style)]], colWidths=[504])
    t_box6.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")), ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#6366f1")), ('LEFTPADDING', (0,0), (-1,-1), 8), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6)]))
    story.append(t_box6)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Command to Type:</b>", body_style))
    c5 = "hdfs dfs -cat /smartedu/analytics/mapreduce/demo_avg_job/part-* | head -n 8"
    t_c5 = Table([[Paragraph(c5, code_style)]], colWidths=[504])
    t_c5.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")), ('LEFTPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(t_c5)
    story.append(Paragraph("<b>Expected Output:</b> Tab-delimited aggregated course performance and cumulative average marks (11.53/20).", body_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("Step 2.3: Apache Hive Data Warehousing (Phase 4)", h2_style))
    speech_2_3 = (
        "<b>What to Say:</b><br/>"
        "\"Next, I will demonstrate Phase 4: Apache Hive Data Warehousing. We first initialize the Hive "
        "warehouse schema and external tables mapped directly to our HDFS dataset, then query it using standard HiveQL "
        "without moving the underlying HDFS blocks.\""
    )
    t_box7 = Table([[Paragraph(speech_2_3, speech_style)]], colWidths=[504])
    t_box7.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")), ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#6366f1")), ('LEFTPADDING', (0,0), (-1,-1), 8), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6)]))
    story.append(t_box7)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>1. Initialize Hive Warehouse (Creates database & tables):</b>", body_style))
    c_init = "bash scripts/phase4/create_hive_database.sh"
    t_cinit = Table([[Paragraph(c_init, code_style)]], colWidths=[504])
    t_cinit.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")), ('LEFTPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(t_cinit)
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>2. Interactive Apache Hive CLI Queries (HiveQL):</b>", body_style))
    c6 = (
        "hive\n"
        "USE smartedu;\n"
        "SHOW TABLES;\n"
        "SELECT course_id, COUNT(*) AS student_count, ROUND(AVG(annual_grade_avg), 2) AS avg_gpa\n"
        "FROM students_ext\n"
        "GROUP BY course_id\n"
        "ORDER BY student_count DESC\n"
        "LIMIT 5;\n"
        "exit;"
    )
    t_c6 = Table([[Paragraph(c6.replace('\n', '<br/>'), code_style)]], colWidths=[504])
    t_c6.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")), ('LEFTPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(t_c6)
    speech_2_4 = (
        "<b>What to Say:</b><br/>"
        "\"The Hive query parsed the table, executed a background MapReduce aggregation, and returned the top courses "
        "by enrollment. I will now hand over to Speaker 3 to present our Machine Learning Dropout Risk Prediction model "
        "and the production Web Application Dashboard.\""
    )
    t_box8 = Table([[Paragraph(speech_2_4, speech_style)]], colWidths=[504])
    t_box8.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")), ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#6366f1")), ('LEFTPADDING', (0,0), (-1,-1), 8), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6)]))
    story.append(t_box8)

    story.append(PageBreak())

    # =========================================================================
    # SPEAKER 3 SECTION
    # =========================================================================
    story.append(Paragraph("PART 3: SPEAKER 3 - Machine Learning, Recommendations & Web UI", h1_style))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#94a3b8"), spaceAfter=8))

    story.append(Paragraph("Step 3.1: Machine Learning Dropout Risk Prediction (Phase 8)", h2_style))
    speech_3_1 = (
        "<b>What to Say:</b><br/>"
        "\"Thank you Speaker 2. While Hadoop and Hive provide distributed batch analytics, our objective is proactive "
        "intervention. In Phase 8, we engineered 21 academic and socio-economic predictors and benchmarked 4 algorithms "
        "on an 80/20 stratified split of 4,424 students. Gradient Boosting achieved champion performance with "
        "93.06% ROC-AUC and 88.70% accuracy, outperforming Random Forest, Logistic Regression, and Decision Trees. "
        "Feature importance reveals that accumulated failed course units, semester 2 grades, and tuition payment "
        "are the top 3 attrition drivers.\""
    )
    t_box9 = Table([[Paragraph(speech_3_1, speech_style)]], colWidths=[504])
    t_box9.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")), ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#10b981")), ('LEFTPADDING', (0,0), (-1,-1), 8), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6)]))
    story.append(t_box9)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Step 3.2: Personalized Recommendation Engine (Phase 9)", h2_style))
    speech_3_2 = (
        "<b>What to Say:</b><br/>"
        "\"In Phase 9, we built an automated intervention engine mapping student distress signals to actionable remediation. "
        "It generated 9,952 prioritized action items: 3,792 Critical items for urgent peer tutoring and financial holds, "
        "1,539 High priority trajectory recovery sessions, and 3,393 enrichment recommendations for high-achieving scholars. "
        "All predictions and recommendations are persisted in relational tables.\""
    )
    t_box10 = Table([[Paragraph(speech_3_2, speech_style)]], colWidths=[504])
    t_box10.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")), ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#10b981")), ('LEFTPADDING', (0,0), (-1,-1), 8), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6)]))
    story.append(t_box10)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Step 3.3: Production Web Dashboard Live Demonstration (Phase 10)", h2_style))
    story.append(Paragraph("Open browser on Windows host at: <b>http://127.0.0.1:8000/</b>", body_style))
    speech_3_3 = (
        "<b>What to Say:</b><br/>"
        "\"Here is our production full-stack application built with FastAPI, Tailwind CSS, and Chart.js.<br/>"
        "1. <b>Overview Tab:</b> We see live KPI cards for all 4,424 enrolled students, overall GPA 10.44/20, "
        "and 1,033 students flagged in the High-Risk tier (23.3%). Below are interactive Doughnut and Course Pass-Rate charts.<br/>"
        "2. <b>Student Roster Tab:</b> Let us switch to the Student Directory. It features server-side pagination and real-time filtering.<br/>"
        "3. <b>Search Demonstration:</b> I will search for student 'STD_11688'. Notice their high risk probability of 91.2%. "
        "Clicking 'Profile' opens their complete academic transcript, semester 1 vs semester 2 drop, and 5 assigned interventions.<br/>"
        "4. <b>Export Report:</b> Clicking 'Export Predictions CSV' initiates an instant download of all 4,424 scored records.<br/>"
        "This completes our end-to-end Big Data & AI pipeline from Hadoop HDFS to real-time administrative intelligence.\""
    )
    t_box11 = Table([[Paragraph(speech_3_3, speech_style)]], colWidths=[504])
    t_box11.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")), ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#10b981")), ('LEFTPADDING', (0,0), (-1,-1), 8), ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6)]))
    story.append(t_box11)
    story.append(Spacer(1, 10))

    # Viva Quick Answers Reference Table
    story.append(Paragraph("Key Viva Answers Reference (For All Presenters)", h2_style))
    viva_data = [
        [Paragraph("<b>Question</b>", body_style), Paragraph("<b>1-Sentence Ideal Answer</b>", body_style)],
        [
            Paragraph("Why use HDFS over local disk?", body_style),
            Paragraph("HDFS provides distributed storage with automatic block replication and fault tolerance across nodes.", body_style)
        ],
        [
            Paragraph("Why MapReduce Streaming?", body_style),
            Paragraph("Hadoop Streaming allows standard Unix I/O with Python scripts while YARN handles parallel cluster distribution.", body_style)
        ],
        [
            Paragraph("Why External Table in Hive?", body_style),
            Paragraph("External tables decouple data from schema so dropping the table preserves underlying HDFS files safely.", body_style)
        ],
        [
            Paragraph("Why Gradient Boosting for ML?", body_style),
            Paragraph("It achieved highest ROC-AUC (93.06%) by sequentially correcting weak learner residuals and handling class imbalance.", body_style)
        ]
    ]
    t_viva = Table(viva_data, colWidths=[150, 354])
    t_viva.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_viva)

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Generated PDF walkthrough: {PDF_PATH}")

if __name__ == "__main__":
    build_pdf()
