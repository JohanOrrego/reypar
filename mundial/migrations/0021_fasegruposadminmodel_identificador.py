# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-02 13:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mundial', '0020_auto_20180501_2150'),
    ]

    operations = [
        migrations.AddField(
            model_name='fasegruposadminmodel',
            name='Identificador',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
