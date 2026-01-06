FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
WORKDIR /app
RUN apt-get update && apt-get install -y default-libmysqlclient-dev build-essential pkg-config && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000

# Create entrypoint script for migrations - fix migration history
RUN echo '#!/bin/bash\n\npython manage.py shell -c "from django.db import connection; cursor = connection.cursor(); cursor.execute(\\"DELETE FROM django_migrations WHERE app IN (\'auth\', \'contenttypes\')\\"); connection.commit(); print(\\"Cleaned migration history\\");" 2>/dev/null || true\n\npython manage.py migrate --noinput\n\nexec \"$@\"' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "2", "--timeout", "30", "dashboard_service.wsgi:application"]
