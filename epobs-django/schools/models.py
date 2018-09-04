from django.db import models


class School(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255)
    admission_fee = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    school_fee = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    canteen_fee = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)

    def __str__(self):
        return self.name
