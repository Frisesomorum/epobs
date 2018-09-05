from django import forms
from django.urls import reverse_lazy
from core.views import SessionRecentsMixin
from schools.views import (
    SchooledListView, SchooledDetailView, SchooledCreateView, get_school,)
from ..models import (
    RevenueTransaction, RevenueCorrectiveJournalEntry, APPROVAL_STATUS_APPROVED,)


class RevenueForm(forms.ModelForm):
    class Meta:
        model = RevenueTransaction
        fields = ('ledger_account', 'amount', 'student', 'notes')

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school')
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = self.fields['student'].queryset.filter(student__school=school)


class List(SchooledListView):
    permission_required = 'finance.view_revenuetransaction'
    model = RevenueTransaction
    template_name = 'finance/revenues/list.html'

    def get_context_data(self, **kwargs):
        context = {}
        context['cje_list'] = RevenueCorrectiveJournalEntry.objects.filter(
            school=get_school(self.request.session)
            ).exclude(approval_status=APPROVAL_STATUS_APPROVED)
        return super().get_context_data(**context)


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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_school(self.request.session)
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        http_response = super().form_valid(form)
        self.add_object_to_session(self.object.pk)
        return http_response
