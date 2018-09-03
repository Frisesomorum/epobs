from django.db import models
import epobs.models as sharedModels

class Employee(sharedModels.Person):
    school = models.ForeignKey(sharedModels.School, on_delete=models.CASCADE, related_name='employees')
    date_hired = models.DateField(blank=True, null=True)
    date_terminated = models.DateField(blank=True, null=True)

class Supplier(models.Model):
    school = models.ForeignKey(sharedModels.School, on_delete=models.CASCADE, related_name='suppliers')
    name = models.CharField(max_length=255)
    date_hired = models.DateField(blank=True, null=True)
    date_terminated = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.name
