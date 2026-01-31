from django.contrib import admin
from .models import VideoGenerationTask


@admin.register(VideoGenerationTask)
class VideoGenerationTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'instructor', 'animation_style', 'status', 'quality', 'progress_percentage', 'created_at')
    list_filter = ('status', 'animation_style', 'quality', 'created_at', 'instructor')
    search_fields = ('course__title', 'instructor__username', 'source_content')
    readonly_fields = ('task_id', 'created_at', 'started_at', 'completed_at', 'progress_percentage', 'error_message')
    fieldsets = (
        ('Task Information', {
            'fields': ('task_id', 'course', 'instructor', 'status'),
        }),
        ('Video Content', {
            'fields': ('source_content', 'animation_style', 'duration', 'quality'),
        }),
        ('Generated Output', {
            'fields': ('generated_video', 'thumbnail'),
        }),
        ('Progress & Status', {
            'fields': ('progress_percentage', 'error_message', 'created_at', 'started_at', 'completed_at'),
        }),
    )
    
    def has_add_permission(self, request):
        # Video generation should be done through the web interface
        return False
