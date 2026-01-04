from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'permissions', views.PermissionViewSet, basename='permission')
router.register(r'roles', views.RoleViewSet, basename='role')
router.register(r'activity-logs', views.UserActivityLogViewSet, basename='activity-log')
router.register(r'login-history', views.LoginHistoryViewSet, basename='login-history')

urlpatterns = [
    # Auth endpoints
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('validate/', views.validate_token, name='validate_token'),
    
    # Google OAuth endpoints
    path('google/login/', views.google_login_url, name='google_login_url'),
    path('google/callback/', views.google_callback, name='google_callback'),
    
    # Profile endpoints
    path('profile/', views.profile, name='profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/avatar/', views.upload_avatar, name='upload_avatar'),
    
    # My activity endpoints
    path('my-activity/', views.my_activity_logs, name='my_activity_logs'),
    path('my-login-history/', views.my_login_history, name='my_login_history'),
    
    # Router URLs (admin)
    path('', include(router.urls)),
]