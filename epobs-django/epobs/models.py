"""
Shared data model classes
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class School(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    admission_fee = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    school_fee = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    canteen_fee = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    # TODO: define static set/get methods

    def save(self, *args, **kwargs):
        if School.objects.exists() and not self.pk:
            raise ValidationError('There can be only one instance of the School class.')
        return super(School, self).save(*args, **kwargs)

class User(AbstractUser):
    pass


class Descriptor(models.Model):
    name = models.CharField(max_length=255, unique=True)
    abbreviation = models.CharField(max_length=15)
    description = models.TextField(max_length=4000, blank=True)
    class Meta:
        abstract = True
    def __str__(self):
        return self.name

class Person(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    email = models.EmailField(blank=True, null=True)
    def __str__(self):
        return self.last_name + ', ' + self.first_name

    class Meta:
        abstract = True
        unique_together = (("first_name", "last_name", "date_of_birth"),)
