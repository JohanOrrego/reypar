# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-23 22:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mundial', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participantesmodel',
            name='Apellidos',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='participantesmodel',
            name='CargoEmpresa',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='participantesmodel',
            name='Celular',
            field=models.CharField(blank=True, max_length=13, null=True),
        ),
        migrations.AlterField(
            model_name='participantesmodel',
            name='Ciudad',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='participantesmodel',
            name='Direccion',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='participantesmodel',
            name='FechaNacimiento',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='participantesmodel',
            name='Identificicacion',
            field=models.CharField(blank=True, max_length=25, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='participantesmodel',
            name='NITEmpresa',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='participantesmodel',
            name='Nombres',
            field=models.CharField(blank=True, max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='participantesmodel',
            name='Sexo',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'Femenino'), (2, 'Masculino')], null=True),
        ),
        migrations.AlterField(
            model_name='participantesmodel',
            name='TipoDocumento',
            field=models.PositiveSmallIntegerField(blank=True, choices=[(1, 'C\xe9dula de Ciudadan\xeda'), (2, 'C\xe9dula de Extranjer\xeda'), (3, 'Pasaporte')], null=True),
        ),
    ]
