from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from epobs.views import DeletionFormMixin, SessionRecentsMixin, CheckSchoolContextMixin, getSchool
from ..models import Employee
from finance.models import EmployeeAccount

class list(PermissionRequiredMixin, ListView):
    permission_required = 'personnel.view_employee'
    model = Employee
    template_name = 'personnel/employees/list.html'
    def get_queryset(self):
        return Employee.objects.filter(school=getSchool(self.request.session))

class add(PermissionRequiredMixin, SessionRecentsMixin, CreateView):
    permission_required = 'personnel.add_employee'
    model = Employee
    fields = ('first_name', 'last_name', 'date_of_birth', 'email', 'date_hired', 'date_terminated')
    template_name = 'personnel/employees/add.html'
    success_url = '/personnel/employees/'

    def form_valid(self, form):
        employee = form.save(commit=False)
        employee.school = getSchool(self.request.session)
        employee.save()
        self.add_object_to_session(employee.pk)
        account = EmployeeAccount.objects.create(employee=employee)
        return HttpResponseRedirect(self.request.path_info)  # Return the user to this page with a fresh form


class edit(PermissionRequiredMixin, CheckSchoolContextMixin, DeletionFormMixin, UpdateView):
    permission_required = 'personnel.change_employee'
    model = Employee
    fields = ('first_name', 'last_name', 'date_of_birth', 'email', 'date_hired', 'date_terminated')
    template_name = 'personnel/employees/edit.html'
    success_url = '/personnel/employees/'
