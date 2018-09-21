from students.models import Student
from personnel.models import Payee
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StudentAccount, PayeeAccount


@receiver(post_save, sender=Student, dispatch_uid="create_linked_student_account")
def create_student_account(sender, instance, created, **kwargs):
    if created:
        StudentAccount.objects.create(student=instance)


@receiver(post_save, sender=Payee, dispatch_uid="create_linked_payee_account")
def create_payee_account(sender, instance, created, **kwargs):
    if created:
        PayeeAccount.objects.create(payee=instance)
