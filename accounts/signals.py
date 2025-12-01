from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        # new user -> create profile
        profile = Profile.objects.create(
            user=instance,
            name=instance.username,
            email=instance.email
        )

        if hasattr(instance, "phone"):
            profile.phone = instance.phone

        profile.save()

    else:
        # update profile safely (only if exists)
        if hasattr(instance, "profile"):
            instance.profile.save()
