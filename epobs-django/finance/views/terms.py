from django import forms
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http.response import HttpResponseRedirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from core.views import DeletionFormMixin
from schools.views import getSchool, CheckSchoolContextMixin
from ..models import (
    Term, ExpenseBudgetItem, RevenueBudgetItem, ExpenseLedgerAccount,
    RevenueLedgerAccount)


class list(PermissionRequiredMixin, ListView):
    permission_required = 'finance.view_term'
    model = Term
    template_name = 'finance/terms/list.html'

    def get_queryset(self):
        return Term.objects.filter(school=getSchool(self.request.session))


class create(PermissionRequiredMixin, CreateView):
    permission_required = 'finance.add_term'
    model = Term
    fields = ('name', 'start', 'end')
    template_name = 'finance/terms/create.html'
    success_url = '/finance/terms/'

    def form_valid(self, form):
        term = form.save(commit=False)
        term.school = getSchool(self.request.session)
        term.save()
        return HttpResponseRedirect(self.get_success_url())


class edit(
        PermissionRequiredMixin, CheckSchoolContextMixin,
        DeletionFormMixin, UpdateView):
    permission_required = 'finance.change_term'
    model = Term
    fields = ('name', 'start', 'end')
    template_name = 'finance/terms/edit.html'
    success_url = '/finance/terms/'


ExpenseBudgetFormSet = inlineformset_factory(
    Term, ExpenseBudgetItem, exclude=('term', 'ledger_account'),
    extra=0, can_delete=False)
RevenueBudgetFormSet = inlineformset_factory(
    Term, RevenueBudgetItem, exclude=('term', 'ledger_account'),
    extra=0, can_delete=False)


class editBudget(PermissionRequiredMixin, UpdateView):
    permission_required = 'finance.change_budgetitem'
    model = Term
    template_name = 'finance/terms/budget.html'
    success_url = '/finance/terms/'
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        term_pk = self.kwargs['pk']
        term = Term.objects.get(pk=term_pk)
        context['term'] = term

        # We need one budget item for each ledger account.
        # They're not automatically generated, so check if they exist
        # and create them if they don't.
        expense_budget_items = ExpenseBudgetItem.objects.filter(term=term)
        existing_ledger_accounts = []
        for item in expense_budget_items:
            existing_ledger_accounts.append(item.ledger_account)
        for ledger in ExpenseLedgerAccount.objects.all():
            if ledger not in existing_ledger_accounts:
                new_budget_item = ExpenseBudgetItem(
                    term=term, ledger_account=ledger)
                new_budget_item.save()

        revenue_budget_items = RevenueBudgetItem.objects.filter(term=term)
        existing_ledger_accounts = []
        for item in revenue_budget_items:
            existing_ledger_accounts.append(item.ledger_account)
        for ledger in RevenueLedgerAccount.objects.all():
            if ledger not in existing_ledger_accounts:
                new_budget_item = RevenueBudgetItem(
                    term=term, ledger_account=ledger)
                new_budget_item.save()

        context['expense_formset'] = ExpenseBudgetFormSet(
            instance=term, prefix='expense')
        context['revenue_formset'] = RevenueBudgetFormSet(
            instance=term, prefix='revenue')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'cancel' in request.POST:
            return redirect(self.get_success_url())
        else:
            term_pk = self.kwargs['pk']
            term = Term.objects.get(pk=term_pk)
            expense_formset = ExpenseBudgetFormSet(
                request.POST, instance=term, prefix='expense')
            revenue_formset = RevenueBudgetFormSet(
                request.POST, instance=term, prefix='revenue')
            if not (expense_formset.is_valid() and revenue_formset.is_valid()):
                return self.form_invalid(expense_formset, revenue_formset)
            return self.form_valid(expense_formset, revenue_formset)

    def form_valid(self, expense_formset, revenue_formset):
        expense_formset.save()
        revenue_formset.save()
        self.object = self.get_object()
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, expense_formset, revenue_formset):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())
