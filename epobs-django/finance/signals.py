from students.models import Student
from personnel.models import Payee
from django.db.models.signals import post_save
from django.dispatch import receiver
from schools.models import GraduatingClass
from .models import StudentAccount, PayeeAccount, RevenueLedgerAccount, SchoolFee


@receiver(post_save, sender=Student, dispatch_uid="create_linked_student_account")
def create_student_account(sender, instance, created, **kwargs):
    if created:
        StudentAccount.objects.create(student=instance)


@receiver(post_save, sender=Payee, dispatch_uid="create_linked_payee_account")
def create_payee_account(sender, instance, created, **kwargs):
    if created:
        PayeeAccount.objects.create(payee=instance)


@receiver(post_save, sender=GraduatingClass, dispatch_uid="create_linked_school_fees_for_graduating_class")
def create_school_fees_for_graduating_class(sender, instance, created, **kwargs):
    if created:
        for ledger_account in RevenueLedgerAccount.objects.filter(is_student_fee=True).all():
            SchoolFee.objects.create(ledger_account=ledger_account, graduating_class=instance)


@receiver(post_save, sender=RevenueLedgerAccount, dispatch_uid="create_linked_school_fees_for_ledger_account")
def create_school_fees_for_ledger_account(sender, instance, created, **kwargs):
    existing_fees = SchoolFee.objects.filter(ledger_account=instance).iterator()
    if instance.is_student_fee:
        for graduating_class in GraduatingClass.objects.all():
            if graduating_class not in existing_fees:
                SchoolFee.objects.create(ledger_account=instance, graduating_class=graduating_class)
