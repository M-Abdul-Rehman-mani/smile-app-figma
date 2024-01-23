# Generated by Django 5.0.1 on 2024-01-22 07:36

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_usersmilemodel_best_smile_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersmilemodel',
            name='best_smile_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
