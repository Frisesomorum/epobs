# Generated by Django 2.1 on 2018-08-17 00:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from epobs.models import User

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('finance', '0002_auto_20180813_2202'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExpenseCorrectiveJournalEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True, max_length=4000)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('amount_charged', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('paid', models.BooleanField()),
                ('when_paid', models.DateTimeField(blank=True, null=True)),
                ('partial_amount_paid', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('approval_status', models.CharField(choices=[('D', 'Draft'), ('S', 'Submitted'), ('A', 'Approved')], default='D', max_length=1)),
                ('date_submitted', models.DateField(blank=True, null=True)),
                ('date_approved', models.DateField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='approved_finance_expensecorrectivejournalentry', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_finance_expensecorrectivejournalentry', to=settings.AUTH_USER_MODEL)),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='related_finance_expensecorrectivejournalentry', to='finance.EmployeeAccount')),
                ('ledger_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_finance_expensecorrectivejournalentry', to='finance.ExpenseLedgerAccount')),
                ('submitted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='submitted_finance_expensecorrectivejournalentry', to=settings.AUTH_USER_MODEL)),
                ('supplier', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='related_finance_expensecorrectivejournalentry', to='finance.SupplierAccount')),
            ],
            options={
                'permissions': (('approve_expensecorrectivejournalentry', 'Can approve expense corrective journal entries'),),
            },
        ),
        migrations.CreateModel(
            name='RevenueCorrectiveJournalEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True, max_length=4000)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('amount_charged', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('paid', models.BooleanField()),
                ('when_paid', models.DateTimeField(blank=True, null=True)),
                ('partial_amount_paid', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('approval_status', models.CharField(choices=[('D', 'Draft'), ('S', 'Submitted'), ('A', 'Approved')], default='D', max_length=1)),
                ('date_submitted', models.DateField(blank=True, null=True)),
                ('date_approved', models.DateField(blank=True, null=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='approved_finance_revenuecorrectivejournalentry', to=settings.AUTH_USER_MODEL)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_finance_revenuecorrectivejournalentry', to=settings.AUTH_USER_MODEL)),
                ('ledger_account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_finance_revenuecorrectivejournalentry', to='finance.RevenueLedgerAccount')),
                ('student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='related_finance_revenuecorrectivejournalentry', to='finance.StudentAccount')),
                ('submitted_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='submitted_finance_revenuecorrectivejournalentry', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': (('approve_revenuecorrectivejournalentry', 'Can approve revenue corrective journal entries'),),
            },
        ),
        migrations.RemoveField(
            model_name='expensetransaction',
            name='date_issued',
        ),
        migrations.RemoveField(
            model_name='expensetransaction',
            name='date_paid',
        ),
        migrations.RemoveField(
            model_name='revenuetransaction',
            name='date_issued',
        ),
        migrations.RemoveField(
            model_name='revenuetransaction',
            name='date_paid',
        ),
        migrations.AddField(
            model_name='expensetransaction',
            name='approval_status',
            field=models.CharField(choices=[('D', 'Draft'), ('S', 'Submitted'), ('A', 'Approved')], default='D', max_length=1),
        ),
        migrations.AddField(
            model_name='expensetransaction',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='approved_finance_expensetransaction', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='expensetransaction',
            name='created_by',
            field=models.ForeignKey(default=User.objects.first().pk, on_delete=django.db.models.deletion.PROTECT, related_name='created_finance_expensetransaction', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='expensetransaction',
            name='date_submitted',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='expensetransaction',
            name='submitted_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='submitted_finance_expensetransaction', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='expensetransaction',
            name='when_paid',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='revenuetransaction',
            name='created_by',
            field=models.ForeignKey(default=User.objects.first().pk, on_delete=django.db.models.deletion.PROTECT, related_name='created_finance_revenuetransaction', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='revenuetransaction',
            name='when_paid',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='expensebudgetitem',
            name='term',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_finance_expensebudgetitem', to='finance.Term'),
        ),
        migrations.AlterField(
            model_name='expensecategory',
            name='fund',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_finance_expensecategory', to='finance.Fund'),
        ),
        migrations.AlterField(
            model_name='expensetransaction',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='related_finance_expensetransaction', to='finance.EmployeeAccount'),
        ),
        migrations.AlterField(
            model_name='expensetransaction',
            name='ledger_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_finance_expensetransaction', to='finance.ExpenseLedgerAccount'),
        ),
        migrations.AlterField(
            model_name='expensetransaction',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='related_finance_expensetransaction', to='finance.SupplierAccount'),
        ),
        migrations.AlterField(
            model_name='revenuebudgetitem',
            name='term',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_finance_revenuebudgetitem', to='finance.Term'),
        ),
        migrations.AlterField(
            model_name='revenuecategory',
            name='fund',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_finance_revenuecategory', to='finance.Fund'),
        ),
        migrations.AlterField(
            model_name='revenuetransaction',
            name='ledger_account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_finance_revenuetransaction', to='finance.RevenueLedgerAccount'),
        ),
        migrations.AlterField(
            model_name='revenuetransaction',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='related_finance_revenuetransaction', to='finance.StudentAccount'),
        ),
        migrations.AddField(
            model_name='expensetransaction',
            name='restatement_for_cje',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='restated_in', to='finance.ExpenseCorrectiveJournalEntry'),
        ),
        migrations.AddField(
            model_name='expensetransaction',
            name='reversal_for_cje',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reversed_in', to='finance.ExpenseCorrectiveJournalEntry'),
        ),
        migrations.AddField(
            model_name='expensetransaction',
            name='revised_by_cje',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='revision_to', to='finance.ExpenseCorrectiveJournalEntry'),
        ),
        migrations.AddField(
            model_name='revenuetransaction',
            name='restatement_for_cje',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='restated_in', to='finance.RevenueCorrectiveJournalEntry'),
        ),
        migrations.AddField(
            model_name='revenuetransaction',
            name='reversal_for_cje',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reversed_in', to='finance.RevenueCorrectiveJournalEntry'),
        ),
        migrations.AddField(
            model_name='revenuetransaction',
            name='revised_by_cje',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='revision_to', to='finance.RevenueCorrectiveJournalEntry'),
        ),
    ]
