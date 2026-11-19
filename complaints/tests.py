from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from complaints.models import UserProfile, Complaint, ComplaintHistory


class UserModelAndProfileTests(TestCase):
    """Tests for User and UserProfile models and role properties."""

    def test_student_profile_creation_and_properties(self):
        user = User.objects.create_user(
            username='STU_TEST_01',
            email='student1@test.edu',
            password='Password123'
        )
        profile = UserProfile.objects.create(
            user=user,
            role=UserProfile.ROLE_STUDENT,
            registration_number='REG_TEST_01',
            department='Computer Science'
        )
        self.assertTrue(profile.is_student)
        self.assertFalse(profile.is_administrator)
        self.assertIn('REG_TEST_01', str(profile))

    def test_admin_profile_creation_and_properties(self):
        admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.edu',
            password='AdminPassword123',
            is_staff=True
        )
        profile = UserProfile.objects.create(
            user=admin_user,
            role=UserProfile.ROLE_ADMIN,
            registration_number='ADMIN_001'
        )
        self.assertTrue(profile.is_administrator)
        self.assertFalse(profile.is_student)


class ComplaintModelTests(TestCase):
    """Tests for Complaint ID generation, choices, and ComplaintHistory."""

    def setUp(self):
        self.student = User.objects.create_user(
            username='STU_TEST_02',
            email='student2@test.edu',
            password='Password123'
        )
        UserProfile.objects.create(
            user=self.student,
            role=UserProfile.ROLE_STUDENT,
            registration_number='REG_TEST_02'
        )

    def test_auto_generated_complaint_id(self):
        complaint1 = Complaint.objects.create(
            student=self.student,
            title='Leaking faucet in restroom',
            category=Complaint.CATEGORY_INFRASTRUCTURE,
            description='Water leaking continuously under the sink in second floor restroom.'
        )
        self.assertTrue(complaint1.complaint_id.startswith('CMP-'))
        self.assertEqual(complaint1.status, Complaint.STATUS_PENDING)

        complaint2 = Complaint.objects.create(
            student=self.student,
            title='Projector cable faulty in room 102',
            category=Complaint.CATEGORY_INFRASTRUCTURE,
            description='The HDMI input cable is torn and screen loses connection.'
        )
        self.assertNotEqual(complaint1.complaint_id, complaint2.complaint_id)

    def test_complaint_history_creation(self):
        complaint = Complaint.objects.create(
            student=self.student,
            title='Wi-Fi dead zone in Library corner',
            category=Complaint.CATEGORY_LIBRARY,
            description='There is zero reception in the reference books row 4.'
        )
        history = ComplaintHistory.objects.create(
            complaint=complaint,
            previous_status='New',
            new_status=Complaint.STATUS_PENDING,
            updated_by=self.student,
            remarks='Initial submission'
        )
        self.assertEqual(complaint.history.count(), 1)
        self.assertEqual(complaint.history.first().new_status, Complaint.STATUS_PENDING)


class RegistrationAndAuthenticationViewsTests(TestCase):
    """Tests for user registration, duplicate prevention, and login redirection."""

    def setUp(self):
        self.client = Client()

    def test_successful_student_registration(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'Alice Wonder',
            'registration_number': 'REG_NEW_99',
            'email': 'alice@test.edu',
            'department': 'Mechanical',
            'phone_number': '+91 99999 88888',
            'password': 'SafePassword123',
            'confirm_password': 'SafePassword123'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(email='alice@test.edu').exists())
        self.assertTrue(UserProfile.objects.filter(registration_number='REG_NEW_99').exists())

    def test_duplicate_email_registration_fails(self):
        User.objects.create_user(username='EXISTING', email='duplicate@test.edu', password='Pass123')
        response = self.client.post(reverse('register'), {
            'full_name': 'Bob Tester',
            'registration_number': 'REG_BOB_01',
            'email': 'duplicate@test.edu',
            'password': 'SafePassword123',
            'confirm_password': 'SafePassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'email', 'An account with this email address already exists.')

    def test_duplicate_registration_number_fails(self):
        user = User.objects.create_user(username='REG_DUP_01', email='first@test.edu', password='Pass123')
        UserProfile.objects.create(user=user, role=UserProfile.ROLE_STUDENT, registration_number='REG_DUP_01')

        response = self.client.post(reverse('register'), {
            'full_name': 'Charlie Test',
            'registration_number': 'REG_DUP_01',
            'email': 'second@test.edu',
            'password': 'SafePassword123',
            'confirm_password': 'SafePassword123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'registration_number', 'This registration number is already registered.')

    def test_password_mismatch_fails(self):
        response = self.client.post(reverse('register'), {
            'full_name': 'Mismatch Test',
            'registration_number': 'REG_MISMATCH',
            'email': 'mismatch@test.edu',
            'password': 'Password123',
            'confirm_password': 'Password456'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context['form'], 'confirm_password', 'Passwords do not match. Please verify and try again.')

    def test_login_with_registration_number_redirects_student(self):
        user = User.objects.create_user(username='STU_LOG_01', email='stu_log@test.edu', password='Password123')
        UserProfile.objects.create(user=user, role=UserProfile.ROLE_STUDENT, registration_number='STU_LOG_01')

        response = self.client.post(reverse('login'), {
            'identifier': 'STU_LOG_01',
            'password': 'Password123'
        })
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_login_with_email_redirects_admin(self):
        admin = User.objects.create_user(username='admin_log', email='admin_log@test.edu', password='AdminPass123', is_staff=True)
        UserProfile.objects.create(user=admin, role=UserProfile.ROLE_ADMIN, registration_number='ADM_01')

        response = self.client.post(reverse('login'), {
            'identifier': 'admin_log@test.edu',
            'password': 'AdminPass123'
        })
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_logout_redirects_to_login(self):
        user = User.objects.create_user(username='user_out', email='out@test.edu', password='Password123')
        self.client.login(username='user_out', password='Password123')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))


class StudentWorkflowAndAccessControlTests(TestCase):
    """Tests for student complaint operations and role-based access restrictions."""

    def setUp(self):
        self.client = Client()
        # Student 1
        self.student1 = User.objects.create_user(username='STU_S1', email='s1@test.edu', password='Password123')
        UserProfile.objects.create(user=self.student1, role=UserProfile.ROLE_STUDENT, registration_number='REG_S1')

        # Student 2
        self.student2 = User.objects.create_user(username='STU_S2', email='s2@test.edu', password='Password123')
        UserProfile.objects.create(user=self.student2, role=UserProfile.ROLE_STUDENT, registration_number='REG_S2')

        # Administrator
        self.admin = User.objects.create_user(username='ADMIN_A1', email='a1@test.edu', password='AdminPass123', is_staff=True)
        UserProfile.objects.create(user=self.admin, role=UserProfile.ROLE_ADMIN, registration_number='ADM_A1')

        # Complaint belonging to student 1
        self.complaint1 = Complaint.objects.create(
            student=self.student1,
            title='Hostel hot water issue in Room 101',
            category=Complaint.CATEGORY_HOSTEL,
            description='Hot water supply stops after 6:30 AM every morning in wing A.'
        )

    def test_submit_complaint_view(self):
        self.client.login(username='STU_S1', password='Password123')
        response = self.client.post(reverse('submit_complaint'), {
            'title': 'Mess food quality on weekends',
            'category': Complaint.CATEGORY_MESS,
            'description': 'The breakfast served on Sunday morning was undercooked and cold.'
        })
        self.assertRedirects(response, reverse('my_complaints'))
        new_complaint = Complaint.objects.filter(title='Mess food quality on weekends').first()
        self.assertIsNotNone(new_complaint)
        self.assertEqual(new_complaint.status, Complaint.STATUS_PENDING)
        self.assertEqual(new_complaint.student, self.student1)
        self.assertTrue(new_complaint.history.exists())

    def test_student_cannot_view_other_students_complaint(self):
        # Logged in as student 2, trying to view student 1's complaint
        self.client.login(username='STU_S2', password='Password123')
        response = self.client.get(reverse('complaint_detail', args=[self.complaint1.complaint_id]))
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_student_cannot_access_admin_dashboard(self):
        self.client.login(username='STU_S1', password='Password123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_student_cannot_access_all_complaints_admin_view(self):
        self.client.login(username='STU_S1', password='Password123')
        response = self.client.get(reverse('all_complaints'))
        self.assertRedirects(response, reverse('student_dashboard'))


class AdminWorkflowTests(TestCase):
    """Tests for administrator dashboard, updating complaint status, and audit history creation."""

    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(username='STU_TEST_ADM', email='stu_adm@test.edu', password='Password123')
        UserProfile.objects.create(user=self.student, role=UserProfile.ROLE_STUDENT, registration_number='REG_ADM_01')

        self.admin = User.objects.create_user(username='ADMIN_BOSS', email='boss@test.edu', password='AdminPass123', is_staff=True)
        UserProfile.objects.create(user=self.admin, role=UserProfile.ROLE_ADMIN, registration_number='ADM_BOSS')

        self.complaint = Complaint.objects.create(
            student=self.student,
            title='Bus delay on Route 4',
            category=Complaint.CATEGORY_TRANSPORT,
            description='Route 4 bus is arriving late by 30 minutes every day.'
        )

    def test_admin_dashboard_metrics(self):
        self.client.login(username='ADMIN_BOSS', password='AdminPass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('total_complaints', response.context)
        self.assertEqual(response.context['total_complaints'], 1)
        self.assertEqual(response.context['pending_complaints'], 1)

    def test_admin_updates_status_and_response(self):
        self.client.login(username='ADMIN_BOSS', password='AdminPass123')
        url = reverse('admin_complaint_detail', args=[self.complaint.complaint_id])

        # Transition status to In Progress
        response = self.client.post(url, {
            'status': Complaint.STATUS_IN_PROGRESS,
            'admin_response': 'Route 4 driver has been notified; GPS schedule under review.',
            'remarks': 'Work order issued to transportation supervisor.'
        })
        self.assertRedirects(response, url)

        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, Complaint.STATUS_IN_PROGRESS)
        self.assertEqual(self.complaint.admin_response, 'Route 4 driver has been notified; GPS schedule under review.')

        # Verify ComplaintHistory creation
        history_entry = self.complaint.history.first()
        self.assertIsNotNone(history_entry)
        self.assertEqual(history_entry.previous_status, Complaint.STATUS_PENDING)
        self.assertEqual(history_entry.new_status, Complaint.STATUS_IN_PROGRESS)
        self.assertEqual(history_entry.updated_by, self.admin)
        self.assertEqual(history_entry.remarks, 'Work order issued to transportation supervisor.')

        # Transition to Resolved
        self.client.post(url, {
            'status': Complaint.STATUS_RESOLVED,
            'admin_response': 'Departure time adjusted by 15 mins. Schedule restored.',
            'remarks': 'Resolved following transport schedule adjustment.'
        })
        self.complaint.refresh_from_db()
        self.assertEqual(self.complaint.status, Complaint.STATUS_RESOLVED)
        self.assertEqual(self.complaint.history.count(), 2)


class SearchAndFilterTests(TestCase):
    """Tests for search and filter functionality in Student and Admin complaint directories."""

    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(username='STU_SF', email='sf@test.edu', password='Password123')
        UserProfile.objects.create(user=self.student, role=UserProfile.ROLE_STUDENT, registration_number='REG_SF')

        self.admin = User.objects.create_user(username='ADMIN_SF', email='admin_sf@test.edu', password='AdminPass123', is_staff=True)
        UserProfile.objects.create(user=self.admin, role=UserProfile.ROLE_ADMIN, registration_number='ADM_SF')

        # Create complaints
        self.c1 = Complaint.objects.create(
            student=self.student,
            title='Air conditioner leaking water',
            category=Complaint.CATEGORY_INFRASTRUCTURE,
            description='Room 101 AC unit',
            status=Complaint.STATUS_PENDING
        )
        self.c2 = Complaint.objects.create(
            student=self.student,
            title='Library textbook shortage for Physics',
            category=Complaint.CATEGORY_LIBRARY,
            description='Not enough physics volumes',
            status=Complaint.STATUS_RESOLVED
        )

    def test_student_filter_by_category_and_status(self):
        self.client.login(username='STU_SF', password='Password123')

        # Filter by Infrastructure
        resp = self.client.get(reverse('my_complaints') + '?category=Infrastructure')
        self.assertEqual(len(resp.context['page_obj']), 1)
        self.assertEqual(resp.context['page_obj'][0].title, 'Air conditioner leaking water')

        # Filter by Resolved
        resp_resolved = self.client.get(reverse('my_complaints') + '?status=Resolved')
        self.assertEqual(len(resp_resolved.context['page_obj']), 1)
        self.assertEqual(resp_resolved.context['page_obj'][0].title, 'Library textbook shortage for Physics')

    def test_admin_search_by_query(self):
        self.client.login(username='ADMIN_SF', password='AdminPass123')

        # Search for 'Physics'
        resp = self.client.get(reverse('all_complaints') + '?q=Physics')
        self.assertEqual(len(resp.context['page_obj']), 1)
        self.assertEqual(resp.context['page_obj'][0].category, Complaint.CATEGORY_LIBRARY)


class ErrorHandlingTests(TestCase):
    """Tests for custom error pages, corrupt uploads, and non-existent complaints."""

    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(username='STU_ERR', email='err@test.edu', password='Password123')
        UserProfile.objects.create(user=self.student, role=UserProfile.ROLE_STUDENT, registration_number='REG_ERR')

    def test_custom_404_view(self):
        resp = self.client.get(reverse('error_404'))
        self.assertEqual(resp.status_code, 404)
        self.assertContains(resp, 'HTTP 404 ERROR', status_code=404)

    def test_custom_403_view(self):
        resp = self.client.get(reverse('error_403'))
        self.assertEqual(resp.status_code, 403)
        self.assertContains(resp, 'HTTP 403 FORBIDDEN', status_code=403)

    def test_custom_500_view(self):
        resp = self.client.get(reverse('error_500'))
        self.assertEqual(resp.status_code, 500)
        self.assertContains(resp, 'HTTP 500 ERROR', status_code=500)

    def test_non_existent_complaint_returns_404(self):
        self.client.login(username='STU_ERR', password='Password123')
        resp = self.client.get('/student/complaints/CMP-DOES-NOT-EXIST/')
        self.assertEqual(resp.status_code, 404)

    def test_corrupt_file_upload_rejected(self):
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.client.login(username='STU_ERR', password='Password123')
        corrupt_file = SimpleUploadedFile(
            'fake_photo.jpg',
            b'NOT_A_REAL_IMAGE_DATA_HEADER',
            content_type='image/jpeg'
        )
        resp = self.client.post(reverse('submit_complaint'), {
            'title': 'Test with corrupt file',
            'category': Complaint.CATEGORY_INFRASTRUCTURE,
            'description': 'Valid description with more than 15 characters.',
            'image': corrupt_file
        })
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['form'].has_error('image'))


class NewFeaturesIntegrationTests(TestCase):
    """
    Tests for Priority tiers, Anonymous whistleblower protection,
    Student satisfaction rating, Printable receipts, and CSV audit exports.
    """

    def setUp(self):
        self.client = Client()
        self.student = User.objects.create_user(
            username='STU_FEAT_01',
            email='feat01@test.edu',
            password='Password123',
            first_name='Alex',
            last_name='Rivera'
        )
        UserProfile.objects.create(
            user=self.student,
            role=UserProfile.ROLE_STUDENT,
            registration_number='REG_FEAT_01',
            department='Computer Science'
        )

        self.student2 = User.objects.create_user(
            username='STU_FEAT_02',
            email='feat02@test.edu',
            password='Password123'
        )
        UserProfile.objects.create(
            user=self.student2,
            role=UserProfile.ROLE_STUDENT,
            registration_number='REG_FEAT_02'
        )

        self.admin = User.objects.create_user(
            username='ADMIN_FEAT',
            email='admin_feat@test.edu',
            password='AdminPass123',
            is_staff=True
        )
        UserProfile.objects.create(
            user=self.admin,
            role=UserProfile.ROLE_ADMIN,
            registration_number='ADM_FEAT'
        )

    def test_priority_and_anonymous_submission(self):
        self.client.login(username='STU_FEAT_01', password='Password123')
        resp = self.client.post(reverse('submit_complaint'), {
            'title': 'Hazardous bare wire near elevator',
            'category': Complaint.CATEGORY_INFRASTRUCTURE,
            'priority': Complaint.PRIORITY_CRITICAL,
            'is_anonymous': True,
            'description': 'High-voltage wire is exposed near third floor east wing elevator.'
        })
        self.assertRedirects(resp, reverse('my_complaints'))

        complaint = Complaint.objects.get(title='Hazardous bare wire near elevator')
        self.assertEqual(complaint.priority, Complaint.PRIORITY_CRITICAL)
        self.assertTrue(complaint.is_anonymous)

        # Verify identity masking
        self.assertEqual(complaint.get_public_student_name(viewer=self.admin), "Anonymous Student [Protected]")
        self.assertEqual(complaint.get_public_reg_number(viewer=self.admin), "CONFIDENTIAL")
        # Submitting student viewing their own complaint sees their own name
        self.assertEqual(complaint.get_public_student_name(viewer=self.student), "Alex Rivera")

    def test_resolution_feedback_and_rating(self):
        complaint = Complaint.objects.create(
            student=self.student,
            title='Corridor light replaced',
            category=Complaint.CATEGORY_INFRASTRUCTURE,
            description='Bulb is flickering continuously.',
            status=Complaint.STATUS_RESOLVED
        )

        self.client.login(username='STU_FEAT_01', password='Password123')
        detail_url = reverse('complaint_detail', kwargs={'complaint_id': complaint.complaint_id})

        # Submit feedback
        post_resp = self.client.post(detail_url, {
            'submit_feedback': '1',
            'satisfaction_rating': '5',
            'student_feedback': 'Electrician arrived quickly and replaced the bulb. Excellent service!'
        })
        self.assertRedirects(post_resp, detail_url)

        complaint.refresh_from_db()
        self.assertEqual(complaint.satisfaction_rating, 5)
        self.assertIn('Electrician arrived quickly', complaint.student_feedback)
        self.assertIsNotNone(complaint.feedback_submitted_at)

    def test_printable_receipt_access(self):
        complaint = Complaint.objects.create(
            student=self.student,
            title='Projector HDMI audio issue',
            category=Complaint.CATEGORY_INFRASTRUCTURE,
            description='Speakers in Hall 4 produce buzz when HDMI is plugged in.'
        )
        receipt_url = reverse('printable_receipt', kwargs={'complaint_id': complaint.complaint_id})

        # Student owner can view receipt
        self.client.login(username='STU_FEAT_01', password='Password123')
        resp = self.client.get(receipt_url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, complaint.complaint_id)
        self.assertContains(resp, "GRIEVANCE REGISTRATION DOSSIER")

        # Other student is blocked
        self.client.login(username='STU_FEAT_02', password='Password123')
        resp_blocked = self.client.get(receipt_url)
        self.assertRedirects(resp_blocked, reverse('student_dashboard'))

    def test_admin_csv_export(self):
        Complaint.objects.create(
            student=self.student,
            title='Laboratory bench damaged',
            category=Complaint.CATEGORY_INFRASTRUCTURE,
            description='Bench 12 wood surface is cracked and uneven.',
            priority=Complaint.PRIORITY_MEDIUM
        )
        self.client.login(username='ADMIN_FEAT', password='AdminPass123')
        resp = self.client.get(reverse('all_complaints') + '?export=csv')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('UniResolve_Grievances_Export.csv', resp['Content-Disposition'])
        content = resp.content.decode('utf-8')
        self.assertIn('Complaint ID,Student Name', content)
        self.assertIn('Laboratory bench damaged', content)


