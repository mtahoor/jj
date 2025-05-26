from django.urls import path
from . import views
from . import views_business_license
from . import views_tax_compliance

app_name = "applications"

urlpatterns = [
    path("", views.application_list, name="list"),
    path("<int:pk>/", views.application_detail, name="detail"),
    path("create/", views.application_create, name="create"),
    path(
        "create/business-registration/",
        views.create_business_registration,
        name="create_business_registration",
    ),
    path(
        "create/tax-compliance/",
        views.create_tax_compliance,
        name="create_tax_compliance",
    ),
    path(
        "create/business-license/",
        views.create_business_license,
        name="create_business_license",
    ),
    path(
        "business-license/",
        views_business_license.business_license_form,
        name="business_license_form",
    ),
    path(
        "tax-compliance/",
        views_tax_compliance.tax_compliance_form,
        name="tax_compliance_form",
    ),
    path(
        "tax-compliance/<int:business_id>/",
        views.apply_tax_compliance,
        name="apply_tax_compliance",
    ),
]
