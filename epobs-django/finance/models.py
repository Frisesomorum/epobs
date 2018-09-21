import datetime
from decimal import Decimal
from django.db import models, OperationalError
from core.models import Descriptor
from schoolauth.models import User, School
from students.models import Student
from personnel.models import Department, Payee


class Fund(Descriptor):
    pass


class Category(Descriptor):
    fund = models.ForeignKey(
        Fund, on_delete=models.CASCADE,
        related_name='related_%(app_label)s_%(class)s')

    class Meta:
        abstract = True


class ExpenseCategory(Category):
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='expense_categories')


class RevenueCategory(Category):
    pass


class LedgerAccount(Descriptor):
    class Meta:
        abstract = True

    @property
    def long_name(self):
        return "%s - %s" % (str(self.category), str(self))


class ExpenseLedgerAccount(LedgerAccount):
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.CASCADE,
        related_name='ledger_accounts')


class RevenueLedgerAccount(LedgerAccount):
    category = models.ForeignKey(
        RevenueCategory, on_delete=models.CASCADE,
        related_name='ledger_accounts')


class BudgetPeriod(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name='budget_periods')
    name = models.CharField(max_length=255, blank=True)
    start = models.DateField()
    end = models.DateField()

    class Meta:
        ordering = ['start', 'end']

    def __str__(self):
        if len(self.name) > 0:
            return self.name
        return str(self.start) + " - " + str(self.end)


class BudgetItem(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    period = models.ForeignKey(
        BudgetPeriod, on_delete=models.CASCADE,
        related_name='related_%(app_label)s_%(class)s')

    class Meta:
        abstract = True
        unique_together = (('period', 'ledger_account'),)

    def __str__(self):
        str(self.period) + " - " + str(self.ledger_account)


class ExpenseBudgetItem(BudgetItem):
    ledger_account = models.ForeignKey(
        ExpenseLedgerAccount, on_delete=models.CASCADE, related_name='budget')


class RevenueBudgetItem(BudgetItem):
    ledger_account = models.ForeignKey(
        RevenueLedgerAccount, on_delete=models.CASCADE, related_name='budget')


class PayeeAccount(models.Model):
    payee = models.OneToOneField(Payee, on_delete=models.CASCADE)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return str(self.payee)

    @property
    def is_active(self):
        return self.payee.is_active


class StudentAccount(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return str(self.student)

    @property
    def balance_due(self):
        return NotImplemented

    @property
    def is_enrolled(self):
        return self.student.is_enrolled


class Transaction(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE,
        related_name='related_%(app_label)s_%(class)s')
    notes = models.TextField(max_length=4000, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.PROTECT,
        related_name='created_%(app_label)s_%(class)s')
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        abstract = True

    def __str__(self):
        return "payment of {0} on {1}".format(self.amount, self.created.date())

    @property
    def date(self):
        if isinstance(self, RequiresApproval):
            return self.date_approved
        return self.created.date()

    @property
    def budget_period(self):
        if self.date is None:
            return None
        for period in BudgetPeriod.objects.filter(school=self.school).all():
            if period.start <= self.date and self.date <= period.end:
                return period
        return None

    def include_in_report(self):
        if (
                isinstance(self, RequiresApproval)
                and self.approval_status != APPROVAL_STATUS_APPROVED):
            return False
        if (
                isinstance(self, AdmitsCorrections)
                and hasattr(self, 'corrected_by_cje')
                and self.corrected_by_cje.approval_status != APPROVAL_STATUS_APPROVED):
            return False
        return True


APPROVAL_STATUS_DRAFT = 'D'
APPROVAL_STATUS_PENDING = 'P'
APPROVAL_STATUS_APPROVED = 'A'
APPROVAL_STATUS_CHOICES = (
    (APPROVAL_STATUS_DRAFT, 'Draft'),
    (APPROVAL_STATUS_PENDING, 'Pending Approval'),
    (APPROVAL_STATUS_APPROVED, 'Approved')
)


class RequiresApproval(models.Model):
    approval_status = models.CharField(
        max_length=1, choices=APPROVAL_STATUS_CHOICES, default=APPROVAL_STATUS_DRAFT)
    date_submitted = models.DateField(blank=True, null=True)
    submitted_by = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True,
        related_name='submitted_%(app_label)s_%(class)s')
    date_approved = models.DateField(blank=True, null=True)
    approved_by = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True,
        related_name='approved_%(app_label)s_%(class)s')

    class Meta:
        abstract = True

    def verify_can_be_edited(self):
        if self.approval_status != APPROVAL_STATUS_DRAFT:
            raise OperationalError("This transaction is not in 'draft' status and cannot be edited.")

    def submit_for_approval(self, user):
        if self.approval_status != APPROVAL_STATUS_DRAFT:
            raise OperationalError("This transaction is not in 'draft' status and cannot be submitted for approval.")
        self.approval_status = APPROVAL_STATUS_PENDING
        self.submitted_by = user
        self.date_submitted = datetime.date.today()
        self.save()

    def unsubmit_for_approval(self):
        if self.approval_status != APPROVAL_STATUS_PENDING:
            raise OperationalError("This transaction is not in 'pending' status and cannot be reverted to draft.")
        self.approval_status = APPROVAL_STATUS_DRAFT
        self.submitted_by = None
        self.date_submitted = None
        self.save()

    def approve(self, user, commit=True):
        if self.approval_status != APPROVAL_STATUS_PENDING:
            raise OperationalError("This transaction is not in 'pending' status and cannot be approved.")
        if self.submitted_by == user:
            raise OperationalError("The same user cannot both submit and approve the same transaction.")
        self.approval_status = APPROVAL_STATUS_APPROVED
        self.approved_by = user
        self.date_approved = datetime.date.today()
        if commit:
            self.save()


class AdmitsCorrections:
    @property
    def has_correction(self):
        return hasattr(self, 'corrected_by_cje')

    @property
    def is_replacement(self):
        return hasattr(self, 'replacement_for_cje')

    @property
    def is_reversal(self):
        return hasattr(self, 'reversal_for_cje')

    def verify_can_be_corrected(self):
        if self.has_correction:
            raise OperationalError("This transaction already has a corrective journal entry attached to it.")
        if self.is_reversal:
            raise OperationalError("This transaction reverses an erroneous transaction and cannot be revised.")
        if isinstance(self, RequiresApproval) and self.approval_status != APPROVAL_STATUS_APPROVED:
            raise OperationalError(
                "This transaction is not yet approved. If you need to make changes, revert the status to draft.")


class ExpenseInfo(Transaction):
    ledger_account = models.ForeignKey(
        ExpenseLedgerAccount, on_delete=models.CASCADE,
        related_name='related_%(app_label)s_%(class)s')
    payee = models.ForeignKey(
        PayeeAccount, on_delete=models.CASCADE, blank=True, null=True,
        related_name='related_%(app_label)s_%(class)s')
    quantity = models.DecimalField(max_digits=15, decimal_places=2, default=1)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        abstract = True

    def calc_amount(self):
        self.amount = (self.quantity * self.unit_cost) - self.discount + self.tax

    def save(self, *args, **kwargs):
        self.calc_amount()
        super().save(*args, **kwargs)


class ExpenseTransaction(AdmitsCorrections, RequiresApproval, ExpenseInfo):
    class Meta:
        permissions = (
            ("approve_expensetransaction", "Can approve expenses"),
        )


class ExpenseCorrectiveJournalEntry(RequiresApproval, ExpenseInfo):
    correction_to = models.OneToOneField(
        ExpenseTransaction, on_delete=models.CASCADE,
        related_name='corrected_by_cje')
    reversed_in = models.OneToOneField(
        ExpenseTransaction, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='reversal_for_cje')
    restated_in = models.OneToOneField(
        ExpenseTransaction, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='restatement_for_cje')

    class Meta:
        permissions = (
            ("approve_expensecorrectivejournalentry",
             "Can approve expense corrective journal entries"),
        )

    def create_reversal_expense(self, user):
        correcting_expense = self.correction_to
        return ExpenseTransaction.objects.create(
            ledger_account=correcting_expense.ledger_account,
            payee=correcting_expense.payee,
            quantity=-correcting_expense.quantity,
            unit_cost=correcting_expense.unit_cost,
            discount=-correcting_expense.discount,
            tax=-correcting_expense.tax,
            amount=-correcting_expense.amount,
            school=correcting_expense.school,
            created_by=user,
            approval_status=APPROVAL_STATUS_APPROVED,
            date_submitted=self.date_submitted,
            submitted_by=self.submitted_by,
            date_approved=self.date_approved,
            approved_by=self.approved_by,
            notes=self.notes,
            )

    def create_restatement_expense(self, user):
        return ExpenseTransaction.objects.create(
            ledger_account=self.ledger_account,
            payee=self.payee,
            quantity=self.quantity,
            unit_cost=self.unit_cost,
            discount=self.discount,
            tax=self.tax,
            amount=self.amount,
            school=self.school,
            created_by=user,
            approval_status=APPROVAL_STATUS_APPROVED,
            date_submitted=self.date_submitted,
            submitted_by=self.submitted_by,
            date_approved=self.date_approved,
            approved_by=self.approved_by,
            notes=self.notes,
            )

    def approve_and_finalize(self, user):
        self.approve(user, commit=False)
        self.reversed_in = self.create_reversal_expense(user)
        self.restated_in = self.create_restatement_expense(user)
        self.save()


class RevenueInfo(Transaction):
    ledger_account = models.ForeignKey(
        RevenueLedgerAccount, on_delete=models.CASCADE,
        related_name='related_%(app_label)s_%(class)s')
    student = models.ForeignKey(
        StudentAccount, on_delete=models.CASCADE, blank=True, null=True,
        related_name='related_%(app_label)s_%(class)s')

    class Meta:
        abstract = True


class RevenueTransaction(RevenueInfo, AdmitsCorrections):
    pass


class RevenueCorrectiveJournalEntry(RequiresApproval, RevenueInfo):
    correction_to = models.OneToOneField(
        RevenueTransaction, on_delete=models.CASCADE,
        related_name='corrected_by_cje')
    reversed_in = models.OneToOneField(
        RevenueTransaction, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='reversal_for_cje')
    restated_in = models.OneToOneField(
        RevenueTransaction, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='restatement_for_cje')

    class Meta:
        permissions = (
            ("approve_revenuecorrectivejournalentry",
             "Can approve revenue corrective journal entries"),
        )

    def create_reversal_revenue(self, user):
        correcting_revenue = self.correction_to
        return RevenueTransaction.objects.create(
            ledger_account=correcting_revenue.ledger_account,
            student=correcting_revenue.student,
            amount=-correcting_revenue.amount,
            school=correcting_revenue.school,
            created_by=user,
            notes=self.notes,
            )

    def create_restatement_revenue(self, user):
        return RevenueTransaction.objects.create(
            ledger_account=self.ledger_account,
            student=self.student,
            amount=self.amount,
            school=self.school,
            created_by=user,
            notes=self.notes,
            )

    def approve_and_finalize(self, user):
        self.approve(user, commit=False)
        self.reversed_in = self.create_reversal_revenue(user)
        self.restated_in = self.create_restatement_revenue(user)
        self.save()


class ReportItem(models.Model):
    category = None
    ledger_account = None
    period = None
    transaction_queryset = None
    budget_items = None
    period_budget = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    period_actual = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    budget_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    percent_used = models.DecimalField(max_digits=5, decimal_places=4, default=0)

    class Meta:
        abstract = True

    def __init__(
            self,
            period=None, school=None, ledger_account=None,
            category=None, report_item_list=None):
        if ledger_account is not None:
            self.construct_line_item(period, school, ledger_account)
        else:
            self.construct_summary_item(category, report_item_list)

    def construct_line_item(self, period, school, ledger_account):
        if isinstance(ledger_account, ExpenseLedgerAccount):
            transaction_model = ExpenseTransaction
            budget_model = ExpenseBudgetItem
        else:
            transaction_model = RevenueTransaction
            budget_model = RevenueBudgetItem
        self.ledger_account = ledger_account
        self.category = ledger_account.category
        self.period = period
        self.transaction_queryset = transaction_model.objects.filter(school=school, ledger_account=ledger_account)
        self.budget_items = budget_model.objects.filter(period__in=period, ledger_account=ledger_account).all()
        self.calc_all()

    def construct_summary_item(self, category, report_item_list):
        self.category = category
        period_budget = 0
        period_actual = 0
        for report_item in report_item_list:
            if (
                    category is None or (
                        report_item.ledger_account is not None
                        and report_item.ledger_account.category == category)):
                period_budget += report_item.period_budget
                period_actual += report_item.period_actual
        self.period_budget = period_budget
        self.period_actual = period_actual
        self.calc_budget_balance()
        self.calc_percent_used()

    def __str__(self):
        if self.ledger_account is not None:
            return str(self.ledger_account)
        if self.category is not None:
            return str(self.category)
        return "Total"

    def calc_all(self):
        self.calc_period_budget()
        self.calc_period_actual()
        self.calc_budget_balance()
        self.calc_percent_used()

    def calc_period_budget(self):
        period_budget = 0
        for budget in self.budget_items:
            period_budget += budget.amount
        self.period_budget = period_budget

    def calc_period_actual(self):
        period_actual = 0
        for transaction in self.transaction_queryset.all():
            if transaction.include_in_report():
                period = transaction.budget_period
                if period is not None and period.pk in self.period:
                    period_actual += transaction.amount
        self.period_actual = period_actual

    def calc_budget_balance(self):
        self.budget_balance = self.period_budget - self.period_actual

    def calc_percent_used(self):
        if self.period_budget == 0:
            self.percent_used = 0
        else:
            self.percent_used = ((self.period_actual / self.period_budget) // Decimal(0.001)) / 10
