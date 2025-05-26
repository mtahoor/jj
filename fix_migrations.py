import os
import django
from django.db import connection

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# Execute SQL to update the migrations table
with connection.cursor() as cursor:
    # Check if the migration is already in the table
    cursor.execute(
        "SELECT * FROM django_migrations WHERE app = 'applications' AND name = '0002_application_rejection_reason_admin_notes'"
    )
    if not cursor.fetchone():
        # Insert the migration record
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES ('applications', '0002_application_rejection_reason_admin_notes', NOW())"
        )
        print(
            "Migration '0002_application_rejection_reason_admin_notes' marked as applied."
        )
    else:
        print(
            "Migration '0002_application_rejection_reason_admin_notes' is already applied."
        )

    # Now insert our merge migration
    cursor.execute(
        "SELECT * FROM django_migrations WHERE app = 'applications' AND name = '0003_merge_20250504_0700'"
    )
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES ('applications', '0003_merge_20250504_0700', NOW())"
        )
        print("Migration '0003_merge_20250504_0700' marked as applied.")
    else:
        print("Migration '0003_merge_20250504_0700' is already applied.")

    # Now insert our remove fields migration
    cursor.execute(
        "SELECT * FROM django_migrations WHERE app = 'applications' AND name = '0004_remove_application_admin_notes_and_more'"
    )
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES ('applications', '0004_remove_application_admin_notes_and_more', NOW())"
        )
        print(
            "Migration '0004_remove_application_admin_notes_and_more' marked as applied."
        )
    else:
        print(
            "Migration '0004_remove_application_admin_notes_and_more' is already applied."
        )

    # Now insert our cleanup migration
    cursor.execute(
        "SELECT * FROM django_migrations WHERE app = 'applications' AND name = '0005_application_model_cleanup'"
    )
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES ('applications', '0005_application_model_cleanup', NOW())"
        )
        print("Migration '0005_application_model_cleanup' marked as applied.")
    else:
        print("Migration '0005_application_model_cleanup' is already applied.")

    # Now insert our add application model migration
    cursor.execute(
        "SELECT * FROM django_migrations WHERE app = 'applications' AND name = '0006_add_application_model'"
    )
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES ('applications', '0006_add_application_model', NOW())"
        )
        print("Migration '0006_add_application_model' marked as applied.")
    else:
        print("Migration '0006_add_application_model' is already applied.")

print("Done!")
