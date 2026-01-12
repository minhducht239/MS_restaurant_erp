import os
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.views.static import serve

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'menu-service'})

def api_root(request):
    return JsonResponse({
        'service': 'Menu Service',
        'version': '1.0.0',
        'endpoints': {
            'menu_items': '/api/menu/',
            'categories': '/api/menu/categories/',
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    path('health/', health_check, name='health_check'),
    # API routes with /api/menu/ prefix
    path('api/menu/', include('menu.urls')),
    # Also keep without prefix for backward compatibility
    path('', include('menu.urls')),
]

# Chỉ serve local media files khi KHÔNG sử dụng DigitalOcean Spaces
# Khi sử dụng Spaces, ảnh được serve trực tiếp từ CDN của Spaces
USE_SPACES = getattr(settings, 'USE_SPACES', os.environ.get('USE_SPACES', 'False').lower() == 'true')
if not USE_SPACES:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

# Also add static serving for DEBUG mode
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
