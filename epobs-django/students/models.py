from django.db import models
from core.models import Person
from schoolauth.models import School
from schools.models import GraduatingClass


class Student(Person):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name='students')
    graduating_class = models.ForeignKey(
        GraduatingClass, on_delete=models.CASCADE, related_name='students')
    is_enrolled = models.BooleanField(default=True)
