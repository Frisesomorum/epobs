import datetime
from django.db import models
from core.models import Person, Descriptor
from schoolauth.models import School


class Department(Descriptor):
    pass


class Employee(Person):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name='employees')
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='employees')


class Supplier(models.Model):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name='suppliers')
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


PAYEE_TYPE_EMPLOYEE = 'E'
PAYEE_TYPE_SUPPLIER = 'S'
PAYEE_TYPE_CHOICES = (
    (PAYEE_TYPE_EMPLOYEE, 'Employee'),
    (PAYEE_TYPE_SUPPLIER, 'Supplier'),
)


class Payee(models.Model):
    type = models.CharField(max_length=1, choices=PAYEE_TYPE_CHOICES)
    employee = models.OneToOneField(
        Employee, on_delete=models.CASCADE, blank=True, null=True, related_name='payee')
    supplier = models.OneToOneField(
        Supplier, on_delete=models.CASCADE, blank=True, null=True, related_name='payee')

    class Meta:
        default_permissions = ()

    def __str__(self):
        return str(self.entity)

    def set_entity(self, entity):
        if isinstance(entity, Employee):
            self.employee = entity
            self.type = PAYEE_TYPE_EMPLOYEE
        else:
            self.supplier = entity
            self.type = PAYEE_TYPE_SUPPLIER

    @property
    def entity(self):
        if self.type == PAYEE_TYPE_EMPLOYEE:
            return self.employee
        elif self.type == PAYEE_TYPE_SUPPLIER:
            return self.supplier
        return None

    @property
    def school(self):
        return self.entity.school

    @property
    def is_active(self):
        return any(
            contract.active for contract
            in Contract.objects.filter(payee=self).all())

    def start_contract(self):
        contract = Contract.objects.filter(payee=self, active=True).first()
        if contract is None:
            contract = Contract.objects.create(payee=self)
        return contract

    def terminate_contract(self):
        for contract in Contract.objects.filter(payee=self, active=True):
            contract.active = False
            contract.date_terminated = datetime.date.today()
            contract.save()

    @property
    def date_hired(self):
        contract = Contract.objects.filter(payee=self).latest('date_opened')
        if contract is None:
            return None
        return contract.date_opened

    @property
    def date_terminated(self):
        contract = Contract.objects.filter(payee=self).latest('date_terminated')
        if contract is None:
            return None
        return contract.date_terminated


class Contract(models.Model):
    active = models.BooleanField(default=True)
    date_opened = models.DateField(blank=True, null=True, auto_now_add=True)
    date_terminated = models.DateField(blank=True, null=True)
    payee = models.ForeignKey(
        Payee, on_delete=models.CASCADE, related_name='contracts')
