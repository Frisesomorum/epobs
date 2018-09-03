import datetime
from django.db import models, OperationalError
from django.core.exceptions import PermissionDenied
import core.models as coreModels
from schools.models import School
from students.models import Student
from personnel.models import Employee, Supplier

class Fund(coreModels.Descriptor):
    pass

class Category(coreModels.Descriptor):
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name='related_%(app_label)s_%(class)s')

    def totalForTerm(self, term):
        return NotImplemented
    def totalYTD(self, year):
        return NotImplemented

    class Meta:
        abstract = True

class ExpenseCategory(Category):
    pass

class RevenueCategory(Category):
    pass

class LedgerAccount(coreModels.Descriptor):
    class Meta:
        abstract = True

class ExpenseLedgerAccount(LedgerAccount):
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, related_name='ledger_accounts')

class RevenueLedgerAccount(LedgerAccount):
    category = models.ForeignKey(RevenueCategory, on_delete=models.CASCADE, related_name='ledger_accounts')


class Term(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='terms')
    name = models.CharField(max_length=255, blank=True)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        if len(self.name) > 0:
            return self.name
        return str(self.start) + " - " + str(self.end)

    def revenueBudgets(self):
        return NotImplemented
    def expenseBudgets(self):
        return NotImplemented
    def revenuesCollected(self):
        return NotImplemented
    def expensesPaid(self):
        return NotImplemented

class BudgetItem(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='related_%(app_label)s_%(class)s')
    def __str__(self):
        str(self.term) + " - " + str(self.ledger_account)
    class Meta:
        abstract = True
        unique_together = (('term', 'ledger_account'),)

class ExpenseBudgetItem(BudgetItem):
    ledger_account = models.ForeignKey(ExpenseLedgerAccount, on_delete=models.CASCADE, related_name='budget')

class RevenueBudgetItem(BudgetItem):
    ledger_account = models.ForeignKey(RevenueLedgerAccount, on_delete=models.CASCADE, related_name='budget')


class Payee(models.Model):
    def balanceDue(self):
        return NotImplemented
    def amountPaid(self):
        return NotImplemented
    class Meta:
        abstract = True

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
    def balanceDue(self):
        return NotImplemented
    def nextPayment(self):
        return NotImplemented


class Transaction(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='related_%(app_label)s_%(class)s')
    notes = models.TextField(max_length=4000, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(coreModels.User, on_delete=models.PROTECT, related_name='created_%(app_label)s_%(class)s')
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        abstract = True

    def __str__(self):
        return "payment of {0} on {1}".format(self.amount, self.created.date())

APPROVAL_STATUS_CHOICES = (
    ('D', 'Draft'),
    ('S', 'Submitted'),
    ('A', 'Approved')
)
class RequiresApproval(models.Model):
    approval_status = models.CharField(max_length=1, choices=APPROVAL_STATUS_CHOICES, default='D')
    date_submitted = models.DateField(blank=True, null=True)
    submitted_by = models.ForeignKey(coreModels.User, on_delete=models.PROTECT, related_name='submitted_%(app_label)s_%(class)s', blank=True, null=True)
    date_approved = models.DateField(blank=True, null=True)
    approved_by = models.ForeignKey(coreModels.User, on_delete=models.PROTECT, related_name='approved_%(app_label)s_%(class)s', blank=True, null=True)
    class Meta:
        abstract=True

    def submitForApproval(self, user):
        if self.approval_status != 'D':
            raise OperationalError("This transaction is not in 'draft' status and cannot be submitted for approval.")
        self.approval_status = 'S'
        self.submitted_by = user
        self.date_submitted = datetime.date.today()
        self.save()

    def unsubmitForApproval(self):
        if self.approval_status != 'S':
            raise OperationalError("This transaction is not in 'submitted' status and cannot be reverted to draft.")
        self.approval_status = 'D'
        self.submitted_by = None
        self.date_submitted = None
        self.save()

    def approve(self, user):
        if self.approval_status != 'S':
            raise OperationalError("This transaction is not in 'submitted' status and cannot be approved.")
        if self.submitted_by == user:
            raise OperationalError("The same user cannot both submit and approve the same transaction.")
        self.approval_status = 'A'
        self.approved_by = user
        self.date_approved = datetime.date.today()
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
        if isinstance(self, RequiresApproval) and self.approval_status != 'A':
            raise OperationalError("This transaction is not yet approved. If you need to make changes, revert the status to draft.")
    class Meta:
        abstract = True

class ExpenseInfo(Transaction):
    ledger_account = models.ForeignKey(ExpenseLedgerAccount, on_delete=models.CASCADE, related_name='related_%(app_label)s_%(class)s')
    employee = models.ForeignKey(EmployeeAccount, on_delete=models.CASCADE, related_name='related_%(app_label)s_%(class)s', blank=True, null=True)
    supplier = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='related_%(app_label)s_%(class)s', blank=True, null=True)
    class Meta:
        abstract=True
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
    correction_to = models.OneToOneField(ExpenseTransaction, on_delete= models.CASCADE, related_name='corrected_by_cje')
    reversed_in = models.OneToOneField(ExpenseTransaction, on_delete= models.SET_NULL, related_name='reversal_for_cje', blank=True, null=True)
    restated_in = models.OneToOneField(ExpenseTransaction, on_delete= models.SET_NULL, related_name='restatement_for_cje', blank=True, null=True)
    class Meta:
        permissions = (
            ("approve_expensecorrectivejournalentry", "Can approve expense corrective journal entries"),
        )

class RevenueInfo(Transaction):
    ledger_account = models.ForeignKey(RevenueLedgerAccount, on_delete=models.CASCADE, related_name='related_%(app_label)s_%(class)s')
    student = models.ForeignKey(StudentAccount, on_delete=models.CASCADE, related_name='related_%(app_label)s_%(class)s', blank=True, null=True)
    class Meta:
        abstract=True

class RevenueTransaction(RevenueInfo, AdmitsCorrections):
    pass

class RevenueCorrectiveJournalEntry(RequiresApproval, RevenueInfo):
    correction_to = models.OneToOneField(RevenueTransaction, on_delete= models.CASCADE, related_name='corrected_by_cje')
    reversed_in = models.OneToOneField(RevenueTransaction, on_delete= models.SET_NULL, related_name='reversal_for_cje', blank=True, null=True)
    restated_in = models.OneToOneField(RevenueTransaction, on_delete= models.SET_NULL, related_name='restatement_for_cje', blank=True, null=True)
    class Meta:
        permissions = (
            ("approve_revenuecorrectivejournalentry", "Can approve revenue corrective journal entries"),
        )
