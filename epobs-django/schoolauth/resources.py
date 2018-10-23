from import_export import resources, widgets, instance_loaders
from .models import User, School, UserSchoolMembership


class UserResource(resources.ModelResource):

    class Meta:
        model = User


class SchoolResource(resources.ModelResource):

    class Meta:
        model = School


class UserSchoolMembershipResource(resources.ModelResource):

    class Meta:
        model = UserSchoolMembership


class SchooledModelInstanceLoader(instance_loaders.ModelInstanceLoader):
    school = None

    def __init__(self, resource, dataset=None):
        super().__init__(resource, dataset)
        if hasattr(resource, 'school'):
            self.school = resource.school

    def get_instance(self, row):
        import_id_fields = self.resource.get_import_id_fields()
        if len(import_id_fields) == 0:
            return None
        try:
            params = {}
            params['school'] = self.school
            for key in import_id_fields:
                field = self.resource.fields[key]
                params[field.attribute] = field.clean(row)
            return self.get_queryset().get(**params)
        except self.resource._meta.model.DoesNotExist:
            return None


class BooleanWidget(widgets.BooleanWidget):
    # Overrides the default widget by allowing 'true' and 't' string values for True
    TRUE_VALUES = ["True", "T", "1", 1]
    FALSE_VALUE = "False"

    def clean(self, value, row=None, *args, **kwargs):
        if isinstance(value, str):
            value = value.capitalize()
        return super().clean(value, row=None, *args, **kwargs)


class ForeignKeyWidget(widgets.ForeignKeyWidget):

    def clean(self, value, row=None, *args, **kwargs):
        # Overrides the default behavior by allowing case-insensitive lookups
        if value:
            field_kwargs = {'{0}__{1}'.format(self.field, 'iexact'): value}
            return self.get_queryset(value, row, *args, **kwargs).get(**field_kwargs)
        else:
            return None


class SchooledForeignKeyWidget(ForeignKeyWidget):
    school = None

    def __init__(self, model, field='pk', *args, **kwargs):
        school = kwargs.pop('school')
        super().__init__(model, field, *args, **kwargs)
        self.school = school

    def get_queryset(self, value, row, *args, **kwargs):
        queryset = super().get_queryset(value, row, *args, **kwargs)
        if hasattr(self.model, 'school_filter_queryset'):
            return self.model.school_filter_queryset(queryset, self.school)
        return queryset.filter(school=self.school)


class SchooledExternalIdWidget(SchooledForeignKeyWidget):

    def __init__(self, model, field='external_id', *args, **kwargs):
        super().__init__(model, field, *args, **kwargs)

    def clean(self, value, row=None, *args, **kwargs):
        if value:
            return self.model.objects.get_by_external_id(value, self.school)
        else:
            return None

    def render(self, value, obj=None):
        if value is None:
            return ""
        return str(value)


class SchooledModelResource(resources.ModelResource):
    school = None
    WIDGETS_MAP = resources.ModelResource.WIDGETS_MAP
    for key in WIDGETS_MAP:
        if WIDGETS_MAP[key] == widgets.BooleanWidget:
            WIDGETS_MAP[key] = BooleanWidget

    class Meta:
        instance_loader_class = SchooledModelInstanceLoader

    def __init__(self, **kwargs):
        super().__init__()
        self.school = kwargs.get('school')

    def init_instance(self, row=None):
        instance = super().init_instance(row=None)
        instance.school = self.school
        return instance
