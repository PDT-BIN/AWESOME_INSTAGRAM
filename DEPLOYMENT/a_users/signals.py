from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from allauth.account.models import EmailAddress

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


@receiver(post_save, sender=Profile)
def update_account_email(sender, instance: Profile, created: bool, **kwargs) -> None:
    profile = instance

    if not created:
        try:
            email_address: EmailAddress = EmailAddress.objects.get_primary(profile.user)
            if email_address.email != profile.email:
                email_address.email = profile.email
                email_address.verified = False
                email_address.save()
        except:
            pass
