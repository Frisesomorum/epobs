# Generated by Django 2.1 on 2018-10-18 22:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='external_id',
            field=models.CharField(blank=True, max_length=31, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='student',
            unique_together=set(),
        ),
    ]
