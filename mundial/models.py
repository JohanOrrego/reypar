# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime

# Create your models here.

# modelo para la clasificacion de los clientes
class ClasificacionClienteModel(models.Model):
	Nombre = models.CharField(max_length=2)
	Cupo = models.IntegerField()

	class Meta:
		db_table = 'tblClasificacionCliente'

	def __unicode__(self):  # __unicode__ for Python 2
		return self.Nombre

# modelo para el registro de los clientes
class ClientesModel(models.Model):

	NIT = models.CharField(max_length=15)
	NombreComercial = models.CharField(max_length=50)
	RazonSocial = models.CharField(max_length=50)
	Ciudad = models.CharField(max_length=50)
	Direccion = models.CharField(max_length=50)
	Telefono = models.CharField(max_length=50)
	Clasificacion = models.ForeignKey(ClasificacionClienteModel, models.DO_NOTHING)
	Vendedor = models.IntegerField()

	class Meta:
		db_table = 'tblClientes'
		unique_together = (('NIT'),)

	@property
	def json(self):
		if len(self.NombreComercial)>3:
			nombreEmpresa=self.NombreComercial
		else:
			nombreEmpresa=self.RazonSocial

		return {
                'NIT' : self.NIT,
                'NombreComercial' : nombreEmpresa,
                'RazonSocial' : self.RazonSocial,
                'Ciudad' : self.Ciudad,
                'Direccion' : self.Direccion,
                'Telefono' : self.Telefono,
                'Clasificacion' : self.Clasificacion.Nombre,
                'Vendedor' : self.Vendedor,
                'total': str(self.Clasificacion.Cupo),
                'cupos':ParticipantesModel.objects.filter(NITEmpresa=self.NIT).count()

            }

# modelo para el registro de los participantes en la polla 
class ParticipantesModel(AbstractUser):
	SEXO_CHOICES = (
		(1,'Femenino'),
		(2,'Masculino'),)
	TIPOIDENTIFICACION_CHOICES = (
		(1,'Cédula de Ciudadanía'),
		(2,'Cédula de Extranjería'),
		(3,'Pasaporte'))
	FechaNacimiento = models.DateField()
	Sexo = models.PositiveSmallIntegerField(choices=SEXO_CHOICES)
	TipoDocumento = models.PositiveSmallIntegerField(choices=TIPOIDENTIFICACION_CHOICES)
	Identificicacion = models.CharField(max_length=25, unique=True)
	Ciudad = models.CharField(max_length=50)
	Telefono = models.CharField(max_length=9,null=True, blank=True)
	Celular = models.CharField(max_length=15)
	Direccion = models.CharField(max_length=50)
	NITEmpresa = models.CharField(max_length=15)
	CargoEmpresa = models.CharField(max_length=15)
	class Meta:
		unique_together = (('email'),)

	@property
	def json(self):

		if self.NITEmpresa != '1' and len(ClientesModel.objects.filter(NIT=self.NITEmpresa).values('NombreComercial')[0]['NombreComercial'])>3:
			nombreEmpresa=ClientesModel.objects.filter(NIT=self.NITEmpresa).values('NombreComercial')[0]['NombreComercial']
		elif self.NITEmpresa != '1':
			nombreEmpresa=ClientesModel.objects.filter(NIT=self.NITEmpresa).values('RazonSocial')[0]['RazonSocial']
		else:
			nombreEmpresa='Administrador'
		return {
            'nombre' : str(self.first_name)+str(' ')+ str(self.last_name),
            'Identificicacion' : self.Identificicacion,
            'Ciudad' : self.Ciudad,
            'NITEmpresa' : self.NITEmpresa,
            'NombreEmpresa': nombreEmpresa,
            'CargoEmpresa' : self.CargoEmpresa,
            }


# modelo para el registro de los participantes en la polla 
class RankingModel(models.Model):
	Participante = models.ForeignKey(ParticipantesModel, models.DO_NOTHING)
	PuntajeFaseGrupos = models.IntegerField(default=0)
	PuntajeOctavos = models.IntegerField(default=0)
	PuntajeCuartos = models.IntegerField(default=0)
	PuntajeSeminFinales = models.IntegerField(default=0)
	PuntajeFinal = models.IntegerField(default=0)
	Puntaje = models.IntegerField()
	FechaRegistro = models.DateTimeField(auto_now_add=True)
	FechaModifica = models.DateTimeField(auto_now=True, null=True, blank=True)

	class Meta:
		db_table = 'tblRankingUsuarios'
		unique_together = (('Participante'),)


# modelo para el regitro de los resultados en la fase de grupos por participantes de la polla mundialista
class FaseGruposUsuariosModel(models.Model):
	FechaPartido = models.DateField()
	Grupo = models.CharField(max_length=10)
	Equipo1 = models.CharField(max_length=50)
	MarcadorEquipo1 = models.IntegerField()
	Equipo2 = models.CharField(max_length=50)
	MarcadorEquipo2 = models.IntegerField()
	Participante = models.ForeignKey(ParticipantesModel, models.DO_NOTHING)
	FechaRegistro = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'tblFaseGruposUsuarios'
		unique_together = (('Grupo','Equipo1','Equipo2','Participante'),)

# modelo para el regitro de los resultados en la fase de grupos por el administrador de la polla mundialista
class FaseGruposAdminModel(models.Model):
	FechaPartido = models.DateField()
	Grupo = models.CharField(max_length=10)
	Equipo1 = models.CharField(max_length=50)
	MarcadorEquipo1 = models.IntegerField()
	Equipo2 = models.CharField(max_length=50)
	MarcadorEquipo2 = models.IntegerField()
	Participante = models.ForeignKey(ParticipantesModel, models.DO_NOTHING)
	Identificador = models.IntegerField()
	FechaRegistro = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'tblFaseGruposAdmin'
		unique_together = (('Grupo','Equipo1','Equipo2','Participante'),)


# modelo para el regitro de los puntos obtenidos por los equipos de cada usuario
class TablasPosocionesUsuariosModel(models.Model):
	Grupo = models.CharField(max_length=10)
	Equipo = models.CharField(max_length=50)
	PartidoJugados = models.IntegerField()
	Ganados = models.IntegerField()
	Empatados = models.IntegerField()
	Perdidos = models.IntegerField()
	GolaFavor = models.IntegerField()
	GolContra = models.IntegerField()
	GolDiferencia = models.IntegerField()
	Puntos = models.IntegerField()
	Participante = models.ForeignKey(ParticipantesModel, models.DO_NOTHING)
	FechaRegistro = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'tblTablasPosocionesUsuarios'
		unique_together = (('Grupo','Equipo','Participante'),)

# modelo para el regitro de los resultados en la fase de octavos por participantes de la polla mundialista
class FaseOctavosUsuariosModel(models.Model):
	FechaPartido = models.DateField()
	Equipo1 = models.CharField(max_length=50)
	MarcadorEquipo1 = models.IntegerField()
	Equipo2 = models.CharField(max_length=50)
	MarcadorEquipo2 = models.IntegerField()
	PenalEquipoGanador = models.CharField(max_length=50)
	Identificador = models.IntegerField()
	Participante = models.ForeignKey(ParticipantesModel, models.DO_NOTHING)
	FechaRegistro = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'tblFaseOctavosUsuarios'
		unique_together = (('Equipo1','Equipo2','Participante'),)

# modelo para el regitro de los resultados en la fase de octavos por participantes de la polla mundialista
class FaseOctavosAdminModel(models.Model):
	FechaPartido = models.DateField()
	Equipo1 = models.CharField(max_length=50)
	MarcadorEquipo1 = models.IntegerField()
	Equipo2 = models.CharField(max_length=50)
	MarcadorEquipo2 = models.IntegerField()
	PenalEquipoGanador = models.CharField(max_length=50)
	Identificador = models.IntegerField()
	Participante = models.ForeignKey(ParticipantesModel, models.DO_NOTHING)
	FechaRegistro = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'tblFaseOctavosAdmin'
		unique_together = (('Equipo1','Equipo2','Participante'),)

# modelo para el regitro de los resultados en la fase de Cuartos por participantes de la polla mundialista
class FaseCuartosUsuariosModel(models.Model):
	FechaPartido = models.DateField()
	Equipo1 = models.CharField(max_length=50)
	MarcadorEquipo1 = models.IntegerField()
	Equipo2 = models.CharField(max_length=50)
	MarcadorEquipo2 = models.IntegerField()
	PenalEquipoGanador = models.CharField(max_length=50)
	Identificador = models.IntegerField()
	Participante = models.ForeignKey(ParticipantesModel, models.DO_NOTHING)
	FechaRegistro = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'tblFaseCuartosUsuarios'
		unique_together = (('Equipo1','Equipo2','Participante'),)

# modelo para el regitro de los resultados en la fase de Cuartos por el admin de la polla mundialista
class FaseCuartosAdminModel(models.Model):
	FechaPartido = models.DateField()
	Equipo1 = models.CharField(max_length=50)
	MarcadorEquipo1 = models.IntegerField()
	Equipo2 = models.CharField(max_length=50)
	MarcadorEquipo2 = models.IntegerField()
	PenalEquipoGanador = models.CharField(max_length=50)
	Identificador = models.IntegerField()
	Participante = models.ForeignKey(ParticipantesModel, models.DO_NOTHING)
	FechaRegistro = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'tblFaseCuartosAdmin'
		unique_together = (('Equipo1','Equipo2','Participante'),)

# modelo para el regitro de los resultados en la fase de semifinales por participantes de la polla mundialista
class FaseSemifinalesUsuariosModel(models.Model):
	FechaPartido = models.DateField()
	Equipo1 = models.CharField(max_length=50)
	MarcadorEquipo1 = models.IntegerField()
	Equipo2 = models.CharField(max_length=50)
	MarcadorEquipo2 = models.IntegerField()
	PenalEquipoGanador = models.CharField(max_length=50)
	Identificador = models.IntegerField()
	Participante = models.ForeignKey(ParticipantesModel, models.DO_NOTHING)
	FechaRegistro = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'tblFaseSemifinalesUsuarios'
		unique_together = (('Equipo1','Equipo2','Participante'),)

# modelo para el regitro de los resultados en la fase de semifinales por el admin de la polla mundialista
class FaseSemifinalesAdminModel(models.Model):
	FechaPartido = models.DateField()
	Equipo1 = models.CharField(max_length=50)
	MarcadorEquipo1 = models.IntegerField()
	Equipo2 = models.CharField(max_length=50)
	MarcadorEquipo2 = models.IntegerField()
	PenalEquipoGanador = models.CharField(max_length=50)
	Identificador = models.IntegerField()
	Participante = models.ForeignKey(ParticipantesModel, models.DO_NOTHING)
	FechaRegistro = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'tblFaseSemifinalesAdmin'
		unique_together = (('Equipo1','Equipo2','Participante'),)

# modelo para el regitro de los resultados de la final por participantes de la polla mundialista
class FaseFinalUsuariosModel(models.Model):
	FechaPartido = models.DateField()
	Equipo1 = models.CharField(max_length=50)
	MarcadorEquipo1 = models.IntegerField()
	Equipo2 = models.CharField(max_length=50)
	MarcadorEquipo2 = models.IntegerField()
	PenalEquipoGanador = models.CharField(max_length=50)
	Identificador = models.IntegerField()
	Participante = models.ForeignKey(ParticipantesModel, models.DO_NOTHING)
	FechaRegistro = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'tblFaseFinalUsuarios'
		unique_together = (('Equipo1','Equipo2','Participante'),)

# modelo para el regitro de los resultados de la final por el admin de la polla mundialista
class FaseFinalAdminModel(models.Model):
	FechaPartido = models.DateField()
	Equipo1 = models.CharField(max_length=50)
	MarcadorEquipo1 = models.IntegerField()
	Equipo2 = models.CharField(max_length=50)
	MarcadorEquipo2 = models.IntegerField()
	PenalEquipoGanador = models.CharField(max_length=50)
	Identificador = models.IntegerField()
	Participante = models.ForeignKey(ParticipantesModel, models.DO_NOTHING)
	FechaRegistro = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = 'tblFaseFinalAdmin'
		unique_together = (('Equipo1','Equipo2','Participante'),)




