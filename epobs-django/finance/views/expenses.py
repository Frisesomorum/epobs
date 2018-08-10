from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from epobs.views import DeletionFormMixin
from ..models import ExpenseTransaction

class list(ListView):
    model = ExpenseTransaction
    template_name = 'finance/expenses/list.html'

class add(CreateView):
    model = ExpenseTransaction
    fields = '__all__'
    template_name = 'finance/expenses/add.html'
    success_url = '/finance/expenses/'

class edit(DeletionFormMixin, UpdateView):
    model = ExpenseTransaction
    fields = '__all__'
    template_name = 'finance/expenses/edit.html'
    success_url = '/finance/expenses/'
