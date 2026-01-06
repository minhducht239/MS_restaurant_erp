"""
Auth Service URL Configuration
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'auth-service'})


def api_root(request):
    return JsonResponse({
        'service': 'Auth Service',
        'version': '1.0.0',
        'endpoints': {
            'login': '/api/auth/login/',
            'register': '/api/auth/register/',
            'refresh': '/api/auth/token/refresh/',
            'profile': '/api/auth/profile/',
            'users': '/api/auth/users/',
        }
    })


urlpatterns = [
    path('', api_root, name='api_root'),
    path('health/', health_check, name='health_check'),
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Auth endpoints with /api/auth/ prefix (for direct access and gateway)
    path('api/auth/', include('authentication.urls')),
    # Also keep without prefix for backward compatibility
    path('', include('authentication.urls')),
]

# Always serve media files (for development and production)
# In production, consider using nginx or cloud storage for better performance
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

# Also add static serving for DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
