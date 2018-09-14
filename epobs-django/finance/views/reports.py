from django import forms
from django.shortcuts import render, redirect
from django.urls import reverse, resolve
from django.views.generic import TemplateView
from django.views.generic.edit import FormView
from schoolauth.views import get_school, register_school_session_data
from .. import models


def index_view(request):
    return render(request, 'reports/index.html')


def set_report_period(session, period):
    session['report_period'] = period
    register_school_session_data(session, 'report_period')


def get_report_period(session):
    return session.get('report_period', default=[])


class SelectPeriodForm(forms.Form):
    period = forms.ModelMultipleChoiceField(
        queryset=models.Term.objects.all()
        )

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school')
        super().__init__(*args, **kwargs)
        self.fields['period'].queryset = self.fields['period'].queryset.filter(school=school)


class SelectPeriod(FormView):
    template_name = 'reports/period_select.html'
    form_class = SelectPeriodForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_school(self.request.session)
        return kwargs

    def dispatch(self, request, *args, **kwargs):
        success_url = reverse(kwargs.pop('next'))
        if success_url == '':
            return redirect('index')
        self.success_url = success_url
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        period = list(form.cleaned_data['period'].values_list('pk', flat=True))
        set_report_period(self.request.session, period)
        return redirect(self.get_success_url())


class SummaryReport(TemplateView):
    get_expenses = False
    get_revenues = False
    period = []

    def dispatch(self, request, *args, **kwargs):
        period = get_report_period(request.session)
        if len(period) == 0:
            return redirect(
                'report-select-period', next=resolve(request.path_info).url_name)
        self.period = period
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['period'] = ", ".join(
            str(models.Term.objects.get(pk=term_pk)) for term_pk in self.period)
        school = get_school(self.request.session)

        if self.get_expenses:
            report_item_list = []
            for ledger_account in models.ExpenseLedgerAccount.objects.all():
                report_item = models.ReportItem(
                    period=self.period, school=school,
                    ledger_account=ledger_account)
                report_item_list.append(report_item)

            context['expense_report_list'] = []
            for category in models.ExpenseCategory.objects.all():
                report_item = models.ReportItem(
                    category=category, report_item_list=report_item_list)
                context['expense_report_list'].append(report_item)
                for report_item in report_item_list:
                    if report_item.ledger_account.category == category:
                        context['expense_report_list'].append(report_item)

        if self.get_revenues:
            context['revenue_report_list'] = []
            for ledger_account in models.RevenueLedgerAccount.objects.all():
                report_item = models.ReportItem(
                    period=self.period, school=school,
                    ledger_account=ledger_account)
                context['revenue_report_list'].append(report_item)

        return context


class ExpenseSummary(SummaryReport):
    template_name = 'reports/expense_summary.html'
    get_expenses = True


class RevenueSummary(SummaryReport):
    template_name = 'reports/revenue_summary.html'
    get_revenues = True


class ExpenseRevenueSummary(SummaryReport):
    template_name = 'reports/expense_revenue_summary.html'
    get_expenses = True
    get_revenues = True
