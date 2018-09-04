from django.db import models
from django.contrib.auth.models import AbstractUser
from schools.models import School


class User(AbstractUser):
    schools = models.ManyToManyField(School, blank=True, related_name='users')

    def __str__(self):
        return self.last_name + ", " + self.first_name

    def is_school_member(self, school_pk):
        if int(school_pk) in list(self.schools.values_list('pk', flat=True)):
            return True
        return False


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

    class Meta:
        abstract = True
        unique_together = (("first_name", "last_name", "date_of_birth"),)

    def __str__(self):
        return self.last_name + ', ' + self.first_name
