# Generated by Django 2.1 on 2018-08-14 05:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('epobs', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_accountant',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_bookkeeper',
        ),
    ]
