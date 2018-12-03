import datetime
from django import forms
from django.shortcuts import redirect
from ..models import Payee, PAYEE_TYPE_EMPLOYEE
from schoolauth.views import SchooledCreateView, get_school_object_or_404
from schoolauth.decorators import school_permission_required


class PayeeForm(forms.ModelForm):
    date_hired = forms.DateField(required=False, label='Date Hired')


class PayeeCreateView(SchooledCreateView):
    def form_valid(self, form):
        http_response = super().form_valid(form)
        date_hired = form.cleaned_data['date_hired']
        if date_hired is not None and date_hired <= datetime.date.today():
            form.instance.payee.start_contract(date_hired)
        return http_response


@school_permission_required('personnel.add_contract')
def start_contract(request, pk):
    payee = get_school_object_or_404(request, Payee, pk=pk)
    payee.start_contract()
    return_url = 'employee-list' if payee.type == PAYEE_TYPE_EMPLOYEE else 'supplier-list'
    return redirect(return_url)


@school_permission_required('personnel.change_contract')
def terminate_contract(request, pk):
    payee = get_school_object_or_404(request, Payee, pk=pk)
    payee.terminate_contract()
    return_url = 'employee-list' if payee.type == PAYEE_TYPE_EMPLOYEE else 'supplier-list'
    return redirect(return_url)
