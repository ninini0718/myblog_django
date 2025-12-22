from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    用户创建时，保证一定且只会有一个 profile
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)
