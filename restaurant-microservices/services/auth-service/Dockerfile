FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set work directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies including gunicorn
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn gevent && \
    pip list | grep gunicorn

# Copy application code
COPY . .

# Install Python packages with proper permissions and ensure PATH
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn gevent && \
    which gunicorn && \
    gunicorn --version

# Create non-root user for security but keep executables accessible
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app && \
    chmod +x /usr/local/bin/gunicorn

# Add user bin to PATH
ENV PATH="/home/appuser/.local/bin:${PATH}"
USER appuser

# Health check - remove curl dependency
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health/', timeout=5)" || exit 1

# Expose port
EXPOSE 8000

# Create entrypoint script for migrations using --fake-initial
RUN printf '#!/bin/bash\nset -e\necho "Running migrations with --fake-initial..."\npython manage.py migrate --noinput --fake-initial\necho "Migrations complete"\nexec "$@"\n' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Use sync workers for MySQL thread safety
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "30", "auth_service.wsgi:application"]