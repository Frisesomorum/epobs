import datetime
from django.db import models
from core.lib import querystring_url
from schoolauth.models import School
from core.models import SingletonModel


class SiteSettings(SingletonModel):
    num_graduating_years = models.SmallIntegerField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for school in School.objects.all():
            GraduatingClass.create_for_school(school)


class SchoolProfile(models.Model):
    school = models.OneToOneField(
        School, on_delete=models.CASCADE, related_name='school_profile')

    def __str__(self):
        return self.school.name


class GraduatingClass(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE,
        related_name='graduating_classes')
    graduating_year = models.SmallIntegerField()
    label = models.CharField(max_length=255, blank=True)
    graduated = models.BooleanField(default=False)

    class Meta:
        unique_together = ('school', 'graduating_year')

    def __str__(self):
        if len(self.label) > 0:
            return self.label
        return "Class of %i" % self.graduating_year

    @classmethod
    def create_for_school(cls, school):
        current_year = datetime.datetime.now().year
        for n in range(SiteSettings.load().num_graduating_years):
            GraduatingClass.objects.get_or_create(
                school=school, graduating_year=current_year+n)

    @property
    def student_list_url(self):
        params = {'graduating_class': self.pk}
        return querystring_url('student-list', params)
