from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from epobs.views import DeletionFormMixin, SessionRecentsMixin
from ..models import Employee
from finance.models import EmployeeAccount

class list(ListView):
    model = Employee
    template_name = 'personnel/employees/list.html'

class add(SessionRecentsMixin, CreateView):
    model = Employee
    fields = '__all__'
    template_name = 'personnel/employees/add.html'
    success_url = '/personnel/employees/'

    def form_valid(self, form):
        employee = form.save()
        self.add_object_to_session(employee.pk)
        account = EmployeeAccount.objects.create(employee=employee)
        return HttpResponseRedirect(self.request.path_info)  # Return the user to this page with a fresh form


class edit(DeletionFormMixin, UpdateView):
    model = Employee
    fields = '__all__'
    template_name = 'personnel/employees/edit.html'
    success_url = '/personnel/employees/'
