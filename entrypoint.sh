#!/bin/bash

set -e

echo "Starting Django application..."

# Change to source directory
cd src

echo "Current directory: $(pwd)"
echo "Environment: ${ENVIRONMENT:-development}"

# Wait for database to be ready (for Railway PostgreSQL)
echo "Waiting for database..."

# Run migrations
echo "Running database migrations..."
python manage.py migrate --noinput || {
    echo "Warning: Migration failed, but continuing..."
}

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if in production and doesn't exist
if [ "$ENVIRONMENT" = "production" ]; then
    echo "Setting up production environment..."
    python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@nexus.com', 'nexus123')" || true
fi

# Start the application
echo "Starting Gunicorn server on port ${PORT:-8000}..."
echo "Environment variables:"
echo "  PORT: ${PORT:-8000}"
echo "  ENVIRONMENT: ${ENVIRONMENT:-development}"
echo "  PYTHONPATH: ${PYTHONPATH}"
echo "  DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE}"

# Test if Django can start
echo "Testing Django startup..."
python -c "import django; django.setup(); print('Django startup successful')" || {
    echo "Django startup failed!"
    exit 1
}

exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${WEB_CONCURRENCY:-1} \
    --threads 2 \
    --timeout 60 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --log-level debug \
    --access-logfile - \
    --error-logfile - \
    --preload