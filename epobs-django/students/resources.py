from schoolauth.resources import SchooledModelResource
from .models import Student


class StudentResource(SchooledModelResource):

    class Meta:
        model = Student
        fields = (
            'external_id', 'first_name', 'last_name', 'date_of_birth',
            'email', 'graduating_year', 'is_enrolled', )
        import_id_fields = ('external_id', )
