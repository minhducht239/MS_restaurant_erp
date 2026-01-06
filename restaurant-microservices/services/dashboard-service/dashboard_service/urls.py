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
    path('', api_root, name='api_root'),
    path('health/', health_check, name='health_check'),
    path('', include('dashboard.urls')),
]
