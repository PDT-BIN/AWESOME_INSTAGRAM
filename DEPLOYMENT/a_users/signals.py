from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404

from .models import Profile


@receiver(post_save, sender=User)
def create_profile(sender, instance: User, created: bool, **kwargs) -> None:
    user = instance
    # CREATE USER, CREATE PROFILE.
    if created:
        Profile.objects.create(user=user, email=user.email)
    # UPDATE USER, UPDATE PROFILE.
    else:
        if not user.is_superuser:
            profile = get_object_or_404(Profile, user=user)
            profile.email = user.email
            profile.save()


@receiver(post_save, sender=Profile)
def update_user(sender, instance: Profile, created: bool, **kwargs) -> None:
    profile = instance
    # UPDATE PROFILE, UPDATE USER.
    if not created:
        user = get_object_or_404(User, pk=profile.user.pk)
        # AVOID INFINITE TRIGGER.
        if user.email != profile.email:
            user.email = profile.email
            user.save()
