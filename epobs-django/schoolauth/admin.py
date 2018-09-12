from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from . import models


class UserCreateForm(UserCreationForm):
    class Meta:
        model = models.User
        fields = ('username', 'first_name', 'last_name', )


class UserAdmin(UserAdmin):
    add_form = UserCreateForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'first_name', 'last_name', 'username', 'password1', 'password2'),
        }),
    )
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': (
            'is_active', 'is_superuser', 'is_staff', )}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


admin.site.register(models.User, UserAdmin)


class SchoolAdmin(admin.ModelAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'location'),
        }),
    )


admin.site.register(models.School, SchoolAdmin)


class UserSchoolMembershipAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('groups')}),
    )


admin.site.register(models.UserSchoolMembership)
