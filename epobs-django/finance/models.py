from django.db import models
import epobs.models as sharedModels
import students.models as studentsModels
import personnel.models as personnelModels
# TODO: set nullability
# TODO: meta properties
# TODO: documentation
# TODO: implement all methods
# TODO: update the UML document to reflect changes done during development

class Term(models.Model):
    start = models.DateField()
    end = models.DateField()

    def revenueBudgets(self):
        return Nothing
    def expenseBudgets(self):
        return Nothing
    def revenuesCollected(self):
        return Nothing
    def expensesPaid(self):
        return Nothing

class Fund(sharedModels.Descriptor):
    pass

class Category(sharedModels.Descriptor):
    fund = models.ForeignKey(Fund, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_categories')

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

class BudgetItem(sharedModels.Descriptor):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_budget')
    class Meta:
        abstract = True

class ExpenseBudgetItem(BudgetItem):
    ledgerAccount = models.ForeignKey(ExpenseLedgerAccount, on_delete=models.CASCADE, related_name='budget')

class RevenueBudgetItem(BudgetItem):
    ledgerAccount = models.ForeignKey(RevenueLedgerAccount, on_delete=models.CASCADE, related_name='budget')

class Transaction(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(max_length=4000)
    amount_charged = models.DecimalField(max_digits=15, decimal_places=2)
    partial_amount_paid = models.DecimalField(max_digits=15, decimal_places=2)
    paid = models.BooleanField()
    date_issued = models.DateField()
    date_paid = models.DateField()

    def balanceDue(self):
        return Nothing

    class Meta:
        abstract = True

class Payee(models.Model):
    def balanceDue(self):
        return Nothing
    def amountPaid(self):
        return Nothing
    class Meta:
        abstract = True

class EmployeeAccount(sharedModels.Person, Payee):
    employee = models.ForeignKey(personnelModels.Employee, on_delete=models.CASCADE)

class SupplierAccount(Payee):
    supplier = models.ForeignKey(personnelModels.Supplier, on_delete=models.CASCADE)

class ExpenseTransaction(Transaction):
    ledgerAccount = models.ForeignKey(ExpenseLedgerAccount, on_delete=models.CASCADE, related_name='expenses')
    employee = models.ForeignKey(EmployeeAccount, on_delete=models.CASCADE, related_name='transactions')
    supplier = models.ForeignKey(SupplierAccount, on_delete=models.CASCADE, related_name='transactions')
    date_approved = models.DateField()
    discount = models.FloatField()
    quantity = models.FloatField()
    unit_cost = models.FloatField()
    unit_of_measure = models.CharField(max_length=255)

class StudentAccount(sharedModels.Person):
    student = models.ForeignKey(studentsModels.Student, on_delete=models.CASCADE)
    def balanceDue(self):
        return Nothing
    def nextPayment(self):
        return Nothing

class RevenueTransaction(Transaction):
    ledgerAccount = models.ForeignKey(RevenueLedgerAccount, on_delete=models.CASCADE, related_name='revenues')
    student = models.ForeignKey(StudentAccount, on_delete=models.CASCADE, related_name='transactions')
