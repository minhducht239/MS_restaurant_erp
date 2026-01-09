from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy', 'service': 'staff-service'})

def api_root(request):
    return JsonResponse({
        'service': 'Staff Service',
        'version': '1.0.0',
        'endpoints': {
            'staff': '/api/staff/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Production Gateway routing (Prefix: /api/staff/) - MUST come first
    path('api/staff/health/', health_check, name='health_check_api'),
    path('api/staff/', include('staff.urls')),
    
    # Health check and root info
    path('health/', health_check, name='health_check'),
    
    # Local development
    path('', include('staff.urls')),
]