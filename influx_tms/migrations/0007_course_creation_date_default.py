# Generated by Django 2.2.7 on 2019-12-02 15:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('influx_tms', '0006_auto_20191202_1042'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='creation_date_default',
            field=models.DateTimeField(blank=True, default=datetime.date(2020, 1, 1), verbose_name='creation date default'),
        ),
    ]
