from django.db import models
import epobs.models as sharedModels

class Student(sharedModels.Person):
    school = models.ForeignKey(sharedModels.School, on_delete=models.CASCADE, related_name='students')
