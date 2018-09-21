from django import forms
from django.shortcuts import redirect
from django.urls import reverse_lazy
from schoolauth.decorators import school_permission_required
from core.views import DeletionFormMixin, SessionRecentsMixin
from schoolauth.views import (
    SchooledListView, SchooledDetailView,
    SchoolFormMixin, get_school, get_school_object_or_404,)
from ..models import (
    ExpenseTransaction, ExpenseCorrectiveJournalEntry, APPROVAL_STATUS_APPROVED,)
from .shared import RequiresApprovalCreateView, RequiresApprovalUpdateView


class List(SchooledListView):
    permission_required = 'finance.view_expensetransaction'
    model = ExpenseTransaction
    template_name = 'finance/expenses/list.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['cje_list'] = ExpenseCorrectiveJournalEntry.objects.filter(
            school=get_school(self.request.session)).exclude(
            approval_status=APPROVAL_STATUS_APPROVED).filter(
            correction_to__in=self.get_queryset())
        return super().get_context_data(**context)


class Drilldown(List):
    def get_queryset(self):
        return super().get_queryset().filter(ledger_account=self.kwargs['ledger_account'])


class Detail(SchooledDetailView):
    permission_required = 'finance.view_expensetransaction'
    model = ExpenseTransaction
    template_name = 'finance/expenses/detail.html'
    context_object_name = 'expense'


class ExpenseForm(SchoolFormMixin, forms.ModelForm):
    class Meta:
        model = ExpenseTransaction
        fields = (
            'ledger_account', 'payee', 'quantity', 'unit_cost', 'discount',
            'tax', 'notes', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payee'].queryset = (
            self.fields['payee'].queryset.filter(payee__employee__school=self.school)
            | self.fields['payee'].queryset.filter(payee__supplier__school=self.school))
        for field in ['quantity', 'unit_cost', 'discount', 'tax']:
            self.fields[field].widget.attrs.update({'class': 'amount-factor'})


class Create(SessionRecentsMixin, RequiresApprovalCreateView):
    permission_required = 'finance.add_expensetransaction'
    model = ExpenseTransaction
    form_class = ExpenseForm
    template_name = 'finance/expenses/create.html'
    success_url = reverse_lazy('expense-create')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        http_response = super().form_valid(form)
        self.add_object_to_session(self.object.pk)
        return http_response


class Edit(DeletionFormMixin, RequiresApprovalUpdateView):
    permission_required = 'finance.change_expensetransaction'
    model = ExpenseTransaction
    form_class = ExpenseForm
    template_name = 'finance/expenses/edit.html'
    success_url = reverse_lazy('expense-list')


@school_permission_required('finance.change_expensetransaction')
def submit_for_approval(request, pk):
    expense = get_school_object_or_404(request, ExpenseTransaction, pk=pk)
    expense.submit_for_approval(request.user)
    return redirect('expense-list')


@school_permission_required('finance.change_expensetransaction')
def unsubmit_for_approval(request, pk):
    expense = get_school_object_or_404(request, ExpenseTransaction, pk=pk)
    expense.unsubmit_for_approval()
    return redirect('expense-list')


@school_permission_required('finance.approve_expensetransaction')
def approve(request, pk):
    expense = get_school_object_or_404(request, ExpenseTransaction, pk=pk)
    expense.approve(request.user)
    return redirect('expense-list')
