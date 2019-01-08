from django import forms
from django.shortcuts import redirect
from django.urls import reverse_lazy
from schoolauth.decorators import school_permission_required
from core.views import DeletionFormMixin, SessionRecentsMixin, ImportTool
from core.lib import QueryStringArg
from schoolauth.views import (
    SchooledListView, SchooledDetailView,
    SchoolFormMixin, get_school, get_school_object_or_404,)
from ..models import (
    ExpenseTransaction, ExpenseCorrectiveJournalEntry, PayeeAccount,
    ExpenseCategory, ExpenseLedgerAccount, APPROVAL_STATUS_APPROVED,)
from .shared import RequiresApprovalCreateView, RequiresApprovalUpdateView
from ..resources import ExpenseResource


EXPENSE_LEDGER_ACCOUNT = QueryStringArg(
    url_arg='ledger_account',
    queryset_arg='ledger_account',
    model=ExpenseLedgerAccount
)

EXPENSE_CATEGORY = QueryStringArg(
    url_arg='category',
    queryset_arg='ledger_account__category',
    model=ExpenseCategory
)

EXPENSE_APPROVAL_STATUS = QueryStringArg(
    url_arg='approval_status',
    queryset_arg='approval_status'
)

EXPENSE_PAYEE = QueryStringArg(
    url_arg='payee',
    queryset_arg='payee',
    model=PayeeAccount
)


class List(SchooledListView):
    permission_required = 'finance.view_expensetransaction'
    model = ExpenseTransaction
    template_name = 'finance/expenses/list.html'
    querystring_args = (EXPENSE_LEDGER_ACCOUNT, EXPENSE_CATEGORY, EXPENSE_APPROVAL_STATUS, EXPENSE_PAYEE, )

    def get_context_data(self, **kwargs):
        context = {}
        context['cje_list'] = ExpenseCorrectiveJournalEntry.objects.filter(
            school=get_school(self.request.session)).exclude(
            approval_status=APPROVAL_STATUS_APPROVED).filter(
            correction_to__in=self.get_queryset())
        return super().get_context_data(**context)


class Detail(SchooledDetailView):
    permission_required = 'finance.view_expensetransaction'
    model = ExpenseTransaction
    template_name = 'finance/expenses/detail.html'
    context_object_name = 'expense'


class LedgerAccountSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            ledger_account = ExpenseLedgerAccount.objects.get(pk=int(value))
            option['attrs']['la_category'] = ledger_account.category.pk
        return option


class ExpenseForm(SchoolFormMixin, forms.ModelForm):
    category = forms.ModelChoiceField(queryset=ExpenseCategory.objects.all(), required=False)

    class Meta:
        model = ExpenseTransaction
        fields = (
            'ledger_account', 'payee', 'quantity', 'unit_cost', 'discount',
            'tax', 'notes', )
        widgets = {
            'ledger_account': LedgerAccountSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payee'].queryset = PayeeAccount.school_filter_queryset(
            self.fields['payee'].queryset, self.school)
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


class Import(ImportTool):
    permission_required = 'finance.add_expensetransaction'
    model = ExpenseTransaction
    resource_class = ExpenseResource
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
