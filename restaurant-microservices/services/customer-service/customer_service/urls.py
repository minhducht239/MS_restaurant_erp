from django.urls import path, include
from django.http import JsonResponse

def health_check(request): 
    return JsonResponse({'status': 'healthy', 'service': 'customer-service'})

def api_root(request):
    return JsonResponse({
        'service': 'Customer Service',
        'version': '1.0.0',
        'endpoints': {
            'customers': '/api/customers/',
        }
    })

urlpatterns = [
    # With /api/customers/ prefix for production gateway routing (MUST come first)
    path('api/customers/health/', health_check, name='health_check_api'),
    path('api/customers/', include('customers.urls')),
    
    # Health check and root info
    path('health/', health_check, name='health_check'),
    
    # Local development without prefix
    path('', include('customers.urls')),
]
