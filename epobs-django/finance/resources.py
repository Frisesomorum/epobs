from import_export import fields
from schoolauth.resources import ForeignKeyWidget, SchooledModelResource, SchooledExternalIdWidget
from .models import (
    ExpenseTransaction, RevenueTransaction, ExpenseLedgerAccount,
    RevenueLedgerAccount, PayeeAccount, StudentAccount, )


class TransactionResource(SchooledModelResource):
    user = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.user = kwargs.get('user')

    def init_instance(self, row=None):
        instance = super().init_instance(row=None)
        instance.created_by = self.user
        return instance


class ExpenseResource(TransactionResource):
    ledger_account = fields.Field(
        attribute='ledger_account',
        widget=ForeignKeyWidget(ExpenseLedgerAccount, 'name'))

    class Meta:
        model = ExpenseTransaction
        fields = ('ledger_account', 'payee', 'quantity', 'unit_cost', 'discount', 'tax', 'notes', )
        import_id_fields = ()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['payee'].widget = SchooledExternalIdWidget(
            PayeeAccount, school=self.school)


class RevenueResource(TransactionResource):
    ledger_account = fields.Field(
        attribute='ledger_account',
        widget=ForeignKeyWidget(RevenueLedgerAccount, 'name'))

    class Meta:
        model = RevenueTransaction
        fields = ('ledger_account', 'student', 'amount', 'notes', )
        import_id_fields = ()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['student'].widget = SchooledExternalIdWidget(
            StudentAccount, school=self.school)
