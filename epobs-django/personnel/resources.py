from import_export import fields
from schoolauth.resources import ForeignKeyWidget, SchooledModelResource
from .models import Employee, Supplier, Department


class EmployeeResource(SchooledModelResource):
    department = fields.Field(
        attribute='department',
        widget=ForeignKeyWidget(Department, 'name'))

    class Meta:
        model = Employee
        fields = ('external_id', 'first_name', 'last_name', 'date_of_birth', 'email', 'department', )
        import_id_fields = ('external_id', )


class SupplierResource(SchooledModelResource):

    class Meta:
        model = Supplier
        fields = ('external_id', 'name', )
        import_id_fields = ('external_id', )
