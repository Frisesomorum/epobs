# Generated by Django 2.2 on 2019-04-12 02:22

from django.db import migrations, models
import finance.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BudgetPeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approval_status', models.CharField(choices=[('D', 'Draft'), ('P', 'Pending Approval'), ('A', 'Approved')], default='D', max_length=1)),
                ('date_submitted', models.DateField(blank=True, null=True)),
                ('date_approved', models.DateField(blank=True, null=True)),
                ('name', models.CharField(blank=True, max_length=255)),
                ('start', models.DateField()),
                ('end', models.DateField()),
            ],
            options={
                'verbose_name': 'budget',
                'ordering': ['start', 'end'],
                'permissions': (('approve_budget', 'Can approve budgets'),),
            },
        ),
        migrations.CreateModel(
            name='ExpenseBudgetItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExpenseCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('abbreviation', models.CharField(blank=True, max_length=15)),
                ('description', models.TextField(blank=True, max_length=4000)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExpenseCorrectiveJournalEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approval_status', models.CharField(choices=[('D', 'Draft'), ('P', 'Pending Approval'), ('A', 'Approved')], default='D', max_length=1)),
                ('date_submitted', models.DateField(blank=True, null=True)),
                ('date_approved', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, max_length=4000)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('quantity', models.DecimalField(decimal_places=2, default=1, max_digits=15)),
                ('unit_cost', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('tax', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
            ],
            options={
                'permissions': (('approve_expensecorrectivejournalentry', 'Can approve expense corrective journal entries'),),
            },
        ),
        migrations.CreateModel(
            name='ExpenseLedgerAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('abbreviation', models.CharField(blank=True, max_length=15)),
                ('description', models.TextField(blank=True, max_length=4000)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExpenseTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approval_status', models.CharField(choices=[('D', 'Draft'), ('P', 'Pending Approval'), ('A', 'Approved')], default='D', max_length=1)),
                ('date_submitted', models.DateField(blank=True, null=True)),
                ('date_approved', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, max_length=4000)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('quantity', models.DecimalField(decimal_places=2, default=1, max_digits=15)),
                ('unit_cost', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('discount', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('tax', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
            ],
            options={
                'permissions': (('approve_expensetransaction', 'Can approve expenses'),),
            },
            bases=(finance.models.AdmitsCorrections, models.Model),
        ),
        migrations.CreateModel(
            name='Fund',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('abbreviation', models.CharField(blank=True, max_length=15)),
                ('description', models.TextField(blank=True, max_length=4000)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PayeeAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='RevenueBudgetItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RevenueCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('abbreviation', models.CharField(blank=True, max_length=15)),
                ('description', models.TextField(blank=True, max_length=4000)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RevenueCorrectiveJournalEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('approval_status', models.CharField(choices=[('D', 'Draft'), ('P', 'Pending Approval'), ('A', 'Approved')], default='D', max_length=1)),
                ('date_submitted', models.DateField(blank=True, null=True)),
                ('date_approved', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, max_length=4000)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
            ],
            options={
                'permissions': (('approve_revenuecorrectivejournalentry', 'Can approve revenue corrective journal entries'),),
            },
        ),
        migrations.CreateModel(
            name='RevenueLedgerAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('abbreviation', models.CharField(blank=True, max_length=15)),
                ('description', models.TextField(blank=True, max_length=4000)),
                ('is_student_fee', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RevenueTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notes', models.TextField(blank=True, max_length=4000)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, finance.models.AdmitsCorrections),
        ),
        migrations.CreateModel(
            name='SchoolFee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
            ],
        ),
        migrations.CreateModel(
            name='StudentAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'default_permissions': (),
            },
        ),
    ]
