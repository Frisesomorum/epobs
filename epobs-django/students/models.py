from django.db import models
from core.models import Person
from schools.models import School

class Student(Person):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='students')
