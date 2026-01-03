from django.urls import path, include
from django.http import JsonResponse

def health_check(request): return JsonResponse({'status': 'healthy', 'service': 'table-service'})

urlpatterns = [
    path('health/', health_check),
    path('api/tables/', include('tables.urls')),
]
