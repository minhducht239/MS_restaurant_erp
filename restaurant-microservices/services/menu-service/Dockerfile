FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /app/media/menu_images

RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health/')" || exit 1

# Create entrypoint script to clear migration history and re-migrate
RUN echo '#!/bin/bash' > /app/entrypoint.sh && \
    echo 'set -e' >> /app/entrypoint.sh && \
    echo 'echo "🔥 Clearing migration history..."' >> /app/entrypoint.sh && \
    echo 'python -c "import os, django; os.environ.setdefault(\\"DJANGO_SETTINGS_MODULE\\", \\"menu_service.settings\\"); django.setup(); from django.db import connection; cursor = connection.cursor(); cursor.execute(\\"DELETE FROM django_migrations\\"); print(\\"✓ History wiped.\\")"' >> /app/entrypoint.sh && \
    echo 'python manage.py migrate contenttypes --fake' >> /app/entrypoint.sh && \
    echo 'python manage.py migrate auth --fake' >> /app/entrypoint.sh && \
    echo 'python manage.py migrate menu --fake' >> /app/entrypoint.sh && \
    echo 'echo "🧹 Clearing migration history again..."' >> /app/entrypoint.sh && \
    echo 'python -c "import os, django; os.environ.setdefault(\\"DJANGO_SETTINGS_MODULE\\", \\"menu_service.settings\\"); django.setup(); from django.db import connection; cursor = connection.cursor(); cursor.execute(\\"DELETE FROM django_migrations\\"); print(\\"✓ History wiped again.\\")"' >> /app/entrypoint.sh && \
    echo 'python manage.py migrate --fake-initial' >> /app/entrypoint.sh && \
    echo 'exec "$@"' >> /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "30", "menu_service.wsgi:application"]
