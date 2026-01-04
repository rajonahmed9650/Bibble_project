from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

@receiver(post_save, sender=User)
def create_profile_on_signup(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            
            name=instance.username or instance.full_name,
            email=instance.email,
            phone=getattr(instance, "phone", None),
        )
