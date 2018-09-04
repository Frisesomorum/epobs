from django.contrib import admin
from django.contrib.auth import views as authViews
from django.conf import settings
from django.urls import path, re_path, include
from core import views as coreViews
from schools import views as schoolViews
from finance.views import terms as termViews
from finance.views import expenses as expenseViews
from finance.views import expensecje as expenseCjeViews
from finance.views import revenues as revenueViews
from finance.views import revenuecje as revenueCjeViews
from personnel.views import employees as employeeViews
from personnel.views import suppliers as supplierViews
from students import views as studentViews

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),

    re_path(r'^$', coreViews.index_view, name='index'),
    re_path(r'login/$', authViews.LoginView.as_view(template_name='login.html'), name='login'),
    re_path(r'logout/$', authViews.LogoutView.as_view(), name='logout'),
    re_path(r'selectschool/$', schoolViews.SelectSchool.as_view(), name='select_school'),

    re_path(r'school/$', schoolViews.EditSchool.as_view(), name='school'),

    re_path(r'finance/terms/$', termViews.List.as_view(), name='list_term'),
    re_path(r'finance/terms/create/$', termViews.Create.as_view(), name='create_term'),
    re_path(r'finance/terms/edit/(?P<pk>\d+)/$', termViews.Edit.as_view(), name='edit_term'),
    re_path(r'finance/budgets/(?P<pk>\d+)/$', termViews.EditBudget.as_view(), name='edit_budget'),

    re_path(r'finance/revenues/$', revenueViews.List.as_view(), name='list_revenues'),
    re_path(r'finance/revenues/add/$', revenueViews.Add.as_view(), name='add_revenues'),
    re_path(r'finance/revenues/view/(?P<pk>\d+)/$', revenueViews.Detail.as_view(), name='view_revenue'),

    re_path(r'finance/revenues/cje/add/(?P<revenue_pk>\d+)/$', revenueCjeViews.Add.as_view(), name='add_revenue_cje'),
    re_path(r'finance/revenues/cje/edit/(?P<pk>\d+)/$', revenueCjeViews.Edit.as_view(), name='edit_revenue_cje'),
    re_path(r'finance/revenues/cje/view/(?P<pk>\d+)/$', revenueCjeViews.Detail.as_view(), name='view_revenue_cje'),
    re_path(r'finance/revenues/cje/submit/(?P<pk>\d+)/$', revenueCjeViews.submit_for_approval, name='submit_revenue_cje'),
    re_path(r'finance/revenues/cje/unsubmit/(?P<pk>\d+)/$', revenueCjeViews.unsubmit_for_approval, name='unsubmit_revenue_cje'),
    re_path(r'finance/revenues/cje/approve/(?P<pk>\d+)/$', revenueCjeViews.approve, name='approve_revenue_cje'),

    re_path(r'finance/expenses/$', expenseViews.List.as_view(), name='list_expenses'),
    re_path(r'finance/expenses/add/$', expenseViews.Add.as_view(), name='add_expenses'),
    re_path(r'finance/expenses/edit/(?P<pk>\d+)/$', expenseViews.Edit.as_view(), name='edit_expense'),
    re_path(r'finance/expenses/view/(?P<pk>\d+)/$', expenseViews.Detail.as_view(), name='view_expense'),
    re_path(r'finance/expenses/submit/(?P<pk>\d+)/$', expenseViews.submit_for_approval, name='submit_expense'),
    re_path(r'finance/expenses/unsubmit/(?P<pk>\d+)/$', expenseViews.unsubmit_for_approval, name='unsubmit_expense'),
    re_path(r'finance/expenses/approve/(?P<pk>\d+)/$', expenseViews.approve, name='approve_expense'),

    re_path(r'finance/expenses/cje/add/(?P<expense_pk>\d+)/$', expenseCjeViews.Add.as_view(), name='add_expense_cje'),
    re_path(r'finance/expenses/cje/edit/(?P<pk>\d+)/$', expenseCjeViews.Edit.as_view(), name='edit_expense_cje'),
    re_path(r'finance/expenses/cje/view/(?P<pk>\d+)/$', expenseCjeViews.Detail.as_view(), name='view_expense_cje'),
    re_path(r'finance/expenses/cje/submit/(?P<pk>\d+)/$', expenseCjeViews.submit_for_approval, name='submit_expense_cje'),
    re_path(r'finance/expenses/cje/unsubmit/(?P<pk>\d+)/$', expenseCjeViews.unsubmit_for_approval, name='unsubmit_expense_cje'),
    re_path(r'finance/expenses/cje/approve/(?P<pk>\d+)/$', expenseCjeViews.approve, name='approve_expense_cje'),

    re_path(r'personnel/employees/$', employeeViews.List.as_view(), name='list_employees'),
    re_path(r'personnel/employees/add/$', employeeViews.Add.as_view(), name='add_employees'),
    re_path(r'personnel/employees/edit/(?P<pk>\d+)/$', employeeViews.Edit.as_view(), name='edit_employee'),

    re_path(r'personnel/suppliers/$', supplierViews.List.as_view(), name='list_suppliers'),
    re_path(r'personnel/suppliers/add/$', supplierViews.Add.as_view(), name='add_suppliers'),
    re_path(r'personnel/suppliers/edit/(?P<pk>\d+)/$', supplierViews.Edit.as_view(), name='edit_supplier'),

    re_path(r'students/$', studentViews.List.as_view(), name='list_students'),
    re_path(r'students/add/$', studentViews.Add.as_view(), name='add_students'),
    re_path(r'students/edit/(?P<pk>\d+)/$', studentViews.Edit.as_view(), name='edit_students'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
