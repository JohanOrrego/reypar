# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-26 15:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mundial', '0010_auto_20180426_1027'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tablasposocionesusuariosmodel',
            unique_together=set([('Grupo', 'Equipo', 'Participante')]),
        ),
    ]