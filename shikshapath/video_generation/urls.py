from django.urls import path
from . import views

app_name = 'video_generation'

urlpatterns = [
    path('generate/<int:course_id>/', views.generate_video, name='generate_video'),
    path('list/<int:course_id>/', views.list_videos, name='list_videos'),
    path('view/<int:video_id>/', views.view_video, name='view_video'),
    path('delete/<int:video_id>/', views.delete_video, name='delete_video'),
    path('status/<int:video_id>/', views.check_video_status, name='check_video_status'),
]
