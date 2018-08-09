from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from epobs.views import DeletionFormMixin
from ..models import RevenueTransaction

class list(ListView):
    model = RevenueTransaction
    template_name = 'finance/revenues/list.html'

class add(CreateView):
    model = RevenueTransaction
    fields = '__all__'
    template_name = 'finance/revenues/add.html'
    success_url = 'finance/revenues/'

class edit(DeletionFormMixin, UpdateView):
    model = RevenueTransaction
    fields = '__all__'
    template_name = 'finance/revenues/edit.html'
    success_url = 'finance/revenues/'
