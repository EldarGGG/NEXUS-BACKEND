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

# Test if we can import the WSGI application
echo "Testing WSGI application import..."
python -c "from core.wsgi import application; print('WSGI application import successful')" || {
    echo "WSGI application import failed!"
    exit 1
}

# Start with simpler configuration first
echo "Starting Gunicorn with simple configuration..."
exec gunicorn core.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 1 \
    --threads 1 \
    --timeout 30 \
    --log-level debug \
    --access-logfile - \
    --error-logfile -