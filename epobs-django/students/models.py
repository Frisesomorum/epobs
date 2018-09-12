from django.db import models
from core.models import Person
from schoolauth.models import School


class Student(Person):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name='students')
