from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'billing-service'})

def api_root(request):
    return JsonResponse({
        'service': 'Billing Service',
        'version': '1.0.0',
        'endpoints': {
            'bills': '/api/billing/',
            'statistics': '/api/billing/statistics/',
        }
    })

urlpatterns = [
    # With /api/billing/ prefix for production gateway routing (MUST come first)
    path('api/billing/health/', health_check, name='health_check_api'),
    path('api/billing/', include('billing.urls')),
    
    # Health check
    path('health/', health_check, name='health_check'),
    
    # Local development without prefix
    path('', include('billing.urls')),
]
