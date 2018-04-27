# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from models import ParticipantesModel

# Register your models here.

class ParticipantesForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = ParticipantesModel

class MyUserAdmin(UserAdmin):
    form = ParticipantesForm

    fieldsets = UserAdmin.fieldsets + (
            (None, {'fields': ('FechaNacimiento','Sexo','TipoDocumento','Identificicacion','Ciudad','Telefono','Celular','Direccion','NITEmpresa','CargoEmpresa')}),
    )

admin.site.register(ParticipantesModel, MyUserAdmin)
