from django.db import models
import epobs.models as sharedModels

class Employee(sharedModels.Person):
    date_hired = models.DateField(blank=True, null=True)
    date_terminated = models.DateField(blank=True, null=True)

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    date_hired = models.DateField(blank=True, null=True)
    date_terminated = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.name
