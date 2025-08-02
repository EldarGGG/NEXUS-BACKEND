from django.http import JsonResponse
from django.db import connection
from django.conf import settings
import os

def health_check(request):
    """Health check endpoint for Railway"""
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return JsonResponse({
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "environment": os.environ.get('ENVIRONMENT', 'development'),
        "debug": settings.DEBUG
    })
