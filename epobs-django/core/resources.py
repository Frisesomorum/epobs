from django.urls import reverse
from finance.resources import ExpenseResource, RevenueResource
from personnel.resources import EmployeeResource, SupplierResource
from students.resources import StudentResource


def get_resource_class(model_name):
    if model_name == 'expenses':
        return ExpenseResource
    if model_name == 'revenues':
        return RevenueResource
    if model_name == 'employees':
        return EmployeeResource
    if model_name == 'suppliers':
        return SupplierResource
    if model_name == 'students':
        return StudentResource


def get_success_url(model_name):
    if model_name == 'expenses':
        return reverse('expense-list')
    if model_name == 'revenues':
        return reverse('revenue-list')
    if model_name == 'employees':
        return reverse('employee-list')
    if model_name == 'suppliers':
        return reverse('supplier-list')
    if model_name == 'students':
        return reverse('student-list')
