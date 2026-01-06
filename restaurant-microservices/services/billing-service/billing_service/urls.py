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
    path('', api_root, name='api_root'),
    path('health/', health_check, name='health_check'),
    path('', include('billing.urls')),
]
