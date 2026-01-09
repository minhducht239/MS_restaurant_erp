#!/bin/bash
set -e

echo "� Running migrations..."
python manage.py migrate --noinput

echo "✅ Migrations complete!"

# Seed default roles & permissions (idempotent)
echo "🔧 Seeding default roles and permissions..."
python manage.py create_default_permissions || true
echo "✅ Seeding complete!"

exec "$@"
