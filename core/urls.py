from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

# API documentation setup
schema_view = get_schema_view(
    openapi.Info(
        title="EODB API",
        default_version="v1",
        description="API for Ease of Doing Business Portal",
        contact=openapi.Contact(email="info@eodb.sc"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    # API URLs
    path("api/", include("api.urls")),
    path(
        "api-docs/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    # App URLs
    path("accounts/", include("accounts.urls")),
    path("applications/", include("applications.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("documents/", include("documents.urls")),
    path("services/", include("services.urls")),
    # Landing page URLs
    path("", include("core.landing_urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
