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
    # With /api/reservations/ prefix for production gateway routing (MUST come first)
    path('api/reservations/health/', health_check, name='health_check_api'),
    path('api/reservations/', include('reservations.urls')),
    
    # Health check and root info
    path('health/', health_check, name='health_check'),
    
    # Local development without prefix
    path('', include('reservations.urls')),
]
