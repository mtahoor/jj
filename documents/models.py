from django.db import models


class Document(models.Model):
    CATEGORY_CHOICES = (
        ("guide", "Guide"),
        ("form", "Form"),
        ("policy", "Policy"),
        ("regulation", "Regulation"),
    )

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    file = models.FileField(upload_to="documents/")
    upload_date = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.title
