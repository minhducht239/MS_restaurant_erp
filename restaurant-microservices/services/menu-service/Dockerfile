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

# Create entrypoint script for migrations - fix migration history
RUN echo '#!/bin/bash\n\npython manage.py shell -c "from django.db import connection; cursor = connection.cursor(); cursor.execute(\\"DELETE FROM django_migrations WHERE app IN (\'auth\', \'contenttypes\')\\"); connection.commit(); print(\\"Cleaned migration history\\");" 2>/dev/null || true\n\npython manage.py migrate --noinput\n\nexec \"$@\"' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--timeout", "30", "menu_service.wsgi:application"]
