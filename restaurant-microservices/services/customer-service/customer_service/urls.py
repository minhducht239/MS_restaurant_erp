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
    path('', api_root, name='api_root'),
    path('health/', health_check, name='health_check'),
    path('', include('customers.urls')),
    
    # With /api/customer/ prefix for production gateway routing
    path('api/customers/', include('customers.urls')),
    path('api/customers/health/', health_check, name='health_check_api'),
]
