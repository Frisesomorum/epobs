from django.urls import reverse_lazy
from core.views import DeletionFormMixin, SessionRecentsMixin, ImportTool
from core.lib import QueryStringArg
from schoolauth.views import (
    SchooledListView, SchooledDetailView, SchooledCreateView, SchooledUpdateView, )
from ..models import Employee, Department
from ..resources import EmployeeResource


EMPLOYEE_DEPARTMENT = QueryStringArg(
    url_arg='department',
    queryset_arg='department',
    model=Department
)


class List(SchooledListView):
    permission_required = 'personnel.view_employee'
    model = Employee
    template_name = 'personnel/employees/list.html'
    querystring_args = (EMPLOYEE_DEPARTMENT, )


class Detail(SchooledDetailView):
    permission_required = 'personnel.view_employee'
    model = Employee
    template_name = 'personnel/employees/detail.html'
    context_object_name = 'employee'


class Create(SessionRecentsMixin, SchooledCreateView):
    permission_required = 'personnel.add_employee'
    model = Employee
    fields = ('first_name', 'last_name', 'date_of_birth', 'email',
              'department', 'external_id', )
    template_name = 'personnel/employees/create.html'
    success_url = reverse_lazy('employee-create')

    def form_valid(self, form):
        http_response = super().form_valid(form)
        self.add_object_to_session(self.object.pk)
        return http_response


class Edit(DeletionFormMixin, SchooledUpdateView):
    permission_required = 'personnel.change_employee'
    model = Employee
    fields = ('first_name', 'last_name', 'date_of_birth', 'email',
              'department', 'external_id', )
    template_name = 'personnel/employees/edit.html'
    success_url = reverse_lazy('employee-list')


class Import(ImportTool):
    permission_required = ('personnel.add_employee', 'personnel.change_employee', )
    model = Employee
    resource_class = EmployeeResource
    success_url = reverse_lazy('employee-list')
