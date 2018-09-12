# Generated by Django 2.1 on 2018-09-12 22:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('schoolauth', '0001_initial'),
        ('personnel', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='supplier',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suppliers', to='schoolauth.School'),
        ),
        migrations.AddField(
            model_name='employee',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='employees', to='schoolauth.School'),
        ),
        migrations.AlterUniqueTogether(
            name='employee',
            unique_together={('first_name', 'last_name', 'date_of_birth')},
        ),
    ]
