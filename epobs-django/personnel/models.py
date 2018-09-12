from django.db import models
from core.models import Person
from schoolauth.models import School


class Employee(Person):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name='employees')
    date_hired = models.DateField(blank=True, null=True)
    date_terminated = models.DateField(blank=True, null=True)


class Supplier(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name='suppliers')
    name = models.CharField(max_length=255)
    date_hired = models.DateField(blank=True, null=True)
    date_terminated = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name
