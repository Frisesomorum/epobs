from django import forms
from django.urls import reverse_lazy
from core.views import SessionRecentsMixin
from schoolauth.views import (
    SchooledListView, SchooledDetailView, SchooledCreateView, SchoolFormMixin, get_school,)
from ..models import (
    RevenueTransaction, RevenueCorrectiveJournalEntry, APPROVAL_STATUS_APPROVED,)


class RevenueForm(SchoolFormMixin, forms.ModelForm):
    class Meta:
        model = RevenueTransaction
        fields = ('ledger_account', 'amount', 'student', 'notes')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = self.fields['student'].queryset.filter(student__school=self.school)


class List(SchooledListView):
    permission_required = 'finance.view_revenuetransaction'
    model = RevenueTransaction
    template_name = 'finance/revenues/list.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['cje_list'] = RevenueCorrectiveJournalEntry.objects.filter(
            school=get_school(self.request.session)).exclude(
            approval_status=APPROVAL_STATUS_APPROVED).filter(
            correction_to__in=self.get_queryset())
        return super().get_context_data(**context)


class Drilldown(List):
    def get_queryset(self):
        return super().get_queryset().filter(ledger_account=self.kwargs['ledger_account'])


class Detail(SchooledDetailView):
    permission_required = 'finance.view_revenuetransaction'
    model = RevenueTransaction
    template_name = 'finance/revenues/detail.html'
    context_object_name = 'revenue'


class Create(SessionRecentsMixin, SchooledCreateView):
    permission_required = 'finance.add_revenuetransaction'
    model = RevenueTransaction
    form_class = RevenueForm
    template_name = 'finance/revenues/create.html'
    success_url = reverse_lazy('revenue-create')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        http_response = super().form_valid(form)
        self.add_object_to_session(self.object.pk)
        return http_response
