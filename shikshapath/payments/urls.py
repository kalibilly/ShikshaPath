from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('course/<int:course_id>/pay/', views.make_payment, name='make_payment'),
    path('confirm/', views.confirm_payment, name='confirm_payment'),
    path('webhook/', views.payment_webhook, name='payment_webhook'),
    path('course/<int:course_id>/payments/', views.course_payments, name='course_payments'),
    path('payouts/', views.payouts_history, name='payout_history'),
    path('course/<int:course_id>/payout/', views.create_payout, name='create_payout'),
]
