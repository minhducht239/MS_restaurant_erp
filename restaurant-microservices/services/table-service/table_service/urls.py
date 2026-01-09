from django.urls import path, include
from django.http import JsonResponse

def health_check(request): 
    return JsonResponse({'status': 'healthy', 'service': 'table-service'})

def api_root(request):
    return JsonResponse({
        'service': 'Table Service',
        'version': '1.0.0',
        'endpoints': {
            'tables': '/api/tables/',
            'orders': '/api/tables/orders/',
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    path('health/', health_check, name='health_check'),
    path('', include('tables.urls')),
    
    # With /api/table/ prefix for production gateway routing
    path('api/tables/', include('tables.urls')),
    path('api/tables/health/', health_check, name='health_check_api'),
]
