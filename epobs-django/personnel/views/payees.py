from django.shortcuts import redirect
from ..models import Payee, PAYEE_TYPE_EMPLOYEE
from schoolauth.views import get_school_object_or_404
from schoolauth.decorators import school_permission_required


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
