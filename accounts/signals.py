from django.db.models.signals  import post_save
from django.dispatch import receiver
from accounts.models import User
from .models import Profile




@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)

        # auto copy user data
        profile.name = instance.username
        profile.email = instance.email
        
        # custom User phone copy
        if hasattr(instance, "phone"):
            profile.phone = instance.phone

        profile.save()
    else:
        instance.profile.save()
