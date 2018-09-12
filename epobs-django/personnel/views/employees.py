from django.urls import reverse_lazy
from core.views import DeletionFormMixin, SessionRecentsMixin
from schoolauth.views import (
    SchooledListView, SchooledCreateView, SchooledUpdateView, )
from ..models import Employee


class List(SchooledListView):
    permission_required = 'personnel.view_employee'
    model = Employee
    template_name = 'personnel/employees/list.html'


class Create(SessionRecentsMixin, SchooledCreateView):
    permission_required = 'personnel.add_employee'
    model = Employee
    fields = ('first_name', 'last_name', 'date_of_birth', 'email',
              'date_hired', 'date_terminated')
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
              'date_hired', 'date_terminated')
    template_name = 'personnel/employees/edit.html'
    success_url = reverse_lazy('employee-list')
