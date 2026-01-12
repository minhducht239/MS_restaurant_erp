# PowerShell script to run migrations for all services

Write-Host "🔄 Running migrations for all services..." -ForegroundColor Cyan

$services = @("auth-service", "menu-service", "billing-service", "customer-service", "table-service", "staff-service", "reservation-service")

foreach ($service in $services) {
    Write-Host "📦 Migrating $service..." -ForegroundColor Yellow
    docker-compose exec -T $service python manage.py migrate --noinput
}

Write-Host " All migrations completed!" -ForegroundColor Green

# Create superuser for auth-service
Write-Host " Creating superuser for auth-service..." -ForegroundColor Cyan

$pythonCode = @"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@restaurant.com', 'admin123', role='admin')
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
"@

docker-compose exec -T auth-service python manage.py shell -c $pythonCode

Write-Host "🎉 Setup completed!" -ForegroundColor Green
