from django.contrib import admin
from .models import Video, VideoProgress, TranscodingJob


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'status', 'duration', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'course_title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(VideoProgress)
class VideoProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'video', 'completion_percent', 'is_completed')
    list_filter = ('is_completed', 'last_watched_at')
    search_fields = ('student_email', 'video_title')


@admin.register(TranscodingJob)
class TranscodingJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'video', 'status', 'created_at', 'completed_at')
    list_filter = ('status', 'created_at')
    search_fields = ('video__title',)
    readonly_fields = ('created_at', 'started_at', 'completed_at')
