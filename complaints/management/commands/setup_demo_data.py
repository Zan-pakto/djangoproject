import os
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from PIL import Image, ImageDraw
from complaints.models import UserProfile, Complaint, ComplaintHistory


def generate_sample_images():
    """Generates sample evidence images on disk if they do not exist."""
    media_dir = os.path.join(settings.MEDIA_ROOT, 'complaints', '2026', '11')
    os.makedirs(media_dir, exist_ok=True)

    samples = [
        ('ac_unit_fault.jpg', (37, 99, 235), 'CAMPUS FACILITIES LOG\nRoom 204 Air Conditioning Unit\nError Code: E4 - Compressor Relay Failure'),
        ('projector_failure.jpg', (220, 38, 38), 'CAMPUS AV HARDWARE FAILURE\nSeminar Hall B Projector\nHDMI Signal Overheat & Power Cutoff'),
        ('water_cooler_leak.jpg', (13, 148, 136), 'CAMPUS FACILITIES REPORT\nMechanical Workshop 2 Cooler\nUV & Sediment Filter Overdue Replacement'),
        ('library_shortage.jpg', (124, 58, 237), 'CENTRAL LIBRARY LOG\nReserve Section Shelf C-4\nTextbook Shortage for Semester 5')
    ]

    for filename, bg_color, text in samples:
        filepath = os.path.join(media_dir, filename)
        if not os.path.exists(filepath):
            img = Image.new('RGB', (800, 480), color=bg_color)
            draw = ImageDraw.Draw(img)
            draw.rectangle([25, 25, 775, 455], outline=(255, 255, 255), width=3)
            draw.text((60, 180), text, fill=(255, 255, 255))
            img.save(filepath, 'JPEG', quality=90)


class Command(BaseCommand):
    help = "Populate database with sample students, administrator, complaints, evidence images, and audit history."

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-user',
            type=str,
            default='admin',
            help='Admin username (default: admin)'
        )
        parser.add_argument(
            '--admin-pass',
            type=str,
            default='Admin@12345',
            help='Admin password (default: Admin@12345)'
        )
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@uniresolve.edu',
            help='Admin email (default: admin@uniresolve.edu)'
        )
        parser.add_argument(
            '--student-pass',
            type=str,
            default='Student@12345',
            help='Password for demo students (default: Student@12345)'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("=== Setting up UniResolve Demo Data ==="))

        # Ensure sample images are generated
        generate_sample_images()

        admin_username = options['admin_user']
        admin_password = options['admin_pass']
        admin_email = options['admin_email']
        student_password = options['student_pass']

        # 1. Create or retrieve Administrator
        admin_user, admin_created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                'email': admin_email,
                'first_name': 'Campus',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if admin_created:
            admin_user.set_password(admin_password)
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f"[+] Created Administrator account: {admin_username}"))
        else:
            self.stdout.write(self.style.WARNING(f"[-] Administrator account '{admin_username}' already exists. Preserving."))

        # Profile for Administrator
        UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'role': UserProfile.ROLE_ADMIN,
                'registration_number': 'ADMIN-001',
                'department': 'Dean of Student Affairs',
                'phone_number': '+91 98000 11111'
            }
        )

        # 2. Sample Students Data
        sample_students_data = [
            {
                'username': 'STU2024001',
                'email': 'john.doe@uniresolve.edu',
                'first_name': 'John',
                'last_name': 'Doe',
                'reg_no': 'STU2024001',
                'dept': 'Computer Science & Engineering',
                'phone': '+91 98765 43210'
            },
            {
                'username': 'STU2024002',
                'email': 'sarah.jenkins@uniresolve.edu',
                'first_name': 'Sarah',
                'last_name': 'Jenkins',
                'reg_no': 'STU2024002',
                'dept': 'Electrical & Electronics Engineering',
                'phone': '+91 98765 43211'
            },
            {
                'username': 'STU2024003',
                'email': 'rahul.sharma@uniresolve.edu',
                'first_name': 'Rahul',
                'last_name': 'Sharma',
                'reg_no': 'STU2024003',
                'dept': 'Mechanical Engineering',
                'phone': '+91 98765 43212'
            },
            {
                'username': 'STU2024004',
                'email': 'emily.chen@uniresolve.edu',
                'first_name': 'Emily',
                'last_name': 'Chen',
                'reg_no': 'STU2024004',
                'dept': 'Civil Engineering',
                'phone': '+91 98765 43213'
            },
            {
                'username': 'STU2024005',
                'email': 'michael.brown@uniresolve.edu',
                'first_name': 'Michael',
                'last_name': 'Brown',
                'reg_no': 'STU2024005',
                'dept': 'Information Technology',
                'phone': '+91 98765 43214'
            },
        ]

        created_students = {}
        for sdata in sample_students_data:
            s_user, s_created = User.objects.get_or_create(
                username=sdata['username'],
                defaults={
                    'email': sdata['email'],
                    'first_name': sdata['first_name'],
                    'last_name': sdata['last_name'],
                }
            )
            if s_created:
                s_user.set_password(student_password)
                s_user.save()
                self.stdout.write(self.style.SUCCESS(f"[+] Created Student: {sdata['first_name']} {sdata['last_name']} ({sdata['reg_no']})"))
            else:
                self.stdout.write(self.style.WARNING(f"[-] Student '{sdata['reg_no']}' already exists. Preserving."))

            UserProfile.objects.get_or_create(
                user=s_user,
                defaults={
                    'role': UserProfile.ROLE_STUDENT,
                    'registration_number': sdata['reg_no'],
                    'department': sdata['dept'],
                    'phone_number': sdata['phone']
                }
            )
            created_students[sdata['reg_no']] = s_user

        # 3. Sample Complaints Data
        now = timezone.now()
        sample_complaints = [
            {
                'student_reg': 'STU2024001',
                'title': 'Air Conditioning malfunction in Computer Lab 3',
                'category': Complaint.CATEGORY_INFRASTRUCTURE,
                'priority': Complaint.PRIORITY_CRITICAL,
                'is_anonymous': False,
                'assigned_to': 'Campus Facilities & HVAC Division',
                'expected_resolution_date': (now - timedelta(days=1)).date(),
                'satisfaction_rating': 5,
                'student_feedback': 'Technician replaced compressor promptly. Room temperature is now comfortable for practicals.',
                'description': 'The two central AC units in Computer Lab 3 (Block B, 2nd floor) are blowing warm air. During afternoon programming practicals, the lab becomes uncomfortably hot and workstations risk overheating.',
                'status': Complaint.STATUS_RESOLVED,
                'image': 'complaints/2026/11/ac_unit_fault.jpg',
                'admin_response': 'HVAC maintenance inspected the refrigerant levels and replaced the faulty compressor relay on Monday. Both AC units are now operating at optimal 21C.',
                'history': [
                    {'from': 'New', 'to': Complaint.STATUS_PENDING, 'by': 'STU2024001', 'remarks': 'Initial grievance filed by student.'},
                    {'from': Complaint.STATUS_PENDING, 'to': Complaint.STATUS_IN_PROGRESS, 'by': 'admin', 'remarks': 'Assigned work order #HVAC-882 to facilities engineering.'},
                    {'from': Complaint.STATUS_IN_PROGRESS, 'to': Complaint.STATUS_RESOLVED, 'by': 'admin', 'remarks': 'Compressor relay replaced. Cooling verified by lab technician.'},
                ]
            },
            {
                'student_reg': 'STU2024001',
                'title': 'Elective Course timetable collision for Sem 6',
                'category': Complaint.CATEGORY_ACADEMIC,
                'priority': Complaint.PRIORITY_HIGH,
                'is_anonymous': False,
                'assigned_to': 'Dean Academic Affairs',
                'expected_resolution_date': (now + timedelta(days=3)).date(),
                'satisfaction_rating': None,
                'student_feedback': '',
                'description': 'Deep Learning (CS601) and Cloud Computing (CS604) have both been scheduled in Slot E on Wednesday afternoon. Many CS students need both courses.',
                'status': Complaint.STATUS_IN_PROGRESS,
                'image': None,
                'admin_response': 'Academic council has reviewed the slot clash. We are adjusting Slot E timings with Department HOD. Revised timetable will be published by Thursday.',
                'history': [
                    {'from': 'New', 'to': Complaint.STATUS_PENDING, 'by': 'STU2024001', 'remarks': 'Initial grievance filed by student.'},
                    {'from': Complaint.STATUS_PENDING, 'to': Complaint.STATUS_IN_PROGRESS, 'by': 'admin', 'remarks': 'Discussed with Academic Dean and CS HOD.'},
                ]
            },
            {
                'student_reg': 'STU2024002',
                'title': 'Wi-Fi access point failure in Girls Hostel Block C',
                'category': Complaint.CATEGORY_HOSTEL,
                'priority': Complaint.PRIORITY_HIGH,
                'is_anonymous': False,
                'assigned_to': 'IT & Network Operations Center',
                'expected_resolution_date': (now - timedelta(days=2)).date(),
                'satisfaction_rating': 5,
                'student_feedback': 'Wi-Fi speed is restored and connection is stable. Thank you for fixing before exams!',
                'description': 'Wi-Fi router on the 3rd floor corridor of Hostel Block C has been stuck in a reboot loop since Friday evening. Over 40 students are unable to submit online assignments.',
                'status': Complaint.STATUS_RESOLVED,
                'image': None,
                'admin_response': 'Campus Network Operations Team replaced the faulty Gigabit PoE injector and rebooted the firmware. High-speed signal is restored across all 3rd floor rooms.',
                'history': [
                    {'from': 'New', 'to': Complaint.STATUS_PENDING, 'by': 'STU2024002', 'remarks': 'Complaint logged by student.'},
                    {'from': Complaint.STATUS_PENDING, 'to': Complaint.STATUS_IN_PROGRESS, 'by': 'admin', 'remarks': 'Network admin dispatched to Block C for hardware diagnostics.'},
                    {'from': Complaint.STATUS_IN_PROGRESS, 'to': Complaint.STATUS_RESOLVED, 'by': 'admin', 'remarks': 'PoE injector replaced and signal integrity verified.'},
                ]
            },
            {
                'student_reg': 'STU2024002',
                'title': 'Delay in publishing Mid-Semester Electrical Machines marks',
                'category': Complaint.CATEGORY_ACADEMIC,
                'priority': Complaint.PRIORITY_MEDIUM,
                'is_anonymous': True,
                'assigned_to': 'Examination Evaluation Cell',
                'expected_resolution_date': (now + timedelta(days=5)).date(),
                'satisfaction_rating': None,
                'student_feedback': '',
                'description': 'The mid-semester evaluation scores for EE302 Electrical Machines have not been uploaded to the student portal despite the 3-week completion deadline.',
                'status': Complaint.STATUS_PENDING,
                'image': None,
                'admin_response': '',
                'history': [
                    {'from': 'New', 'to': Complaint.STATUS_PENDING, 'by': 'STU2024002', 'remarks': 'Grievance submitted by student [Anonymous].'},
                ]
            },
            {
                'student_reg': 'STU2024003',
                'title': 'Water cooler filter replacement needed on Mechanical Block 1st Floor',
                'category': Complaint.CATEGORY_INFRASTRUCTURE,
                'priority': Complaint.PRIORITY_HIGH,
                'is_anonymous': False,
                'assigned_to': 'Campus Estate & Water Maintenance',
                'expected_resolution_date': (now + timedelta(days=1)).date(),
                'satisfaction_rating': None,
                'student_feedback': '',
                'description': 'The drinking water cooler near Workshop 2 has yellow-tinted water and foul odor. The UV filter indicator light has turned red indicating replacement overdue.',
                'status': Complaint.STATUS_IN_PROGRESS,
                'image': 'complaints/2026/11/water_cooler_leak.jpg',
                'admin_response': 'Plumbing contractor has cordoned off the cooler and temporary mineral water jars have been placed. New RO membrane and sediment filters are being installed today.',
                'history': [
                    {'from': 'New', 'to': Complaint.STATUS_PENDING, 'by': 'STU2024003', 'remarks': 'Grievance submitted.'},
                    {'from': Complaint.STATUS_PENDING, 'to': Complaint.STATUS_IN_PROGRESS, 'by': 'admin', 'remarks': 'Water supply disconnected for safety. Filter replacement in progress.'},
                ]
            },
            {
                'student_reg': 'STU2024003',
                'title': 'Food hygiene issues in Central Mess dinner counter',
                'category': Complaint.CATEGORY_MESS,
                'priority': Complaint.PRIORITY_CRITICAL,
                'is_anonymous': True,
                'assigned_to': 'Hostel Mess & Hygiene Oversight Committee',
                'expected_resolution_date': (now - timedelta(days=1)).date(),
                'satisfaction_rating': 4,
                'student_feedback': 'Mess manager met student committee and kitchen sanitation improved noticeably.',
                'description': 'On Saturday evening, the vegetable curry served at Central Mess counter 2 was stale and had an unhygienic odor. Several students complained to the mess supervisor.',
                'status': Complaint.STATUS_RESOLVED,
                'image': None,
                'admin_response': 'Mess committee conducted an unannounced inspection with the campus health officer. The catering vendor has been issued an official warning and penalized per tender terms.',
                'history': [
                    {'from': 'New', 'to': Complaint.STATUS_PENDING, 'by': 'STU2024003', 'remarks': 'Complaint filed.'},
                    {'from': Complaint.STATUS_PENDING, 'to': Complaint.STATUS_IN_PROGRESS, 'by': 'admin', 'remarks': 'Emergency mess committee convened.'},
                    {'from': Complaint.STATUS_IN_PROGRESS, 'to': Complaint.STATUS_RESOLVED, 'by': 'admin', 'remarks': 'Vendor penalized and kitchen sanitation protocols reinforced.'},
                ]
            },
            {
                'student_reg': 'STU2024004',
                'title': 'Shortage of standard reference books for Structural Analysis',
                'category': Complaint.CATEGORY_LIBRARY,
                'priority': Complaint.PRIORITY_LOW,
                'is_anonymous': False,
                'assigned_to': 'Central Library Board',
                'expected_resolution_date': (now + timedelta(days=4)).date(),
                'satisfaction_rating': None,
                'student_feedback': '',
                'description': 'Only 3 copies of "Structural Analysis" by R.C. Hibbeler are available in the Central Library reserve section for a batch of 85 students. We request additional copies or e-book licenses.',
                'status': Complaint.STATUS_IN_PROGRESS,
                'image': 'complaints/2026/11/library_shortage.jpg',
                'admin_response': 'Chief Librarian has placed purchase order #LIB-2026-44 for 10 additional hard copies and activated campus-wide Springer digital access.',
                'history': [
                    {'from': 'New', 'to': Complaint.STATUS_PENDING, 'by': 'STU2024004', 'remarks': 'Grievance submitted.'},
                    {'from': Complaint.STATUS_PENDING, 'to': Complaint.STATUS_IN_PROGRESS, 'by': 'admin', 'remarks': 'Order placed with university bookstore.'},
                ]
            },
            {
                'student_reg': 'STU2024004',
                'title': 'College Bus Route 7 arriving 30 minutes late consistently',
                'category': Complaint.CATEGORY_TRANSPORT,
                'priority': Complaint.PRIORITY_MEDIUM,
                'is_anonymous': False,
                'assigned_to': 'Transport & Fleet Operations',
                'expected_resolution_date': (now - timedelta(days=3)).date(),
                'satisfaction_rating': 5,
                'student_feedback': 'Bus route revised through bypass road. Timely arrival restored!',
                'description': 'Bus #7 from South Metro Station to campus arrives 25-35 minutes late every morning due to improper route planning, causing students to miss 8:30 AM lectures.',
                'status': Complaint.STATUS_RESOLVED,
                'image': None,
                'admin_response': 'Transport supervisor rerouted Bus #7 through the newly opened Eastern Bypass starting Monday. Departure time adjusted to 7:45 AM. Bus now arrives by 8:20 AM.',
                'history': [
                    {'from': 'New', 'to': Complaint.STATUS_PENDING, 'by': 'STU2024004', 'remarks': 'Grievance submitted.'},
                    {'from': Complaint.STATUS_PENDING, 'to': Complaint.STATUS_IN_PROGRESS, 'by': 'admin', 'remarks': 'Transport manager analyzing GPS logs of Route 7.'},
                    {'from': Complaint.STATUS_IN_PROGRESS, 'to': Complaint.STATUS_RESOLVED, 'by': 'admin', 'remarks': 'Route revised through Eastern Bypass; schedule restored.'},
                ]
            },
            {
                'student_reg': 'STU2024005',
                'title': 'Evening campus shuttle frequency insufficient between 6 PM to 8 PM',
                'category': Complaint.CATEGORY_TRANSPORT,
                'priority': Complaint.PRIORITY_LOW,
                'is_anonymous': False,
                'assigned_to': 'Campus Transport Section',
                'expected_resolution_date': (now + timedelta(days=2)).date(),
                'satisfaction_rating': None,
                'student_feedback': '',
                'description': 'Students leaving laboratories and research centers after 6:30 PM face severe crowding and long waits for the internal campus shuttle to the main gate.',
                'status': Complaint.STATUS_PENDING,
                'image': None,
                'admin_response': '',
                'history': [
                    {'from': 'New', 'to': Complaint.STATUS_PENDING, 'by': 'STU2024005', 'remarks': 'Grievance submitted.'},
                ]
            },
            {
                'student_reg': 'STU2024005',
                'title': 'Damaged projector in Seminar Hall B',
                'category': Complaint.CATEGORY_INFRASTRUCTURE,
                'priority': Complaint.PRIORITY_HIGH,
                'is_anonymous': False,
                'assigned_to': 'Audiovisual & Lab Hardware Section',
                'expected_resolution_date': (now + timedelta(days=2)).date(),
                'satisfaction_rating': None,
                'student_feedback': '',
                'description': 'The overhead HDMI projector in Seminar Hall B flickers green and turns off after 15 minutes of presentation. Guest lectures and project reviews cannot be conducted.',
                'status': Complaint.STATUS_IN_PROGRESS,
                'image': 'complaints/2026/11/projector_failure.jpg',
                'admin_response': 'AV technical staff diagnosed a faulty power supply unit and HDMI board. Replacement hardware will be delivered tomorrow.',
                'history': [
                    {'from': 'New', 'to': Complaint.STATUS_PENDING, 'by': 'STU2024001', 'remarks': 'Grievance submitted.'},
                    {'from': Complaint.STATUS_PENDING, 'to': Complaint.STATUS_IN_PROGRESS, 'by': 'admin', 'remarks': 'AV staff checked projector hardware.'},
                ]
            },
            {
                'student_reg': 'STU2024001',
                'title': 'Sports Complex indoor badminton court lights broken',
                'category': Complaint.CATEGORY_OTHER,
                'priority': Complaint.PRIORITY_LOW,
                'is_anonymous': False,
                'assigned_to': 'Electrical Maintenance Unit',
                'expected_resolution_date': (now - timedelta(days=2)).date(),
                'satisfaction_rating': 5,
                'student_feedback': 'Court floodlights were replaced with bright LED drivers. Great playing conditions!',
                'description': 'Two of the four high-bay LED floodlights over Badminton Court 2 have stopped working, leaving half the playing area dim during evening college team practice.',
                'status': Complaint.STATUS_RESOLVED,
                'image': None,
                'admin_response': 'Electrician team replaced both high-bay LED drivers and installed surge protectors. All court lights are fully functional.',
                'history': [
                    {'from': 'New', 'to': Complaint.STATUS_PENDING, 'by': 'STU2024001', 'remarks': 'Grievance submitted.'},
                    {'from': Complaint.STATUS_PENDING, 'to': Complaint.STATUS_IN_PROGRESS, 'by': 'admin', 'remarks': 'Maintenance work order created.'},
                    {'from': Complaint.STATUS_IN_PROGRESS, 'to': Complaint.STATUS_RESOLVED, 'by': 'admin', 'remarks': 'LED drivers replaced and tested.'},
                ]
            },
            {
                'student_reg': 'STU2024003',
                'title': 'Hot water solar geyser not functional in Boys Hostel 2',
                'category': Complaint.CATEGORY_HOSTEL,
                'priority': Complaint.PRIORITY_CRITICAL,
                'is_anonymous': False,
                'assigned_to': 'Hostel 2 Warden Office',
                'expected_resolution_date': (now - timedelta(days=1)).date(),
                'satisfaction_rating': None,
                'student_feedback': '',
                'description': 'The rooftop solar heating unit for Hostel 2 (Wings A and B) is not producing hot water in early morning hours. Water temperature is cold at 6 AM.',
                'status': Complaint.STATUS_PENDING,
                'image': None,
                'admin_response': '',
                'history': [
                    {'from': 'New', 'to': Complaint.STATUS_PENDING, 'by': 'STU2024003', 'remarks': 'Grievance submitted.'},
                ]
            },
        ]

        # 4. Insert Complaints & Histories
        now = timezone.now()
        complaints_created_count = 0

        for idx, cdata in enumerate(sample_complaints):
            student_user = created_students.get(cdata['student_reg'])
            if not student_user:
                continue

            existing_complaint = Complaint.objects.filter(
                title=cdata['title'],
                student=student_user
            ).first()

            if existing_complaint:
                existing_complaint.priority = cdata.get('priority', existing_complaint.priority)
                existing_complaint.is_anonymous = cdata.get('is_anonymous', existing_complaint.is_anonymous)
                existing_complaint.assigned_to = cdata.get('assigned_to', existing_complaint.assigned_to)
                existing_complaint.expected_resolution_date = cdata.get('expected_resolution_date', existing_complaint.expected_resolution_date)
                existing_complaint.satisfaction_rating = cdata.get('satisfaction_rating', existing_complaint.satisfaction_rating)
                existing_complaint.student_feedback = cdata.get('student_feedback', existing_complaint.student_feedback)
                if not existing_complaint.image and cdata.get('image'):
                    existing_complaint.image = cdata['image']
                existing_complaint.save()
                self.stdout.write(self.style.SUCCESS(f"[✓] Updated fields for existing '{existing_complaint.complaint_id}'"))
                continue

            complaint = Complaint(
                student=student_user,
                title=cdata['title'],
                category=cdata['category'],
                priority=cdata.get('priority', Complaint.PRIORITY_MEDIUM),
                is_anonymous=cdata.get('is_anonymous', False),
                assigned_to=cdata.get('assigned_to', ''),
                expected_resolution_date=cdata.get('expected_resolution_date'),
                satisfaction_rating=cdata.get('satisfaction_rating'),
                student_feedback=cdata.get('student_feedback', ''),
                description=cdata['description'],
                status=cdata['status'],
                admin_response=cdata['admin_response'],
                image=cdata.get('image')
            )
            complaint.save()
            complaints_created_count += 1

            history_list = cdata.get('history', [])
            for h_idx, hdata in enumerate(history_list):
                updater = admin_user if hdata['by'] == 'admin' else student_user
                h_time = now - timedelta(days=(len(history_list) - h_idx), hours=h_idx * 3)

                entry = ComplaintHistory.objects.create(
                    complaint=complaint,
                    previous_status=hdata['from'],
                    new_status=hdata['to'],
                    updated_by=updater,
                    remarks=hdata['remarks']
                )
                ComplaintHistory.objects.filter(id=entry.id).update(timestamp=h_time)

            self.stdout.write(self.style.SUCCESS(
                f"[+] Created Complaint: {complaint.complaint_id} ({complaint.category} - {complaint.status} - Priority: {complaint.priority})"
            ))

        self.stdout.write(self.style.SUCCESS("\n" + "=" * 65))
        self.stdout.write(self.style.SUCCESS("✓ UNRESOLVE MODERN DATA & EVIDENCE SETUP COMPLETED"))
        self.stdout.write(self.style.SUCCESS("=" * 65))
        self.stdout.write(f"Total Complaints In Database: {Complaint.objects.count()}")
