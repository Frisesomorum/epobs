# Generated by Django 2.1.2 on 2018-12-03 04:25

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('personnel', '0003_auto_20181018_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='date_opened',
            field=models.DateField(blank=True, default=django.utils.timezone.now),
        ),
    ]