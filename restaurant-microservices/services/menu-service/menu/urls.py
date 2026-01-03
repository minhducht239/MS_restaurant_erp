from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'items', views.MenuItemViewSet, basename='menuitem')

urlpatterns = [
    path('categories/', views.categories, name='categories'),
    path('', include(router.urls)),
]
