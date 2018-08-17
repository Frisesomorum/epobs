import datetime
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from epobs.views import DeletionFormMixin,SessionRecentsMixin
from ..models import RevenueTransaction

class list(PermissionRequiredMixin, ListView):
    permission_required = 'finance.view_revenuetransaction'
    model = RevenueTransaction
    template_name = 'finance/revenues/list.html'

class detail(PermissionRequiredMixin, DetailView):
    permission_required = 'finance.view_revenuetransaction'
    model = RevenueTransaction
    template_name = 'finance/revenues/detail.html'
    context_object_name = 'revenue'

class add(PermissionRequiredMixin, SessionRecentsMixin, CreateView):
    permission_required = 'finance.add_revenuetransaction'
    model = RevenueTransaction
    fields = ('ledger_account', 'amount_charged', 'paid', 'partial_amount_paid',
        'student', 'notes')
    template_name = 'finance/revenues/add.html'
    success_url = '/finance/revenues/'

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.created_by = self.request.user
        if transaction.paid:
            transaction.when_paid = datetime.datetime.now()
        transaction.save()
        self.add_object_to_session(transaction.pk)
        return HttpResponseRedirect(self.request.path_info)  # Return the user to this page with a fresh form
