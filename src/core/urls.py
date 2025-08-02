from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from .health_views import health_check, simple_health_check

urlpatterns = [
      path('admin/', admin.site.urls),
      path('api/v1/health/', health_check, name='health_check'),
      path('health/', simple_health_check, name='simple_health_check'),
      path('', include('users.urls')),  # This includes auth/login/ and auth/signup/
      path('stores/', include('stores.urls')),
      path('api/v1/', include('orders.urls')),
      path('api/v1/', include('stores.api_urls')),
      path('', include('django.contrib.auth.urls')),
      path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
      path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
