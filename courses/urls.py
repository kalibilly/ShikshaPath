from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_courses, name='search'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/create/', views.create_course, name='create_course'),
    path('course/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('course/<int:course_id>/add-resource/', views.add_resource, name='add_resource'),
    path('resource/<int:resource_id>/delete/', views.delete_resource, name='delete_resource'),
    path('course/<int:course_id>/rate/', views.add_rating, name='add_rating'),
    path('course/<int:course_id>/referral/', views.generate_referral_link, name='generate_referral'),
]
