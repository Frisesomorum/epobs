# Generated by Django 2.1 on 2018-08-17 02:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_auto_20180816_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expensecorrectivejournalentry',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='expensetransaction',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='revenuecorrectivejournalentry',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='revenuetransaction',
            name='paid',
            field=models.BooleanField(default=False),
        ),
    ]
