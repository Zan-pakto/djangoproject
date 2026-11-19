from django.urls import path
from . import views

urlpatterns = [
    # Public & Auth routes
    path('', views.landing_view, name='landing'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_redirect_view, name='dashboard_redirect'),

    # Student routes
    path('student/dashboard/', views.student_dashboard_view, name='student_dashboard'),
    path('student/complaints/submit/', views.submit_complaint_view, name='submit_complaint'),
    path('student/complaints/', views.my_complaints_view, name='my_complaints'),
    path('student/complaints/<str:complaint_id>/', views.complaint_detail_view, name='complaint_detail'),
    path('student/complaints/<str:complaint_id>/history/', views.complaint_history_view, name='complaint_history'),
    path('student/complaints/<str:complaint_id>/receipt/', views.printable_receipt_view, name='printable_receipt'),

    # Administrator routes
    path('management/dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('management/complaints/', views.all_complaints_view, name='all_complaints'),
    path('management/complaints/<str:complaint_id>/', views.admin_complaint_detail_view, name='admin_complaint_detail'),

    # Error pages preview routes (convenient for class testing & design review)
    path('error/404/', views.custom_404_view, name='error_404'),
    path('error/403/', views.custom_403_view, name='error_403'),
    path('error/500/', views.custom_500_view, name='error_500'),
    path('error/400/', views.custom_400_view, name='error_400'),
]
