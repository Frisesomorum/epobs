import datetime
from import_export import fields, widgets, results
from schoolauth.resources import ForeignKeyWidget, SchooledModelResource
from .models import Employee, Supplier, Department


class PayeeResource(SchooledModelResource):
    date_hired = fields.Field(widget=widgets.DateWidget())

    def after_import_row(self, row, row_result, **kwargs):
        super().after_import_row(row, row_result, **kwargs)
        if row_result.import_type == results.RowResult.IMPORT_TYPE_NEW:
            date_hired = widgets.DateWidget().clean(row.get('date_hired'))
            if date_hired is not None and date_hired <= datetime.date.today():
                instance = self._meta.model.objects.get(pk=row_result.object_id)
                instance.payee.start_contract(date_hired)


class EmployeeResource(PayeeResource):
    department = fields.Field(
        attribute='department',
        widget=ForeignKeyWidget(Department, 'name'))

    class Meta:
        model = Employee
        fields = (
            'external_id', 'first_name', 'last_name', 'date_of_birth',
            'email', 'department', 'date_hired', )
        import_id_fields = ('external_id', )


class SupplierResource(PayeeResource):

    class Meta:
        model = Supplier
        fields = ('external_id', 'name', 'date_hired', )
        import_id_fields = ('external_id', )
