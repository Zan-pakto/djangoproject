from django.contrib import admin
from .models import UserProfile, Complaint, ComplaintHistory


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'registration_number', 'role', 'department', 'phone_number', 'created_at')
    list_filter = ('role', 'department')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email', 'registration_number')
    ordering = ('-created_at',)


class ComplaintHistoryInline(admin.TabularInline):
    model = ComplaintHistory
    extra = 0
    readonly_fields = ('previous_status', 'new_status', 'updated_by', 'timestamp', 'remarks')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('complaint_id', 'title', 'student', 'category', 'priority', 'status', 'assigned_to', 'is_anonymous', 'created_at')
    list_filter = ('status', 'priority', 'category', 'is_anonymous', 'created_at')
    search_fields = ('complaint_id', 'title', 'description', 'student__username', 'student__first_name', 'student__last_name', 'student__email')
    readonly_fields = ('complaint_id', 'created_at', 'updated_at')
    inlines = [ComplaintHistoryInline]
    ordering = ('-created_at',)


@admin.register(ComplaintHistory)
class ComplaintHistoryAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'previous_status', 'new_status', 'updated_by', 'timestamp')
    list_filter = ('previous_status', 'new_status', 'timestamp')
    search_fields = ('complaint__complaint_id', 'complaint__title', 'updated_by__username', 'remarks')
    readonly_fields = ('complaint', 'previous_status', 'new_status', 'updated_by', 'timestamp', 'remarks')
    ordering = ('-timestamp',)
