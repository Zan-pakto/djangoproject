# UniResolve – Smart Academic Grievance & Student Redressal System

**UniResolve** is an enterprise-grade, student-centric academic grievance management ecosystem engineered with **Python 3**, **Django**, **SQLite**, and **Bootstrap 5**.

Built to replace legacy complaint boxes and repetitive college ticket systems, UniResolve introduces an institutional grievance workflow with **4-tier urgency triage**, **confidential anonymous reporting**, **departmental delegation with SLA target tracking**, **post-resolution student satisfaction ratings**, **printable official A4 grievance dossiers**, and **CSV audit compliance exports**.

---

## 🌟 What Makes UniResolve Unique

| Legacy / Typical College Complaint Systems | UniResolve Modern Ecosystem |
| :--- | :--- |
| Simple open text fields with no priority differentiation | **4-Tier Urgency Matrix** (Low, Medium, High, and Critical with live pulsating indicators) |
| Identity always visible, discouraging sensitive harassment/whistleblower reporting | **Encrypted Anonymous Filing** (student identity protected on student & admin listings) |
| Unassigned tickets with indefinite wait times | **Department Delegation & Target ETA Tracking** with automated overdue warnings |
| One-way communication ending at "Resolved" | **Student Post-Resolution 5-Star Rating & Review Loop** |
| Digital only, difficult to produce for official committee hearings | **Institutional Printable Grievance Dossier (A4 format)** with security seals and audit stamp |
| Manual database inspection for audits | **One-Click CSV Audit Export** for UGC / NAAC grievance redressal accreditation compliance |
| Generic blue Bootstrap tables | **Modern SaaS Glassmorphism UI** with deep Tech Indigo & Emerald palette |

---

## 🚀 Core Features

### 🎓 Student Experience Portal
- **Fast Registration & Identification**: Auto-verified account creation mapped to student registration number, department, and `@uniresolve.edu` institutional identity.
- **Smart Grievance Filing**:
  - 8 Campus Categories (*Academic, Hostel, Mess & Dining, Infrastructure, Transportation, Library, Administration & Accounts, Safety & Campus Life*).
  - 4 Urgency Priority Levels (*Low, Medium, High, Critical*).
  - **Confidential Mode**: Toggle anonymous grievance submission to mask your name and registration number from public and administrative views.
  - Image Evidence Attachment with automated format validation and 5MB size limit.
- **Student Redressal Dashboard**:
  - Live campus notice alerts and turnaround metrics.
  - Urgency indicators with visual pulsing badges for critical grievances.
  - Direct prompt to rate resolved grievances.
- **Personal Grievance Directory**: Filter submissions by status, category, and priority level with instant search.
- **Post-Resolution Feedback & Star Rating**: Rate administrative redressal quality on a 1-to-5 star scale with written feedback upon issue completion.
- **Official Grievance Dossier / Receipt**: One-click printable A4 dossier formatted for submission to grievance committees or official paper records.

### 🛡️ Administrator & Dean Console
- **Executive Analytics Dashboard**:
  - Total, Pending, In Progress, and Resolved grievance metrics.
  - **Critical Grievance Counter** for immediate intervention.
  - **Overdue SLA Warning Metric** tracking tickets exceeding their target resolution date.
  - **Protected Anonymous Grievances Count**.
  - **Average Student Satisfaction Rating** (e.g., 4.9 / 5.0 ⭐) aggregated across all student feedback.
- **Master Grievance Directory**:
  - Live filtering by Status, Category, Priority Level, and Anonymous status.
  - One-click **CSV Compliance Export** generating full audit spreadsheets.
- **Review & Resolution Action Center**:
  - Department / Authority assignment (*IT Cell, Hostel Warden, Maintenance Division, etc.*).
  - Target Resolution Date (ETA) setting.
  - Official student response dispatch.
  - Internal administrative audit remarks.
- **Immutable Audit Trail (`ComplaintHistory`)**: Full historical record logging every status transition, timestamp, and responsible official.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.14 / 3.x, Django 6.x
- **Database**: SQLite3 (relational schema with foreign keys and cascade rules)
- **Frontend**: HTML5, CSS3, Bootstrap 5.3.3, Bootstrap Icons 1.11.3, Custom CSS Variables
- **Imaging**: Pillow for secure photo validation and storage
- **Security**: Django PBKDF2 SHA256 password hashing, CSRF token verification, custom `@student_required` and `@admin_required` RBAC decorators

---

## 📂 Project Architecture

```text
student_complaint_system/
│
├── manage.py                                 # Django CLI utility
├── requirements.txt                          # Project dependencies
├── db.sqlite3                                # SQLite database (seeded with demo data)
├── README.md                                 # Project documentation
│
├── college_complaint_system/                 # Core configuration
│   ├── settings.py                           # App configuration, templates, media, static
│   ├── urls.py                               # Master routing & static/media handlers
│   ├── wsgi.py                               # WSGI web server gateway
│   └── asgi.py                               # ASGI asynchronous gateway
│
├── complaints/                               # UniResolve Application Logic
│   ├── admin.py                              # Django admin configuration & inlines
│   ├── apps.py                               # App registration
│   ├── decorators.py                         # Strict role-based access control (@student_required, @admin_required)
│   ├── forms.py                              # Validated forms (Registration, Login, Complaint, Feedback, Admin Action)
│   ├── models.py                             # UserProfile, Complaint, ComplaintHistory
│   ├── urls.py                               # URL routing for 13 views
│   ├── views.py                              # Function-based views with filtering, CSV export & rating handling
│   ├── tests.py                              # 28 comprehensive automated tests (100% passing)
│   └── management/
│       └── commands/
│           └── setup_demo_data.py            # Idempotent demo data seeder command
│
├── templates/                                # Django Templates
│   ├── base.html                             # Master layout with sidebar & topbar
│   ├── landing.html                          # UniResolve public showcase landing page
│   ├── 400.html, 403.html, 404.html, 500.html# Custom error pages
│   ├── registration/
│   │   ├── login.html                        # Modern sign-in with 1-click test credentials
│   │   └── register.html                     # Student onboarding form
│   └── complaints/
│       ├── student_dashboard.html            # Student dashboard with urgency & notice indicators
│       ├── submit_complaint.html             # Multi-tier grievance submission with anonymity toggle
│       ├── my_complaints.html                # Student grievances list with priority filters
│       ├── complaint_detail.html             # Grievance view with post-resolution star rating form
│       ├── printable_receipt.html            # Institutional A4 printable receipt dossier
│       ├── complaint_history.html            # Complete audit trail & status timeline
│       ├── admin_dashboard.html              # Admin command center with SLA & satisfaction metrics
│       ├── all_complaints.html               # Admin master directory with CSV export & filters
│       └── admin_complaint_detail.html       # Authority assignment, ETA date & resolution form
│
├── static/
│   ├── css/
│   │   └── style.css                         # Tech Indigo modern design system & animations
│   └── js/
│       └── script.js                         # Mobile navigation toggle & client-side validation
│
└── media/                                    # Uploaded grievance photographs
    └── complaints/
```

---

## ⚡ Quick Start & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Apply Database Migrations
```bash
python manage.py migrate
```

### 3. Seed Realistic Demo Data
Populate the database with ready-to-test students, admin accounts, complaints across all priorities, audit trails, and student ratings:
```bash
python manage.py setup_demo_data
```
*(Idempotent: safe to run multiple times without creating duplicates).*

### 4. Run Automated Test Suite
```bash
python manage.py test
```
**All 28 unit and integration tests** verify registration, role access control, priority handling, anonymous identity masking, post-resolution reviews, CSV export, and printable dossier authorization.

### 5. Launch the Development Server
```bash
python manage.py runserver
```
Open your browser and navigate to: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🔑 Demo Access Credentials

### 🛡️ Campus Administrator Console
- **Username**: `admin` *(or email: `admin@uniresolve.edu`)*
- **Password**: `Admin@12345`
- **Admin Dashboard**: [http://127.0.0.1:8000/management/dashboard/](http://127.0.0.1:8000/management/dashboard/)

### 🎓 Sample Student Accounts
All student demo accounts share the password: **`Student@12345`**

| Student Name | Registration No (Username) | Institutional Email | Department |
| :--- | :--- | :--- | :--- |
| **John Doe** | `STU2024001` | `john.doe@uniresolve.edu` | Computer Science & Engineering |
| **Sarah Jenkins** | `STU2024002` | `sarah.jenkins@uniresolve.edu` | Electrical & Electronics Engineering |
| **Rahul Sharma** | `STU2024003` | `rahul.sharma@uniresolve.edu` | Mechanical Engineering |
| **Emily Chen** | `STU2024004` | `emily.chen@uniresolve.edu` | Civil Engineering |
| **Michael Brown** | `STU2024005` | `michael.brown@uniresolve.edu` | Information Technology |

> **Pro-Tip**: Use the **1-Click Quick Autofill** buttons directly on the [Sign In Page](http://127.0.0.1:8000/login/) to instantly log in as Administrator or Student without typing!

---

## 📋 Compliance & Academic Evaluation Highlights

1. **UGC / NAAC Compliance**: Meets Indian Higher Education guidelines for formal digital grievance redressal mechanisms with audit trails.
2. **Whistleblower Protection**: True anonymous reporting safeguarding students raising sensitive safety or ethical concerns.
3. **Accountability & Quality Assurance**: 5-star student rating mechanism allows college leadership to monitor how satisfied students are with department interventions.
4. **Data Portability**: Full CSV audit data export enables easy import into Microsoft Excel, Tableau, or accreditation filings.
