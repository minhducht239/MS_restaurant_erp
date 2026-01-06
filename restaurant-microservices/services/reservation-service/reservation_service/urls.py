from django.urls import path, include
from django.http import JsonResponse

def health_check(request): 
    return JsonResponse({'status': 'healthy', 'service': 'reservation-service'})

def api_root(request):
    return JsonResponse({
        'service': 'Reservation Service',
        'version': '1.0.0',
        'endpoints': {
            'reservations': '/api/reservations/',
        }
    })

urlpatterns = [
    path('', api_root, name='api_root'),
    path('health/', health_check, name='health_check'),
    path('', include('reservations.urls')),
    
    # With /api/reservation/ prefix for production gateway routing
    path('api/reservation/', include('reservations.urls')),
    path('api/reservation/health/', health_check, name='health_check_api'),
]
