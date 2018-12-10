from django.forms import inlineformset_factory
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from core.views import DeletionFormMixin
from schoolauth.views import (
    SchooledListView, SchooledCreateView, SchooledUpdateView, )
from ..models import (
    BudgetPeriod, ExpenseBudgetItem, RevenueBudgetItem, ExpenseLedgerAccount,
    RevenueLedgerAccount, )


class List(SchooledListView):
    permission_required = 'finance.view_budgetperiod'
    model = BudgetPeriod
    template_name = 'finance/budgets/list.html'


class Create(SchooledCreateView):
    permission_required = 'finance.add_budgetperiod'
    model = BudgetPeriod
    fields = ('name', 'start', 'end')
    template_name = 'finance/budgets/create.html'
    success_url = reverse_lazy('budget-list')


class EditPeriod(DeletionFormMixin, SchooledUpdateView):
    permission_required = 'finance.change_budgetperiod'
    model = BudgetPeriod
    fields = ('name', 'start', 'end')
    template_name = 'finance/budgets/period.html'
    success_url = reverse_lazy('budget-list')


ExpenseBudgetFormSet = inlineformset_factory(
    BudgetPeriod, ExpenseBudgetItem, exclude=('period', 'ledger_account'),
    extra=0, can_delete=False)
RevenueBudgetFormSet = inlineformset_factory(
    BudgetPeriod, RevenueBudgetItem, exclude=('period', 'ledger_account'),
    extra=0, can_delete=False)


class EditBudget(SchooledUpdateView):
    permission_required = (
        'finance.change_expensebudgetitem', 'finance.change_revenuebudgetitem')
    model = BudgetPeriod
    template_name = 'finance/budgets/amounts.html'
    success_url = reverse_lazy('budget-list')
    fields = '__all__'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period_pk = self.kwargs['pk']
        period = BudgetPeriod.objects.get(pk=period_pk)
        context['period'] = period

        # We need one budget item for each ledger account.
        # They're not automatically generated, so check if they exist
        # and create them if they don't.
        for ledger in ExpenseLedgerAccount.objects.all():
            ExpenseBudgetItem.objects.get_or_create(period=period, ledger_account=ledger)
        for ledger in RevenueLedgerAccount.objects.all():
            RevenueBudgetItem.objects.get_or_create(period=period, ledger_account=ledger)

        context['expense_formset'] = ExpenseBudgetFormSet(
            instance=period, prefix='expense')
        context['revenue_formset'] = RevenueBudgetFormSet(
            instance=period, prefix='revenue')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        period_pk = self.kwargs['pk']
        period = BudgetPeriod.objects.get(pk=period_pk)
        expense_formset = ExpenseBudgetFormSet(
            request.POST, instance=period, prefix='expense')
        revenue_formset = RevenueBudgetFormSet(
            request.POST, instance=period, prefix='revenue')
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
