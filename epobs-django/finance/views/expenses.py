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


class list(PermissionRequiredMixin, ListView):
    permission_required = 'finance.view_expensetransaction'
    model = ExpenseTransaction
    template_name = 'finance/expenses/list.html'

    def get_queryset(self):
        return ExpenseTransaction.objects.filter(school=getSchool(self.request.session))

    def get_context_data(self, **kwargs):
        context = {}
        context['cje_list'] = ExpenseCorrectiveJournalEntry.objects.filter(school=getSchool(self.request.session)).exclude(approval_status='A')
        return super().get_context_data(**context)

class detail(PermissionRequiredMixin, CheckSchoolContextMixin, DetailView):
    permission_required = 'finance.view_expensetransaction'
    model = ExpenseTransaction
    template_name = 'finance/expenses/detail.html'
    context_object_name = 'expense'

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = ExpenseTransaction
        fields = ('ledger_account', 'amount', 'employee', 'supplier',
             'discount', 'quantity', 'unit_cost', 'unit_of_measure', 'notes')
    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school')
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = self.fields['employee'].queryset.filter(employee__school=school)
        self.fields['supplier'].queryset = self.fields['supplier'].queryset.filter(supplier__school=school)

class add(PermissionRequiredMixin, SessionRecentsMixin, CreateView):
    permission_required = 'finance.add_expensetransaction'
    model = ExpenseTransaction
    form_class = ExpenseForm
    template_name = 'finance/expenses/add.html'
    success_url = '/finance/expenses/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = getSchool(self.request.session)
        return kwargs

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.created_by = self.request.user
        transaction.school = getSchool(self.request.session)
        transaction.save()
        self.add_object_to_session(transaction.pk)
        return HttpResponseRedirect(self.request.path_info)  # Return the user to this page with a fresh form


class edit(PermissionRequiredMixin, CheckSchoolContextMixin, DeletionFormMixin, UpdateView):
    permission_required = 'finance.change_expensetransaction'
    model = ExpenseTransaction
    form_class = ExpenseForm
    template_name = 'finance/expenses/edit.html'
    success_url = '/finance/expenses/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = getSchool(self.request.session)
        return kwargs

    def render_to_response(self, context, **kwargs):
        expense = self.get_object()
        if expense.approval_status != 'D':
            raise OperationalError("This transaction is not in 'draft' status and cannot be edited.")
        return super().render_to_response(context, **kwargs)

@permission_required('finance.change_expensetransaction')
def submitForApproval(request, pk):
    expense = get_school_object_or_404(request, ExpenseTransaction, pk=pk)
    expense.submitForApproval(request.user)
    return redirect('list_expenses')

@permission_required('finance.change_expensetransaction')
def unsubmitForApproval(request, pk):
    expense = get_school_object_or_404(request, ExpenseTransaction, pk=pk)
    expense.unsubmitForApproval()
    return redirect('list_expenses')

@permission_required('finance.approve_expensetransaction')
def approve(request, pk):
    expense = get_school_object_or_404(request, ExpenseTransaction, pk=pk)
    expense.approve(request.user)
    return redirect('list_expenses')
