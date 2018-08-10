from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from epobs.views import DeletionFormMixin
from ..models import Supplier

class list(ListView):
    model = Supplier
    template_name = 'personnel/suppliers/list.html'

class add(CreateView):
    model = Supplier
    fields = '__all__'
    template_name = 'personnel/suppliers/add.html'
    success_url = '/personnel/suppliers/'

class edit(DeletionFormMixin, UpdateView):
    model = Supplier
    fields = '__all__'
    template_name = 'personnel/suppliers/edit.html'
    success_url = '/personnel/suppliers/'
