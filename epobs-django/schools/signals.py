from schoolauth.models import School
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SchoolProfile


@receiver(post_save, sender=School, dispatch_uid="create_linked_school_profile")
def create_school_profile(sender, instance, created, **kwargs):
    if created:
        SchoolProfile.objects.create(school=instance)
