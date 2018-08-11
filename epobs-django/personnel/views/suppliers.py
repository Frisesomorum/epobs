from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from epobs.views import DeletionFormMixin, SessionRecentsMixin
from ..models import Supplier

class list(ListView):
    model = Supplier
    template_name = 'personnel/suppliers/list.html'

class add(SessionRecentsMixin, CreateView):
    model = Supplier
    fields = '__all__'
    template_name = 'personnel/suppliers/add.html'
    success_url = '/personnel/suppliers/'

    def form_valid(self, form):
        transaction = form.save()
        self.add_object_to_session(transaction.pk)
        return HttpResponseRedirect(self.request.path_info)  # Return the user to this page with a fresh form


class edit(DeletionFormMixin, UpdateView):
    model = Supplier
    fields = '__all__'
    template_name = 'personnel/suppliers/edit.html'
    success_url = '/personnel/suppliers/'
