from import_export.admin import ImportExportModelAdmin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from . import models, resources


class ImportExportModelAdmin21(ImportExportModelAdmin):
    def get_export_queryset(self, request):
            """
            Returns export queryset.
            Default implementation respects applied search and filters.
            """
            list_display = self.get_list_display(request)
            list_display_links = self.get_list_display_links(request, list_display)
            list_filter = self.get_list_filter(request)
            search_fields = self.get_search_fields(request)
            if self.get_actions(request):
                list_display = ['action_checkbox'] + list(list_display)

            ChangeList = self.get_changelist(request)
            cl = ChangeList(request, self.model, list_display,
                            list_display_links, list_filter, self.date_hierarchy,
                            search_fields, self.list_select_related, self.list_per_page,
                            self.list_max_show_all, self.list_editable, self, self.sortable_by
                            )

            return cl.get_queryset(request)


class UserCreateForm(UserCreationForm):
    class Meta:
        model = models.User
        fields = ('username', 'first_name', 'last_name', )


class UserAdmin(ImportExportModelAdmin21, UserAdmin):
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
    resource_class = resources.UserResource


admin.site.register(models.User, UserAdmin)


class SchoolAdmin(ImportExportModelAdmin21, admin.ModelAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'location'),
        }),
    )
    resource_class = resources.SchoolResource


admin.site.register(models.School, SchoolAdmin)


class UserSchoolMembershipAdmin(ImportExportModelAdmin21, admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('user', 'school', 'groups', )}),
    )
    resource_class = resources.UserSchoolMembershipResource


admin.site.register(models.UserSchoolMembership, UserSchoolMembershipAdmin)
