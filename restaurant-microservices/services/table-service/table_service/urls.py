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
    # With /api/tables/ prefix for production gateway routing (MUST come first)
    path('api/tables/health/', health_check, name='health_check_api'),
    path('api/tables/', include('tables.urls')),
    
    # Health check and root info
    path('health/', health_check, name='health_check'),
    
    # Local development without prefix
    path('', include('tables.urls')),
]
