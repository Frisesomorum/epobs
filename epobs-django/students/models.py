from django.db import models
import epobs.models as sharedModels

class Student(sharedModels.Person):
    class Meta:
        unique_together = (("first_name", "last_name", "date_of_birth"),)
