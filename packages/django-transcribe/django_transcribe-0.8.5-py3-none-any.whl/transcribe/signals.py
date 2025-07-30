"""Application Signals"""
import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TranscribeUser

logger = logging.getLogger(__file__)
User = get_user_model()


@receiver(post_save, sender=User)
def manage_user_profile(sender, instance, created, **kwargs):
    if created:
        TranscribeUser.objects.create(user=instance)


def update_staff_membership(user):
    """
    Makes sure the is_staff attribute is set on the user if they are a
    superuser of in the admin group. If they are not, make sure is_staff is
    false.
    """
    if user.groups.filter(name='Admin').exists() or user.is_superuser:
        user.is_staff = True
    else:
        user.is_staff = False


def update_user(sender, request, user, **kwargs):
    """
    Update user information when the user logs in successfully.
    """

    update_staff_membership(user)
    user.is_active = True

    user.save()


user_logged_in.connect(update_user, sender=User)
