from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from core.models import Person
from core.lib import querystring_url
from schoolauth.models import School, SchoolExternalId
from schools.models import GraduatingClass


class Student(SchoolExternalId, Person):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name='students')
    graduating_year = models.SmallIntegerField(blank=True, null=True)
    is_enrolled = models.BooleanField(default=True)

    def __str__(self):
        return '{0}, {1} [{2}]'.format(self.last_name, self.first_name, self.external_id)

    def default_external_id(self):
        return '{0}{1}'.format(self.first_name[0], self.last_name[0:6]).lower()

    @property
    def graduating_class(self):
        if self.graduating_year is None:
            return None
        try:
            graduating_class = GraduatingClass.objects.get(school=self.school, graduating_year=self.graduating_year)
        except ObjectDoesNotExist:
            return None
        return graduating_class

    @property
    def revenue_list_url(self):
        params = {'student': self.account.pk}
        return querystring_url('revenue-list', params)

    @property
    def revenue_create_url(self):
        params = {'student': self.account.pk}
        return querystring_url('revenue-create', params)
