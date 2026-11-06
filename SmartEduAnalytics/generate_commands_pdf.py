"""
SmartEdu Analytics - Commands Cheatsheet Generator for 3 Presenters
File: generate_commands_pdf.py
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfgen import canvas

PDF_PATH = r"d:\bdampr\SmartEduAnalytics\SmartEdu_Commands_Cheatsheet.pdf"

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
        self.drawString(54, 750, "SmartEdu Analytics - Live Execution Commands Cheatsheet (3 Presenters)")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        self.line(54, 45, 558, 45)
        self.setFont("Helvetica", 8)
        self.drawString(54, 32, "Big Data Analytics (BDA) Lab Practical Demonstration")
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

    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=18, leading=22,
        textColor=colors.HexColor("#0f172a"), spaceAfter=2
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle', parent=styles['Normal'],
        fontName='Helvetica', fontSize=10, leading=14,
        textColor=colors.HexColor("#0284c7"), spaceAfter=8
    )
    speaker_header = ParagraphStyle(
        'SpeakerHead', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=11, leading=15,
        textColor=colors.HexColor("#0f172a"), spaceBefore=8, spaceAfter=3
    )
    cmd_title = ParagraphStyle(
        'CmdTitle', parent=styles['Normal'],
        fontName='Helvetica-Bold', fontSize=8.5, leading=11,
        textColor=colors.HexColor("#1e293b"), spaceBefore=3, spaceAfter=2
    )
    code_style = ParagraphStyle(
        'CodeStyle', parent=styles['Normal'],
        fontName='Courier-Bold', fontSize=7.5, leading=10,
        textColor=colors.HexColor("#0284c7")
    )
    body_style = ParagraphStyle(
        'BodyText', parent=styles['Normal'],
        fontName='Helvetica', fontSize=8, leading=11,
        textColor=colors.HexColor("#475569")
    )

    story = []

    story.append(Paragraph("SmartEdu Analytics: Live Commands Cheatsheet", title_style))
    story.append(Paragraph("Step-by-step verified terminal commands for each presenter during evaluation", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0284c7"), spaceAfter=6))

    # ================= ONE-TIME SETUP =================
    story.append(Paragraph("0. ONE-TIME CLOUDERA VM SETUP (Run Once Before Presentation)", speaker_header))
    setup_cmd = (
        "cd ~\n"
        "wget -O smartedu.tar.gz http://192.168.56.1:8889/smartedu.tar.gz || wget -O smartedu.tar.gz http://10.0.2.2:8889/smartedu.tar.gz\n"
        "tar -xzvf smartedu.tar.gz -C ~\n"
        "cd ~/SmartEduAnalytics\n"
        "chmod +x scripts/phase2/*.sh scripts/phase3/*.sh scripts/phase3/*.py scripts/phase4/*.sh run_all_cloudera.sh"
    )
    t_box = Table([[Paragraph(setup_cmd.replace('\n', '<br/>'), code_style)]], colWidths=[504])
    t_box.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")), ('LEFTPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(t_box)
    story.append(Spacer(1, 4))

    # ================= SPEAKER 1 =================
    story.append(Paragraph("SPEAKER 1: HDFS Storage & Health Inspection (Cloudera VM Terminal)", speaker_header))
    story.append(Paragraph("<b>Terminal Environment:</b> Cloudera QuickStart VM 5.13.0 (User: <code>cloudera</code>)", body_style))
    
    s1_cmds = [
        ("1. Navigate to Project Directory:", "cd /home/cloudera/SmartEduAnalytics"),
        ("2. Ingest Dataset into HDFS:", "bash scripts/phase2/upload_dataset_to_hdfs.sh . -f"),
        ("3. List All HDFS Directories & Files Recursively:", "hdfs dfs -ls -R /smartedu"),
        ("4. Verify HDFS Health & 128 MB Block Allocation:", "hdfs fsck /smartedu/processed/preprocessed_student_data.csv -files -blocks"),
        ("5. Preview First 5 Rows of HDFS Preprocessed Data:", "hdfs dfs -cat /smartedu/processed/preprocessed_student_data.csv | head -n 5"),
        ("6. Open NameNode Web Interface in Browser:", "Firefox URL: http://localhost:50070 (Utilities -> Browse the file system -> /smartedu/processed)")
    ]

    for title, cmd in s1_cmds:
        story.append(Paragraph(f"<b>{title}</b>", cmd_title))
        t_box = Table([[Paragraph(cmd.replace('\n', '<br/>'), code_style)]], colWidths=[504])
        t_box.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")), ('LEFTPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
        story.append(t_box)
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 4))

    # ================= SPEAKER 2 =================
    story.append(Paragraph("SPEAKER 2: MapReduce Streaming & Apache Hive (Cloudera VM Terminal)", speaker_header))
    story.append(Paragraph("<b>Terminal Environment:</b> Cloudera QuickStart VM (Hadoop 2.6.0, YARN, Hive 1.1.0)", body_style))

    s2_cmds = [
        (
            "1. Execute Distributed MapReduce Job (Fail-Safe with auto-clean):",
            "hdfs dfs -rm -r -f /smartedu/analytics/mapreduce/demo_avg_job 2>/dev/null\n"
            "hadoop jar /usr/lib/hadoop-mapreduce/hadoop-streaming.jar \\\n"
            "  -input /smartedu/processed/preprocessed_student_data.csv \\\n"
            "  -output /smartedu/analytics/mapreduce/demo_avg_job \\\n"
            "  -mapper \"python mapper_average.py\" \\\n"
            "  -reducer \"python reducer_average.py\" \\\n"
            "  -file scripts/phase3/mapper_average.py \\\n"
            "  -file scripts/phase3/reducer_average.py"
        ),
        ("2. View YARN ResourceManager UI (Shows SUCCEEDED status):", "Firefox URL: http://localhost:8088"),
        ("3. Read MapReduce Output Partitions from HDFS:", "hdfs dfs -cat /smartedu/analytics/mapreduce/demo_avg_job/part-* | head -n 10"),
        ("4. Initialize Hive Data Warehouse Schema:", "bash scripts/phase4/create_hive_database.sh"),
        (
            "5. Interactive Apache Hive CLI Queries (HiveQL):",
            "hive\n"
            "USE smartedu;\n"
            "SHOW TABLES;\n"
            "DESCRIBE students_ext;\n"
            "SELECT course_id, COUNT(*) AS total_students, ROUND(AVG(annual_grade_avg), 2) AS avg_gpa FROM students_ext GROUP BY course_id ORDER BY total_students DESC LIMIT 5;\n"
            "exit;"
        )
    ]

    for title, cmd in s2_cmds:
        story.append(Paragraph(f"<b>{title}</b>", cmd_title))
        t_box = Table([[Paragraph(cmd.replace('\n', '<br/>'), code_style)]], colWidths=[504])
        t_box.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")), ('LEFTPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
        story.append(t_box)
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 4))

    # ================= SPEAKER 3 =================
    story.append(Paragraph("SPEAKER 3: Web Dashboard & System Integration (Windows Host)", speaker_header))
    story.append(Paragraph("<b>Environment:</b> Windows PowerShell Terminal & Web Browser", body_style))

    s3_cmds = [
        ("1. Launch FastAPI Server & Web Application:", "cd d:\\bdampr\\SmartEduAnalytics\nd:\\bdampr\\.venv\\Scripts\\python.exe run_all.py --server-only"),
        ("2. Open Interactive Web Dashboard in Browser:", "Browser URL: http://127.0.0.1:8000/  (Admin: admin / smartedu2026)"),
        ("3. Walkthrough Sequence in Dashboard:", 
         "- Overview Tab: Point to 4,424 Total Students, 10.44 GPA, 1,033 High Risk (23.3%), and Doughnut Chart\n"
         "- Student Roster Tab: Search 'STD_11688' -> Click 'Profile' modal to show Semester 1 vs 2 grades & interventions\n"
         "- Dropout Risk ML Tab: Point to Gradient Boosting champion benchmark (93.06% ROC-AUC, 88.70% Acc)\n"
         "- Top Header: Click 'Export Predictions CSV' to download complete scored dataset"),
        ("4. Automated Backend API Verification Suite:", "d:\\bdampr\\.venv\\Scripts\\python.exe phase10_dashboard\\backend\\test_api.py")
    ]

    for title, cmd in s3_cmds:
        story.append(Paragraph(f"<b>{title}</b>", cmd_title))
        t_box = Table([[Paragraph(cmd.replace('\n', '<br/>'), code_style)]], colWidths=[504])
        t_box.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0f172a")), ('LEFTPADDING', (0,0), (-1,-1), 6), ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
        story.append(t_box)
        story.append(Spacer(1, 2))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] Generated Commands PDF: {PDF_PATH}")

if __name__ == "__main__":
    build_pdf()
