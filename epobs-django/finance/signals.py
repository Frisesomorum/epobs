from students.models import Student
from personnel.models import Employee, Supplier
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StudentAccount, EmployeeAccount, SupplierAccount


@receiver(post_save, sender=Student, dispatch_uid="create_linked_student_account")
def create_student_account(sender, instance, created, **kwargs):
    if created:
        StudentAccount.objects.create(student=instance)


@receiver(post_save, sender=Employee, dispatch_uid="create_linked_employee_account")
def create_employee_account(sender, instance, created, **kwargs):
    if created:
        EmployeeAccount.objects.create(employee=instance)


@receiver(post_save, sender=Supplier, dispatch_uid="create_linked_supplier_account")
def create_supplier_account(sender, instance, created, **kwargs):
    if created:
        SupplierAccount.objects.create(supplier=instance)
