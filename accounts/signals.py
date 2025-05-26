from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """Create a Profile for new users"""
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    """Save the profile when the user is saved"""
    # Check if profile exists before saving
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        # Create profile if it doesn't exist
        Profile.objects.create(user=instance)
