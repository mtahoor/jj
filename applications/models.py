from django.db import models
from django.contrib.auth.models import User


class Application(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("under_review", "Under Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="applications"
    )
    application_type = models.CharField(max_length=100)
    reference_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    submission_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    data = models.TextField(
        blank=True, null=True
    )  # JSON data for application-specific fields

    def __str__(self):
        return f"{self.reference_number} - {self.application_type}"


class Business(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="businesses")
    name = models.CharField(max_length=255)
    business_type = models.CharField(max_length=100)
    address = models.TextField()
    category = models.CharField(max_length=100)
    reference = models.CharField(max_length=50, unique=True)
    registration_date = models.DateField()
    is_approved = models.BooleanField(default=False)
    tin = models.CharField(max_length=50, blank=True, null=True)
    has_license = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
