from django.contrib import admin
from django.contrib.auth import views as authViews
from django.conf import settings
from django.urls import path, re_path, include
from epobs import views as indexViews
from finance.views import terms as termViews
from finance.views import expenses as expenseViews
from finance.views import expensecje as expenseCjeViews
from finance.views import revenues as revenueViews
from personnel.views import employees as employeeViews
from personnel.views import suppliers as supplierViews
from students import views as studentViews

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),

    re_path(r'^$', indexViews.index_view, name='index'),
    re_path(r'login/$', authViews.LoginView.as_view(template_name='login.html'), name='login'),
    re_path(r'logout/$', authViews.LogoutView.as_view(), name='logout'),

    re_path(r'school/$', indexViews.EditSchool.as_view(), name='school'),

    re_path(r'finance/terms/$', termViews.list.as_view(), name='list_term'),
    re_path(r'finance/terms/create/$', termViews.create.as_view(), name='create_term'),
    re_path(r'finance/terms/edit/(?P<pk>\d+)/$', termViews.edit.as_view(), name='edit_term'),
    re_path(r'finance/budgets/(?P<pk>\d+)/$', termViews.editBudget.as_view(), name='edit_budget'),

    re_path(r'finance/revenues/$', revenueViews.list.as_view(), name='list_revenues'),
    re_path(r'finance/revenues/add/$', revenueViews.add.as_view(), name='add_revenues'),
    re_path(r'finance/revenues/view/(?P<pk>\d+)/$', revenueViews.detail.as_view(), name='view_revenue'),

    re_path(r'finance/expenses/$', expenseViews.list.as_view(), name='list_expenses'),
    re_path(r'finance/expenses/add/$', expenseViews.add.as_view(), name='add_expenses'),
    re_path(r'finance/expenses/edit/(?P<pk>\d+)/$', expenseViews.edit.as_view(), name='edit_expense'),
    re_path(r'finance/expenses/view/(?P<pk>\d+)/$', expenseViews.detail.as_view(), name='view_expense'),
    re_path(r'finance/expenses/submit/(?P<pk>\d+)/$', expenseViews.submitForApproval, name='submit_expense'),
    re_path(r'finance/expenses/unsubmit/(?P<pk>\d+)/$', expenseViews.unsubmitForApproval, name='unsubmit_expense'),
    re_path(r'finance/expenses/approve/(?P<pk>\d+)/$', expenseViews.approve, name='approve_expense'),

    re_path(r'finance/expenses/cje/add/(?P<expense_pk>\d+)/$', expenseCjeViews.add.as_view(), name='add_expense_cje'),
    re_path(r'finance/expenses/cje/edit/(?P<pk>\d+)/$', expenseCjeViews.edit.as_view(), name='edit_expense_cje'),
    re_path(r'finance/expenses/cje/view/(?P<pk>\d+)/$', expenseCjeViews.detail.as_view(), name='view_expense_cje'),
    re_path(r'finance/expenses/cje/submit/(?P<pk>\d+)/$', expenseCjeViews.submitForApproval, name='submit_expense_cje'),
    re_path(r'finance/expenses/cje/unsubmit/(?P<pk>\d+)/$', expenseCjeViews.unsubmitForApproval, name='unsubmit_expense_cje'),
    re_path(r'finance/expenses/cje/approve/(?P<pk>\d+)/$', expenseCjeViews.approve, name='approve_expense_cje'),

    re_path(r'personnel/employees/$', employeeViews.list.as_view(), name='list_employees'),
    re_path(r'personnel/employees/add/$', employeeViews.add.as_view(), name='add_employees'),
    re_path(r'personnel/employees/edit/(?P<pk>\d+)/$', employeeViews.edit.as_view(), name='edit_employee'),

    re_path(r'personnel/suppliers/$', supplierViews.list.as_view(), name='list_suppliers'),
    re_path(r'personnel/suppliers/add/$', supplierViews.add.as_view(), name='add_suppliers'),
    re_path(r'personnel/suppliers/edit/(?P<pk>\d+)/$', supplierViews.edit.as_view(), name='edit_supplier'),

    re_path(r'students/$', studentViews.list.as_view(), name='list_students'),
    re_path(r'students/add/$', studentViews.add.as_view(), name='add_students'),
    re_path(r'students/edit/(?P<pk>\d+)/$', studentViews.edit.as_view(), name='edit_students'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
