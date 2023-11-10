# Generated by Django 4.0 on 2023-11-08 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('STUDENT', 'Student'), ('TEACHER', 'Teacher')], default='STUDENT', max_length=10, verbose_name='Role'),
        ),
    ]
