# Generated by Django 2.1.2 on 2019-03-14 08:17

from django.db import migrations, models
import django.db.models.deletion
from ..models import PayeeAccount


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0006_auto_20190102_1852'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expensecorrectivejournalentry',
            name='payee',
            field=models.ForeignKey(default=PayeeAccount.objects.first().pk, on_delete=django.db.models.deletion.CASCADE, related_name='related_finance_expensecorrectivejournalentry', to='finance.PayeeAccount'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='expensetransaction',
            name='payee',
            field=models.ForeignKey(default=PayeeAccount.objects.first().pk, on_delete=django.db.models.deletion.CASCADE, related_name='related_finance_expensetransaction', to='finance.PayeeAccount'),
            preserve_default=False,
        ),
    ]
