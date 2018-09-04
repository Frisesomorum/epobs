import datetime
from django.db import models, OperationalError
import core.models as coreModels
from schools.models import School
from students.models import Student
from personnel.models import Employee, Supplier


class Fund(coreModels.Descriptor):
    pass


class Category(coreModels.Descriptor):
    fund = models.ForeignKey(
        Fund, on_delete=models.CASCADE,
        related_name='related_%(app_label)s_%(class)s')

    class Meta:
        abstract = True

    def total_for_term(self, term):
        return NotImplemented

    def total_YTD(self, year):
        return NotImplemented


class ExpenseCategory(Category):
    pass


class RevenueCategory(Category):
    pass


class LedgerAccount(coreModels.Descriptor):
    class Meta:
        abstract = True


class ExpenseLedgerAccount(LedgerAccount):
    category = models.ForeignKey(
        ExpenseCategory, on_delete=models.CASCADE,
        related_name='ledger_accounts')


class RevenueLedgerAccount(LedgerAccount):
    category = models.ForeignKey(
        RevenueCategory, on_delete=models.CASCADE,
        related_name='ledger_accounts')


class Term(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name='terms')
    name = models.CharField(max_length=255, blank=True)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        if len(self.name) > 0:
            return self.name
        return str(self.start) + " - " + str(self.end)

    def revenue_budgets(self):
        return NotImplemented

    def expense_budgets(self):
        return NotImplemented

    def revenues_collected(self):
        return NotImplemented

    def expenses_paid(self):
        return NotImplemented


class BudgetItem(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    term = models.ForeignKey(
        Term, on_delete=models.CASCADE,
        related_name='related_%(app_label)s_%(class)s')

    class Meta:
        abstract = True
        unique_together = (('term', 'ledger_account'),)

    def __str__(self):
        str(self.term) + " - " + str(self.ledger_account)


class ExpenseBudgetItem(BudgetItem):
    ledger_account = models.ForeignKey(
        ExpenseLedgerAccount, on_delete=models.CASCADE, related_name='budget')


class RevenueBudgetItem(BudgetItem):
    ledger_account = models.ForeignKey(
        RevenueLedgerAccount, on_delete=models.CASCADE, related_name='budget')


class Payee(models.Model):
    class Meta:
        abstract = True

    def balance_due(self):
        return NotImplemented

    def amount_paid(self):
        return NotImplemented


class EmployeeAccount(Payee):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.employee)


class SupplierAccount(Payee):
    supplier = models.OneToOneField(Supplier, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.supplier)


class StudentAccount(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.student)

    @property
    def balance_due(self):
        return NotImplemented

    def next_payment(self):
        return NotImplemented


class Transaction(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE,
        related_name='related_%(app_label)s_%(class)s')
    notes = models.TextField(max_length=4000, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        coreModels.User, on_delete=models.PROTECT,
        related_name='created_%(app_label)s_%(class)s')
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        abstract = True

    def __str__(self):
        return "payment of {0} on {1}".format(self.amount, self.created.date())


APPROVAL_STATUS_DRAFT = 'D'
APPROVAL_STATUS_SUBMITTED = 'S'
APPROVAL_STATUS_APPROVED = 'A'
APPROVAL_STATUS_CHOICES = (
    (APPROVAL_STATUS_DRAFT, 'Draft'),
    (APPROVAL_STATUS_SUBMITTED, 'Submitted'),
    (APPROVAL_STATUS_APPROVED, 'Approved')
)


class RequiresApproval(models.Model):
    approval_status = models.CharField(
        max_length=1, choices=APPROVAL_STATUS_CHOICES, default=APPROVAL_STATUS_DRAFT)
    date_submitted = models.DateField(blank=True, null=True)
    submitted_by = models.ForeignKey(
        coreModels.User, on_delete=models.PROTECT, blank=True, null=True,
        related_name='submitted_%(app_label)s_%(class)s')
    date_approved = models.DateField(blank=True, null=True)
    approved_by = models.ForeignKey(
        coreModels.User, on_delete=models.PROTECT, blank=True, null=True,
        related_name='approved_%(app_label)s_%(class)s')

    class Meta:
        abstract = True

    def submit_for_approval(self, user):
        if self.approval_status != APPROVAL_STATUS_DRAFT:
            raise OperationalError("This transaction is not in 'draft' status and cannot be submitted for approval.")
        self.approval_status = APPROVAL_STATUS_SUBMITTED
        self.submitted_by = user
        self.date_submitted = datetime.date.today()
        self.save()

    def unsubmit_for_approval(self):
        if self.approval_status != APPROVAL_STATUS_SUBMITTED:
            raise OperationalError("This transaction is not in 'submitted' status and cannot be reverted to draft.")
        self.approval_status = APPROVAL_STATUS_DRAFT
        self.submitted_by = None
        self.date_submitted = None
        self.save()

    def approve(self, user):
        if self.approval_status != APPROVAL_STATUS_SUBMITTED:
            raise OperationalError("This transaction is not in 'submitted' status and cannot be approved.")
        if self.submitted_by == user:
            raise OperationalError("The same user cannot both submit and approve the same transaction.")
        self.approval_status = APPROVAL_STATUS_APPROVED
        self.approved_by = user
        self.date_approved = datetime.date.today()
        self.save()


class AdmitsCorrections:
    class Meta:
        abstract = True

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
    employee = models.ForeignKey(
        EmployeeAccount, on_delete=models.CASCADE, blank=True, null=True,
        related_name='related_%(app_label)s_%(class)s')
    supplier = models.ForeignKey(
        SupplierAccount, on_delete=models.CASCADE, blank=True, null=True,
        related_name='related_%(app_label)s_%(class)s')

    class Meta:
        abstract = True

    @property
    def payee(self):
        if self.employee:
            return self.employee
        return self.supplier


class ExpenseTransaction(AdmitsCorrections, RequiresApproval, ExpenseInfo):
    discount = models.FloatField(blank=True, null=True)
    quantity = models.FloatField(blank=True, null=True)
    unit_cost = models.FloatField(blank=True, null=True)
    unit_of_measure = models.CharField(max_length=255, blank=True)

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
