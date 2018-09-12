from django import forms
from django.shortcuts import redirect
from django.urls import reverse_lazy
from schoolauth.decorators import school_permission_required
from core.views import DeletionFormMixin, SessionRecentsMixin
from schoolauth.views import (
    SchooledListView, SchooledDetailView, SchooledCreateView, SchooledUpdateView,
    get_school, get_school_object_or_404,)
from ..models import (
    ExpenseTransaction, ExpenseCorrectiveJournalEntry, APPROVAL_STATUS_APPROVED,)


class List(SchooledListView):
    permission_required = 'finance.view_expensetransaction'
    model = ExpenseTransaction
    template_name = 'finance/expenses/list.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['cje_list'] = ExpenseCorrectiveJournalEntry.objects.filter(
            school=get_school(self.request.session)
            ).exclude(approval_status=APPROVAL_STATUS_APPROVED)
        return super().get_context_data(**context)


class Detail(SchooledDetailView):
    permission_required = 'finance.view_expensetransaction'
    model = ExpenseTransaction
    template_name = 'finance/expenses/detail.html'
    context_object_name = 'expense'


class ExpenseForm(forms.ModelForm):
    class Meta:
        model = ExpenseTransaction
        fields = (
            'ledger_account', 'amount', 'employee', 'supplier', 'discount',
            'quantity', 'unit_cost', 'unit_of_measure', 'notes')

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school')
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = self.fields['employee'].queryset.filter(employee__school=school)
        self.fields['supplier'].queryset = self.fields['supplier'].queryset.filter(supplier__school=school)


class Create(SessionRecentsMixin, SchooledCreateView):
    permission_required = 'finance.add_expensetransaction'
    model = ExpenseTransaction
    form_class = ExpenseForm
    template_name = 'finance/expenses/create.html'
    success_url = reverse_lazy('expense-create')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_school(self.request.session)
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        http_response = super().form_valid(form)
        self.add_object_to_session(self.object.pk)
        return http_response


class Edit(DeletionFormMixin, SchooledUpdateView):
    permission_required = 'finance.change_expensetransaction'
    model = ExpenseTransaction
    form_class = ExpenseForm
    template_name = 'finance/expenses/edit.html'
    success_url = reverse_lazy('expense-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_school(self.request.session)
        return kwargs


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
