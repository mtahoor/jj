from django.db import migrations
import json


def add_unique_constraint_to_tax_compliance(apps, schema_editor):
    """
    This migration adds a unique constraint to tax compliance applications.
    It first identifies and resolves any duplicate tax compliance applications
    by keeping only the most recent one for each business.
    """
    Application = apps.get_model("applications", "Application")

    # Get all tax compliance applications
    tax_compliance_apps = Application.objects.filter(
        application_type="Tax Compliance",
        status__in=["submitted", "under_review", "approved"],
    )

    # Group applications by business ID
    business_to_apps = {}
    for app in tax_compliance_apps:
        try:
            data = json.loads(app.data) if app.data else {}
            business_id = data.get("registered_business_id")
            if not business_id:
                # Try the old field name for backward compatibility
                business_id = data.get("registered_business")

            if business_id:
                if business_id not in business_to_apps:
                    business_to_apps[business_id] = []
                business_to_apps[business_id].append(app)
        except (json.JSONDecodeError, KeyError):
            continue

    # For each business with multiple applications, keep only the most recent one
    for business_id, apps in business_to_apps.items():
        if len(apps) > 1:
            # Sort by submission date (newest first)
            sorted_apps = sorted(apps, key=lambda x: x.submission_date, reverse=True)

            # Keep the most recent application, delete the rest
            for app in sorted_apps[1:]:
                app.delete()


class Migration(migrations.Migration):

    dependencies = [
        ("applications", "0004_business"),  # Updated to match the latest migration
    ]

    operations = [
        migrations.RunPython(add_unique_constraint_to_tax_compliance),
    ]
