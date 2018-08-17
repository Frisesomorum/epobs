import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.db import OperationalError
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from epobs.views import DeletionFormMixin, SessionRecentsMixin
from ..models import ExpenseTransaction, ExpenseCorrectiveJournalEntry


class detail(PermissionRequiredMixin, DetailView):
    permission_required = 'finance.view_expensecorrectivejournalentry'
    model = ExpenseCorrectiveJournalEntry
    template_name = 'finance/expenses/cje/detail.html'
    context_object_name = 'expensecje'

class add(PermissionRequiredMixin, CreateView):
    permission_required = 'finance.add_expensecorrectivejournalentry'
    model = ExpenseCorrectiveJournalEntry
    fields = ('ledger_account', 'amount_charged', 'employee', 'supplier', 'notes')
    template_name = 'finance/expenses/cje/add.html'
    success_url = '/finance/expenses/'

    def get_context_data(self, **kwargs):
        context = {}
        correcting_expense = get_object_or_404(ExpenseTransaction, pk=self.kwargs['expense_pk'])
        if correcting_expense.corrected_by_cje:
            raise OperationalError("This transaction already has a corrective journal entry attached to it.")
        if correcting_expense.reversal_for_cje:
            raise OperationalError("This transaction reverses an erroneous transaction and cannot be revised.")
        if correcting_expense.approval_status != 'A':
            raise OperationalError("This transaction is not yet approved. If you need to make changes, revert the status to draft.")
        context['correcting_expense'] = correcting_expense
        return super().get_context_data(**context)

    def get_initial(self):
        initial = super(CreateView, self).get_initial().copy()
        correcting_expense = get_object_or_404(ExpenseTransaction, pk=self.kwargs['expense_pk'])
        initial['ledger_account'] = correcting_expense.ledger_account
        initial['employee'] = correcting_expense.employee
        initial['supplier'] = correcting_expense.supplier
        initial['amount_charged'] = correcting_expense.amount_charged
        return initial

    def form_valid(self, form):
        expensecje = form.save(commit=False)
        expensecje.created_by = self.request.user
        expensecje.save()
        correcting_expense = self.get_context_data()['correcting_expense']
        correcting_expense.corrected_by_cje = expensecje
        correcting_expense.save()
        return HttpResponseRedirect(self.success_url)


class edit(PermissionRequiredMixin, DeletionFormMixin, UpdateView):
    permission_required = 'finance.change_expensecorrectivejournalentry'
    model = ExpenseCorrectiveJournalEntry
    fields = ('ledger_account', 'amount_charged', 'employee', 'supplier', 'notes')
    template_name = 'finance/expenses/cje/edit.html'
    success_url = '/finance/expenses/'

    def render_to_response(self, context, **kwargs):
        expensecje = self.get_object()
        if expensecje.approval_status != 'D':
            raise OperationalError("This transaction is not in 'draft' status and cannot be edited.")
        return super().render_to_response(context, **kwargs)


@permission_required('finance.change_expensecorrectivejournalentry')
def submitForApproval(request, pk):
    expensecje = get_object_or_404(ExpenseCorrectiveJournalEntry, pk=pk)
    expensecje.submitForApproval(request.user)
    return redirect('list_expenses')

@permission_required('finance.change_expensecorrectivejournalentry')
def unsubmitForApproval(request, pk):
    expensecje = get_object_or_404(ExpenseCorrectiveJournalEntry, pk=pk)
    expensecje.unsubmitForApproval()
    return redirect('list_expenses')

@permission_required('finance.approve_expensecorrectivejournalentry')
def approve(request, pk):
    expensecje = get_object_or_404(ExpenseCorrectiveJournalEntry, pk=pk)
    user = request.user
    expensecje.approve(user)
    correcting_expense = expensecje.correction_to

    reversal_expense = ExpenseTransaction(
        ledger_account = correcting_expense.ledger_account,
        employee = correcting_expense.employee,
        supplier = correcting_expense.supplier,
        amount_charged = -correcting_expense.amount_charged,
        created_by = user,
        paid = True,
        when_paid = datetime.datetime.now(),
        approval_status = 'A',
        date_submitted = expensecje.date_submitted,
        submitted_by = expensecje.submitted_by,
        date_approved = expensecje.date_approved,
        approved_by = expensecje.approved_by,
        notes = expensecje.notes,
        reversal_for_cje = expensecje
        )
    reversal_expense.save()

    restatement_expense = ExpenseTransaction(
        ledger_account = expensecje.ledger_account,
        employee = expensecje.employee,
        supplier = expensecje.supplier,
        amount_charged = expensecje.amount_charged,
        created_by = user,
        paid = True,
        when_paid = datetime.datetime.now(),
        approval_status = 'A',
        date_submitted = expensecje.date_submitted,
        submitted_by = expensecje.submitted_by,
        date_approved = expensecje.date_approved,
        approved_by = expensecje.approved_by,
        notes = expensecje.notes,
        restatement_for_cje = expensecje
        )
    restatement_expense.save()
    return redirect('list_expenses')
