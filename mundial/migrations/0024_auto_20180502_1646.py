# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-05-02 21:46
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mundial', '0023_auto_20180502_1616'),
    ]

    operations = [
        migrations.CreateModel(
            name='FaseFinalAdminModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('FechaPartido', models.DateField()),
                ('Equipo1', models.CharField(max_length=50)),
                ('MarcadorEquipo1', models.IntegerField()),
                ('Equipo2', models.CharField(max_length=50)),
                ('MarcadorEquipo2', models.IntegerField()),
                ('PenalEquipoGanador', models.CharField(max_length=50)),
                ('Identificador', models.IntegerField()),
                ('FechaRegistro', models.DateTimeField(auto_now_add=True)),
                ('Participante', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'tblFaseFinalAdmin',
            },
        ),
        migrations.AlterUniqueTogether(
            name='fasefinaladminmodel',
            unique_together=set([('Equipo1', 'Equipo2', 'Participante')]),
        ),
    ]
