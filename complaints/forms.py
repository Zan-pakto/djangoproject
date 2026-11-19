import os
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Complaint, UserProfile


class StudentRegistrationForm(forms.Form):
    """
    Form for registering a new student account with registration number
    and automated User + UserProfile creation.
    """
    full_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. John Doe',
            'autocomplete': 'name',
        }),
        label="Full Name"
    )
    registration_number = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. STU2024001',
            'autocomplete': 'off',
        }),
        label="Student Registration Number"
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'student@uniresolve.edu',
            'autocomplete': 'email',
        }),
        label="Email Address"
    )
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Computer Science & Engineering',
        }),
        label="Department / Course (Optional)"
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. +91 98765 43210',
        }),
        label="Phone Number (Optional)"
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum 6 characters',
            'autocomplete': 'new-password',
        }),
        label="Password",
        help_text="Password must be at least 6 characters long."
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter your password',
            'autocomplete': 'new-password',
        }),
        label="Confirm Password"
    )

    def clean_registration_number(self):
        reg_no = self.cleaned_data.get('registration_number', '').strip().upper()
        if not reg_no:
            raise ValidationError("Registration number is required.")
        if UserProfile.objects.filter(registration_number__iexact=reg_no).exists():
            raise ValidationError("This registration number is already registered.")
        # Also ensure no username collision
        if User.objects.filter(username__iexact=reg_no).exists():
            raise ValidationError("An account with this registration number already exists.")
        return reg_no

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not email:
            raise ValidationError("Email address is required.")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password and len(password) < 6:
            raise ValidationError("Password must be at least 6 characters long.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match. Please verify and try again.")
        return cleaned_data

    def save(self):
        """
        Creates User and associated UserProfile.
        """
        reg_no = self.cleaned_data['registration_number']
        email = self.cleaned_data['email']
        full_name = self.cleaned_data['full_name'].strip()
        parts = full_name.split(' ', 1)
        first_name = parts[0]
        last_name = parts[1] if len(parts) > 1 else ''

        user = User.objects.create_user(
            username=reg_no,
            email=email,
            password=self.cleaned_data['password'],
            first_name=first_name,
            last_name=last_name
        )

        profile = UserProfile.objects.create(
            user=user,
            role=UserProfile.ROLE_STUDENT,
            registration_number=reg_no,
            department=self.cleaned_data.get('department', '').strip(),
            phone_number=self.cleaned_data.get('phone_number', '').strip()
        )
        return user


class StudentLoginForm(forms.Form):
    """
    Login form that accepts either registration number, email, or username.
    """
    identifier = forms.CharField(
        label="Registration Number / Email / Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your Reg No, Email or Username',
            'autocomplete': 'username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password',
        })
    )


class ComplaintForm(forms.ModelForm):
    """
    Student complaint submission form with file type, size validation,
    priority level, and anonymous submission option.
    """
    class Meta:
        model = Complaint
        fields = ['title', 'category', 'priority', 'is_anonymous', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Air conditioning compressor failure in Room 302',
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'anonymousCheck',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Provide specific details, including building/block number, lab/room, when the issue started, and any relevant observations...',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }
        labels = {
            'is_anonymous': 'Submit Anonymously (Mask my identity on public and admin listings)',
            'priority': 'Urgency / Severity Level',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'priority' in self.fields:
            self.fields['priority'].required = False
            self.fields['priority'].initial = Complaint.PRIORITY_MEDIUM

    def clean_priority(self):
        return self.cleaned_data.get('priority') or Complaint.PRIORITY_MEDIUM

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 5:
            raise ValidationError("Title is too short. Please provide a clear title (at least 5 characters).")
        return title

    def clean_description(self):
        desc = self.cleaned_data.get('description', '').strip()
        if len(desc) < 15:
            raise ValidationError("Description is too brief. Please describe the problem in at least 15 characters.")
        return desc

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return None

        # Max file size: 5MB
        max_size_mb = 5
        if image.size > max_size_mb * 1024 * 1024:
            raise ValidationError(f"Image file size must not exceed {max_size_mb} MB.")

        # Allowed extensions
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
        ext = os.path.splitext(image.name)[1].lower()
        if ext not in allowed_extensions:
            raise ValidationError(
                f"Unsupported image format ({ext}). Allowed formats are: JPG, JPEG, PNG, WEBP, GIF."
            )

        # Verify image integrity using Pillow (catches corrupt or spoofed files)
        try:
            from PIL import Image
            img = Image.open(image)
            img.verify()
            if hasattr(image, 'seek'):
                image.seek(0)
        except Exception:
            raise ValidationError("The uploaded file is corrupt or not a valid image format.")

        return image


class AdminComplaintUpdateForm(forms.ModelForm):
    """
    Administrator form for changing complaint status, assigning departments,
    setting target resolution dates (ETA), and providing feedback.
    """
    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional internal remarks or transition summary for this update (saved to history audit log)...',
        }),
        label="Status Change Remarks (Optional)",
        help_text="Logged in the complaint history timeline."
    )

    class Meta:
        model = Complaint
        fields = ['status', 'assigned_to', 'expected_resolution_date', 'admin_response']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select',
            }),
            'assigned_to': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Campus Maintenance Cell / IT Helpdesk / Hostel Warden',
            }),
            'expected_resolution_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'admin_response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Official administrative response visible to the student...',
            }),
        }
        labels = {
            'assigned_to': 'Assigned Authority / Department',
            'expected_resolution_date': 'Target Resolution Date (ETA)',
            'admin_response': 'Official Resolution Feedback',
        }


class ComplaintFeedbackForm(forms.ModelForm):
    """
    Student resolution rating and feedback form.
    """
    class Meta:
        model = Complaint
        fields = ['satisfaction_rating', 'student_feedback']
        widgets = {
            'satisfaction_rating': forms.Select(attrs={
                'class': 'form-select',
            }),
            'student_feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Share your feedback on the resolution timeliness, support quality, and outcome...',
            }),
        }
        labels = {
            'satisfaction_rating': 'How satisfied are you with the resolution?',
            'student_feedback': 'Student Comments & Review',
        }
