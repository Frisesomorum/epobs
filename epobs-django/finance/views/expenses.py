from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from epobs.views import DeletionFormMixin, SessionRecentsMixin
from ..models import ExpenseTransaction


class list(PermissionRequiredMixin, ListView):
    permission_required = 'finance.view_expensetransaction'
    model = ExpenseTransaction
    template_name = 'finance/expenses/list.html'

class add(PermissionRequiredMixin, SessionRecentsMixin, CreateView):
    permission_required = 'finance.add_expensetransaction'
    model = ExpenseTransaction
    fields = '__all__'
    template_name = 'finance/expenses/add.html'
    success_url = '/finance/expenses/'

    def form_valid(self, form):
        transaction = form.save()
        self.add_object_to_session(transaction.pk)
        return HttpResponseRedirect(self.request.path_info)  # Return the user to this page with a fresh form


class edit(PermissionRequiredMixin, DeletionFormMixin, UpdateView):
    permission_required = 'finance.change_expensetransaction'
    model = ExpenseTransaction
    fields = '__all__'
    template_name = 'finance/expenses/edit.html'
    success_url = '/finance/expenses/'
