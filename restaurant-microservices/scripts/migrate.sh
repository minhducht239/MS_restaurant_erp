#!/bin/bash
# Script to run migrations for all services

echo "🔄 Running migrations for all services..."

services=("auth-service" "menu-service" "billing-service" "customer-service" "table-service" "staff-service" "reservation-service")

for service in "${services[@]}"; do
    echo "📦 Migrating $service..."
    docker-compose exec -T $service python manage.py migrate --noinput
done

echo "✅ All migrations completed!"

# Create superuser for auth-service
echo "🔐 Creating superuser for auth-service..."
docker-compose exec -T auth-service python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@restaurant.com', 'admin123', role='admin')
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists')
"

echo "🎉 Setup completed!"
