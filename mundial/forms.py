# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from models import *
from django.forms import ModelForm, ModelChoiceField
from datetime import *
import os, sys
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class RegistroParticipantesForm(UserCreationForm):

	password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'class':'form-control'}))
	password2 = forms.CharField(label='Contraseña (confirmar)', widget=forms.PasswordInput(attrs={'class':'form-control','data-validate-linked':'password1'}))

	NombreComercial = forms.CharField(label='Nombre comercial', widget=forms.TextInput(attrs={'class':'form-control', 'readonly': 'readonly'}),required=False)
	RazonSocial = forms.CharField(label='Razón social', widget=forms.TextInput(attrs={'class':'form-control', 'readonly': 'readonly'}),required=False)
	DireccionCliente = forms.CharField(label='Dirección cliente', widget=forms.TextInput(attrs={'class':'form-control', 'readonly': 'readonly'}),required=False)
	CiudadCliente = forms.CharField(label='Ciudad Cliente', widget=forms.TextInput(attrs={'class':'form-control', 'readonly': 'readonly'}),required=False)
	
	class Meta:
		model= ParticipantesModel
		fields=[
		'first_name',
		'last_name',
		'email',
		'FechaNacimiento',
		'Sexo',
		'TipoDocumento',
		'Identificicacion',
		'Ciudad',
		'Telefono',
		'Celular',
		'Direccion',
		'NITEmpresa',
		'CargoEmpresa',
		'username',
		'password1',
		'password2',
		]
		labels={
		'first_name' : 'Nombres',
		'last_name' : 'Apellidos',
		'email' : 'Correo electrónico',
		'FechaNacimiento' : 'Fecha nacimiento',
		'Sexo':'Sexo',
		'TipoDocumento': 'Tipo de documento',
		'Identificicacion' : 'Número de documento',
		'Ciudad' : 'Ciudad',
		'Telefono' :'Teléfono',
		'Celular' :'Celular',
		'Direccion' :'Dirección',
		'NITEmpresa' :'NIT empresa',
		'CargoEmpresa' :'Cargo en su empresa',
		'username' : 'Nombre de usuario',
		'password1' : 'Contraseña',
		'password2' : 'Contraseña (Confirmación)',
		}
		help_texts = {
            'username': 'Requiere. 150 caracteres o menos. letras, dígitos.'
        }
		widgets={
		'first_name':forms.TextInput(attrs={'class':'form-control','required': 'true'}),
		'last_name':forms.TextInput(attrs={'class':'form-control','required': 'true'}),
		'email':forms.TextInput(attrs={'class':'form-control','required': 'true', 'type':'email'}),
		'FechaNacimiento': forms.TextInput(attrs={'class':'form-control', 'id':'datepicker', 'data-inputmask':'"mask": "9999-99-99"','data-mask':'true'}),
		'Sexo' : forms.Select(attrs={'class':'form-control'}),
		'TipoDocumento' : forms.Select(attrs={'class':'form-control'}),
		'Identificicacion':forms.TextInput(attrs={'class':'form-control','type':'tel'}),
		'Ciudad':forms.TextInput(attrs={'class':'form-control','type':'text','pattern':'[a-zA-Z]*'}),
		'Telefono':forms.TextInput(attrs={'class':'form-control','type':'tel' }),
		'Celular':forms.TextInput(attrs={'class':'form-control', 'type':'tel'}),
		'Direccion':forms.TextInput(attrs={'class':'form-control'}),
		'NITEmpresa':forms.TextInput(attrs={'class':'form-control'}),
		'CargoEmpresa':forms.TextInput(attrs={'class':'form-control'}),
		'username':forms.TextInput(attrs={'class':'form-control'}),
		}
class FiltroForms(forms.Form):
		criterio=forms.CharField(label='NIT Cliente', widget=forms.TextInput(attrs={'class':'form-control'}),required=True)
		

