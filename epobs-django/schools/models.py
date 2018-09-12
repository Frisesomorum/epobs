from django.db import models
from schoolauth.models import School


class SchoolProfile(models.Model):
    school = models.OneToOneField(
        School, on_delete=models.CASCADE, related_name='school_profile')
    admission_fee = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    school_fee = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    canteen_fee = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return self.school.name
