from django import forms
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.db import OperationalError
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import permission_required
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from core.views import DeletionFormMixin
from schools.views import get_school, get_school_object_or_404, CheckSchoolContextMixin
from ..models import RevenueTransaction, RevenueCorrectiveJournalEntry


class RevenueCjeForm(forms.ModelForm):
    class Meta:
        model = RevenueCorrectiveJournalEntry
        fields = ('ledger_account', 'amount', 'student', 'notes')

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school')
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = self.fields['student'].queryset.filter(student__school=school)


class Detail(PermissionRequiredMixin, CheckSchoolContextMixin, DetailView):
    permission_required = 'finance.view_revenuecorrectivejournalentry'
    model = RevenueCorrectiveJournalEntry
    template_name = 'finance/revenues/cje/detail.html'
    context_object_name = 'revenuecje'


class Add(PermissionRequiredMixin, CreateView):
    permission_required = 'finance.add_revenuecorrectivejournalentry'
    model = RevenueCorrectiveJournalEntry
    form_class = RevenueCjeForm
    template_name = 'finance/revenues/cje/add.html'
    success_url = '/finance/revenues/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_school(self.request.session)
        return kwargs

    def get_context_data(self, **kwargs):
        context = {}
        correcting_revenue = get_school_object_or_404(
            self.request, RevenueTransaction, pk=self.kwargs['revenue_pk'])
        correcting_revenue.verify_can_be_corrected()
        context['correcting_revenue'] = correcting_revenue
        return super().get_context_data(**context)

    def get_initial(self):
        initial = super(CreateView, self).get_initial().copy()
        correcting_revenue = get_school_object_or_404(
            self.request, RevenueTransaction, pk=self.kwargs['revenue_pk'])
        initial['ledger_account'] = correcting_revenue.ledger_account
        initial['student'] = correcting_revenue.student
        initial['amount'] = correcting_revenue.amount
        return initial

    def form_valid(self, form):
        revenuecje = form.save(commit=False)
        revenuecje.created_by = self.request.user
        revenuecje.school = get_school(self.request.session)
        revenuecje.correction_to = self.get_context_data()['correcting_revenue']
        revenuecje.save()
        return HttpResponseRedirect(self.success_url)


class Edit(
        PermissionRequiredMixin, CheckSchoolContextMixin,
        DeletionFormMixin, UpdateView):
    permission_required = 'finance.change_revenuecorrectivejournalentry'
    model = RevenueCorrectiveJournalEntry
    form_class = RevenueCjeForm
    template_name = 'finance/revenues/cje/edit.html'
    success_url = '/finance/revenues/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_school(self.request.session)
        return kwargs

    def render_to_response(self, context, **kwargs):
        revenuecje = self.get_object()
        if revenuecje.approval_status != 'D':
            raise OperationalError("This transaction is not in 'draft' status and cannot be edited.")
        return super().render_to_response(context, **kwargs)


@permission_required('finance.change_revenuecorrectivejournalentry')
def submit_for_approval(request, pk):
    revenuecje = get_school_object_or_404(
        request, RevenueCorrectiveJournalEntry, pk=pk)
    revenuecje.submit_for_approval(request.user)
    return redirect('list_revenues')


@permission_required('finance.change_revenuecorrectivejournalentry')
def unsubmit_for_approval(request, pk):
    revenuecje = get_school_object_or_404(
        request, RevenueCorrectiveJournalEntry, pk=pk)
    revenuecje.unsubmit_for_approval()
    return redirect('list_revenues')


@permission_required('finance.approve_revenuecorrectivejournalentry')
def approve(request, pk):
    revenuecje = get_school_object_or_404(
        request, RevenueCorrectiveJournalEntry, pk=pk)
    user = request.user
    revenuecje.approve(user)
    correcting_revenue = revenuecje.correction_to

    reversal_revenue = RevenueTransaction(
        ledger_account=correcting_revenue.ledger_account,
        student=correcting_revenue.student,
        amount=-correcting_revenue.amount,
        school=correcting_revenue.school,
        created_by=user,
        notes=revenuecje.notes,
        )
    reversal_revenue.save()
    revenuecje.reversed_in = reversal_revenue

    restatement_revenue = RevenueTransaction(
        ledger_account=revenuecje.ledger_account,
        student=revenuecje.student,
        amount=revenuecje.amount,
        school=revenuecje.school,
        created_by=user,
        notes=revenuecje.notes,
        )
    restatement_revenue.save()
    revenuecje.restated_in = restatement_revenue

    revenuecje.save()
    return redirect('list_revenues')
