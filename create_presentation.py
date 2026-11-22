import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_path):
    prs = Presentation()
    # 16:9 Widescreen standard
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Theme Colors
    NAVY_DARK = RGBColor(11, 15, 25)       # #0b0f19
    NAVY_CARD = RGBColor(17, 24, 39)       # #111827
    LIGHT_BG = RGBColor(248, 250, 252)     # #f8fafc
    WHITE = RGBColor(255, 255, 255)
    INDIGO = RGBColor(79, 70, 229)         # #4f46e5
    CYAN = RGBColor(6, 182, 212)           # #06b6d4
    EMERALD = RGBColor(16, 185, 129)       # #10b981
    AMBER = RGBColor(245, 158, 11)         # #f59e0b
    ROSE = RGBColor(239, 68, 68)           # #ef4444
    TEXT_MAIN = RGBColor(15, 23, 42)       # #0f172a
    TEXT_MUTED = RGBColor(100, 116, 139)   # #64748b
    CARD_BG = RGBColor(255, 255, 255)
    BORDER_COLOR = RGBColor(226, 232, 240) # #e2e8f0

    def add_bg(slide, color):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, tag_text, title_text, dark=False):
        # Category Tag Pill
        tag_box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.45), Inches(3.2), Inches(0.38))
        tag_box.fill.solid()
        tag_box.fill.fore_color.rgb = RGBColor(79, 70, 229) if dark else RGBColor(238, 242, 255)
        tag_box.line.color.rgb = RGBColor(99, 102, 241)
        tf_tag = tag_box.text_frame
        tf_tag.vertical_anchor = MSO_ANCHOR.MIDDLE
        p_tag = tf_tag.paragraphs[0]
        p_tag.alignment = PP_ALIGN.CENTER
        p_tag.text = tag_text.upper()
        p_tag.font.size = Pt(9.5)
        p_tag.font.bold = True
        p_tag.font.color.rgb = WHITE if dark else INDIGO

        # Title
        tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.7), Inches(0.75))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = WHITE if dark else TEXT_MAIN

        # Footer watermark
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.05), Inches(11.7), Inches(0.35))
        tf_f = footer_box.text_frame
        p_f = tf_f.paragraphs[0]
        p_f.text = "UniResolve – Smart Academic Grievance & Student Redressal System | Semester VII Project"
        p_f.font.size = Pt(9)
        p_f.font.color.rgb = RGBColor(148, 163, 184) if dark else RGBColor(148, 163, 184)

    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE (Dark Mode)
    # -------------------------------------------------------------
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1, NAVY_DARK)

    # Decorative banner pill
    pill = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(1.1), Inches(4.5), Inches(0.45))
    pill.fill.solid()
    pill.fill.fore_color.rgb = RGBColor(30, 41, 59)
    pill.line.color.rgb = INDIGO
    p_pill = pill.text_frame.paragraphs[0]
    p_pill.text = "🛡️ CAPSTONE / ACADEMIC PROJECT PRESENTATION"
    p_pill.font.size = Pt(10)
    p_pill.font.bold = True
    p_pill.font.color.rgb = CYAN

    # Main Project Title
    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.65), Inches(11.3), Inches(2.2))
    t_frame = t_box.text_frame
    t_frame.word_wrap = True
    p1 = t_frame.paragraphs[0]
    p1.text = "UniResolve"
    p1.font.size = Pt(50)
    p1.font.bold = True
    p1.font.color.rgb = WHITE

    p2 = t_frame.add_paragraph()
    p2.text = "Smart Academic Grievance & Student Redressal System"
    p2.font.size = Pt(24)
    p2.font.bold = True
    p2.font.color.rgb = CYAN

    p3 = t_frame.add_paragraph()
    p3.text = "An institutional web ecosystem for 4-tier urgency grievance triage, confidential anonymous reporting, SLA turnaround tracking, and UGC/NAAC compliance."
    p3.font.size = Pt(13)
    p3.font.color.rgb = RGBColor(148, 163, 184)

    # Info Cards at bottom of Slide 1
    cards_data = [
        ("Technology Stack", "Python 3.14 & Django 6.0\nBootstrap 5.3 & SQLite3"),
        ("Key Innovation", "Whistleblower Anonymity\n4 Urgency Severity Tiers"),
        ("Quality Assurance", "28 Automated Tests (100%)\nZero System Check Warnings")
    ]
    for i, (head, desc) in enumerate(cards_data):
        c = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0 + i * 3.8), Inches(4.6), Inches(3.5), Inches(1.8))
        c.fill.solid()
        c.fill.fore_color.rgb = NAVY_CARD
        c.line.color.rgb = RGBColor(51, 65, 85)
        tf_c = c.text_frame
        tf_c.word_wrap = True
        p_h = tf_c.paragraphs[0]
        p_h.text = head
        p_h.font.size = Pt(13)
        p_h.font.bold = True
        p_h.font.color.rgb = WHITE
        p_d = tf_c.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(11)
        p_d.font.color.rgb = RGBColor(148, 163, 184)

    # -------------------------------------------------------------
    # SLIDE 2: PROBLEM STATEMENT & MOTIVATION
    # -------------------------------------------------------------
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2, LIGHT_BG)
    add_header(s2, "The Challenge", "Problem Statement & Educational Context")

    probs = [
        ("📦 Fragmented Physical Boxes", "Traditional campus suggestion boxes suffer from lost submissions, zero receipt generation, and manual administrative delays with no audit trail."),
        ("⏳ Zero Visibility & Accountability", "Students have no way to verify if their issue was read, which department is handling it, or what the expected turnaround (ETA) date is."),
        ("🤐 Fear of Retaliation", "Reporting sensitive harassment, grading disputes, or ragging issues is avoided by students due to lack of confidential, anonymous submission modes."),
        ("📜 Regulatory Accreditation Gaps", "UGC & AICTE guidelines mandate structured grievance redressal mechanisms with permanent time-stamped history logs for college accreditations.")
    ]

    for i, (title, desc) in enumerate(probs):
        x = Inches(0.8 + (i % 2) * 5.9)
        y = Inches(1.7 + (i // 2) * 2.5)
        card = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.6), Inches(2.2))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11.5)
        p2.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 3: UNIRESOLVE SOLUTION & INNOVATIONS
    # -------------------------------------------------------------
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3, LIGHT_BG)
    add_header(s3, "Core Innovation", "What Sets UniResolve Apart From Generic Systems")

    features = [
        ("🚨 4-Tier Urgency Matrix", "Low (Routine), Medium (Standard), High (Urgent), and Critical (Emergency with animated pulsing alert badges).", INDIGO),
        ("🕵️ Encrypted Anonymous Mode", "Students can check 'Submit Anonymously' to mask identity on public and admin dashboards while preserving logs.", EMERALD),
        ("🏢 Department Delegation & SLA", "Admins route issues to specific authorities (IT, Hostel Warden, Maintenance) with target resolution dates (ETAs).", CYAN),
        ("⭐ 5-Star Resolution Review Loop", "Upon issue resolution, students rate redressal quality (1-5 stars) and submit written feedback.", AMBER),
        ("📄 Printable Official A4 Dossier", "One-click generation of formatted A4 complaint receipts with QR seal and timestamps for official paper hearings.", INDIGO),
        ("📊 1-Click CSV Audit Export", "Administrators can export complete grievance datasets to CSV spreadsheets for NAAC/UGC accreditation compliance.", ROSE)
    ]

    for i, (title, desc, color) in enumerate(features):
        x = Inches(0.8 + (i % 3) * 3.9)
        y = Inches(1.7 + (i // 3) * 2.5)
        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(3.7), Inches(2.2))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(13.5)
        p.font.bold = True
        p.font.color.rgb = color
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 4: SYSTEM ARCHITECTURE & TECH STACK
    # -------------------------------------------------------------
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4, LIGHT_BG)
    add_header(s4, "Engineering", "System Architecture & Technology Stack")

    layers = [
        ("Presentation Layer", "HTML5, CSS3, Bootstrap 5.3.3, Bootstrap Icons 1.11, JavaScript\nResponsive Glassmorphic UI with dynamic color hierarchy", INDIGO),
        ("Application Layer", "Python 3.14, Django 6.0 MVT (Model-View-Template) Architecture\n13 Specialized Views, Custom Forms, and Validations", CYAN),
        ("Security & RBAC Layer", "Custom Role-Based Decorators (@student_required, @admin_required)\nPBKDF2 SHA-256 Password Hashing, CSRF Defense Tokens", EMERALD),
        ("Data & Media Layer", "SQLite3 Relational Database Engine with relational integrity\nPillow Image Processing (5MB size check, format validation)", AMBER)
    ]

    for i, (layer, details, color) in enumerate(layers):
        card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6 + i * 1.3), Inches(11.7), Inches(1.15))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"Layer {i+1}: {layer}"
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = color
        p2 = tf.add_paragraph()
        p2.text = details
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 5: DATABASE SCHEMA & DATA MODELS
    # -------------------------------------------------------------
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5, LIGHT_BG)
    add_header(s5, "Relational Schema", "Database Design & Key Entity Relationships")

    models_info = [
        ("UserProfile Model", "Extends Django auth.User via OneToOneField\n• role: 'Student' or 'Administrator'\n• registration_number: Unique college roll no\n• department & phone_number: Optional metadata\n• Helper properties: is_student, is_administrator", INDIGO),
        ("Complaint Model", "Central grievance entity with unique ID (CMP-YYYYMMDD-XXXX)\n• category: Academic, Hostel, Mess, Infra, etc. (8 choices)\n• priority: Low, Medium, High, Critical\n• is_anonymous: Boolean identity protection\n• assigned_to & expected_resolution_date: SLA fields\n• satisfaction_rating & student_feedback: Review loop", CYAN),
        ("ComplaintHistory Model", "Immutable audit ledger for institutional compliance\n• complaint: ForeignKey to Complaint (CASCADE)\n• previous_status & new_status: State changes\n• timestamp: Automated time stamp\n• updated_by: Attributed admin/student user\n• remarks: Permanent audit justification notes", EMERALD)
    ]

    for i, (m_name, m_desc, col) in enumerate(models_info):
        card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 3.9), Inches(1.6), Inches(3.7), Inches(5.1))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = m_name
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = col
        p2 = tf.add_paragraph()
        p2.text = m_desc
        p2.font.size = Pt(11.5)
        p2.font.color.rgb = TEXT_MAIN

    # -------------------------------------------------------------
    # SLIDE 6: STUDENT EXPERIENCE PORTAL
    # -------------------------------------------------------------
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6, LIGHT_BG)
    add_header(s6, "User Interface", "Student Portal: Features & Workflow")

    student_features = [
        ("1. Streamlined Registration", "Sign up with official student roll number, college email, department, and secure password with verification."),
        ("2. Priority Grievance Submission", "Choose from 8 categories, select urgency tier (Low, Med, High, Critical), upload photos, and toggle Anonymous mode."),
        ("3. Interactive Dashboard", "Real-time counter tiles for Total, Pending, In Progress, and Resolved grievances, plus urgent status notifications."),
        ("4. Personal Directory & Search", "Search personal complaints by ticket ID or title; filter instantly by status, category, and urgency level."),
        ("5. Post-Resolution Rating & Review", "Once resolved by the college, rate the resolution 1 to 5 stars and submit written satisfaction feedback."),
        ("6. Official Dossier Download", "Generate a printable institutional A4 grievance receipt complete with QR verification seal and audit history.")
    ]

    for i, (t, d) in enumerate(student_features):
        x = Inches(0.8 + (i % 2) * 5.9)
        y = Inches(1.6 + (i // 2) * 1.7)
        card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.6), Inches(1.5))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = t
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = INDIGO
        p2 = tf.add_paragraph()
        p2.text = d
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 7: ADMINISTRATOR & DEAN CONSOLE
    # -------------------------------------------------------------
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7, LIGHT_BG)
    add_header(s7, "Administrative Console", "Management Dashboard & Resolution Action Center")

    admin_features = [
        ("📈 Command Center Metrics", "Live analytics counters for Total, Pending, In Progress, and Resolved grievances, plus Critical Count, Overdue SLA alerts, and Average Student Satisfaction (e.g. 4.9/5.0)."),
        ("🔍 Master Complaint Directory", "Comprehensive directory with multi-filter controls (Status, Category, Priority, Anonymity) and full-text keyword search across students and ticket IDs."),
        ("⚡ Review & Resolution Form", "Admins change lifecycle status (Pending → In Progress → Resolved), assign target departments, set expected resolution dates (ETA), and dispatch official responses."),
        ("📥 1-Click CSV Audit Export", "Export full complaints dataset with ticket ID, student info, category, priority, ETA, and satisfaction rating directly into Microsoft Excel / CSV spreadsheets.")
    ]

    for i, (t, d) in enumerate(admin_features):
        x = Inches(0.8 + (i % 2) * 5.9)
        y = Inches(1.7 + (i // 2) * 2.5)
        card = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.6), Inches(2.2))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = t
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = NAVY_DARK
        p2 = tf.add_paragraph()
        p2.text = d
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 8: SECURITY, PRIVACY & COMPLIANCE
    # -------------------------------------------------------------
    s8 = prs.slides.add_slide(blank_layout)
    add_bg(s8, LIGHT_BG)
    add_header(s8, "Governance & Security", "Data Privacy, Access Boundaries & Legal Compliance")

    sec_cards = [
        ("🔐 Strict Role Isolation", "Custom decorators (@student_required and @admin_required) verify user roles at the view level. Students cannot view other students' tickets or access administrative dashboards."),
        ("🛡️ Identity Concealment", "When submitted anonymously, the student's name and roll number are masked across all public listings and admin views, preventing retaliatory action for sensitive reports."),
        ("📜 Immutable Audit Ledger", "Every status change generates a permanent ComplaintHistory record tracking the previous status, new status, timestamp, and responsible user."),
        ("🏛️ Higher Education Compliance", "Directly satisfies UGC (Grievance Redressal Regulations) and NAAC Criterion II & V standards for digital institutional student grievance systems.")
    ]

    for i, (t, d) in enumerate(sec_cards):
        x = Inches(0.8 + (i % 2) * 5.9)
        y = Inches(1.7 + (i // 2) * 2.5)
        card = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.6), Inches(2.2))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = t
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = EMERALD
        p2 = tf.add_paragraph()
        p2.text = d
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 9: AUTOMATED TESTING & VERIFICATION
    # -------------------------------------------------------------
    s9 = prs.slides.add_slide(blank_layout)
    add_bg(s9, LIGHT_BG)
    add_header(s9, "Quality Assurance", "Automated Testing & System Verification")

    # Top Metric Banner
    banner = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.6), Inches(11.7), Inches(1.1))
    banner.fill.solid()
    banner.fill.fore_color.rgb = RGBColor(236, 253, 245)
    banner.line.color.rgb = EMERALD
    tf_b = banner.text_frame
    p_b1 = tf_b.paragraphs[0]
    p_b1.text = "✅ 28 Automated Unit & Integration Tests Passing (100% Success Rate)"
    p_b1.font.size = Pt(16)
    p_b1.font.bold = True
    p_b1.font.color.rgb = RGBColor(4, 120, 87)
    p_b2 = tf_b.add_paragraph()
    p_b2.text = "Ran 28 tests in ~24s • System check identified 0 issues • Zero regression failures"
    p_b2.font.size = Pt(11)
    p_b2.font.color.rgb = RGBColor(4, 120, 87)

    test_groups = [
        ("UserModelAndProfileTests", "Validates student vs admin role properties, registration numbers, and string representations."),
        ("ComplaintModelTests", "Verifies automatic ticket ID generation (CMP-YYYYMMDD-XXXX) and ComplaintHistory relational tracking."),
        ("AuthenticationViewsTests", "Ensures duplicate emails/roll numbers are blocked and password hashing works securely."),
        ("StudentWorkflowTests", "Validates grievance filing, image upload size limits, and access restriction to own complaints only."),
        ("AdminWorkflowTests", "Tests admin status updates, department assignments, official response logging, and history records."),
        ("NewFeaturesIntegrationTests", "Tests 4-tier urgency filtering, anonymous identity masking, post-resolution reviews, CSV export, and receipt permissions.")
    ]

    for i, (tg, td) in enumerate(test_groups):
        x = Inches(0.8 + (i % 3) * 3.9)
        y = Inches(3.0 + (i // 3) * 1.9)
        card = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(3.7), Inches(1.7))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = tg
        p.font.size = Pt(12.5)
        p.font.bold = True
        p.font.color.rgb = TEXT_MAIN
        p2 = tf.add_paragraph()
        p2.text = td
        p2.font.size = Pt(10)
        p2.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 10: DEMO CREDENTIALS & EVALUATION SHORTCUTS
    # -------------------------------------------------------------
    s10 = prs.slides.add_slide(blank_layout)
    add_bg(s10, LIGHT_BG)
    add_header(s10, "Evaluation Guide", "Live Demonstration Credentials & Shortcuts")

    cred_cards = [
        ("🛡️ Administrator Account", "Access the Dean / Management Console\n• Username: admin\n• Email: admin@uniresolve.edu\n• Password: Admin@12345\n• Dashboard: /management/dashboard/\nCapabilities: Update complaint status, assign departments, set target ETAs, review anonymous reports, export CSV.", ROSE),
        ("🎓 Student Account 1 (John Doe)", "Computer Science & Engineering\n• Username / Reg No: STU2024001\n• Email: john.doe@uniresolve.edu\n• Password: Student@12345\n• Dashboard: /student/dashboard/\nCapabilities: File urgent grievances, attach evidence, submit 5-star resolution ratings, print official A4 receipts.", INDIGO),
        ("🎓 Student Account 2 (Sarah Jenkins)", "Electrical & Electronics Engineering\n• Username / Reg No: STU2024002\n• Email: sarah.jenkins@uniresolve.edu\n• Password: Student@12345\n• Dashboard: /student/dashboard/\nCapabilities: Track existing hostel & academic complaints, view real-time admin feedback and audit logs.", CYAN)
    ]

    for i, (title, desc, color) in enumerate(cred_cards):
        card = s10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i * 3.9), Inches(1.6), Inches(3.7), Inches(5.1))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = color
        p2 = tf.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(11.5)
        p2.font.color.rgb = TEXT_MAIN

    # -------------------------------------------------------------
    # SLIDE 11: FUTURE ENHANCEMENTS & ROADMAP
    # -------------------------------------------------------------
    s11 = prs.slides.add_slide(blank_layout)
    add_bg(s11, LIGHT_BG)
    add_header(s11, "Roadmap", "Future Enhancements & Scalability")

    roadmap = [
        ("📱 Real-Time Notifications", "Integrating Twilio and SendGrid for automated SMS, WhatsApp, and email alerts on every status progression."),
        ("🤖 AI Ticket Classification", "Using LLMs for automatic ticket duplicate detection, urgency verification, and automated routing to department heads."),
        ("📲 Native Mobile App", "Building cross-platform Flutter/React Native mobile applications for offline complaint drafting and push notifications."),
        ("🏢 Multi-College SaaS", "Extending the single-college architecture into a multi-tenant SaaS platform serving multiple colleges in a university network.")
    ]

    for i, (t, d) in enumerate(roadmap):
        x = Inches(0.8 + (i % 2) * 5.9)
        y = Inches(1.7 + (i // 2) * 2.5)
        card = s11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.6), Inches(2.2))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_COLOR
        tf = card.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = t
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = INDIGO
        p2 = tf.add_paragraph()
        p2.text = d
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_MUTED

    # -------------------------------------------------------------
    # SLIDE 12: CONCLUSION & QUESTIONS (Dark Mode)
    # -------------------------------------------------------------
    s12 = prs.slides.add_slide(blank_layout)
    add_bg(s12, NAVY_DARK)

    # Center Box
    c_box = s12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(2.0), Inches(1.5), Inches(9.333), Inches(4.5))
    c_box.fill.solid()
    c_box.fill.fore_color.rgb = NAVY_CARD
    c_box.line.color.rgb = INDIGO
    tf_end = c_box.text_frame
    tf_end.word_wrap = True

    p_end1 = tf_end.paragraphs[0]
    p_end1.alignment = PP_ALIGN.CENTER
    p_end1.text = "Thank You!"
    p_end1.font.size = Pt(44)
    p_end1.font.bold = True
    p_end1.font.color.rgb = WHITE

    p_end2 = tf_end.add_paragraph()
    p_end2.alignment = PP_ALIGN.CENTER
    p_end2.text = "UniResolve – Smart Academic Grievance & Student Redressal System"
    p_end2.font.size = Pt(20)
    p_end2.font.bold = True
    p_end2.font.color.rgb = CYAN

    p_end3 = tf_end.add_paragraph()
    p_end3.alignment = PP_ALIGN.CENTER
    p_end3.text = "\nProject Code Repository:\nhttps://github.com/Zan-pakto/djangoproject.git\n\nQuestions & Viva Evaluation"
    p_end3.font.size = Pt(14)
    p_end3.font.color.rgb = RGBColor(148, 163, 184)

    # Save presentation
    prs.save(output_path)
    print(f"Presentation successfully saved to: {output_path}")

if __name__ == "__main__":
    out_file = r"D:\sem7java\student_complaint_system\UniResolve_Project_Presentation.pptx"
    create_deck(out_file)
