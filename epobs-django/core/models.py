from django.db import models


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
