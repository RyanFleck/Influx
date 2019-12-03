# Generated by Django 2.2.7 on 2019-12-03 19:07

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('influx_tms', '0009_team_team_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='program_of_study',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='creation_deadline_default',
            field=models.DateTimeField(blank=True, default=datetime.date(2020, 1, 2), verbose_name='creation deadline default'),
        ),
    ]
