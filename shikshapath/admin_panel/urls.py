from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard', views.admin_dashboard, name='dashboard'),
    path('users/', views.admin_users, name='users'),
    path('user/<int:user_id>/', views.admin_user_detail, name='user_detail'),
    path('user/<int:user_id>/action/', views.admin_user_action, name='user_action'),
    path('courses/', views.admin_courses, name='courses'),
    path('course/<int:course_id>/', views.admin_course_detail, name='course_detail'),
    path('course/<int:course_id>/action/', views.admin_course_action, name='course_action'),
    path('payments/', views.admin_payments, name='payments'),
    path('payments/export/', views.admin_payments_export, name='payments_export'),
    path('audit-logs/', views.admin_audit_log, name='audit_logs'),
    path('audit-logs/export/', views.admin_audit_export, name='audit_logs_export'),
]
