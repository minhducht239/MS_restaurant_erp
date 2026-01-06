from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

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
    path('', include('menu.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
