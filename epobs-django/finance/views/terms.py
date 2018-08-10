from django import forms
from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, FormView
from epobs.views import DeletionFormMixin
from ..models import Term, ExpenseBudgetItem, RevenueBudgetItem, ExpenseLedgerAccount, RevenueLedgerAccount

class list(ListView):
    model = Term
    template_name = 'finance/terms/list.html'

class create(CreateView):
    model = Term
    fields = '__all__'
    template_name = 'finance/terms/create.html'
    success_url = 'finance/terms/'

class edit(DeletionFormMixin, UpdateView):
    model = Term
    fields = '__all__'
    template_name = 'finance/terms/edit.html'
    success_url = 'finance/terms/'

class budgetForm(forms.Form):
    pass

class editBudget(FormView):
    form_class = budgetForm
    template_name = 'finance/terms/budget.html'
    success_url = 'finance/terms/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        term_pk = self.kwargs['term_pk']
        term = Term.objects.get(pk=term_pk)
        context['term'] = term

        # We need one budget item for each ledger account.
        # They're not automatically generated, so check if they exist and create them if they don't.
        expense_budget_items = ExpenseBudgetItem.objects.filter(term=term)
        existing_ledger_accounts = []
        for item in expense_budget_items:
            existing_ledger_accounts.append(item.ledger_account)
        for ledger in ExpenseLedgerAccount.objects.all():
            if ledger not in existing_ledger_accounts:
                new_budget_item = ExpenseBudgetItem(term=term, ledger_account=ledger)
                new_budget_item.save()
        context['expense_budget_items'] = ExpenseBudgetItem.objects.filter(term=term)

        revenue_budget_items = RevenueBudgetItem.objects.filter(term=term)
        existing_ledger_accounts = []
        for item in revenue_budget_items:
            existing_ledger_accounts.append(item.ledger_account)
        for ledger in RevenueLedgerAccount.objects.all():
            if ledger not in existing_ledger_accounts:
                new_budget_item = RevenueBudgetItem(term=term, ledger_account=ledger)
                new_budget_item.save()
        context['revenue_budget_items'] = RevenueBudgetItem.objects.filter(term=term)

        return context

    def post(self, request, **kwargs):
        if 'cancel' in request.POST:
            return redirect(self.get_success_url())
        else:
            return super().post(request, **kwargs)
