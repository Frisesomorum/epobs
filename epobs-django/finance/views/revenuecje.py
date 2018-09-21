from django import forms
from django.shortcuts import redirect
from django.urls import reverse_lazy
from schoolauth.decorators import school_permission_required
from core.views import DeletionFormMixin
from schoolauth.views import (
    SchooledDetailView, SchoolFormMixin, get_school_object_or_404, )
from ..models import RevenueTransaction, RevenueCorrectiveJournalEntry
from .shared import RequiresApprovalCreateView, RequiresApprovalUpdateView


class RevenueCjeForm(SchoolFormMixin, forms.ModelForm):
    class Meta:
        model = RevenueCorrectiveJournalEntry
        fields = ('ledger_account', 'amount', 'student', 'notes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = self.fields['student'].queryset.filter(student__school=self.school)


class Detail(SchooledDetailView):
    permission_required = 'finance.view_revenuecorrectivejournalentry'
    model = RevenueCorrectiveJournalEntry
    template_name = 'finance/revenues/cje/detail.html'
    context_object_name = 'revenuecje'


class Create(RequiresApprovalCreateView):
    permission_required = 'finance.add_revenuecorrectivejournalentry'
    model = RevenueCorrectiveJournalEntry
    form_class = RevenueCjeForm
    template_name = 'finance/revenues/cje/create.html'
    success_url = reverse_lazy('revenue-list')

    def get_context_data(self, **kwargs):
        context = {}
        correcting_revenue = get_school_object_or_404(
            self.request, RevenueTransaction, pk=self.kwargs['revenue_pk'])
        correcting_revenue.verify_can_be_corrected()
        context['correcting_revenue'] = correcting_revenue
        return super().get_context_data(**context)

    def get_initial(self):
        initial = super().get_initial().copy()
        correcting_revenue = get_school_object_or_404(
            self.request, RevenueTransaction, pk=self.kwargs['revenue_pk'])
        initial['ledger_account'] = correcting_revenue.ledger_account
        initial['student'] = correcting_revenue.student
        initial['amount'] = correcting_revenue.amount
        return initial

    def form_valid(self, form):
        form.instance.correction_to = self.get_context_data()['correcting_revenue']
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class Edit(DeletionFormMixin, RequiresApprovalUpdateView):
    permission_required = 'finance.change_revenuecorrectivejournalentry'
    model = RevenueCorrectiveJournalEntry
    form_class = RevenueCjeForm
    template_name = 'finance/revenues/cje/edit.html'
    success_url = reverse_lazy('revenue-list')


@school_permission_required('finance.change_revenuecorrectivejournalentry')
def submit_for_approval(request, pk):
    revenuecje = get_school_object_or_404(
        request, RevenueCorrectiveJournalEntry, pk=pk)
    revenuecje.submit_for_approval(request.user)
    return redirect('revenue-list')


@school_permission_required('finance.change_revenuecorrectivejournalentry')
def unsubmit_for_approval(request, pk):
    revenuecje = get_school_object_or_404(
        request, RevenueCorrectiveJournalEntry, pk=pk)
    revenuecje.unsubmit_for_approval()
    return redirect('revenue-list')


@school_permission_required('finance.approve_revenuecorrectivejournalentry')
def approve(request, pk):
    revenuecje = get_school_object_or_404(
        request, RevenueCorrectiveJournalEntry, pk=pk)
    revenuecje.approve_and_finalize(request.user)
    return redirect('revenue-list')
