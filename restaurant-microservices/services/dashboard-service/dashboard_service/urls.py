from django.urls import path, include
from django.http import JsonResponse

def health_check(request): 
    return JsonResponse({'status': 'healthy', 'service': 'dashboard-service'})

def api_root(request):
    return JsonResponse({
        'service': 'Dashboard Service',
        'version': '1.0.0',
        'endpoints': {
            'dashboard': '/api/dashboard/',
            'stats': '/api/dashboard/stats/',
        }
    })

urlpatterns = [
    # With /api/dashboard/ prefix for production gateway routing (MUST come first)
    path('api/dashboard/health/', health_check, name='health_check_api'),
    path('api/dashboard/', include('dashboard.urls')),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # Local development without prefix
    path('', include('dashboard.urls')),
]
