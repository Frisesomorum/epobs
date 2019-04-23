from django.db import models
from django.urls import reverse
from core.lib import querystring_url
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
    graduating_year = models.SmallIntegerField()
    label = models.CharField(max_length=255, blank=True, verbose_name='class name')
    graduated = models.BooleanField(default=False)

    class Meta:
        unique_together = ('school', 'graduating_year')

    def __str__(self):
        if len(self.label) > 0:
            return self.label
        return "Class of %i" % self.graduating_year

    def get_absolute_url(self):
        return reverse('class-edit', args=[str(self.id)])

    @property
    def student_list_url(self):
        params = {'graduating_year': self.graduating_year}
        return querystring_url('student-list', params)
