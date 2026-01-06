"""
Auth Service URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
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
    
    # Auth endpoints - App Platform routes /api/auth/* to this service
    path('', include('authentication.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
