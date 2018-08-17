import datetime
from django.db import OperationalError
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from epobs.views import DeletionFormMixin, SessionRecentsMixin
from ..models import ExpenseTransaction


class list(PermissionRequiredMixin, ListView):
    permission_required = 'finance.view_expensetransaction'
    model = ExpenseTransaction
    template_name = 'finance/expenses/list.html'

class detail(PermissionRequiredMixin, DetailView):
    permission_required = 'finance.view_expensetransaction'
    model = ExpenseTransaction
    template_name = 'finance/expenses/detail.html'
    context_object_name = 'expense'

class add(PermissionRequiredMixin, SessionRecentsMixin, CreateView):
    permission_required = 'finance.add_expensetransaction'
    model = ExpenseTransaction
    fields = ('notes', 'amount_charged', 'ledger_account', 'employee',
        'supplier', 'discount', 'quantity', 'unit_cost', 'unit_of_measure')
    template_name = 'finance/expenses/add.html'
    success_url = '/finance/expenses/'

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.created_by = self.request.user
        transaction.save()
        self.add_object_to_session(transaction.pk)
        return HttpResponseRedirect(self.request.path_info)  # Return the user to this page with a fresh form


class edit(PermissionRequiredMixin, DeletionFormMixin, UpdateView):
    permission_required = 'finance.change_expensetransaction'
    model = ExpenseTransaction
    fields = ('notes', 'amount_charged', 'ledger_account', 'employee',
        'supplier', 'discount', 'quantity', 'unit_cost', 'unit_of_measure')
    template_name = 'finance/expenses/edit.html'
    success_url = '/finance/expenses/'

    def render_to_response(self, context, **kwargs):
        expense = self.get_object()
        if expense.approval_status != 'D':
            raise OperationalError("This transaction is not in 'draft' status and cannot be edited.")
        return super().render_to_response(context, **kwargs)

def submitForApproval(request, pk):
    expense = get_object_or_404(ExpenseTransaction, pk=pk)
    if expense.approval_status != 'D':
        raise OperationalError("This transaction is not in 'draft' status and cannot be submitted for approval.")
    if not request.user.has_perm('finance.change_expensetransaction'):
        raise PermissionDenied("You do not have authorization to submit expenses for approval.")
    expense.approval_status = 'S'
    expense.submitted_by = request.user
    expense.date_submitted = datetime.date.today()
    expense.save()
    return redirect('list_expenses')

def approve(request, pk):
    expense = get_object_or_404(ExpenseTransaction, pk=pk)
    if expense.approval_status != 'S':
        raise OperationalError("This transaction is not in 'submitted' status and cannot be approved.")
    if not request.user.has_perm('finance.approve_expensetransaction'):
        raise PermissionDenied("You do not have authorization to approve expenses.")
    if expense.submitted_by == request.user:
        raise OperationalError("The same user cannot both submit and approve the same expense.")
    expense.approval_status = 'A'
    expense.approved_by = request.user
    expense.date_approved = datetime.date.today()
    expense.paid = True
    expense.when_paid = datetime.datetime.now()
    expense.save()
    return redirect('list_expenses')
