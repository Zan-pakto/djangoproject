import json
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Avg
from django.http import HttpResponseForbidden, HttpResponse
from django.utils import timezone

from .models import Complaint, ComplaintHistory, UserProfile
from .forms import (
    StudentRegistrationForm,
    StudentLoginForm,
    ComplaintForm,
    AdminComplaintUpdateForm,
    ComplaintFeedbackForm,
)
from .decorators import student_required, admin_required


def landing_view(request):
    """
    Public landing page for UniResolve.
    """
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    # Aggregate public metrics for demonstration
    total_complaints = Complaint.objects.count()
    resolved_complaints = Complaint.objects.filter(status=Complaint.STATUS_RESOLVED).count()
    total_students = UserProfile.objects.filter(role=UserProfile.ROLE_STUDENT).count()

    resolution_rate = int((resolved_complaints / total_complaints * 100)) if total_complaints > 0 else 98
    avg_rating_val = Complaint.objects.filter(satisfaction_rating__isnull=False).aggregate(Avg('satisfaction_rating'))['satisfaction_rating__avg']
    avg_rating = round(avg_rating_val, 1) if avg_rating_val else 4.9

    context = {
        'total_complaints': total_complaints,
        'resolved_complaints': resolved_complaints,
        'total_students': total_students,
        'resolution_rate': resolution_rate,
        'avg_rating': avg_rating,
    }
    return render(request, 'landing.html', context)


def register_view(request):
    """
    Student registration view with validation and profile creation.
    """
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Account created successfully for {user.get_full_name() or user.username}! "
                f"You can now log in using your Registration Number ({form.cleaned_data['registration_number']}) or Email."
            )
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors indicated below.")
    else:
        form = StudentRegistrationForm()

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    """
    Unified login view supporting registration number, email, or username.
    """
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier'].strip()
            password = form.cleaned_data['password']

            # Resolve user by username, email, or profile registration number
            target_user = None

            # 1. Match by username (case-insensitive)
            target_user = User.objects.filter(username__iexact=identifier).first()

            # 2. Match by email
            if not target_user:
                target_user = User.objects.filter(email__iexact=identifier).first()

            # 3. Match by student registration number
            if not target_user:
                profile = UserProfile.objects.filter(registration_number__iexact=identifier).select_related('user').first()
                if profile:
                    target_user = profile.user

            if target_user:
                user = authenticate(request, username=target_user.username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)

                    is_admin = user.is_staff or user.is_superuser
                    if hasattr(user, 'profile') and user.profile.is_administrator:
                        is_admin = True
                    return redirect('admin_dashboard' if is_admin else 'student_dashboard')

            messages.error(
                request,
                "Invalid login credentials. Please check your Registration Number / Email and password."
            )
    else:
        form = StudentLoginForm()

    return render(request, 'registration/login.html', {'form': form})


def logout_view(request):
    """
    Logs out the user and redirects to login with confirmation.
    """
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('login')


@login_required
def dashboard_redirect_view(request):
    """
    Directs authenticated users to their role-specific dashboard.
    """
    is_admin = request.user.is_staff or request.user.is_superuser
    if hasattr(request.user, 'profile') and request.user.profile.is_administrator:
        is_admin = True

    if is_admin:
        return redirect('admin_dashboard')
    return redirect('student_dashboard')


# =====================================================================
# Student Views
# =====================================================================

@login_required
@student_required
def student_dashboard_view(request):
    """
    Student Dashboard showing metrics, recent complaints, priority summaries,
    and prompt for unrated resolutions.
    """
    user_complaints = Complaint.objects.filter(student=request.user)

    total_count = user_complaints.count()
    pending_count = user_complaints.filter(status=Complaint.STATUS_PENDING).count()
    in_progress_count = user_complaints.filter(status=Complaint.STATUS_IN_PROGRESS).count()
    resolved_count = user_complaints.filter(status=Complaint.STATUS_RESOLVED).count()

    urgent_count = user_complaints.filter(priority__in=[Complaint.PRIORITY_HIGH, Complaint.PRIORITY_CRITICAL]).count()
    unrated_count = user_complaints.filter(status=Complaint.STATUS_RESOLVED, satisfaction_rating__isnull=True).count()

    recent_complaints = user_complaints.order_by('-created_at')[:6]

    chart_status_data = json.dumps({
        'labels': ['Pending Review', 'In Progress', 'Resolved'],
        'counts': [pending_count, in_progress_count, resolved_count],
        'colors': ['#f59e0b', '#6366f1', '#10b981']
    })

    context = {
        'total_count': total_count,
        'pending_count': pending_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'urgent_count': urgent_count,
        'unrated_count': unrated_count,
        'recent_complaints': recent_complaints,
        'chart_status_data': chart_status_data,
    }
    return render(request, 'complaints/student_dashboard.html', context)


@login_required
@student_required
def submit_complaint_view(request):
    """
    Allows a student to submit a new complaint with priority level,
    confidential anonymity toggle, and optional photo attachment.
    """
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.student = request.user
            complaint.status = Complaint.STATUS_PENDING
            complaint.save()

            history_note = f"Grievance initially submitted with [{complaint.priority}] priority."
            if complaint.is_anonymous:
                history_note += " (Student identity requested to be protected/anonymous)."

            # Record initial history
            ComplaintHistory.objects.create(
                complaint=complaint,
                previous_status='New',
                new_status=Complaint.STATUS_PENDING,
                updated_by=request.user,
                remarks=history_note
            )

            messages.success(
                request,
                f"Grievance {complaint.complaint_id} has been submitted successfully! "
                f"Urgency: {complaint.priority}. Our administration has received your ticket."
            )
            return redirect('my_complaints')
        else:
            messages.error(request, "Please fix the errors in the form below.")
    else:
        form = ComplaintForm()

    return render(request, 'complaints/submit_complaint.html', {'form': form})


@login_required
@student_required
def my_complaints_view(request):
    """
    Lists all complaints submitted by the logged-in student with filters & pagination.
    """
    complaints = Complaint.objects.filter(student=request.user)

    # Filtering by status
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        complaints = complaints.filter(status=status_filter)

    # Filtering by category
    category_filter = request.GET.get('category', '').strip()
    if category_filter:
        complaints = complaints.filter(category=category_filter)

    # Filtering by priority
    priority_filter = request.GET.get('priority', '').strip()
    if priority_filter:
        complaints = complaints.filter(priority=priority_filter)

    # Search by title or ID
    search_query = request.GET.get('q', '').strip()
    if search_query:
        complaints = complaints.filter(
            Q(title__icontains=search_query) |
            Q(complaint_id__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Pagination: 8 per page
    paginator = Paginator(complaints, 8)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'priority_filter': priority_filter,
        'search_query': search_query,
        'category_choices': Complaint.CATEGORY_CHOICES,
        'status_choices': Complaint.STATUS_CHOICES,
        'priority_choices': Complaint.PRIORITY_CHOICES,
        'total_filtered': complaints.count(),
    }
    return render(request, 'complaints/my_complaints.html', context)


@login_required
def complaint_detail_view(request, complaint_id):
    """
    Displays full details for a complaint with resolution rating & feedback submission.
    Strictly prevents students from viewing other students' complaints.
    """
    complaint = get_object_or_404(
        Complaint.objects.select_related('student', 'student__profile'),
        complaint_id=complaint_id
    )

    # Access control check
    is_admin = request.user.is_staff or request.user.is_superuser
    if hasattr(request.user, 'profile') and request.user.profile.is_administrator:
        is_admin = True

    if not is_admin and complaint.student != request.user:
        messages.error(request, "Access denied. You cannot view complaints filed by other students.")
        return redirect('student_dashboard')

    # Student feedback & rating submission
    feedback_form = None
    if complaint.student == request.user and complaint.status == Complaint.STATUS_RESOLVED:
        if request.method == 'POST' and 'submit_feedback' in request.POST:
            feedback_form = ComplaintFeedbackForm(request.POST, instance=complaint)
            if feedback_form.is_valid():
                fb = feedback_form.save(commit=False)
                fb.feedback_submitted_at = timezone.now()
                fb.save()
                messages.success(request, "Thank you! Your resolution rating & feedback have been submitted successfully.")
                return redirect('complaint_detail', complaint_id=complaint.complaint_id)
        else:
            feedback_form = ComplaintFeedbackForm(instance=complaint)

    history_entries = complaint.history.select_related('updated_by').order_by('-timestamp')

    context = {
        'complaint': complaint,
        'history_entries': history_entries,
        'feedback_form': feedback_form,
        'is_admin': is_admin,
    }
    return render(request, 'complaints/complaint_detail.html', context)


@login_required
def complaint_history_view(request, complaint_id):
    """
    Displays full audit trail for a complaint.
    """
    complaint = get_object_or_404(
        Complaint.objects.select_related('student', 'student__profile'),
        complaint_id=complaint_id
    )

    # Access control
    is_admin = request.user.is_staff or request.user.is_superuser
    if hasattr(request.user, 'profile') and request.user.profile.is_administrator:
        is_admin = True

    if not is_admin and complaint.student != request.user:
        messages.error(request, "Access denied. You cannot view history for this complaint.")
        return redirect('student_dashboard')

    history_entries = complaint.history.select_related('updated_by').order_by('-timestamp')

    context = {
        'complaint': complaint,
        'history_entries': history_entries,
        'is_admin': is_admin,
    }
    return render(request, 'complaints/complaint_history.html', context)


@login_required
def printable_receipt_view(request, complaint_id):
    """
    Renders an official, printable A4-ready grievance acknowledgment receipt
    for records, accreditation, and student proof.
    """
    complaint = get_object_or_404(
        Complaint.objects.select_related('student', 'student__profile'),
        complaint_id=complaint_id
    )

    is_admin = request.user.is_staff or request.user.is_superuser
    if hasattr(request.user, 'profile') and request.user.profile.is_administrator:
        is_admin = True

    if not is_admin and complaint.student != request.user:
        messages.error(request, "Access denied. You cannot print receipt for this complaint.")
        return redirect('student_dashboard')

    return render(request, 'complaints/printable_receipt.html', {
        'complaint': complaint,
        'is_admin': is_admin,
    })


# =====================================================================
# Administrator Views
# =====================================================================

@login_required
@admin_required
def admin_dashboard_view(request):
    """
    Administrator dashboard with metrics, category breakdown,
    status distribution, priority breakdown, satisfaction scores, and recent complaints.
    """
    total_complaints = Complaint.objects.count()
    pending_complaints = Complaint.objects.filter(status=Complaint.STATUS_PENDING).count()
    in_progress_complaints = Complaint.objects.filter(status=Complaint.STATUS_IN_PROGRESS).count()
    resolved_complaints = Complaint.objects.filter(status=Complaint.STATUS_RESOLVED).count()

    total_students = UserProfile.objects.filter(role=UserProfile.ROLE_STUDENT).count()

    # Priority metrics
    critical_complaints = Complaint.objects.filter(priority=Complaint.PRIORITY_CRITICAL).count()
    high_complaints = Complaint.objects.filter(priority=Complaint.PRIORITY_HIGH).count()
    anonymous_complaints = Complaint.objects.filter(is_anonymous=True).count()
    overdue_complaints = Complaint.objects.filter(
        status__in=[Complaint.STATUS_PENDING, Complaint.STATUS_IN_PROGRESS],
        expected_resolution_date__lt=timezone.now().date()
    ).count()

    # Satisfaction ratings
    rating_avg = Complaint.objects.filter(satisfaction_rating__isnull=False).aggregate(Avg('satisfaction_rating'))['satisfaction_rating__avg']
    avg_satisfaction = round(rating_avg, 1) if rating_avg else 4.8
    total_reviews = Complaint.objects.filter(satisfaction_rating__isnull=False).count()

    # Percentage calculations for distribution bars
    pending_pct = round((pending_complaints / total_complaints * 100), 1) if total_complaints > 0 else 0
    in_progress_pct = round((in_progress_complaints / total_complaints * 100), 1) if total_complaints > 0 else 0
    resolved_pct = round((resolved_complaints / total_complaints * 100), 1) if total_complaints > 0 else 0

    # Category distribution
    categories_data = []
    for cat_key, cat_label in Complaint.CATEGORY_CHOICES:
        count = Complaint.objects.filter(category=cat_key).count()
        categories_data.append({
            'key': cat_key,
            'label': cat_label,
            'count': count,
            'pct': round((count / total_complaints * 100), 1) if total_complaints > 0 else 0
        })

    latest_complaints = Complaint.objects.select_related(
        'student', 'student__profile'
    ).order_by('-created_at')[:8]

    chart_status_data = json.dumps({
        'labels': ['Pending Review', 'In Progress', 'Resolved'],
        'counts': [pending_complaints, in_progress_complaints, resolved_complaints],
        'colors': ['#f59e0b', '#6366f1', '#10b981']
    })

    chart_category_data = json.dumps({
        'labels': [cat['label'] for cat in categories_data],
        'counts': [cat['count'] for cat in categories_data],
        'colors': ['#4f46e5', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#64748b']
    })

    context = {
        'total_complaints': total_complaints,
        'pending_complaints': pending_complaints,
        'in_progress_complaints': in_progress_complaints,
        'resolved_complaints': resolved_complaints,
        'total_students': total_students,
        'critical_complaints': critical_complaints,
        'high_complaints': high_complaints,
        'anonymous_complaints': anonymous_complaints,
        'overdue_complaints': overdue_complaints,
        'avg_satisfaction': avg_satisfaction,
        'total_reviews': total_reviews,
        'pending_pct': pending_pct,
        'in_progress_pct': in_progress_pct,
        'resolved_pct': resolved_pct,
        'categories_data': categories_data,
        'latest_complaints': latest_complaints,
        'chart_status_data': chart_status_data,
        'chart_category_data': chart_category_data,
    }
    return render(request, 'complaints/admin_dashboard.html', context)


@login_required
@admin_required
def all_complaints_view(request):
    """
    Searchable, filterable, and paginated master complaints table for administrators
    with priority filters, anonymous toggle, and CSV export.
    """
    complaints = Complaint.objects.select_related('student', 'student__profile').all()

    # Status filter
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        complaints = complaints.filter(status=status_filter)

    # Category filter
    category_filter = request.GET.get('category', '').strip()
    if category_filter:
        complaints = complaints.filter(category=category_filter)

    # Priority filter
    priority_filter = request.GET.get('priority', '').strip()
    if priority_filter:
        complaints = complaints.filter(priority=priority_filter)

    # Anonymous filter
    anon_filter = request.GET.get('anonymous', '').strip()
    if anon_filter == 'yes':
        complaints = complaints.filter(is_anonymous=True)

    # Search filter
    search_query = request.GET.get('q', '').strip()
    if search_query:
        complaints = complaints.filter(
            Q(title__icontains=search_query) |
            Q(complaint_id__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(student__first_name__icontains=search_query) |
            Q(student__last_name__icontains=search_query) |
            Q(student__username__icontains=search_query) |
            Q(student__profile__registration_number__icontains=search_query)
        )

    # CSV Export
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="UniResolve_Grievances_Export.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Complaint ID', 'Student Name', 'Registration No', 'Category',
            'Priority', 'Title', 'Status', 'Assigned Authority',
            'Target ETA', 'Anonymous', 'Created At', 'Rating (1-5)'
        ])
        for c in complaints:
            writer.writerow([
                c.complaint_id,
                c.get_public_student_name(),
                c.get_public_reg_number(),
                c.category,
                c.priority,
                c.title,
                c.status,
                c.assigned_to or 'Unassigned',
                c.expected_resolution_date.strftime('%Y-%m-%d') if c.expected_resolution_date else 'N/A',
                'Yes' if c.is_anonymous else 'No',
                c.created_at.strftime('%Y-%m-%d %H:%M'),
                c.satisfaction_rating or 'Unrated'
            ])
        return response

    # Pagination: 10 per page
    paginator = Paginator(complaints, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except (PageNotAnInteger, EmptyPage):
        page_obj = paginator.get_page(1)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'priority_filter': priority_filter,
        'anon_filter': anon_filter,
        'search_query': search_query,
        'category_choices': Complaint.CATEGORY_CHOICES,
        'status_choices': Complaint.STATUS_CHOICES,
        'priority_choices': Complaint.PRIORITY_CHOICES,
        'total_filtered': complaints.count(),
    }
    return render(request, 'complaints/all_complaints.html', context)


@login_required
@admin_required
def admin_complaint_detail_view(request, complaint_id):
    """
    Admin complaint management view allowing status transitions,
    assigning departments, setting target resolution dates,
    adding administrative responses, and reviewing the audit trail.
    """
    complaint = get_object_or_404(
        Complaint.objects.select_related('student', 'student__profile'),
        complaint_id=complaint_id
    )

    if request.method == 'POST':
        # Retrieve the original persisted status and assignment before mutation
        old_status = Complaint.objects.values_list('status', flat=True).get(pk=complaint.pk)
        old_assigned = complaint.assigned_to
        form = AdminComplaintUpdateForm(request.POST, instance=complaint)
        if form.is_valid():
            updated_complaint = form.save(commit=False)
            new_status = updated_complaint.status
            new_assigned = updated_complaint.assigned_to
            remarks = form.cleaned_data.get('remarks', '').strip()
            admin_response = updated_complaint.admin_response.strip()

            updated_complaint.save()

            # Record history entry if status changed, assigned_to changed, or remarks were provided
            if old_status != new_status or old_assigned != new_assigned or remarks or admin_response:
                history_remarks = remarks
                if not history_remarks:
                    notes = []
                    if old_status != new_status:
                        notes.append(f"Status changed from '{old_status}' to '{new_status}'")
                    if old_assigned != new_assigned and new_assigned:
                        notes.append(f"Assigned to {new_assigned}")
                    if updated_complaint.expected_resolution_date:
                        notes.append(f"Target ETA: {updated_complaint.expected_resolution_date}")
                    history_remarks = ". ".join(notes) if notes else "Administrative update recorded."

                ComplaintHistory.objects.create(
                    complaint=updated_complaint,
                    previous_status=old_status,
                    new_status=new_status,
                    updated_by=request.user,
                    remarks=history_remarks
                )

            messages.success(
                request,
                f"Complaint {complaint.complaint_id} updated successfully. Status: {new_status}."
            )
            return redirect('admin_complaint_detail', complaint_id=complaint.complaint_id)
        else:
            messages.error(request, "Failed to update complaint. Please verify form inputs.")
    else:
        form = AdminComplaintUpdateForm(instance=complaint)

    history_entries = complaint.history.select_related('updated_by').order_by('-timestamp')

    context = {
        'complaint': complaint,
        'form': form,
        'history_entries': history_entries,
    }
    return render(request, 'complaints/admin_complaint_detail.html', context)


# =====================================================================
# Custom Error Handlers
# =====================================================================

def custom_404_view(request, exception=None):
    """Custom 404 handler for Page / Resource Not Found."""
    return render(request, '404.html', status=404)


def custom_403_view(request, exception=None):
    """Custom 403 handler for Access Denied / Permission Errors."""
    return render(request, '403.html', status=403)


def custom_500_view(request):
    """Custom 500 handler for Internal Server Errors."""
    return render(request, '500.html', status=500)


def custom_400_view(request, exception=None):
    """Custom 400 handler for Malformed / Bad Requests."""
    return render(request, '400.html', status=400)
