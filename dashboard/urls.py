from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="home"),
    path("admin/", views.admin_dashboard, name="admin"),
    path("review-applications/", views.review_applications, name="review_applications"),
    path(
        "applications/<int:pk>/",
        views.admin_application_detail,
        name="application_detail",
    ),
]
