# Generated by Django 2.1 on 2018-09-12 22:57

from django.db import migrations, models
import finance.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
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
                ('abbreviation', models.CharField(max_length=15)),
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
                ('notes', models.TextField(blank=True, max_length=4000)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('approval_status', models.CharField(choices=[('D', 'Draft'), ('S', 'Submitted'), ('A', 'Approved')], default='D', max_length=1)),
                ('date_submitted', models.DateField(blank=True, null=True)),
                ('date_approved', models.DateField(blank=True, null=True)),
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
                ('abbreviation', models.CharField(max_length=15)),
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
                ('notes', models.TextField(blank=True, max_length=4000)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('approval_status', models.CharField(choices=[('D', 'Draft'), ('S', 'Submitted'), ('A', 'Approved')], default='D', max_length=1)),
                ('date_submitted', models.DateField(blank=True, null=True)),
                ('date_approved', models.DateField(blank=True, null=True)),
                ('discount', models.FloatField(blank=True, null=True)),
                ('quantity', models.FloatField(blank=True, null=True)),
                ('unit_cost', models.FloatField(blank=True, null=True)),
                ('unit_of_measure', models.CharField(blank=True, max_length=255)),
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
                ('abbreviation', models.CharField(max_length=15)),
                ('description', models.TextField(blank=True, max_length=4000)),
            ],
            options={
                'abstract': False,
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
                ('abbreviation', models.CharField(max_length=15)),
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
                ('notes', models.TextField(blank=True, max_length=4000)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('amount', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('approval_status', models.CharField(choices=[('D', 'Draft'), ('S', 'Submitted'), ('A', 'Approved')], default='D', max_length=1)),
                ('date_submitted', models.DateField(blank=True, null=True)),
                ('date_approved', models.DateField(blank=True, null=True)),
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
                ('abbreviation', models.CharField(max_length=15)),
                ('description', models.TextField(blank=True, max_length=4000)),
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
            name='StudentAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='SupplierAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255)),
                ('start', models.DateField()),
                ('end', models.DateField()),
            ],
        ),
    ]
