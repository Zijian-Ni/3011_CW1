"""
URL configuration for sportspulse project.

The API lives under /api/ and documentation is served at /api/docs/.
The admin site is kept at /admin/ for database management (Lecture 6, slide 9).
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from .views import admin_portal, dashboard, fan_portal

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('fan/', fan_portal, name='fan-portal'),
    path('admin-portal/', admin_portal, name='admin-portal'),

    # Admin site for manual data management
    path('admin/', admin.site.urls),

    # API endpoints — all routed through the api app
    path('api/', include('api.urls')),

    # OpenAPI schema (machine-readable JSON)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    # Interactive Swagger UI documentation
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),

    # Alternative ReDoc documentation view
    path(
        'api/redoc/',
        SpectacularRedocView.as_view(url_name='schema'),
        name='redoc',
    ),
]
