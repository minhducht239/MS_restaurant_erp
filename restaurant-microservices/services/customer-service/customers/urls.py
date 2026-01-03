from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'', views.CustomerViewSet, basename='customer')

urlpatterns = [
    path('update-from-bill/', views.update_from_bill, name='update_from_bill'),
    path('', include(router.urls)),
]
