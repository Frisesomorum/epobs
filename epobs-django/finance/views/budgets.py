from django.forms import inlineformset_factory
from django.shortcuts import redirect
from django.urls import reverse_lazy
from schoolauth.decorators import school_permission_required
from schoolauth.views import (
    SchooledListView, SchooledDetailView, SchooledCreateView,
    SchooledUpdateView, get_school_object_or_404, )
from ..models import (
    BudgetPeriod, ExpenseBudgetItem, RevenueBudgetItem, ExpenseLedgerAccount,
    RevenueLedgerAccount, )
from .shared import RequiresApprovalUpdateView


class List(SchooledListView):
    permission_required = 'finance.view_budgetperiod'
    model = BudgetPeriod
    template_name = 'finance/budgets/list.html'


class Detail(SchooledDetailView):
    permission_required = 'finance.view_budgetperiod'
    model = BudgetPeriod
    template_name = 'finance/budgets/detail.html'
    context_object_name = 'budget'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = self.get_object()
        context['amounts'] = {}
        for budget_item in ExpenseBudgetItem.objects.filter(period=period).all():
            context['amounts'][budget_item.ledger_account] = budget_item.amount
        for budget_item in RevenueBudgetItem.objects.filter(period=period).all():
            context['amounts'][budget_item.ledger_account] = budget_item.amount
        return context


class Create(SchooledCreateView):
    permission_required = 'finance.add_budgetperiod'
    model = BudgetPeriod
    fields = ('name', 'start', 'end')
    template_name = 'finance/budgets/create.html'


ExpenseBudgetFormSet = inlineformset_factory(
    BudgetPeriod, ExpenseBudgetItem, exclude=('period', 'ledger_account'),
    extra=0, can_delete=False)
RevenueBudgetFormSet = inlineformset_factory(
    BudgetPeriod, RevenueBudgetItem, exclude=('period', 'ledger_account'),
    extra=0, can_delete=False)


class Edit(RequiresApprovalUpdateView):
    permission_required = (
        'finance.change_budgetperiod',
        'finance.change_expensebudgetitem', 'finance.change_revenuebudgetitem', )
    model = BudgetPeriod
    template_name = 'finance/budgets/edit.html'
    success_url = reverse_lazy('budget-list')
    fields = ('name', 'start', 'end')

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
        if 'delete' in request.POST:
            self.object.delete()
            return redirect(self.get_success_url())
        form = self.get_form()
        period_pk = self.kwargs['pk']
        period = BudgetPeriod.objects.get(pk=period_pk)
        expense_formset = ExpenseBudgetFormSet(
            request.POST, instance=period, prefix='expense')
        revenue_formset = RevenueBudgetFormSet(
            request.POST, instance=period, prefix='revenue')
        if not (form.is_valid() and expense_formset.is_valid() and revenue_formset.is_valid()):
            return self.form_invalid(form, expense_formset, revenue_formset)
        return self.form_valid(form, expense_formset, revenue_formset)

    def form_valid(self, form, expense_formset, revenue_formset):
        expense_formset.save()
        revenue_formset.save()
        return super().form_valid(form)

    def form_invalid(self, form, expense_formset, revenue_formset):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())


class EditApproved(SchooledUpdateView):
    permission_required = 'finance.change_budgetperiod'
    model = BudgetPeriod
    template_name = 'finance/budgets/edit_approved.html'
    success_url = reverse_lazy('budget-list')
    fields = ('name', )


@school_permission_required('finance.change_budgetperiod')
def submit_for_approval(request, pk):
    expense = get_school_object_or_404(request, BudgetPeriod, pk=pk)
    expense.submit_for_approval(request.user)
    return redirect('budget-list')


@school_permission_required('finance.change_budgetperiod')
def unsubmit_for_approval(request, pk):
    expense = get_school_object_or_404(request, BudgetPeriod, pk=pk)
    expense.unsubmit_for_approval()
    return redirect('budget-list')


@school_permission_required('finance.approve_budget')
def approve(request, pk):
    expense = get_school_object_or_404(request, BudgetPeriod, pk=pk)
    expense.approve(request.user)
    return redirect('budget-list')
