from django.db.models.signals import post_save
from django.dispatch import receiver
from . import models


@receiver(post_save, sender=models.Employee, dispatch_uid="create_linked_employee_payee")
def create_employee_payee(sender, instance, created, **kwargs):
    if created:
        payee = models.Payee()
        payee.set_entity(instance)
        payee.save()


@receiver(post_save, sender=models.Supplier, dispatch_uid="create_linked_supplier_payee")
def create_supplier_payee(sender, instance, created, **kwargs):
    if created:
        payee = models.Payee()
        payee.set_entity(instance)
        payee.save()
