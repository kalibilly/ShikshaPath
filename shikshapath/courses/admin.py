from django.contrib import admin
from .models import Course, Enrollment, CourseResource, CourseRating, CourseReferral

# Register your models here.
admin.site.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'price', 'status', 'is_private', 'is_suspended', 'created_at', )
    search_fields = ('title', 'instructor__email', )
    list_filter = ('status', 'is_private', 'is_suspended', 'is_flagged', 'created_at',)
    readonly_fields = ('created_at', 'updated_at', 'made_private_at')
    fieldsets = (
        (None, {'fields': ('title', 'description', 'instructor', 'price',)}),
        ('Media', {'fields': ('thumbnail',)}),
        ('Status', {'fields': ('status', 'is_suspended', 'suspended_reason', 'is_flagged', 'flag_reason',)}),
        ('Privacy', {'fields': ('is_private', 'made_private_at')}),
        ('Settings', {'fields': ('platform_fee_percentage',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at',)}),
    )


admin.site.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'is_active', 'progress_percent', 'enrolled_at', )
    search_fields = ('course__title', 'student__email', )
    list_filter = ('is_active', 'enrolled_at',)
    readonly_fields = ('enrolled_at', 'completed_at', )


admin.site.register(CourseResource)
class CourseResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'resource_type', 'order', 'created_at')
    search_fields = ('title', 'course__title')
    list_filter = ('resource_type', 'created_at')
    ordering = ('course', 'order')


admin.site.register(CourseRating)
class CourseRatingAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'rating', 'created_at')
    search_fields = ('course__title', 'student__email')
    list_filter = ('rating', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(CourseReferral)
class CourseReferralAdmin(admin.ModelAdmin):
    list_display = ('course', 'referrer', 'referred_student', 'is_converted', 'created_at')
    search_fields = ('course__title', 'referrer__email', 'referred_student__email')
    list_filter = ('is_converted', 'created_at')
    readonly_fields = ('created_at', 'converted_at')

