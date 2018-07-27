from django.db import models
import epobs.models as sharedModels

class Employee(sharedModels.Person):
    date_hired = models.DateField()
    date_terminated = models.DateField()

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    date_hired = models.DateField()
    date_terminated = models.DateField()
