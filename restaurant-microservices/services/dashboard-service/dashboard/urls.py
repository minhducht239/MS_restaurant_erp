from django.urls import path
from . import views

urlpatterns = [
    path('statistics/', views.statistics, name='statistics'),
    path('weekly-revenue/', views.weekly_revenue, name='weekly_revenue'),
    path('monthly-revenue/', views.monthly_revenue, name='monthly_revenue'),
    path('top-items/', views.top_items, name='top_items'),
    path('customer-stats/', views.customer_stats, name='customer_stats'),
]
