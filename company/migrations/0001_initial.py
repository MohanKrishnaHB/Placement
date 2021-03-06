# Generated by Django 2.2.2 on 2019-09-22 11:21

from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Company',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=50)),
                ('description', models.TextField()),
                ('venue', models.CharField(default='MITM', max_length=50)),
                ('date_of_visit', models.DateField()),
                ('min_SSLC_percentage', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('min_PUC_percentage', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5)),
                ('min_CGPA', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=4)),
                ('max_SSLC_percentage', models.DecimalField(decimal_places=2, default=Decimal('100.00'), max_digits=5)),
                ('max_PUC_percentage', models.DecimalField(decimal_places=2, default=Decimal('100.00'), max_digits=5)),
                ('max_CGPA', models.DecimalField(decimal_places=2, default=Decimal('10.00'), max_digits=4)),
                ('package', models.CharField(default='Open', max_length=10)),
                ('status', models.CharField(choices=[('0', 'Not-active'), ('2', 'Active'), ('1', 'Finished')], default='0', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Company_Round',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField()),
                ('round_title', models.CharField(max_length=80)),
                ('round_date', models.DateField()),
                ('status', models.CharField(choices=[('1', 'Not-active'), ('2', 'Active'), ('0', 'Finished')], default='1', max_length=15)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.Company')),
            ],
        ),
        migrations.CreateModel(
            name='Company_Department',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('department', models.CharField(choices=[('ISE', 'ISE'), ('CSE', 'CSE'), ('ECE', 'ECE'), ('MEC', 'MEC'), ('CIV', 'CIV'), ('MBA', 'MBA'), ('MCA', 'MCA')], max_length=10)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='company.Company')),
            ],
        ),
    ]
