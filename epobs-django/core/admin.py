from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from .models import User

class UserCreateForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name' , 'last_name', 'groups', 'schools')

class UserAdmin(UserAdmin):
    add_form = UserCreateForm

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'username', 'groups', 'schools', 'password1', 'password2'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_superuser', 'is_staff', 'groups', 'schools')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

admin.site.register(User, UserAdmin)
