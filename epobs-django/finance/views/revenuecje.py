from django import forms
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from core.views import DeletionFormMixin
from schools.views import (
    SchooledDetailView, SchooledCreateView, SchooledUpdateView,
    get_school, get_school_object_or_404, )
from ..models import RevenueTransaction, RevenueCorrectiveJournalEntry


class RevenueCjeForm(forms.ModelForm):
    class Meta:
        model = RevenueCorrectiveJournalEntry
        fields = ('ledger_account', 'amount', 'student', 'notes')

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school')
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = self.fields['student'].queryset.filter(student__school=school)


class Detail(SchooledDetailView):
    permission_required = 'finance.view_revenuecorrectivejournalentry'
    model = RevenueCorrectiveJournalEntry
    template_name = 'finance/revenues/cje/detail.html'
    context_object_name = 'revenuecje'


class Add(SchooledCreateView):
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
        initial = super(SchooledCreateView, self).get_initial().copy()
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


class Edit(DeletionFormMixin, SchooledUpdateView):
    permission_required = 'finance.change_revenuecorrectivejournalentry'
    model = RevenueCorrectiveJournalEntry
    form_class = RevenueCjeForm
    template_name = 'finance/revenues/cje/edit.html'
    success_url = '/finance/revenues/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_school(self.request.session)
        return kwargs


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
    revenuecje.approve_and_finalize(request.user)
    return redirect('list_revenues')
