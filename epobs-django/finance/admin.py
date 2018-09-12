from django.contrib import admin
from . import models


admin.site.register(models.Fund)
admin.site.register(models.ExpenseCategory)
admin.site.register(models.RevenueCategory)
admin.site.register(models.ExpenseLedgerAccount)
admin.site.register(models.RevenueLedgerAccount)
