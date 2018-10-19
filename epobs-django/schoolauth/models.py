from django.db import models
from django.contrib.auth import models as authModels


class User(authModels.AbstractUser):
    def __str__(self):
        return '{0}, {1} [{2}]'.format(self.last_name, self.first_name, self.username)

    def get_schools(self):
        return (
            school_membership.school for
            school_membership in UserSchoolMembership.objects.filter(user=self)
        )

    def is_school_member(self, school):
        return not (self.get_school_membership(school) is None)

    def get_school_membership(self, school):
        if type(school) is int:
            return UserSchoolMembership.objects.get(user=self, school__pk=school)
        return UserSchoolMembership.objects.get(user=self, school=school)

    def has_school_perm(self, perm, school):
        school_membership = self.get_school_membership(school)
        if school_membership is None:
            return False
        if not school_membership.has_perm(perm):
            return False
        return True

    def has_school_perms(self, perms, school):
        school_membership = self.get_school_membership(school)
        if school_membership is None:
            return False
        for permission in perms:
            if not school_membership.has_perm(permission):
                return False
        return True


class School(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)

    class Meta:
        unique_together = ('name', 'location')

    def __str__(self):
        return self.name


class UserSchoolMembership(models.Model):
    """
    This is an attempt at using Django's permissions framework to define
    multiple permission sets per user, depending on the currently selected
    school. It more or less reimplements PermissionsMixin from
    django.contrib.auth.models, but removes the user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='school_perms')
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='user_perms')
    groups = models.ManyToManyField(authModels.Group, blank=True, related_name="+")

    class Meta:
        unique_together = ('user', 'school')

    def __str__(self):
        return str(self.user) + ": " + str(self.school)

    def get_all_permissions(self):
        perm_cache_name = '_group_perm_cache'
        if not hasattr(self, perm_cache_name):
            perms = set()
            for group in self.groups.all():
                for perm in group.permissions.all():
                    perms.add('%s.%s' % (perm.content_type.app_label, perm.codename))
            setattr(self, perm_cache_name, perms)
        return getattr(self, perm_cache_name)

    def has_perm(self, perm):
        return perm in self.get_all_permissions()

    def has_perms(self, perm_list):
        return all(self.has_perm(perm) for perm in perm_list)

    def has_module_perms(self, app_label):
        return any(
            perm[:perm.index('.')] == app_label
            for perm in self.get_all_permissions()
        )

    def get_groups_display(self):
        return ", ".join(group.name for group in self.groups.all())


class SchoolExternalIdManager(models.Manager):
    def get_by_external_id(self, external_id, school):
        return self.get(external_id=external_id, school=school)


class SchoolExternalId(models.Model):
    objects = SchoolExternalIdManager()
    external_id = models.CharField(max_length=31, unique=True, blank=True)

    class Meta:
        abstract = True

    @classmethod
    def id_exists(cls, external_id):
        cls.object.get(external_id)

    def generate_external_id(self):
        if len(self.external_id) > 0:
            external_id = self.external_id
        else:
            external_id = self.default_external_id()
        suffix = 1
        while True:
            if not type(self).objects.filter(external_id=external_id).exists():
                break
            elif type(self).objects.get(external_id=external_id) == self:
                break
            suffix += 1
            external_id = '{0}{1}'.format(external_id, suffix)
        return external_id

    def default_external_id(self):
        return NotImplemented

    def save(self, *args, **kwargs):
        self.external_id = self.generate_external_id()
        super().save(*args, **kwargs)
