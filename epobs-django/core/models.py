from django.db import models


class SingletonModel(models.Model):

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


class DescriptorManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class Descriptor(models.Model):
    objects = DescriptorManager()
    name = models.CharField(max_length=255, unique=True)
    abbreviation = models.CharField(max_length=15, blank=True)
    description = models.TextField(max_length=4000, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name, )

    def abbv(self):
        if hasattr(self, 'abbreviation'):
            return self.abbreviation
        name = self.name
        return (name[:13] + '..') if len(name) > 15 else name


class Person(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    email = models.EmailField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.last_name + ', ' + self.first_name
