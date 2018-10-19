from django.db import models
from core.models import Person
from schoolauth.models import School, SchoolExternalId
from schools.models import GraduatingClass


class Student(SchoolExternalId, Person):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name='students')
    graduating_class = models.ForeignKey(
        GraduatingClass, on_delete=models.CASCADE, related_name='students')
    is_enrolled = models.BooleanField(default=True)

    def __str__(self):
        return '{0}, {1} [{2}]'.format(self.last_name, self.first_name, self.external_id)

    def default_external_id(self):
        return '{0}{1}'.format(self.first_name[0], self.last_name[0:6]).lower()
