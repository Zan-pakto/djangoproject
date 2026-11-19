"""
URL configuration for college_complaint_system project.
CampusCare – College Complaint Management System.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('', include('complaints.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Production Custom Error Handlers
handler404 = 'complaints.views.custom_404_view'
handler500 = 'complaints.views.custom_500_view'
handler403 = 'complaints.views.custom_403_view'
handler400 = 'complaints.views.custom_400_view'
