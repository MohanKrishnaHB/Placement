# Generated by Django 2.2.2 on 2019-10-02 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company_round',
            name='round_type',
            field=models.CharField(choices=[('Aptitude', 'Aptitude'), ('Technical', 'Technical'), ('Discussion', 'Discussion'), ('Interview', 'Interview')], default='Aptitude', max_length=30),
        ),
    ]
