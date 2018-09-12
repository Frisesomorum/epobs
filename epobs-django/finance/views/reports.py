from django.shortcuts import render
from django.views.generic.list import ListView
from ..models import ExpenseLedgerAccount


def index_view(request):
    return render(request, 'reports/index.html')


class ExpenseSummary(ListView):
    model = ExpenseLedgerAccount
    template_name = 'reports/expense_summary.html'
