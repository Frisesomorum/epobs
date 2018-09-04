from django import forms
from django.http import HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from core.views import SessionRecentsMixin
from schools.views import get_school, CheckSchoolContextMixin
from ..models import RevenueTransaction, RevenueCorrectiveJournalEntry


class RevenueForm(forms.ModelForm):
    class Meta:
        model = RevenueTransaction
        fields = ('ledger_account', 'amount', 'student', 'notes')

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school')
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = self.fields['student'].queryset.filter(student__school=school)


class List(PermissionRequiredMixin, ListView):
    permission_required = 'finance.view_revenuetransaction'
    model = RevenueTransaction
    template_name = 'finance/revenues/list.html'

    def get_queryset(self):
        return RevenueTransaction.objects.filter(
            school=get_school(self.request.session))

    def get_context_data(self, **kwargs):
        context = {}
        context['cje_list'] = RevenueCorrectiveJournalEntry.objects.filter(
            school=get_school(self.request.session)).exclude(approval_status='A')
        return super().get_context_data(**context)


class Detail(PermissionRequiredMixin, CheckSchoolContextMixin, DetailView):
    permission_required = 'finance.view_revenuetransaction'
    model = RevenueTransaction
    template_name = 'finance/revenues/detail.html'
    context_object_name = 'revenue'


class Add(PermissionRequiredMixin, SessionRecentsMixin, CreateView):
    permission_required = 'finance.add_revenuetransaction'
    model = RevenueTransaction
    form_class = RevenueForm
    template_name = 'finance/revenues/add.html'
    success_url = '/finance/revenues/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_school(self.request.session)
        return kwargs

    def form_valid(self, form):
        transaction = form.save(commit=False)
        transaction.created_by = self.request.user
        transaction.school = get_school(self.request.session)
        transaction.save()
        self.add_object_to_session(transaction.pk)
        # Return the user to this page with a fresh form
        return HttpResponseRedirect(self.request.path_info)
