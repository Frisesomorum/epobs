from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from epobs.views import DeletionFormMixin
from ..models import Employee

class list(ListView):
    model = Employee
    template_name = 'personnel/employees/list.html'

class add(CreateView):
    model = Employee
    fields = '__all__'
    template_name = 'personnel/employees/add.html'
    success_url = '/personnel/employees/'

class edit(DeletionFormMixin, UpdateView):
    model = Employee
    fields = '__all__'
    template_name = 'personnel/employees/edit.html'
    success_url = '/personnel/employees/'
