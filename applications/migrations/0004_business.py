from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("applications", "0003_merge_20250504_0700"),
    ]

    operations = [
        migrations.CreateModel(
            name="Business",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("business_type", models.CharField(max_length=100)),
                ("address", models.TextField()),
                ("category", models.CharField(max_length=100)),
                ("reference", models.CharField(max_length=50, unique=True)),
                ("registration_date", models.DateField()),
                ("is_approved", models.BooleanField(default=False)),
                ("tin", models.CharField(blank=True, max_length=50, null=True)),
                ("has_license", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="businesses",
                        to="auth.user",
                    ),
                ),
            ],
        ),
    ]
