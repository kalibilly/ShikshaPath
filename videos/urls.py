from django.urls import path
from . import views

app_name = 'videos'

urlpatterns = [
    path('course/<int:course_id>/upload', views.upload_video, name='upload_video'),
    path('watch/<int:video_id>/', views.watch_video, name='watch_video'),
    path('stream/<int:video_id>/', views.stream_video, name='stream_video'),
    path('video/<int:video_id>/progress/', views.save_progress, name='save_progress'),
]
