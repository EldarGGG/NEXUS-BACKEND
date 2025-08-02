from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

def simple_health_check(request):
    """Simple health check that doesn't depend on database"""
    return JsonResponse({
        "status": "healthy",
        "message": "Server is running",
        "environment": os.environ.get('ENVIRONMENT', 'development'),
        "port": os.environ.get('PORT', '8000')
    })

def health_check(request):
    """Health check endpoint for Railway and Docker"""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
            logger.info("Database health check passed")
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        logger.error(f"Database health check failed: {e}")
    
    # Check if all required apps are loaded
    try:
        from django.apps import apps
        apps.check_apps_ready()
        apps_status = "healthy"
        logger.info("Apps health check passed")
    except Exception as e:
        apps_status = f"unhealthy: {str(e)}"
        logger.error(f"Apps health check failed: {e}")
    
    # Check if Django settings are properly configured
    try:
        # Test if we can access settings
        test_setting = settings.DEBUG
        settings_status = "healthy"
        logger.info("Settings health check passed")
    except Exception as e:
        settings_status = f"unhealthy: {str(e)}"
        logger.error(f"Settings health check failed: {e}")
    
    # Consider healthy if at least database and settings are working
    overall_status = "healthy" if db_status == "healthy" and settings_status == "healthy" else "unhealthy"
    
    response_data = {
        "status": overall_status,
        "database": db_status,
        "apps": apps_status,
        "settings": settings_status,
        "environment": os.environ.get('ENVIRONMENT', 'development'),
        "debug": settings.DEBUG,
        "port": os.environ.get('PORT', '8000')
    }
    
    status_code = 200 if overall_status == "healthy" else 503
    return JsonResponse(response_data, status=status_code)
