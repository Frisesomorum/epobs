from schoolauth.resources import SchooledModelResource, SchooledForeignKeyWidget
from schools.models import GraduatingClass
from .models import Student


class StudentResource(SchooledModelResource):

    class Meta:
        model = Student
        fields = (
            'external_id', 'first_name', 'last_name', 'date_of_birth',
            'email', 'graduating_class', 'is_enrolled', )
        import_id_fields = ('external_id', )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['graduating_class'].widget = SchooledForeignKeyWidget(
            GraduatingClass, 'graduating_year', school=self.school)
