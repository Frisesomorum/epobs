from django.db import models
from schoolauth.models import School


class SchoolProfile(models.Model):
    school = models.OneToOneField(
        School, on_delete=models.CASCADE, related_name='school_profile')

    def __str__(self):
        return self.school.name


class GraduatingClass(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE,
        related_name='graduating_classes')
    graduating_year = models.SmallIntegerField(unique=True)
    label = models.CharField(max_length=255, blank=True)
    admission_fee = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    school_fee = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    canteen_fee = models.DecimalField(
        max_digits=15, decimal_places=2, default=0)
    graduated = models.BooleanField(default=False)

    def __str__(self):
        if len(self.label) > 0:
            return self.label
        return "Class of %i" % self.graduating_year
