from django.db import models
from django.contrib.auth.models import User
# TODO: set nullability
# TODO: meta properties
# TODO: documentation
# TODO: implement all methods
# TODO: update the UML document to reflect changes done during development

class School(models.Model):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    admission_fee = models.DecimalField(max_digits=15, decimal_places=2)
    school_fee = models.DecimalField(max_digits=15, decimal_places=2)
    canteen_fee = models.DecimalField(max_digits=15, decimal_places=2)
    # TODO: define static set/get methods

class Descriptor(models.Model):
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=15)
    description = models.TextField(max_length=4000)
    class Meta:
        abstract = True

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

class Fund(Descriptor):
    pass

class Category(Descriptor):
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

class LedgerAccount(Descriptor):
    class Meta:
        abstract = True

class ExpenseLedgerAccount(LedgerAccount):
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, related_name='ledger_accounts')

class RevenueLedgerAccount(LedgerAccount):
    category = models.ForeignKey(RevenueCategory, on_delete=models.CASCADE, related_name='ledger_accounts')

class BudgetItem(Descriptor):
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='%(app_label)s_%(class)s_budget')
    class Meta:
        abstract = True

class ExpenseBudgetItem(BudgetItem):
    ledgerAccount = models.ForeignKey(ExpenseLedgerAccount, on_delete=models.CASCADE, related_name='budget')

class RevenueBudgetItem(BudgetItem):
    ledgerAccount = models.ForeignKey(RevenueLedgerAccount, on_delete=models.CASCADE, related_name='budget')

class Person(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    email = models.CharField(max_length=255)
    def __str__(self):
        return self.last_name + ', ' + self.first_name

    class Meta:
        abstract = True

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
    date_hired = models.DateField()
    date_terminated = models.DateField()
    def balanceDue(self):
        return Nothing
    def amountPaid(self):
        return Nothing
    class Meta:
        abstract = True

class Employee(Person, Payee):
    pass

class Supplier(Payee):
    name = models.CharField(max_length=255)

class ExpenseTransaction(Transaction):
    ledgerAccount = models.ForeignKey(ExpenseLedgerAccount, on_delete=models.CASCADE, related_name='expenses')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='transactions')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='transactions')
    date_approved = models.DateField()
    discount = models.FloatField()
    quantity = models.FloatField()
    unit_cost = models.FloatField()
    unit_of_measure = models.CharField(max_length=255)

# class StudentAccount(Student, term):
##  get student student = Student(id)
##  amounthistory =  Student.records
##  current_amount_due = Student.current_amount_due
##  next_payment  = Student.next_payment
##  balanceDue()
class Student(Person):
    def balanceDue(self):
        return Nothing

class RevenueTransaction(Transaction):
    ledgerAccount = models.ForeignKey(RevenueLedgerAccount, on_delete=models.CASCADE, related_name='revenues')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='transactions')
