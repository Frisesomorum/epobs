# Generated by Django 2.1 on 2018-09-21 06:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('schoolauth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GraduatingClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('graduating_year', models.SmallIntegerField(unique=True)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('admission_fee', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('school_fee', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('canteen_fee', models.DecimalField(decimal_places=2, default=0, max_digits=15)),
                ('graduated', models.BooleanField(default=False)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='graduating_classes', to='schoolauth.School')),
            ],
        ),
        migrations.CreateModel(
            name='SchoolProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='school_profile', to='schoolauth.School')),
            ],
        ),
    ]