import os
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserProfile(models.Model):
    """
    Extends Django's built-in User model with student/admin role
    and student-specific details like registration number.
    """
    ROLE_STUDENT = 'STUDENT'
    ROLE_ADMIN = 'ADMIN'
    ROLE_CHOICES = [
        (ROLE_STUDENT, 'Student'),
        (ROLE_ADMIN, 'Administrator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    registration_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        help_text="Unique student registration or roll number (e.g., STU2024001)"
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        name = self.user.get_full_name() or self.user.username
        reg = f" [{self.registration_number}]" if self.registration_number else ""
        return f"{name}{reg} - {self.get_role_display()}"

    @property
    def is_student(self):
        return self.role == self.ROLE_STUDENT

    @property
    def is_administrator(self):
        return self.role == self.ROLE_ADMIN or self.user.is_staff or self.user.is_superuser


class Complaint(models.Model):
    """
    Core complaint model tracking issue submissions, categories,
    status transitions, and administrative feedback.
    """
    CATEGORY_ACADEMIC = 'Academic'
    CATEGORY_INFRASTRUCTURE = 'Infrastructure'
    CATEGORY_HOSTEL = 'Hostel'
    CATEGORY_MESS = 'Mess/Food'
    CATEGORY_LIBRARY = 'Library'
    CATEGORY_TRANSPORT = 'Transportation'
    CATEGORY_OTHER = 'Other'

    CATEGORY_CHOICES = [
        (CATEGORY_ACADEMIC, 'Academic'),
        (CATEGORY_INFRASTRUCTURE, 'Infrastructure'),
        (CATEGORY_HOSTEL, 'Hostel'),
        (CATEGORY_MESS, 'Mess/Food'),
        (CATEGORY_LIBRARY, 'Library'),
        (CATEGORY_TRANSPORT, 'Transportation'),
        (CATEGORY_OTHER, 'Other'),
    ]

    STATUS_PENDING = 'Pending'
    STATUS_IN_PROGRESS = 'In Progress'
    STATUS_RESOLVED = 'Resolved'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_RESOLVED, 'Resolved'),
    ]

    PRIORITY_LOW = 'Low'
    PRIORITY_MEDIUM = 'Medium'
    PRIORITY_HIGH = 'High'
    PRIORITY_CRITICAL = 'Critical'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low - Routine Request'),
        (PRIORITY_MEDIUM, 'Medium - Standard Priority'),
        (PRIORITY_HIGH, 'High - Urgent Attention'),
        (PRIORITY_CRITICAL, 'Critical - Emergency / High Impact'),
    ]

    complaint_id = models.CharField(
        max_length=25,
        unique=True,
        editable=False,
        help_text="Unique auto-generated complaint tracking ID"
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='complaints',
        help_text="Student who submitted this complaint"
    )
    title = models.CharField(max_length=200, help_text="Brief summary of the complaint")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
        help_text="Urgency/Impact level of the grievance"
    )
    is_anonymous = models.BooleanField(
        default=False,
        help_text="Mask identity on public and administrative complaint dashboards"
    )
    description = models.TextField(help_text="Detailed description of the issue")
    image = models.ImageField(
        upload_to='complaints/%Y/%m/',
        blank=True,
        null=True,
        help_text="Optional supporting image/photo (max 5MB)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    assigned_to = models.CharField(
        max_length=120,
        blank=True,
        null=True,
        help_text="Designated authority or campus department handling resolution"
    )
    expected_resolution_date = models.DateField(
        blank=True,
        null=True,
        help_text="Target resolution date (ETA)"
    )
    admin_response = models.TextField(
        blank=True,
        help_text="Official remarks and resolution updates from administration"
    )
    satisfaction_rating = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        choices=[
            (1, '1 - Very Dissatisfied'),
            (2, '2 - Dissatisfied'),
            (3, '3 - Neutral'),
            (4, '4 - Satisfied'),
            (5, '5 - Very Satisfied'),
        ],
        help_text="Student satisfaction score upon resolution (1 to 5)"
    )
    student_feedback = models.TextField(
        blank=True,
        help_text="Student feedback remarks following grievance resolution"
    )
    feedback_submitted_at = models.DateTimeField(
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'

    def __str__(self):
        return f"{self.complaint_id}: {self.title} ({self.status})"

    def save(self, *args, **kwargs):
        # Auto-generate unique complaint tracking ID if missing
        if not self.complaint_id:
            year = datetime.now().year
            prefix = f"CMP-{year}-"
            # Find the highest existing sequence number for the current year
            last_record = (
                Complaint.objects.filter(complaint_id__startswith=prefix)
                .order_by('-complaint_id')
                .first()
            )
            if last_record and last_record.complaint_id:
                try:
                    last_num = int(last_record.complaint_id.split('-')[-1])
                    seq = last_num + 1
                except (ValueError, IndexError):
                    seq = Complaint.objects.count() + 1
            else:
                seq = 1
            # Ensure uniqueness
            candidate_id = f"{prefix}{seq:04d}"
            while Complaint.objects.filter(complaint_id=candidate_id).exists():
                seq += 1
                candidate_id = f"{prefix}{seq:04d}"
            self.complaint_id = candidate_id

        super().save(*args, **kwargs)

    @property
    def status_badge_class(self):
        """Returns Bootstrap 5 badge CSS classes for complaint status."""
        mapping = {
            self.STATUS_PENDING: 'bg-warning text-dark',
            self.STATUS_IN_PROGRESS: 'bg-primary text-white',
            self.STATUS_RESOLVED: 'bg-success text-white',
        }
        return mapping.get(self.status, 'bg-secondary text-white')

    @property
    def status_icon(self):
        """Returns Bootstrap icon class for status."""
        mapping = {
            self.STATUS_PENDING: 'bi-hourglass-split',
            self.STATUS_IN_PROGRESS: 'bi-gear-wide-connected',
            self.STATUS_RESOLVED: 'bi-check-circle-fill',
        }
        return mapping.get(self.status, 'bi-circle')

    @property
    def category_icon(self):
        """Returns Bootstrap icon class for category."""
        mapping = {
            self.CATEGORY_ACADEMIC: 'bi-mortarboard-fill',
            self.CATEGORY_INFRASTRUCTURE: 'bi-building-fill',
            self.CATEGORY_HOSTEL: 'bi-house-door-fill',
            self.CATEGORY_MESS: 'bi-cup-hot-fill',
            self.CATEGORY_LIBRARY: 'bi-journal-bookmark-fill',
            self.CATEGORY_TRANSPORT: 'bi-bus-front-fill',
            self.CATEGORY_OTHER: 'bi-grid-fill',
        }
        return mapping.get(self.category, 'bi-tag-fill')

    @property
    def priority_badge_class(self):
        """Returns badge CSS class for priority level."""
        mapping = {
            self.PRIORITY_LOW: 'badge-priority-low',
            self.PRIORITY_MEDIUM: 'badge-priority-medium',
            self.PRIORITY_HIGH: 'badge-priority-high',
            self.PRIORITY_CRITICAL: 'badge-priority-critical',
        }
        return mapping.get(self.priority, 'badge-priority-medium')

    @property
    def priority_icon(self):
        """Returns Bootstrap icon for priority level."""
        mapping = {
            self.PRIORITY_LOW: 'bi-dash-circle',
            self.PRIORITY_MEDIUM: 'bi-info-circle-fill',
            self.PRIORITY_HIGH: 'bi-exclamation-triangle-fill',
            self.PRIORITY_CRITICAL: 'bi-lightning-charge-fill',
        }
        return mapping.get(self.priority, 'bi-flag-fill')

    @property
    def is_overdue(self):
        """Returns True if grievance is not resolved and target ETA is past."""
        if self.status != self.STATUS_RESOLVED and self.expected_resolution_date:
            from django.utils import timezone
            return self.expected_resolution_date < timezone.now().date()
        return False

    def get_public_student_name(self, viewer=None):
        """Returns student name, masking if anonymous (unless viewer is the student himself)."""
        if self.is_anonymous and (not viewer or viewer != self.student):
            return "Anonymous Student [Protected]"
        return self.student.get_full_name() or self.student.username

    def get_public_reg_number(self, viewer=None):
        """Returns student registration number, masking if anonymous."""
        if self.is_anonymous and (not viewer or viewer != self.student):
            return "CONFIDENTIAL"
        if hasattr(self.student, 'profile') and self.student.profile.registration_number:
            return self.student.profile.registration_number
        return self.student.username


class ComplaintHistory(models.Model):
    """
    Audit log tracking all status changes and administration remarks
    associated with a complaint.
    """
    complaint = models.ForeignKey(
        Complaint,
        on_delete=models.CASCADE,
        related_name='history'
    )
    previous_status = models.CharField(max_length=20, choices=Complaint.STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=Complaint.STATUS_CHOICES)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='complaint_history_entries'
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    remarks = models.TextField(blank=True, help_text="Notes recorded at the time of change")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Complaint History'
        verbose_name_plural = 'Complaint Histories'

    def __str__(self):
        return f"{self.complaint.complaint_id}: {self.previous_status} -> {self.new_status} on {self.timestamp:%Y-%m-%d %H:%M}"
