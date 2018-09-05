from django import forms
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import permission_required
from core.views import DeletionFormMixin
from schools.views import (
    SchooledDetailView, SchooledCreateView, SchooledUpdateView,
    get_school, get_school_object_or_404, )
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


class Detail(SchooledDetailView):
    permission_required = 'finance.view_expensecorrectivejournalentry'
    model = ExpenseCorrectiveJournalEntry
    template_name = 'finance/expenses/cje/detail.html'
    context_object_name = 'expensecje'


class Create(SchooledCreateView):
    permission_required = 'finance.add_expensecorrectivejournalentry'
    model = ExpenseCorrectiveJournalEntry
    form_class = ExpenseCjeForm
    template_name = 'finance/expenses/cje/create.html'
    success_url = reverse_lazy('expense-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_school(self.request.session)
        return kwargs

    def get_context_data(self, **kwargs):
        context = {}
        correcting_expense = get_school_object_or_404(
            self.request, ExpenseTransaction, pk=self.kwargs['expense_pk'])
        correcting_expense.verify_can_be_corrected()
        context['correcting_expense'] = correcting_expense
        return super().get_context_data(**context)

    def get_initial(self):
        initial = super().get_initial().copy()
        correcting_expense = get_school_object_or_404(
            self.request, ExpenseTransaction, pk=self.kwargs['expense_pk'])
        initial['ledger_account'] = correcting_expense.ledger_account
        initial['employee'] = correcting_expense.employee
        initial['supplier'] = correcting_expense.supplier
        initial['amount'] = correcting_expense.amount
        return initial

    def form_valid(self, form):
        form.instance.correction_to = self.get_context_data()['correcting_expense']
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class Edit(DeletionFormMixin, SchooledUpdateView):
    permission_required = 'finance.change_expensecorrectivejournalentry'
    model = ExpenseCorrectiveJournalEntry
    form_class = ExpenseCjeForm
    template_name = 'finance/expenses/cje/edit.html'
    success_url = reverse_lazy('expense-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_school(self.request.session)
        return kwargs


@permission_required('finance.change_expensecorrectivejournalentry')
def submit_for_approval(request, pk):
    expensecje = get_school_object_or_404(
        request, ExpenseCorrectiveJournalEntry, pk=pk)
    expensecje.submit_for_approval(request.user)
    return redirect('expense-list')


@permission_required('finance.change_expensecorrectivejournalentry')
def unsubmit_for_approval(request, pk):
    expensecje = get_school_object_or_404(
        request, ExpenseCorrectiveJournalEntry, pk=pk)
    expensecje.unsubmit_for_approval()
    return redirect('expense-list')


@permission_required('finance.approve_expensecorrectivejournalentry')
def approve(request, pk):
    expensecje = get_school_object_or_404(
        request, ExpenseCorrectiveJournalEntry, pk=pk)
    expensecje.approve_and_finalize(request.user)
    return redirect('expense-list')
