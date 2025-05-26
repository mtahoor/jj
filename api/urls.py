from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "api"

router = routers.DefaultRouter()
# Register API viewsets here when created
# Example: router.register('users', UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "businesses/approved/",
        views.get_approved_businesses,
        name="approved_businesses",
    ),
    path(
        "businesses/with-tin/",
        views.get_businesses_with_tin,
        name="businesses_with_tin",
    ),
]
