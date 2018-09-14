from django.contrib import admin
from django.contrib.auth import views as authViews
from django.conf import settings
from django.urls import path, re_path, include
from core import views as coreViews
from schoolauth import views as schoolAuthViews
from schools import views as schoolViews
from personnel.views import employees as employeeViews
from personnel.views import suppliers as supplierViews
from students import views as studentViews
from finance.views import terms as termViews
from finance.views import expenses as expenseViews
from finance.views import expensecje as expenseCjeViews
from finance.views import revenues as revenueViews
from finance.views import revenuecje as revenueCjeViews
from finance.views import reports as reportViews

urlpatterns = [
    path('admin/', admin.site.urls, name='admin'),

    re_path(r'^$', coreViews.index_view, name='index'),
    re_path(r'login/$', authViews.LoginView.as_view(template_name='login.html'), name='login'),
    re_path(r'logout/$', authViews.LogoutView.as_view(), name='logout'),
    re_path(r'selectschool/$', schoolAuthViews.SelectSchool.as_view(), name='school-select'),

    re_path(r'school/$', schoolViews.Edit.as_view(), name='school-edit'),
    re_path(r'user/new$', schoolViews.CreateUser.as_view(), name='user-create'),
    re_path(r'school/membership/$', schoolViews.ListMembership.as_view(), name='member-list'),
    re_path(r'school/membership/new/$', schoolViews.CreateMembership.as_view(), name='member-create'),
    re_path(r'school/membership/(?P<pk>\d+)/edit/$', schoolViews.EditMembership.as_view(), name='member-edit'),

    re_path(r'employees/$', employeeViews.List.as_view(), name='employee-list'),
    re_path(r'employees/new/$', employeeViews.Create.as_view(), name='employee-create'),
    re_path(r'employees/(?P<pk>\d+)/edit/$', employeeViews.Edit.as_view(), name='employee-edit'),

    re_path(r'suppliers/$', supplierViews.List.as_view(), name='supplier-list'),
    re_path(r'suppliers/new/$', supplierViews.Create.as_view(), name='supplier-create'),
    re_path(r'suppliers/(?P<pk>\d+)/edit/$', supplierViews.Edit.as_view(), name='supplier-edit'),

    re_path(r'students/$', studentViews.List.as_view(), name='student-list'),
    re_path(r'students/new/$', studentViews.Create.as_view(), name='student-create'),
    re_path(r'students/(?P<pk>\d+)/edit/$', studentViews.Edit.as_view(), name='student-edit'),

    re_path(r'terms/$', termViews.List.as_view(), name='term-list'),
    re_path(r'terms/new/$', termViews.Create.as_view(), name='term-create'),
    re_path(r'terms/(?P<pk>\d+)/edit/$', termViews.Edit.as_view(), name='term-edit'),
    re_path(r'budgets/(?P<pk>\d+)/$', termViews.EditBudget.as_view(), name='budget-edit'),

    re_path(r'expenses/$', expenseViews.List.as_view(), name='expense-list'),
    re_path(r'expenses/drilldown/(?P<ledger_account>\d+)/$', expenseViews.Drilldown.as_view(),
            name='expense-drilldown'),
    re_path(r'expenses/(?P<pk>\d+)/$', expenseViews.Detail.as_view(), name='expense-detail'),
    re_path(r'expenses/new/$', expenseViews.Create.as_view(), name='expense-create'),
    re_path(r'expenses/(?P<pk>\d+)/edit/$', expenseViews.Edit.as_view(), name='expense-edit'),
    re_path(r'expenses/(?P<pk>\d+)/submit/$', expenseViews.submit_for_approval, name='expense-submit'),
    re_path(r'expenses/(?P<pk>\d+)/unsubmit/$', expenseViews.unsubmit_for_approval, name='expense-unsubmit'),
    re_path(r'expenses/(?P<pk>\d+)/approve/$', expenseViews.approve, name='expense-approve'),

    re_path(r'expenses/cje/(?P<pk>\d+)/$', expenseCjeViews.Detail.as_view(), name='expense-cje-detail'),
    re_path(r'expenses/cje/new/(?P<expense_pk>\d+)/$', expenseCjeViews.Create.as_view(), name='expense-cje-create'),
    re_path(r'expenses/cje/(?P<pk>\d+)/edit/$', expenseCjeViews.Edit.as_view(), name='expense-cje-edit'),
    re_path(r'expenses/cje/(?P<pk>\d+)/submit/$', expenseCjeViews.submit_for_approval, name='expense-cje-submit'),
    re_path(
        r'expenses/cje/(?P<pk>\d+)/unsubmit/$', expenseCjeViews.unsubmit_for_approval, name='expense-cje-unsubmit'),
    re_path(r'expenses/cje/(?P<pk>\d+)/approve/$', expenseCjeViews.approve, name='expense-cje-approve'),

    re_path(r'revenues/$', revenueViews.List.as_view(), name='revenue-list'),
    re_path(r'revenues/drilldown/(?P<ledger_account>\d+)/$', revenueViews.Drilldown.as_view(),
            name='revenue-drilldown'),
    re_path(r'revenues/(?P<pk>\d+)/$', revenueViews.Detail.as_view(), name='revenue-detail'),
    re_path(r'revenues/new/$', revenueViews.Create.as_view(), name='revenue-create'),

    re_path(r'revenues/cje/(?P<pk>\d+)/$', revenueCjeViews.Detail.as_view(), name='revenue-cje-detail'),
    re_path(r'revenues/cje/new/(?P<revenue_pk>\d+)/$', revenueCjeViews.Create.as_view(), name='revenue-cje-create'),
    re_path(r'revenues/cje/(?P<pk>\d+)/edit/$', revenueCjeViews.Edit.as_view(), name='revenue-cje-edit'),
    re_path(r'revenues/cje/(?P<pk>\d+)/submit/$', revenueCjeViews.submit_for_approval, name='revenue-cje-submit'),
    re_path(
        r'revenues/cje/(?P<pk>\d+)/unsubmit/$', revenueCjeViews.unsubmit_for_approval, name='revenue-cje-unsubmit'),
    re_path(r'revenues/cje/(?P<pk>\d+)/approve/$', revenueCjeViews.approve, name='revenue-cje-approve'),

    re_path(r'reports/index/$', reportViews.index_view, name='report-index'),
    re_path(r'reports/select-period/(?P<next>[\w-]+)$', reportViews.SelectPeriod.as_view(),
            name='report-select-period'),
    re_path(r'reports/expense-summary/$', reportViews.ExpenseSummary.as_view(), name='report-expense-summary'),
    re_path(r'reports/revenue-summary/$', reportViews.RevenueSummary.as_view(), name='report-revenue-summary'),
    re_path(r'reports/expense-revenue-summary/$', reportViews.ExpenseRevenueSummary.as_view(),
            name='report-expense-revenue-summary'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
