from django.contrib import admin
from .models import School

class SchoolAdmin(admin.ModelAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'location'),
        }),
    )

    fieldsets = (
        (None, {'fields': ('name', 'location')}),
    )

admin.site.register(School, SchoolAdmin)
