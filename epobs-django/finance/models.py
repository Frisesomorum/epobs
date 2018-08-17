import datetime
from django.db import models, OperationalError
from django.core.exceptions import PermissionDenied
import epobs.models as sharedModels
import students.models as studentsModels
import personnel.models as personnelModels

class Fund(sharedModels.Descriptor):
    pass

class Category(sharedModels.Descriptor):
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name='related_%(app_label)s_%(class)s')

    def totalForTerm(self, term):
        return Nothing
    def totalYTD(self, year):
        return Nothing

    class Meta:
        abstract = True

class ExpenseCategory(Category):
    pass

class RevenueCategory(Category):
    pass

class LedgerAccount(sharedModels.Descriptor):
    class Meta:
        abstract = True

class ExpenseLedgerAccount(LedgerAccount):
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, related_name='ledger_accounts')

class RevenueLedgerAccount(LedgerAccount):
    category = models.ForeignKey(RevenueCategory, on_delete=models.CASCADE, related_name='ledger_accounts')


class Term(models.Model):
    name = models.CharField(max_length=255, blank=True)
    start = models.DateField()
    end = models.DateField()

    def __str__(self):
        if len(self.name) > 0:
            return self.name
        return str(self.start) + " - " + str(self.end)

    def revenueBudgets(self):
        return Nothing
    def expenseBudgets(self):
        return Nothing
    def revenuesCollected(self):
        return Nothing
    def expensesPaid(self):
        return Nothing

class BudgetItem(models.Model):
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='related_%(app_label)s_%(class)s')
    def __str__(self):
        str(self.term) + " - " + str(self.ledger_account)
    class Meta:
        abstract = True
        unique_together = (("term", "ledger_account"),)

class ExpenseBudgetItem(BudgetItem):
    ledger_account = models.ForeignKey(ExpenseLedgerAccount, on_delete=models.CASCADE, related_name='budget')

class RevenueBudgetItem(BudgetItem):
    ledger_account = models.ForeignKey(RevenueLedgerAccount, on_delete=models.CASCADE, related_name='budget')


class Payee(models.Model):
    def balanceDue(self):
        return Nothing
    def amountPaid(self):
        return Nothing
    class Meta:
        abstract = True

class EmployeeAccount(Payee):
    employee = models.OneToOneField(personnelModels.Employee, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.employee)

class SupplierAccount(Payee):
    supplier = models.OneToOneField(personnelModels.Supplier, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.supplier)

class StudentAccount(models.Model):
    student = models.OneToOneField(studentsModels.Student, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.student)

    @property
    def balanceDue(self):
        sum = 0
        for transaction in self.related_finance_revenuetransaction.filter(paid=False):
            sum += transaction.balanceDue
        return sum
    def nextPayment(self):
        return NotImplented


class Transaction(models.Model):
    notes = models.TextField(max_length=4000, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(sharedModels.User, on_delete=models.PROTECT, related_name='created_%(app_label)s_%(class)s')
    amount_charged = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    paid = models.BooleanField(default=False)
    when_paid = models.DateTimeField(blank=True, null=True)
    partial_amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    @property
    def balanceDue(self):
        if self.paid:
            return 0
        return self.amount_charged - self.partial_amount_paid

    class Meta:
        abstract = True

APPROVAL_STATUS_CHOICES = (
    ('D', 'Draft'),
    ('S', 'Submitted'),
    ('A', 'Approved')
)
class RequiresApproval(models.Model):
    approval_status = models.CharField(max_length=1, choices=APPROVAL_STATUS_CHOICES, default='D')
    date_submitted = models.DateField(blank=True, null=True)
    submitted_by = models.ForeignKey(sharedModels.User, on_delete=models.PROTECT, related_name='submitted_%(app_label)s_%(class)s', blank=True, null=True)
    date_approved = models.DateField(blank=True, null=True)
    approved_by = models.ForeignKey(sharedModels.User, on_delete=models.PROTECT, related_name='approved_%(app_label)s_%(class)s', blank=True, null=True)
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

class ExpenseCorrectiveJournalEntry(RequiresApproval, ExpenseInfo):
    class Meta:
        permissions = (
            ("approve_expensecorrectivejournalentry", "Can approve expense corrective journal entries"),
        )

class ExpenseTransaction(RequiresApproval, ExpenseInfo):
    discount = models.FloatField(blank=True, null=True)
    quantity = models.FloatField(blank=True, null=True)
    unit_cost = models.FloatField(blank=True, null=True)
    unit_of_measure = models.CharField(max_length=255, blank=True)

    revised_by_cje = models.OneToOneField(ExpenseCorrectiveJournalEntry, on_delete= models.CASCADE, related_name='revision_to', blank=True, null=True)
    reversal_for_cje = models.OneToOneField(ExpenseCorrectiveJournalEntry, on_delete= models.CASCADE, related_name='reversed_in', blank=True, null=True)
    restatement_for_cje = models.OneToOneField(ExpenseCorrectiveJournalEntry, on_delete= models.CASCADE, related_name='restated_in', blank=True, null=True)
    class Meta:
        permissions = (
            ("approve_expensetransaction", "Can approve expenses"),
        )

class RevenueInfo(Transaction):
    ledger_account = models.ForeignKey(RevenueLedgerAccount, on_delete=models.CASCADE, related_name='related_%(app_label)s_%(class)s')
    student = models.ForeignKey(StudentAccount, on_delete=models.CASCADE, related_name='related_%(app_label)s_%(class)s', blank=True, null=True)
    class Meta:
        abstract=True

class RevenueCorrectiveJournalEntry(RequiresApproval, RevenueInfo):
    class Meta:
        permissions = (
            ("approve_revenuecorrectivejournalentry", "Can approve revenue corrective journal entries"),
        )

class RevenueTransaction(RevenueInfo):
    revised_by_cje = models.OneToOneField(RevenueCorrectiveJournalEntry, on_delete= models.CASCADE, related_name='revision_to', blank=True, null=True)
    reversal_for_cje = models.OneToOneField(RevenueCorrectiveJournalEntry, on_delete= models.CASCADE, related_name='reversed_in', blank=True, null=True)
    restatement_for_cje = models.OneToOneField(RevenueCorrectiveJournalEntry, on_delete= models.CASCADE, related_name='restated_in', blank=True, null=True)
