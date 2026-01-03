from django.urls import path, include
from django.http import JsonResponse

def health_check(request): return JsonResponse({'status': 'healthy', 'service': 'staff-service'})

urlpatterns = [
    path('health/', health_check),
    path('api/staff/', include('staff.urls')),
]
