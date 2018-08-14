from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from epobs.views import DeletionFormMixin, SessionRecentsMixin
from ..models import Supplier
from finance.models import SupplierAccount

class list(PermissionRequiredMixin, ListView):
    permission_required = 'personnel.view_supplier'
    model = Supplier
    template_name = 'personnel/suppliers/list.html'

class add(PermissionRequiredMixin, SessionRecentsMixin, CreateView):
    permission_required = 'personnel.add_supplier'
    model = Supplier
    fields = '__all__'
    template_name = 'personnel/suppliers/add.html'
    success_url = '/personnel/suppliers/'

    def form_valid(self, form):
        supplier = form.save()
        self.add_object_to_session(supplier.pk)
        account = SupplierAccount.objects.create(supplier=supplier)
        return HttpResponseRedirect(self.request.path_info)  # Return the user to this page with a fresh form


class edit(PermissionRequiredMixin, DeletionFormMixin, UpdateView):
    permission_required = 'personnel.change_supplier'
    model = Supplier
    fields = '__all__'
    template_name = 'personnel/suppliers/edit.html'
    success_url = '/personnel/suppliers/'
