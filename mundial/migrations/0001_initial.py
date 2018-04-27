# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-23 22:42
from __future__ import unicode_literals

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParticipantesModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.ASCIIUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('Nombres', models.CharField(max_length=25)),
                ('Apellidos', models.CharField(max_length=25)),
                ('FechaNacimiento', models.DateField()),
                ('Sexo', models.PositiveSmallIntegerField(choices=[(1, 'Femenino'), (2, 'Masculino')])),
                ('TipoDocumento', models.PositiveSmallIntegerField(choices=[(1, 'C\xe9dula de Ciudadan\xeda'), (2, 'C\xe9dula de Extranjer\xeda'), (3, 'Pasaporte')])),
                ('Identificicacion', models.CharField(max_length=25, unique=True)),
                ('Ciudad', models.CharField(max_length=50)),
                ('Telefono', models.CharField(blank=True, max_length=9, null=True)),
                ('Celular', models.CharField(max_length=13)),
                ('Direccion', models.CharField(max_length=50)),
                ('NITEmpresa', models.CharField(max_length=15)),
                ('CargoEmpresa', models.CharField(max_length=15)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='ClasificacionClienteModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Nombre', models.CharField(max_length=2)),
                ('Cupo', models.IntegerField()),
            ],
            options={
                'db_table': 'tblClasificacionCliente',
            },
        ),
        migrations.CreateModel(
            name='ClientesModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('NIT', models.CharField(max_length=15)),
                ('NombreComercial', models.CharField(max_length=50)),
                ('RazonSocial', models.CharField(max_length=50)),
                ('Ciudad', models.CharField(max_length=50)),
                ('Direccion', models.CharField(max_length=50)),
                ('Telefono', models.CharField(max_length=50)),
                ('Vendedor', models.IntegerField()),
                ('Clasificacion', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='mundial.ClasificacionClienteModel')),
            ],
            options={
                'db_table': 'tblClientes',
            },
        ),
        migrations.AlterUniqueTogether(
            name='clientesmodel',
            unique_together=set([('NIT',)]),
        ),
    ]
