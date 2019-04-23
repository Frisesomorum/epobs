from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from schoolauth.decorators import school_permission_required
from schoolauth.views import (
    SchooledListView, SchooledDetailView, SchooledCreateView,
    SchooledUpdateView, get_school_object_or_404, )
from ..models import (
    BudgetPeriod, ExpenseBudgetItem, RevenueBudgetItem, ExpenseCategory,
    ExpenseLedgerAccount, RevenueLedgerAccount, )
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
        context['expense_amounts'] = period.get_expense_budget_items()
        context['revenue_amounts'] = period.get_revenue_budget_items()
        return context


class BudgetPeriodForm(forms.ModelForm):
    class Meta:
        model = BudgetPeriod
        fields = ('name', 'start', 'end')

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data['start']
        end_date = cleaned_data['end']
        if start_date > end_date:
            raise ValidationError(
                'The start date is later than the end date.',
                code='date_inversion',
            )
        return self.cleaned_data


class Create(SchooledCreateView):
    permission_required = 'finance.add_budgetperiod'
    model = BudgetPeriod
    form_class = BudgetPeriodForm
    template_name = 'finance/budgets/create.html'

    def form_valid(self, form):
        http_response = super().form_valid(form)
        # Create associated BudgetItems in the foreground, because we will
        # immediately redirect to the edit view, where we need the BudgetItems
        for ledger in ExpenseLedgerAccount.objects.all():
            ExpenseBudgetItem.objects.get_or_create(period=self.object, ledger_account=ledger)
        for ledger in RevenueLedgerAccount.objects.all():
            RevenueBudgetItem.objects.get_or_create(period=self.object, ledger_account=ledger)
        return http_response


ExpenseBudgetFormSet = forms.inlineformset_factory(
    BudgetPeriod, ExpenseBudgetItem, exclude=('period', 'ledger_account'),
    extra=0, can_delete=False)
RevenueBudgetFormSet = forms.inlineformset_factory(
    BudgetPeriod, RevenueBudgetItem, exclude=('period', 'ledger_account'),
    extra=0, can_delete=False)


class Edit(RequiresApprovalUpdateView):
    permission_required = (
        'finance.change_budgetperiod',
        'finance.change_expensebudgetitem', 'finance.change_revenuebudgetitem', )
    model = BudgetPeriod
    form_class = BudgetPeriodForm
    template_name = 'finance/budgets/edit.html'
    success_url = reverse_lazy('budget-list')
    context_object_name = 'period'

    def create_formsets(self, request):
        period = self.get_object()
        formsets = {}
        for category in ExpenseCategory.objects.all():
            if request.method == 'POST':
                formsets[category] = ExpenseBudgetFormSet(
                    request.POST, instance=period, prefix='{0}'.format(category.pk),
                    queryset=ExpenseBudgetItem.objects.filter(ledger_account__category=category))
            else:
                formsets[category] = ExpenseBudgetFormSet(
                    instance=period, prefix='{0}'.format(category.pk),
                    queryset=ExpenseBudgetItem.objects.filter(ledger_account__category=category))
        if request.method == 'POST':
            formsets['Revenue'] = RevenueBudgetFormSet(
                request.POST, instance=period, prefix='rev')
        else:
            formsets['Revenue'] = RevenueBudgetFormSet(
                instance=period, prefix='rev')
        return formsets

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'budget_items' not in context.keys():
            context['budget_items'] = self.create_formsets(self.request)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'delete' in request.POST:
            self.object.delete()
            return redirect(self.get_success_url())
        form = self.get_form()
        formsets = self.create_formsets(request)
        is_valid = form.is_valid()
        for formset in formsets.values():
            is_valid &= formset.is_valid()
        if is_valid:
            return self.form_valid(form, formsets)
        return self.form_invalid(form, formsets)

    def form_valid(self, form, formsets):
        for formset in formsets.values():
            formset.save()
        return super().form_valid(form)

    def form_invalid(self, form, formsets):
        return self.render_to_response(self.get_context_data(form=form, budget_items=formsets))


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
