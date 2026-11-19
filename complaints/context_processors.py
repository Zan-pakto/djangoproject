from .models import Complaint

def complaint_stats(request):
    """
    Supplies global counts for notification badges in the navigation sidebar.
    """
    if not request.user.is_authenticated:
        return {}

    is_admin = request.user.is_staff or request.user.is_superuser
    if hasattr(request.user, 'profile') and request.user.profile.is_administrator:
        is_admin = True

    try:
        if is_admin:
            pending_count = Complaint.objects.filter(status=Complaint.STATUS_PENDING).count()
            total_count = Complaint.objects.count()
        else:
            pending_count = Complaint.objects.filter(student=request.user, status=Complaint.STATUS_PENDING).count()
            total_count = Complaint.objects.filter(student=request.user).count()
    except Exception:
        pending_count = 0
        total_count = 0

    return {
        'nav_pending_count': pending_count,
        'nav_total_count': total_count,
    }
