from django.shortcuts import redirect
from django.urls import reverse_lazy
from schoolauth.decorators import school_permission_required
from core.views import DeletionFormMixin
from schoolauth.views import (
    SchooledDetailView, get_school_object_or_404, )
from ..models import ExpenseTransaction, ExpenseCorrectiveJournalEntry
from .expenses import ExpenseForm
from .shared import RequiresApprovalCreateView, RequiresApprovalUpdateView


class ExpenseCjeForm(ExpenseForm):
    class Meta:
        model = ExpenseCorrectiveJournalEntry
        fields = (
            'ledger_account', 'payee', 'quantity', 'unit_cost', 'discount',
            'tax', 'notes', )


class Detail(SchooledDetailView):
    permission_required = 'finance.view_expensecorrectivejournalentry'
    model = ExpenseCorrectiveJournalEntry
    template_name = 'finance/expenses/cje/detail.html'
    context_object_name = 'expensecje'


class Create(RequiresApprovalCreateView):
    permission_required = 'finance.add_expensecorrectivejournalentry'
    model = ExpenseCorrectiveJournalEntry
    form_class = ExpenseCjeForm
    template_name = 'finance/expenses/cje/create.html'
    success_url = reverse_lazy('expense-list')

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
        initial['payee'] = correcting_expense.payee
        initial['quantity'] = correcting_expense.quantity
        initial['unit_cost'] = correcting_expense.unit_cost
        initial['discount'] = correcting_expense.discount
        initial['tax'] = correcting_expense.tax
        return initial

    def form_valid(self, form):
        form.instance.correction_to = self.get_context_data()['correcting_expense']
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class Edit(DeletionFormMixin, RequiresApprovalUpdateView):
    permission_required = 'finance.change_expensecorrectivejournalentry'
    model = ExpenseCorrectiveJournalEntry
    form_class = ExpenseCjeForm
    template_name = 'finance/expenses/cje/edit.html'
    success_url = reverse_lazy('expense-list')


@school_permission_required('finance.change_expensecorrectivejournalentry')
def submit_for_approval(request, pk):
    expensecje = get_school_object_or_404(
        request, ExpenseCorrectiveJournalEntry, pk=pk)
    expensecje.submit_for_approval(request.user)
    return redirect('expense-list')


@school_permission_required('finance.change_expensecorrectivejournalentry')
def unsubmit_for_approval(request, pk):
    expensecje = get_school_object_or_404(
        request, ExpenseCorrectiveJournalEntry, pk=pk)
    expensecje.unsubmit_for_approval()
    return redirect('expense-list')


@school_permission_required('finance.approve_expensecorrectivejournalentry')
def approve(request, pk):
    expensecje = get_school_object_or_404(
        request, ExpenseCorrectiveJournalEntry, pk=pk)
    expensecje.approve_and_finalize(request.user)
    return redirect('expense-list')
