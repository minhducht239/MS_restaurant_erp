from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'bills', views.BillViewSet, basename='bill')

urlpatterns = [
    path('dashboard/', views.dashboard_stats, name='dashboard_stats'),
    path('', include(router.urls)),
]
