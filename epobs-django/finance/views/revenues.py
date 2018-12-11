from django import forms
from django.urls import reverse_lazy
from django.shortcuts import redirect
from core.views import SessionRecentsMixin, ImportTool
from core.lib import QueryStringArg
from schoolauth.views import (
    SchooledListView, SchooledDetailView, SchooledCreateView, SchoolFormMixin, get_school,)
from ..models import (
    RevenueTransaction, RevenueCorrectiveJournalEntry, StudentAccount,
    RevenueLedgerAccount, RevenueCategory, APPROVAL_STATUS_APPROVED,)
from ..resources import RevenueResource


class RevenueForm(SchoolFormMixin, forms.ModelForm):
    class Meta:
        model = RevenueTransaction
        fields = ('ledger_account', 'amount', 'student', 'notes', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = StudentAccount.school_filter_queryset(
            self.fields['student'].queryset, self.school)


class RevenueCreateForm(SchoolFormMixin, forms.ModelForm):
    class Meta:
        model = RevenueTransaction
        fields = ('student', 'notes', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = StudentAccount.school_filter_queryset(
            self.fields['student'].queryset, self.school)
        for ledger_account in RevenueLedgerAccount.objects.all():
            self.fields[ledger_account.name] = forms.DecimalField(required=False)


REVENUE_LEDGER_ACCOUNT = QueryStringArg(
    url_arg='ledger_account',
    queryset_arg='ledger_account',
    model=RevenueLedgerAccount
)

REVENUE_CATEGORY = QueryStringArg(
    url_arg='category',
    queryset_arg='ledger_account__category',
    model=RevenueCategory
)

REVENUE_STUDENT = QueryStringArg(
    url_arg='student',
    queryset_arg='student',
    model=StudentAccount
)


class List(SchooledListView):
    permission_required = 'finance.view_revenuetransaction'
    model = RevenueTransaction
    template_name = 'finance/revenues/list.html'
    querystring_args = (REVENUE_LEDGER_ACCOUNT, REVENUE_CATEGORY, REVENUE_STUDENT, )

    def get_context_data(self, **kwargs):
        context = {}
        context['cje_list'] = RevenueCorrectiveJournalEntry.objects.filter(
            school=get_school(self.request.session)).exclude(
            approval_status=APPROVAL_STATUS_APPROVED).filter(
            correction_to__in=self.get_queryset())
        return super().get_context_data(**context)


class Detail(SchooledDetailView):
    permission_required = 'finance.view_revenuetransaction'
    model = RevenueTransaction
    template_name = 'finance/revenues/detail.html'
    context_object_name = 'revenue'


class Create(SessionRecentsMixin, SchooledCreateView):
    permission_required = 'finance.add_revenuetransaction'
    model = RevenueTransaction
    form_class = RevenueCreateForm
    template_name = 'finance/revenues/create.html'
    success_url = reverse_lazy('revenue-create')
    default_student = None

    def get(self, request, *args, **kwargs):
        student = request.GET.get('student', default=None)
        if student is not None:
            self.default_student = student
        return super().get(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial().copy()
        if self.default_student is not None:
            initial['student'] = self.default_student
            student_account = StudentAccount.objects.get(pk=self.default_student)
            balances = student_account.balance_due_by_ledger_account()
            for ledger_account in balances.keys():
                initial[ledger_account.name] = balances[ledger_account]
        return initial

    def form_valid(self, form):
        student_account = form.cleaned_data['student']
        notes = form.cleaned_data['notes']
        user = self.request.user
        school = get_school(self.request.session)
        for ledger_account in RevenueLedgerAccount.objects.all():
            amount = form.cleaned_data[ledger_account.name]
            if amount is not None and amount > 0:
                revenue = RevenueTransaction.objects.create(
                    school=school,
                    student=student_account,
                    ledger_account=ledger_account,
                    amount=amount,
                    notes=notes,
                    created_by=user,
                )
                self.add_object_to_session(revenue.pk)
        return redirect(self.success_url)


class Import(ImportTool):
    permission_required = 'finance.add_revenuetransaction'
    model = RevenueTransaction
    resource_class = RevenueResource
    success_url = reverse_lazy('revenue-list')
