import datetime
from django import forms
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.db import OperationalError
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from core.views import DeletionFormMixin, SessionRecentsMixin
from schools.views import getSchool, get_school_object_or_404, CheckSchoolContextMixin
from ..models import ExpenseTransaction, ExpenseCorrectiveJournalEntry


class ExpenseCjeForm(forms.ModelForm):
    class Meta:
        model = ExpenseCorrectiveJournalEntry
        fields = ('ledger_account', 'amount', 'employee', 'supplier', 'notes')
    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school')
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = self.fields['employee'].queryset.filter(employee__school=school)
        self.fields['supplier'].queryset = self.fields['supplier'].queryset.filter(supplier__school=school)

class detail(PermissionRequiredMixin, CheckSchoolContextMixin, DetailView):
    permission_required = 'finance.view_expensecorrectivejournalentry'
    model = ExpenseCorrectiveJournalEntry
    template_name = 'finance/expenses/cje/detail.html'
    context_object_name = 'expensecje'

class add(PermissionRequiredMixin, CreateView):
    permission_required = 'finance.add_expensecorrectivejournalentry'
    model = ExpenseCorrectiveJournalEntry
    form_class = ExpenseCjeForm
    template_name = 'finance/expenses/cje/add.html'
    success_url = '/finance/expenses/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = getSchool(self.request.session)
        return kwargs

    def get_context_data(self, **kwargs):
        context = {}
        correcting_expense = get_school_object_or_404(self.request, ExpenseTransaction, pk=self.kwargs['expense_pk'])
        correcting_expense.verify_can_be_corrected()
        context['correcting_expense'] = correcting_expense
        return super().get_context_data(**context)

    def get_initial(self):
        initial = super(CreateView, self).get_initial().copy()
        correcting_expense = get_school_object_or_404(self.request, ExpenseTransaction, pk=self.kwargs['expense_pk'])
        initial['ledger_account'] = correcting_expense.ledger_account
        initial['employee'] = correcting_expense.employee
        initial['supplier'] = correcting_expense.supplier
        initial['amount'] = correcting_expense.amount
        return initial

    def form_valid(self, form):
        expensecje = form.save(commit=False)
        expensecje.created_by = self.request.user
        expensecje.school = getSchool(self.request.session)
        expensecje.correction_to = self.get_context_data()['correcting_expense']
        expensecje.save()
        return HttpResponseRedirect(self.success_url)


class edit(PermissionRequiredMixin, CheckSchoolContextMixin, DeletionFormMixin, UpdateView):
    permission_required = 'finance.change_expensecorrectivejournalentry'
    model = ExpenseCorrectiveJournalEntry
    form_class = ExpenseCjeForm
    template_name = 'finance/expenses/cje/edit.html'
    success_url = '/finance/expenses/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = getSchool(self.request.session)
        return kwargs

    def render_to_response(self, context, **kwargs):
        expensecje = self.get_object()
        if expensecje.approval_status != 'D':
            raise OperationalError("This transaction is not in 'draft' status and cannot be edited.")
        return super().render_to_response(context, **kwargs)


@permission_required('finance.change_expensecorrectivejournalentry')
def submitForApproval(request, pk):
    expensecje = get_school_object_or_404(request, ExpenseCorrectiveJournalEntry, pk=pk)
    expensecje.submitForApproval(request.user)
    return redirect('list_expenses')

@permission_required('finance.change_expensecorrectivejournalentry')
def unsubmitForApproval(request, pk):
    expensecje = get_school_object_or_404(request, ExpenseCorrectiveJournalEntry, pk=pk)
    expensecje.unsubmitForApproval()
    return redirect('list_expenses')

@permission_required('finance.approve_expensecorrectivejournalentry')
def approve(request, pk):
    expensecje = get_school_object_or_404(request, ExpenseCorrectiveJournalEntry, pk=pk)
    user = request.user
    expensecje.approve(user)
    correcting_expense = expensecje.correction_to

    reversal_expense = ExpenseTransaction(
        ledger_account = correcting_expense.ledger_account,
        employee = correcting_expense.employee,
        supplier = correcting_expense.supplier,
        amount = -correcting_expense.amount,
        school = correcting_expense.school,
        created_by = user,
        approval_status = 'A',
        date_submitted = expensecje.date_submitted,
        submitted_by = expensecje.submitted_by,
        date_approved = expensecje.date_approved,
        approved_by = expensecje.approved_by,
        notes = expensecje.notes,
        )
    reversal_expense.save()
    expensecje.reversed_in = reversal_expense

    restatement_expense = ExpenseTransaction(
        ledger_account = expensecje.ledger_account,
        employee = expensecje.employee,
        supplier = expensecje.supplier,
        amount = expensecje.amount,
        school = expensecje.school,
        created_by = user,
        approval_status = 'A',
        date_submitted = expensecje.date_submitted,
        submitted_by = expensecje.submitted_by,
        date_approved = expensecje.date_approved,
        approved_by = expensecje.approved_by,
        notes = expensecje.notes,
        )
    restatement_expense.save()
    expensecje.restated_in = restatement_expense

    expensecje.save()
    return redirect('list_expenses')
