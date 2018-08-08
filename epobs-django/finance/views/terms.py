from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from epobs.views import UpdateDeleteView
from ..models import Term

class list(ListView):
    model = Term
    template_name = 'finance/terms/list.html'

class create(CreateView):
    model = Term
    fields = '__all__'
    template_name = 'finance/terms/create.html'
    success_url = 'finance/terms/'

class edit(UpdateDeleteView):
    model = Term
    fields = '__all__'
    template_name = 'finance/terms/edit.html'
    success_url = 'finance/terms/'
