# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.files.storage import default_storage
from django.db.models.fields.files import FieldFile
from django.views.generic import CreateView, FormView, ListView, DetailView, UpdateView, DeleteView, View
from django.views.generic.base import TemplateView
from django.contrib import messages
from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, Context, loader
from django.template.loader import get_template
from django.shortcuts import render_to_response
from django.db import connection
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.models import User
from forms import *
from models import *
from django.db.models import Sum
from django.core.exceptions import ValidationError
from django.contrib.auth import update_session_auth_hash
from django.db import IntegrityError
from decimal import Decimal
from django.core.serializers import serialize
from django.core.cache import cache
import json
from django.db.models import Count
from django.core.serializers.json import DjangoJSONEncoder
import sweetify
from sweetify.views import SweetifySuccessMixin
from django.core.mail import EmailMessage
import datetime


# Create your views here.
class RegistroUsuarioView(SweetifySuccessMixin,CreateView):
	model = ParticipantesModel
	form_class = RegistroParticipantesForm
	template_name = 'registroUsuarios.html'

	def get_context_data(self, *args, **kwargs):
		context = super(RegistroUsuarioView,self).get_context_data(*args, **kwargs)
		if 'form' not in context:
			context['form'] = self.form_class(self.request.GET)
		return context

	def post(self,request, *args, **kwargs):
		self.object = self.get_object
		form = self.form_class(request.POST)
		if form.is_valid():
			countClientes = ParticipantesModel.objects.filter(NITEmpresa=form.cleaned_data['NITEmpresa']).count()
			Empresa = ClientesModel.objects.get(NIT=form.cleaned_data['NITEmpresa'])
			countCupos = Empresa.Clasificacion.Cupo
			print(countCupos)
			if countClientes == countCupos:
				sweetify.error(request, 'No se permiten mas participates para este cliente!')
				return render(request, 'registroUsuarios.html', {'form': form })
			else:
				form.save()
				contexto_email = {
		            'Nombre': form.cleaned_data['first_name'] + ' ' + form.cleaned_data['last_name'],
		            'username': form.cleaned_data['username'],
		            'password': form.cleaned_data['password1']
		        }
				mensaje = get_template('plantillaCorreo.html').render(contexto_email)
				email = EmailMessage('Reypar', mensaje , to=[form.cleaned_data['email']], from_email='johan4201@gmail.com')
				email.content_subtype = "html"
				email.send()
				return HttpResponseRedirect('/accounts/login/')
		else:
			return render(request, 'registroUsuarios.html', {'form': form }) 

class TerminosCondicionesView(TemplateView):
	template_name = 'terminosCondiciones.html'

#validar en el formulario si la edad es mayor a 18 años
def ValidarClienteView(request):
    if request.method == 'POST':
        try:
        	ClientesModel.objects.get(NIT=request.POST['ident'])
        	clienteValido = ClientesModel.objects.filter(NIT= request.POST['ident'])
        	valido =  serialize('json', clienteValido)
        	return HttpResponse(json.dumps(valido), content_type='application/json')
        except ClientesModel.DoesNotExist:
               #si arroja un error quiere decir que no encontro nada en la base de datos, por lo cual si se puede guardar...
            valido = False
    return HttpResponse(json.dumps({'valido': valido}), content_type='application/json') # se empaqueta la respuesta en forma de json, y se envia, para que el front la reciba como JSON

# vista para cargar el template de la pagina principal iframe 
class PrincipalView(TemplateView):
	template_name = 'principal.html'

# pagina de inicio del usuario
def InicioView(request):
	countUsuarioFase = FaseGruposUsuariosModel.objects.filter(Participante= request.user.id).count()
	countUsuarioOctavos = FaseOctavosUsuariosModel.objects.filter(Participante= request.user.id).count()
	countUsuarioCuartos = FaseCuartosUsuariosModel.objects.filter(Participante= request.user.id).count()
	countUsuarioSemifinales = FaseSemifinalesUsuariosModel.objects.filter(Participante= request.user.id).count()
	countUsuariofinal = FaseFinalUsuariosModel.objects.filter(Participante= request.user.id).count()
	if request.user.is_superuser == 1:
		return HttpResponseRedirect('/PrincipalRegistroResultados/')
	if countUsuarioFase == 0:
		return HttpResponseRedirect('/registroFaseGrupos/')
	if countUsuarioOctavos == 0:
		return HttpResponseRedirect('/registroOctavos/')
	if countUsuarioCuartos == 0:
		return HttpResponseRedirect('/registroCuartos/')
	if countUsuarioSemifinales == 0:
		return HttpResponseRedirect('/registroSemifinales/')
	if countUsuariofinal == 0:
		return HttpResponseRedirect('/registroFinales/')
	else:
		return HttpResponseRedirect('/verFaseGrupos/')

# vista para el registro de los resultados de la fase de grupos por usuario
def RegistroFaseGruposView(request):
	if request.method == 'POST':
		try:

			# Captura de las lista del grupo A
			grupo1A = request.POST.getlist('1_Groups_A')
			grupo2A = request.POST.getlist('2_Groups_A')
			grupo3A = request.POST.getlist('3_Groups_A')
			grupo4A = request.POST.getlist('4_Groups_A')
			grupo5A = request.POST.getlist('5_Groups_A')
			grupo6A = request.POST.getlist('6_Groups_A')

			# Captura de las lista del grupo B
			grupo1B = request.POST.getlist('1_Groups_B')
			grupo2B = request.POST.getlist('2_Groups_B')
			grupo3B = request.POST.getlist('3_Groups_B')
			grupo4B = request.POST.getlist('4_Groups_B')
			grupo5B = request.POST.getlist('5_Groups_B')
			grupo6B = request.POST.getlist('6_Groups_B')

			# Captura de las lista del grupo C
			grupo1C = request.POST.getlist('1_Groups_C')
			grupo2C = request.POST.getlist('2_Groups_C')
			grupo3C = request.POST.getlist('3_Groups_C')
			grupo4C = request.POST.getlist('4_Groups_C')
			grupo5C = request.POST.getlist('5_Groups_C')
			grupo6C = request.POST.getlist('6_Groups_C')

			# Captura de las lista del grupo D
			grupo1D = request.POST.getlist('1_Groups_D')
			grupo2D = request.POST.getlist('2_Groups_D')
			grupo3D = request.POST.getlist('3_Groups_D')
			grupo4D = request.POST.getlist('4_Groups_D')
			grupo5D = request.POST.getlist('5_Groups_D')
			grupo6D = request.POST.getlist('6_Groups_D')

			# Captura de las lista del grupo E
			grupo1E = request.POST.getlist('1_Groups_E')
			grupo2E = request.POST.getlist('2_Groups_E')
			grupo3E = request.POST.getlist('3_Groups_E')
			grupo4E = request.POST.getlist('4_Groups_E')
			grupo5E = request.POST.getlist('5_Groups_E')
			grupo6E = request.POST.getlist('6_Groups_E')

			# Captura de las lista del grupo F
			grupo1F = request.POST.getlist('1_Groups_F')
			grupo2F = request.POST.getlist('2_Groups_F')
			grupo3F = request.POST.getlist('3_Groups_F')
			grupo4F = request.POST.getlist('4_Groups_F')
			grupo5F = request.POST.getlist('5_Groups_F')
			grupo6F = request.POST.getlist('6_Groups_F')

			# Captura de las lista del grupo G
			grupo1G = request.POST.getlist('1_Groups_G')
			grupo2G = request.POST.getlist('2_Groups_G')
			grupo3G = request.POST.getlist('3_Groups_G')
			grupo4G = request.POST.getlist('4_Groups_G')
			grupo5G = request.POST.getlist('5_Groups_G')
			grupo6G = request.POST.getlist('6_Groups_G')

			# Captura de las lista del grupo H
			grupo1H = request.POST.getlist('1_Groups_H')
			grupo2H = request.POST.getlist('2_Groups_H')
			grupo3H = request.POST.getlist('3_Groups_H')
			grupo4H = request.POST.getlist('4_Groups_H')
			grupo5H = request.POST.getlist('5_Groups_H')
			grupo6H = request.POST.getlist('6_Groups_H')

			ListResultado=[grupo1A,grupo2A,grupo3A,grupo4A,grupo5A,grupo6A,
					grupo1B,grupo2B,grupo3B,grupo4B,grupo5B,grupo6B,
					grupo1C,grupo2C,grupo3C,grupo4C,grupo5C,grupo6C,
					grupo1D,grupo2D,grupo3D,grupo4D,grupo5D,grupo6D,
					grupo1E,grupo2E,grupo3E,grupo4E,grupo5E,grupo6E,
					grupo1F,grupo2F,grupo3F,grupo4F,grupo5F,grupo6F,
					grupo1G,grupo2G,grupo3G,grupo4G,grupo5G,grupo6G,
					grupo1H,grupo2H,grupo3H,grupo4H,grupo5H,grupo6H,			
			]

			Empate = ValidarEmpateGrupos(ListResultado)

			if Empate > 0:

				sweetify.warning(request, 'Por favor ingresar resultados para los defrentes partidos de la fase de grupos, no se permiten resultados en 0')

			else:

				RegistarResultadosFaseGrupos(ListResultado)

				sweetify.success(request, 'Registro fase de grupos exitoso!')

				return HttpResponseRedirect('/registroOctavos/')

		
		except IntegrityError as e:
		    sweetify.error(request, 'El usuario ya registro la fase de grupos!')

	return render(request, 'registroResultados/registroFaseGrupos.html')

# funcion para el registro en base de datos del list con los resultados registrados por el usuario
def RegistarResultadosFaseGrupos(ListResultado):
    objs = [
        FaseGruposUsuariosModel(
            FechaPartido=e[0],
            Grupo=e[1],
            Equipo1=e[2],
            MarcadorEquipo1=e[3],
            Equipo2=e[4],
            MarcadorEquipo2 = e[5],
            Participante =ParticipantesModel.objects.get(id=e[6]),  

        )
    for e in ListResultado
    ]
    detalleFaseGruposUsuario = FaseGruposUsuariosModel.objects.bulk_create(objs)

    for i in ListResultado:
    	# registro del resultado en la Tabla Posociones por Usuarios
    	RegistroPosicionesEquiposUsuarios(i)

# funcion para validar si existen resultados en cero en la fase de octavos
def ValidarEmpateGrupos(ListResultado):
	contar=0
	for i in ListResultado:
		if i[2] == i[4] and i[5] == i[6]:
			contar += contar + 1

	return contar

def verFaseGruposView(request):
	FaseGrupos = FaseGruposUsuariosModel.objects.filter(Participante= request.user.id)
	Octavos = FaseOctavosUsuariosModel.objects.filter(Participante= request.user.id)
	Cuartos = FaseCuartosUsuariosModel.objects.filter(Participante= request.user.id)
	Semis = FaseSemifinalesUsuariosModel.objects.filter(Participante= request.user.id)
	Final = FaseFinalUsuariosModel.objects.filter(Participante= request.user.id)
	print FaseGrupos
	return render(request,'verFaseGrupos.html',{'FaseGrupos':FaseGrupos,'Octavos':Octavos,'Cuartos':Cuartos,'Semis':Semis,'Final':Final})

# funcion para el registro de los equipos en la tablas de posiciones por usuarios
def RegistroPosicionesEquiposUsuarios(partidojugado):
	equipoUno = TablasPosocionesUsuariosModel.objects.filter(Grupo=partidojugado[1] , Equipo=partidojugado[2], Participante=partidojugado[6]).exists()
	equipoDos = TablasPosocionesUsuariosModel.objects.filter(Grupo=partidojugado[1] , Equipo=partidojugado[4], Participante=partidojugado[6]).exists()

	# se valida si el primer equipo existe si, si existe se ingresa el resultado a base de datos
	if equipoUno == True:
		idEquipo = TablasPosocionesUsuariosModel.objects.filter(Grupo=partidojugado[1] , Equipo=partidojugado[2], Participante=partidojugado[6]).values('id')[0]
		EquipoResultado1 = TablasPosocionesUsuariosModel.objects.get(id=idEquipo['id'])
		# en el caso de empate
		if partidojugado[3] == partidojugado[5]:
			EquipoResultado1.Grupo = partidojugado[1]
			EquipoResultado1.Equipo = partidojugado[2]
			EquipoResultado1.PartidoJugados = int(EquipoResultado1.PartidoJugados) + 1
			EquipoResultado1.Ganados = int(EquipoResultado1.Ganados) + 0
			EquipoResultado1.Empatados = int(EquipoResultado1.Empatados) + 1
			EquipoResultado1.Perdidos = int(EquipoResultado1.Perdidos) + 0
			EquipoResultado1.GolaFavor = int(EquipoResultado1.GolaFavor) + int(partidojugado[3])
			EquipoResultado1.GolContra = int(EquipoResultado1.GolContra) + int(partidojugado[5])
			EquipoResultado1.GolDiferencia = int(EquipoResultado1.GolaFavor) - int(EquipoResultado1.GolContra)
			EquipoResultado1.Puntos = int(EquipoResultado1.Puntos + 1)
			EquipoResultado1.Participante = ParticipantesModel.objects.get(id=partidojugado[6])
			EquipoResultado1.save()

		# en el caso del equipo uno ser ganador 
		elif partidojugado[3] > partidojugado[5]:
			EquipoResultado1.Grupo = partidojugado[1]
			EquipoResultado1.Equipo = partidojugado[2]
			EquipoResultado1.PartidoJugados = int(EquipoResultado1.PartidoJugados) + 1
			EquipoResultado1.Ganados = int(EquipoResultado1.Ganados) + 1
			EquipoResultado1.Empatados = int(EquipoResultado1.Empatados) + 0
			EquipoResultado1.Perdidos = int(EquipoResultado1.Perdidos) + 0
			EquipoResultado1.GolaFavor = int(EquipoResultado1.GolaFavor) + int(partidojugado[3])
			EquipoResultado1.GolContra = int(EquipoResultado1.GolContra) + int(partidojugado[5])
			EquipoResultado1.GolDiferencia = int(EquipoResultado1.GolaFavor) - int(EquipoResultado1.GolContra)
			EquipoResultado1.Puntos = int(EquipoResultado1.Puntos) + 3
			EquipoResultado1.Participante = ParticipantesModel.objects.get(id=partidojugado[6])
			EquipoResultado1.save()

		# en el caso del equipo uno ser perdedor
		elif partidojugado[3] < partidojugado[5]:
			EquipoResultado1.Grupo = partidojugado[1]
			EquipoResultado1.Equipo = partidojugado[2]
			EquipoResultado1.PartidoJugados = int(EquipoResultado1.PartidoJugados) + 1
			EquipoResultado1.Ganados = int(EquipoResultado1.Ganados) + 0
			EquipoResultado1.Empatados = int(EquipoResultado1.Empatados) + 0
			EquipoResultado1.Perdidos = int(EquipoResultado1.Perdidos) + 1
			EquipoResultado1.GolaFavor = int(EquipoResultado1.GolaFavor) + int(partidojugado[3])
			EquipoResultado1.GolContra = int(EquipoResultado1.GolContra) + int(partidojugado[5])
			EquipoResultado1.GolDiferencia = int(EquipoResultado1.GolaFavor) - int(EquipoResultado1.GolContra)
			EquipoResultado1.Puntos = int(EquipoResultado1.Puntos) + 0
			EquipoResultado1.Participante = ParticipantesModel.objects.get(id=partidojugado[6])
			EquipoResultado1.save()

	# si no existe el primer equipo en la tabla de resultados se crea
	if equipoUno == False:
		# en el caso de empate
		if partidojugado[3] == partidojugado[5]:

			EquipoResultado1 = TablasPosocionesUsuariosModel (Grupo = partidojugado[1], 
				Equipo = partidojugado[2], 
				PartidoJugados = 1, 
				Ganados = 0, 
				Empatados = 1,
				Perdidos = 0,
				GolaFavor = partidojugado[3],
				GolContra = partidojugado[5],
				GolDiferencia = int(partidojugado[3]) - int(partidojugado[5]),
				Puntos = 1,
				Participante = ParticipantesModel.objects.get(id=partidojugado[6])
				)
			EquipoResultado1.save (force_insert = True)

		# en el caso del equipo uno ser ganador 
		elif partidojugado[3] > partidojugado[5]:

			EquipoResultado1 = TablasPosocionesUsuariosModel (Grupo = partidojugado[1], 
				Equipo = partidojugado[2], 
				PartidoJugados = 1, 
				Ganados = 1, 
				Empatados = 0,
				Perdidos = 0,
				GolaFavor = partidojugado[3],
				GolContra = partidojugado[5],
				GolDiferencia = int(partidojugado[3]) - int(partidojugado[5]),
				Puntos = 3,
				Participante = ParticipantesModel.objects.get(id=partidojugado[6])
				)
			EquipoResultado1.save (force_insert = True)

		# en el caso del equipo uno ser perdedor
		elif partidojugado[3] < partidojugado[5]:

			EquipoResultado1 = TablasPosocionesUsuariosModel (Grupo = partidojugado[1], 
				Equipo = partidojugado[2], 
				PartidoJugados = 1, 
				Ganados = 0, 
				Empatados = 0,
				Perdidos = 1,
				GolaFavor = partidojugado[3],
				GolContra = partidojugado[5],
				GolDiferencia = int(partidojugado[3]) - int(partidojugado[5]),
				Puntos = 0,
				Participante = ParticipantesModel.objects.get(id=partidojugado[6])
				)
			EquipoResultado1.save (force_insert = True)

	# se valida si el segundo equipo existe si, si existe se ingresa el resultado a base de datos
	if equipoDos == True:
		idEquipo2 = TablasPosocionesUsuariosModel.objects.filter(Grupo=partidojugado[1] , Equipo=partidojugado[4], Participante=partidojugado[6]).values('id')[0]
		EquipoResultado2 = TablasPosocionesUsuariosModel.objects.get(id=idEquipo2['id'])
		# en el caso de empate
		if partidojugado[5] == partidojugado[3]:
			EquipoResultado2.Grupo = partidojugado[1]
			EquipoResultado2.Equipo = partidojugado[4]
			EquipoResultado2.PartidoJugados = int(EquipoResultado2.PartidoJugados) + 1
			EquipoResultado2.Ganados = int(EquipoResultado2.Ganados) + 0
			EquipoResultado2.Empatados = int(EquipoResultado2.Empatados) + 1
			EquipoResultado2.Perdidos = int(EquipoResultado2.Perdidos) + 0
			EquipoResultado2.GolaFavor = int(EquipoResultado2.GolaFavor) + int(partidojugado[5])
			EquipoResultado2.GolContra = int(EquipoResultado2.GolContra) + int(partidojugado[3])
			EquipoResultado2.GolDiferencia = int(EquipoResultado2.GolaFavor) - int(EquipoResultado2.GolContra)
			EquipoResultado2.Puntos = int(EquipoResultado2.Puntos) + 1
			EquipoResultado2.Participante = ParticipantesModel.objects.get(id=partidojugado[6])
			EquipoResultado2.save()

		# en el caso del equipo uno ser ganador 
		elif partidojugado[5] > partidojugado[3]:
			EquipoResultado2.Grupo = partidojugado[1]
			EquipoResultado2.Equipo = partidojugado[4]
			EquipoResultado2.PartidoJugados = int(EquipoResultado2.PartidoJugados) + 1
			EquipoResultado2.Ganados = int(EquipoResultado2.Ganados) + 1
			EquipoResultado2.Empatados = int(EquipoResultado2.Empatados) + 0
			EquipoResultado2.Perdidos = int(EquipoResultado2.Perdidos) + 0
			EquipoResultado2.GolaFavor = int(EquipoResultado2.GolaFavor) + int(partidojugado[3])
			EquipoResultado2.GolContra = int(EquipoResultado2.GolContra) + int(partidojugado[5])
			EquipoResultado2.GolDiferencia = int(EquipoResultado2.GolaFavor) - int(EquipoResultado2.GolContra)
			EquipoResultado2.Puntos = int(EquipoResultado2.Puntos) + 3
			EquipoResultado2.Participante = ParticipantesModel.objects.get(id=partidojugado[6])
			EquipoResultado2.save()

		# en el caso del equipo uno ser perdedor
		elif partidojugado[5] < partidojugado[3]:
			EquipoResultado2.Grupo = partidojugado[1]
			EquipoResultado2.Equipo = partidojugado[4]
			EquipoResultado2.PartidoJugados = int(EquipoResultado2.PartidoJugados) + 1
			EquipoResultado2.Ganados = int(EquipoResultado2.Ganados) + 0
			EquipoResultado2.Empatados = int(EquipoResultado2.Empatados) + 0
			EquipoResultado2.Perdidos = int(EquipoResultado2.Perdidos) + 1
			EquipoResultado2.GolaFavor = int(EquipoResultado2.GolaFavor) + int(partidojugado[5])
			EquipoResultado2.GolContra = int(EquipoResultado2.GolContra) + int(partidojugado[3])
			EquipoResultado2.GolDiferencia = int(EquipoResultado2.GolaFavor) - int(EquipoResultado2.GolContra)
			EquipoResultado2.Puntos = int(EquipoResultado2.Puntos) + 0
			EquipoResultado2.Participante = ParticipantesModel.objects.get(id=partidojugado[6])
			EquipoResultado2.save()

	# si no existe el segundo equipo en la tabla de resultados se crea
	if equipoDos == False:
		# en el caso de empate
		if partidojugado[5] == partidojugado[3]:

			EquipoResultado2 = TablasPosocionesUsuariosModel (Grupo = partidojugado[1], 
				Equipo = partidojugado[4], 
				PartidoJugados = 1, 
				Ganados = 0, 
				Empatados = 1,
				Perdidos = 0,
				GolaFavor = partidojugado[5],
				GolContra = partidojugado[3],
				GolDiferencia = int(partidojugado[5]) - int(partidojugado[3]),
				Puntos = 1,
				Participante = ParticipantesModel.objects.get(id=partidojugado[6])
				)
			EquipoResultado2.save (force_insert = True)

		# en el caso del equipo uno ser ganador 
		elif partidojugado[5] > partidojugado[3]:

			EquipoResultado2 = TablasPosocionesUsuariosModel (Grupo = partidojugado[1], 
				Equipo = partidojugado[4], 
				PartidoJugados = 1, 
				Ganados = 1, 
				Empatados = 0,
				Perdidos = 0,
				GolaFavor = partidojugado[5],
				GolContra = partidojugado[3],
				GolDiferencia = int(partidojugado[5]) - int(partidojugado[3]),
				Puntos = 3,
				Participante = ParticipantesModel.objects.get(id=partidojugado[6])
				)
			EquipoResultado2.save (force_insert = True)

		# en el caso del equipo uno ser perdedor
		elif partidojugado[5] < partidojugado[3]:

			EquipoResultado2 = TablasPosocionesUsuariosModel (Grupo = partidojugado[1], 
				Equipo = partidojugado[4], 
				PartidoJugados = 1, 
				Ganados = 0, 
				Empatados = 0,
				Perdidos = 1,
				GolaFavor = partidojugado[5],
				GolContra = partidojugado[3],
				GolDiferencia = int(partidojugado[5]) - int(partidojugado[3]),
				Puntos = 0,
				Participante = ParticipantesModel.objects.get(id=partidojugado[6])
				)
			EquipoResultado2.save (force_insert = True)

# vista para el registro de los octavos de usuario
def RegistroOctavosView(request):
	grupos = TablasPosocionesUsuariosModel.objects.values('Grupo').filter(Participante= request.user.id).distinct()
	mejoresDosEquipos =[]
	for grupo in grupos:
		mejoresDosEquipos += TablasPosocionesUsuariosModel.objects.values('Grupo','Equipo').filter(Grupo__in=grupo['Grupo'],Participante= request.user.id).order_by('-Puntos','-GolDiferencia')[:2]

	partido1 = [mejoresDosEquipos[0],mejoresDosEquipos[3], {'fecha':datetime.datetime(2018, 06, 30)},{'identificador':49}]
	partido2 = [mejoresDosEquipos[4],mejoresDosEquipos[7], {'fecha':datetime.datetime(2018, 06, 30)},{'identificador':50}]
	partido3 = [mejoresDosEquipos[2],mejoresDosEquipos[1], {'fecha':datetime.datetime(2018, 07, 01)},{'identificador':51}]
	partido4 = [mejoresDosEquipos[6],mejoresDosEquipos[5], {'fecha':datetime.datetime(2018, 07, 01)},{'identificador':52}]
	partido5 = [mejoresDosEquipos[8],mejoresDosEquipos[11], {'fecha':datetime.datetime(2018, 07, 02)},{'identificador':53}]
	partido6 = [mejoresDosEquipos[12],mejoresDosEquipos[15], {'fecha':datetime.datetime(2018, 07, 02)},{'identificador':54}]
	partido7 = [mejoresDosEquipos[10],mejoresDosEquipos[9], {'fecha':datetime.datetime(2018, 07, 03)},{'identificador':55}]
	partido8 = [mejoresDosEquipos[14],mejoresDosEquipos[13], {'fecha':datetime.datetime(2018, 07, 03)},{'identificador':56}]

	if request.method == 'POST':
		try:
			resultadoOctavos1 = request.POST.getlist('partido1')
			resultadoOctavos2 = request.POST.getlist('partido2')
			resultadoOctavos3 = request.POST.getlist('partido3')
			resultadoOctavos4 = request.POST.getlist('partido4')
			resultadoOctavos5 = request.POST.getlist('partido5')
			resultadoOctavos6 = request.POST.getlist('partido6')
			resultadoOctavos7 = request.POST.getlist('partido7')
			resultadoOctavos8 = request.POST.getlist('partido8')

			if len(resultadoOctavos1) < 8:
				resultadoOctavos1.insert(5, 0)

			if len(resultadoOctavos2) < 8:
				resultadoOctavos2.insert(5, 0)

			if len(resultadoOctavos3) < 8:
				resultadoOctavos3.insert(5, 0)

			if len(resultadoOctavos4) < 8:
				resultadoOctavos4.insert(5, 0)

			if len(resultadoOctavos5) < 8:
				resultadoOctavos5.insert(5, 0)

			if len(resultadoOctavos6) < 8:
				resultadoOctavos6.insert(5, 0)

			if len(resultadoOctavos7) < 8:
				resultadoOctavos7.insert(5, 0)

			if len(resultadoOctavos8) < 8:
				resultadoOctavos8.insert(5, 0)


			ListResultado=[resultadoOctavos1,resultadoOctavos2,resultadoOctavos3,resultadoOctavos4,
						resultadoOctavos5,resultadoOctavos6,resultadoOctavos7,resultadoOctavos8,			
				]

			Empate = ValidarEmpate(ListResultado)

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseOctavos(ListResultado)

				sweetify.success(request, 'Registro fase de octavos de final exitoso!')

				return HttpResponseRedirect('/registroCuartos/')

		except IntegrityError as e:
		    sweetify.error(request, 'El usuario ya registro la fase de octavos de final!')

	return render(request,'registroResultados/registroOctavos.html',
		{'partido1':partido1, 'partido2':partido2,
		'partido3':partido3, 'partido4':partido4,
		'partido5':partido5, 'partido6':partido6,
		'partido7':partido7, 'partido8':partido8,
		})

# funcion para validar si existen resultados en cero en la fase de octavos
def ValidarEmpate(ListResultado):
	contar=0
	for i in ListResultado:
		if i[2] == i[4]:
			if i[5] == '0':
				contar += contar + 1
	return contar

# funcion para el registro en base de datos del list con los resultados registrados para la fase de octavos por el usuario
def RegistarResultadosFaseOctavos(ListResultado):
    objs = [
        FaseOctavosUsuariosModel(
        	FechaPartido = e[0],
			Equipo1 = e[1],
			MarcadorEquipo1 = e[2],
			Equipo2 = e[3],
			MarcadorEquipo2 = e[4],
			PenalEquipoGanador = e[5],
			Identificador = e[6],
			Participante = ParticipantesModel.objects.get(id=e[7]),  

        )
    for e in ListResultado
    ]
    detalleFaseOctavosUsuarios = FaseOctavosUsuariosModel.objects.bulk_create(objs)

#vista para el formulario de registro de fase de cuartos
def RegistroFaseCuartosView(request):
	EquiposCuartos = FaseOctavosUsuariosModel.objects.filter(Participante= request.user.id)
	equipos =[]
	for i in EquiposCuartos:
		if i.MarcadorEquipo1 == i.MarcadorEquipo2:
			if i.PenalEquipoGanador == '1':
				equipos += [[i.Equipo1]]
			if i.PenalEquipoGanador == '2':
				equipos += [[i.Equipo2]]
		if i.MarcadorEquipo1 > i.MarcadorEquipo2:
			equipos += [[i.Equipo1]]
		if i.MarcadorEquipo1 < i.MarcadorEquipo2:
			equipos += [[i.Equipo2]]
	
	for x in equipos[0]:
		equipo1=x

	for x in equipos[1]:
		equipo2=x

	for x in equipos[2]:
		equipo3=x

	for x in equipos[3]:
		equipo4=x

	for x in equipos[4]:
		equipo5=x

	for x in equipos[5]:
		equipo6=x

	for x in equipos[6]:
		equipo7=x

	for x in equipos[7]:
		equipo8=x

	
	partido1 = [{'Equipo':equipo1},{'Equipo':equipo2}, {'fecha':datetime.datetime(2018, 07, 06)},{'identificador':57}]
	partido2 = [{'Equipo':equipo3},{'Equipo':equipo4}, {'fecha':datetime.datetime(2018, 07, 06)},{'identificador':58}]
	partido3 = [{'Equipo':equipo5},{'Equipo':equipo6}, {'fecha':datetime.datetime(2018, 07, 07)},{'identificador':59}]
	partido4 = [{'Equipo':equipo7},{'Equipo':equipo8}, {'fecha':datetime.datetime(2018, 07, 07)},{'identificador':60}]

	if request.method == 'POST':
		try:
			resultadoCuartos1 = request.POST.getlist('partido1')
			resultadoCuartos2 = request.POST.getlist('partido2')
			resultadoCuartos3 = request.POST.getlist('partido3')
			resultadoCuartos4 = request.POST.getlist('partido4')

			if len(resultadoCuartos1) < 8:
				resultadoCuartos1.insert(5, 0)

			if len(resultadoCuartos2) < 8:
				resultadoCuartos2.insert(5, 0)

			if len(resultadoCuartos3) < 8:
				resultadoCuartos3.insert(5, 0)

			if len(resultadoCuartos4) < 8:
				resultadoCuartos4.insert(5, 0)


			ListResultado=[resultadoCuartos1,resultadoCuartos2,resultadoCuartos3,resultadoCuartos4			
				]

			Empate = ValidarEmpate(ListResultado)

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseCuarto(ListResultado)

				sweetify.success(request, 'Registro fase de cuartos de final exitoso!')

				return HttpResponseRedirect('/registroSemifinales/')

		except IntegrityError as e:
		    sweetify.error(request, 'El usuario ya registro la fase de cuartos de final!')



	return render(request,'registroResultados/registroCuartos.html',
		{'partido1':partido1, 'partido2':partido2,
		'partido3':partido3, 'partido4':partido4,
		})

# funcion para el registro en base de datos del list con los resultados registrados para la fase de cuartos por el usuario
def RegistarResultadosFaseCuarto(ListResultado):
    objs = [
        FaseCuartosUsuariosModel(
        	FechaPartido = e[0],
			Equipo1 = e[1],
			MarcadorEquipo1 = e[2],
			Equipo2 = e[3],
			MarcadorEquipo2 = e[4],
			PenalEquipoGanador = e[5],
			Identificador = e[6],
			Participante = ParticipantesModel.objects.get(id=e[7]),  

        )
    for e in ListResultado
    ]
    detalleFaseCuartosUsuarios = FaseCuartosUsuariosModel.objects.bulk_create(objs)

#vista para el formulario de registro de fase de semifinales
def RegistroFaseSemifinalesView(request):
	EquiposSemifinales = FaseCuartosUsuariosModel.objects.filter(Participante= request.user.id)
	equipos =[]
	for i in EquiposSemifinales:
		if i.MarcadorEquipo1 == i.MarcadorEquipo2:
			if i.PenalEquipoGanador == '1':
				equipos += [[i.Equipo1]]
			if i.PenalEquipoGanador == '2':
				equipos += [[i.Equipo2]]
		if i.MarcadorEquipo1 > i.MarcadorEquipo2:
			equipos += [[i.Equipo1]]
		if i.MarcadorEquipo1 < i.MarcadorEquipo2:
			equipos += [[i.Equipo2]]

	print(equipos)
	
	for x in equipos[0]:
		equipo1=x

	for x in equipos[1]:
		equipo2=x

	for x in equipos[2]:
		equipo3=x

	for x in equipos[3]:
		equipo4=x


	partido1 = [{'Equipo':equipo1},{'Equipo':equipo2}, {'fecha':datetime.datetime(2018, 07, 10)},{'identificador':61}]
	partido2 = [{'Equipo':equipo3},{'Equipo':equipo4}, {'fecha':datetime.datetime(2018, 07, 11)},{'identificador':62}]


	if request.method == 'POST':
		try:
			resultadoSemifinales1 = request.POST.getlist('partido1')
			resultadoSemifinales2 = request.POST.getlist('partido2')

			if len(resultadoSemifinales1) < 8:
				resultadoSemifinales1.insert(5, 0)

			if len(resultadoSemifinales2) < 8:
				resultadoSemifinales2.insert(5, 0)



			ListResultado=[resultadoSemifinales1,resultadoSemifinales2]

			Empate = ValidarEmpate(ListResultado)

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseSemifinales(ListResultado)

				sweetify.success(request, 'Registro fase de semifinales exitoso!')
				
				return HttpResponseRedirect('/registroFinales/')


		except IntegrityError as e:
		    sweetify.error(request, 'El usuario ya registro la fase de semifinales!')



	return render(request,'registroResultados/registroSemifinales.html',
		{'partido1':partido1, 'partido2':partido2
		})

# funcion para el registro en base de datos del list con los resultados registrados para la fase de cuartos por el usuario
def RegistarResultadosFaseSemifinales(ListResultado):
    objs = [
        FaseSemifinalesUsuariosModel(
        	FechaPartido = e[0],
			Equipo1 = e[1],
			MarcadorEquipo1 = e[2],
			Equipo2 = e[3],
			MarcadorEquipo2 = e[4],
			PenalEquipoGanador = e[5],
			Identificador = e[6],
			Participante = ParticipantesModel.objects.get(id=e[7]),  

        )
    for e in ListResultado
    ]
    detalleFaseSemifinalesUsuarios = FaseSemifinalesUsuariosModel.objects.bulk_create(objs)

#vista para el formulario de registro de fase de finales
def RegistroFaseFinalView(request):
	EquiposFinales = FaseSemifinalesUsuariosModel.objects.filter(Participante= request.user.id)
	equiposGanadores =[]
	equiposPerdedores =[]

	for i in EquiposFinales:
		if i.MarcadorEquipo1 == i.MarcadorEquipo2:
			if i.PenalEquipoGanador == '1':
				equiposGanadores += [[i.Equipo1]]
				equiposPerdedores += [[i.Equipo2]]
				
			if i.PenalEquipoGanador == '2':
				equiposGanadores += [[i.Equipo2]]
				equiposPerdedores += [[i.Equipo1]]
			
		if i.MarcadorEquipo1 > i.MarcadorEquipo2:
			equiposGanadores += [[i.Equipo1]]
			equiposPerdedores += [[i.Equipo2]]

		if i.MarcadorEquipo1 < i.MarcadorEquipo2:
			equiposGanadores += [[i.Equipo2]]
			equiposPerdedores += [[i.Equipo1]]
			

	print(equiposGanadores)
	print(equiposPerdedores)


	for x in equiposGanadores[0]:
		equipo1=x

	for x in equiposGanadores[1]:
		equipo2=x

	for x in equiposPerdedores[0]:
		equipo3=x

	for x in equiposPerdedores[1]:
		equipo4=x


	partido1 = [{'Equipo':equipo1},{'Equipo':equipo2}, {'fecha':datetime.datetime(2018, 07, 15)},{'identificador':61}]
	partido2 = [{'Equipo':equipo3},{'Equipo':equipo4}, {'fecha':datetime.datetime(2018, 07, 14)},{'identificador':62}]


	if request.method == 'POST':
		try:
			resultadoFinal = request.POST.getlist('partido1')
			resultadoTercerPuesto = request.POST.getlist('partido2')

			if len(resultadoFinal) < 8:
				resultadoFinal.insert(5, 0)

			if len(resultadoTercerPuesto) < 8:
				resultadoTercerPuesto.insert(5, 0)



			ListResultado=[resultadoFinal,resultadoTercerPuesto]

			Empate = ValidarEmpate(ListResultado)

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')
				return HttpResponseRedirect('/')

			else:

				RegistarResultadosFaseFinal(ListResultado)

				sweetify.success(request, 'Registro de la final exitoso!')

				return HttpResponseRedirect('/verFaseGrupos/')

		except IntegrityError as e:
		    sweetify.error(request, 'El usuario ya registro la fase de semifinales!')



	return render(request,'registroResultados/registroFinales.html',
		{'partido1':partido1, 'partido2':partido2
		})

# funcion para el registro en base de datos del list con los resultados registrados para la final por el usuario
def RegistarResultadosFaseFinal(ListResultado):
    objs = [
        FaseFinalUsuariosModel(
        	FechaPartido = e[0],
			Equipo1 = e[1],
			MarcadorEquipo1 = e[2],
			Equipo2 = e[3],
			MarcadorEquipo2 = e[4],
			PenalEquipoGanador = e[5],
			Identificador = e[6],
			Participante = ParticipantesModel.objects.get(id=e[7]),  

        )
    for e in ListResultado
    ]
    detalleFaseFinalUsuarios = FaseFinalUsuariosModel.objects.bulk_create(objs)


# vista para cargar el template principal del admin para registro de resultados
class RegistroResultadosAdminView(TemplateView):
	template_name = 'adminResultados/principalRegistroResultadosAdmin.html'

# vista para el registro de los resultados de la fase de grupos por el Administrador
def RegistroFaseGruposAdminView(request):
	if request.method=='POST' and 'btn_1_Groups_A' in request.POST:
		try:

			grupo1A = request.POST.getlist('1_Groups_A')
			RegistarResultadosFaseGruposAdmin(grupo1A)
			ObtenerPuntajeUsuarios(grupo1A,0)
			RegistroPosicionesEquiposUsuarios(grupo1A)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:

		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_2_Groups_A' in request.POST:
		try:

			grupo2A = request.POST.getlist('2_Groups_A')
			RegistarResultadosFaseGruposAdmin(grupo2A)
			ObtenerPuntajeUsuarios(grupo2A,0)
			RegistroPosicionesEquiposUsuarios(grupo2A)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_3_Groups_A' in request.POST:
		try:

			grupo3A = request.POST.getlist('3_Groups_A')
			RegistarResultadosFaseGruposAdmin(grupo3A)
			ObtenerPuntajeUsuarios(grupo3A,0)
			RegistroPosicionesEquiposUsuarios(grupo3A)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_4_Groups_A' in request.POST:
		try:

			grupo4A = request.POST.getlist('4_Groups_A')
			RegistarResultadosFaseGruposAdmin(grupo4A)
			ObtenerPuntajeUsuarios(grupo4A,0)
			RegistroPosicionesEquiposUsuarios(grupo4A)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_5_Groups_A' in request.POST:
		try:

			grupo5A = request.POST.getlist('5_Groups_A')
			RegistarResultadosFaseGruposAdmin(grupo5A)
			ObtenerPuntajeUsuarios(grupo5A,0)
			RegistroPosicionesEquiposUsuarios(grupo5A)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_6_Groups_A' in request.POST:
		try:

			grupo6A = request.POST.getlist('6_Groups_A')
			RegistarResultadosFaseGruposAdmin(grupo6A)
			ObtenerPuntajeUsuarios(grupo6A,0)
			RegistroPosicionesEquiposUsuarios(grupo6A)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_1_Groups_B' in request.POST:
		try:

			grupo1B = request.POST.getlist('1_Groups_B')
			RegistarResultadosFaseGruposAdmin(grupo1B)
			ObtenerPuntajeUsuarios(grupo1B,0)
			RegistroPosicionesEquiposUsuarios(grupo1B)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_2_Groups_B' in request.POST:
		try:

			grupo2B = request.POST.getlist('2_Groups_B')
			RegistarResultadosFaseGruposAdmin(grupo2B)
			ObtenerPuntajeUsuarios(grupo2B,0)
			RegistroPosicionesEquiposUsuarios(grupo2B)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_3_Groups_B' in request.POST:
		try:

			grupo3B = request.POST.getlist('3_Groups_B')
			RegistarResultadosFaseGruposAdmin(grupo3B)
			ObtenerPuntajeUsuarios(grupo3B,0)
			RegistroPosicionesEquiposUsuarios(grupo3B)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_4_Groups_B' in request.POST:
		try:

			grupo4B = request.POST.getlist('4_Groups_B')
			RegistarResultadosFaseGruposAdmin(grupo4B)
			ObtenerPuntajeUsuarios(grupo4B,0)
			RegistroPosicionesEquiposUsuarios(grupo4B)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_5_Groups_B' in request.POST:
		try:

			grupo5B = request.POST.getlist('5_Groups_B')
			RegistarResultadosFaseGruposAdmin(grupo5B)
			ObtenerPuntajeUsuarios(grupo5B,0)
			RegistroPosicionesEquiposUsuarios(grupo5B)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_6_Groups_B' in request.POST:
		try:

			grupo6B = request.POST.getlist('6_Groups_B')
			RegistarResultadosFaseGruposAdmin(grupo6B)
			ObtenerPuntajeUsuarios(grupo6B,0)
			RegistroPosicionesEquiposUsuarios(grupo6B)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_1_Groups_C' in request.POST:
		try:

			grupo1C = request.POST.getlist('1_Groups_C')
			RegistarResultadosFaseGruposAdmin(grupo1C)
			ObtenerPuntajeUsuarios(grupo1C,0)
			RegistroPosicionesEquiposUsuarios(grupo1C)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_2_Groups_C' in request.POST:
		try:

			grupo2C = request.POST.getlist('2_Groups_C')
			RegistarResultadosFaseGruposAdmin(grupo2C)
			ObtenerPuntajeUsuarios(grupo2C,0)
			RegistroPosicionesEquiposUsuarios(grupo2C)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_3_Groups_C' in request.POST:
		try:

			grupo3C = request.POST.getlist('3_Groups_C')
			RegistarResultadosFaseGruposAdmin(grupo3C)
			ObtenerPuntajeUsuarios(grupo3C,0)
			RegistroPosicionesEquiposUsuarios(grupo3C)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_4_Groups_C' in request.POST:
		try:

			grupo4C = request.POST.getlist('4_Groups_C')
			RegistarResultadosFaseGruposAdmin(grupo4C)
			ObtenerPuntajeUsuarios(grupo4C,0)
			RegistroPosicionesEquiposUsuarios(grupo4C)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_5_Groups_C' in request.POST:
		try:

			grupo5C = request.POST.getlist('5_Groups_C')
			RegistarResultadosFaseGruposAdmin(grupo5C)
			ObtenerPuntajeUsuarios(grupo5C,0)
			RegistroPosicionesEquiposUsuarios(grupo5C)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_6_Groups_C' in request.POST:
		try:

			grupo6C = request.POST.getlist('6_Groups_C')
			RegistarResultadosFaseGruposAdmin(grupo6C)
			ObtenerPuntajeUsuarios(grupo6C,0)
			RegistroPosicionesEquiposUsuarios(grupo6C)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_1_Groups_D' in request.POST:
		try:

			grupo1D = request.POST.getlist('1_Groups_D')
			RegistarResultadosFaseGruposAdmin(grupo1D)
			ObtenerPuntajeUsuarios(grupo1D,0)
			RegistroPosicionesEquiposUsuarios(grupo1D)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_2_Groups_D' in request.POST:
		try:

			grupo2D = request.POST.getlist('2_Groups_D')
			RegistarResultadosFaseGruposAdmin(grupo2D)
			ObtenerPuntajeUsuarios(grupo2D,0)
			RegistroPosicionesEquiposUsuarios(grupo2D)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_3_Groups_D' in request.POST:
		try:

			grupo3D = request.POST.getlist('3_Groups_D')
			RegistarResultadosFaseGruposAdmin(grupo3D)
			ObtenerPuntajeUsuarios(grupo3D,0)
			RegistroPosicionesEquiposUsuarios(grupo3D)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_4_Groups_D' in request.POST:
		try:

			grupo4D = request.POST.getlist('4_Groups_D')
			RegistarResultadosFaseGruposAdmin(grupo4D)
			ObtenerPuntajeUsuarios(grupo4D,0)
			RegistroPosicionesEquiposUsuarios(grupo4D)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_5_Groups_D' in request.POST:
		try:

			grupo5D = request.POST.getlist('5_Groups_D')
			RegistarResultadosFaseGruposAdmin(grupo5D)
			ObtenerPuntajeUsuarios(grupo5D,0)
			RegistroPosicionesEquiposUsuarios(grupo5D)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_6_Groups_D' in request.POST:
		try:

			grupo6D = request.POST.getlist('6_Groups_D')
			RegistarResultadosFaseGruposAdmin(grupo6D)
			ObtenerPuntajeUsuarios(grupo6D,0)
			RegistroPosicionesEquiposUsuarios(grupo6D)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_1_Groups_E' in request.POST:
		try:

			grupo1E = request.POST.getlist('1_Groups_E')
			RegistarResultadosFaseGruposAdmin(grupo1E)
			ObtenerPuntajeUsuarios(grupo1E,0)
			RegistroPosicionesEquiposUsuarios(grupo1E)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_2_Groups_E' in request.POST:
		try:

			grupo2E = request.POST.getlist('2_Groups_E')
			RegistarResultadosFaseGruposAdmin(grupo2E)
			ObtenerPuntajeUsuarios(grupo2E,0)
			RegistroPosicionesEquiposUsuarios(grupo2E)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_3_Groups_E' in request.POST:
		try:

			grupo3E = request.POST.getlist('3_Groups_E')
			RegistarResultadosFaseGruposAdmin(grupo3E)
			ObtenerPuntajeUsuarios(grupo3E,0)
			RegistroPosicionesEquiposUsuarios(grupo3E)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_4_Groups_E' in request.POST:
		try:

			grupo4E = request.POST.getlist('4_Groups_E')
			RegistarResultadosFaseGruposAdmin(grupo4E)
			ObtenerPuntajeUsuarios(grupo4E,0)
			RegistroPosicionesEquiposUsuarios(grupo4E)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_5_Groups_E' in request.POST:
		try:

			grupo5E = request.POST.getlist('5_Groups_E')
			RegistarResultadosFaseGruposAdmin(grupo5E)
			ObtenerPuntajeUsuarios(grupo5E,0)
			RegistroPosicionesEquiposUsuarios(grupo5E)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_6_Groups_E' in request.POST:
		try:

			grupo6E = request.POST.getlist('6_Groups_E')
			RegistarResultadosFaseGruposAdmin(grupo6E)
			ObtenerPuntajeUsuarios(grupo6E,0)
			RegistroPosicionesEquiposUsuarios(grupo6E)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_1_Groups_F' in request.POST:
		try:

			grupo1F = request.POST.getlist('1_Groups_F')
			RegistarResultadosFaseGruposAdmin(grupo1F)
			ObtenerPuntajeUsuarios(grupo1F,0)
			RegistroPosicionesEquiposUsuarios(grupo1F)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_2_Groups_F' in request.POST:
		try:

			grupo2F = request.POST.getlist('2_Groups_F')
			RegistarResultadosFaseGruposAdmin(grupo2F)
			ObtenerPuntajeUsuarios(grupo2F,0)
			RegistroPosicionesEquiposUsuarios(grupo2F)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_3_Groups_F' in request.POST:
		try:

			grupo3F = request.POST.getlist('3_Groups_F')
			RegistarResultadosFaseGruposAdmin(grupo3F)
			ObtenerPuntajeUsuarios(grupo3F,0)
			RegistroPosicionesEquiposUsuarios(grupo3F)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_4_Groups_F' in request.POST:
		try:

			grupo4F = request.POST.getlist('4_Groups_F')
			RegistarResultadosFaseGruposAdmin(grupo4F)
			ObtenerPuntajeUsuarios(grupo4F,0)
			RegistroPosicionesEquiposUsuarios(grupo4F)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_5_Groups_F' in request.POST:
		try:

			grupo5F = request.POST.getlist('5_Groups_F')
			RegistarResultadosFaseGruposAdmin(grupo5F)
			ObtenerPuntajeUsuarios(grupo5F,0)
			RegistroPosicionesEquiposUsuarios(grupo5F)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_6_Groups_F' in request.POST:
		try:

			grupo6F = request.POST.getlist('6_Groups_F')
			RegistarResultadosFaseGruposAdmin(grupo6F)
			ObtenerPuntajeUsuarios(grupo6F,0)
			RegistroPosicionesEquiposUsuarios(grupo6F)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_1_Groups_G' in request.POST:
		try:

			grupo1G = request.POST.getlist('1_Groups_G')
			RegistarResultadosFaseGruposAdmin(grupo1G)
			ObtenerPuntajeUsuarios(grupo1G,0)
			RegistroPosicionesEquiposUsuarios(grupo1G)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_2_Groups_G' in request.POST:
		try:

			grupo2G = request.POST.getlist('2_Groups_G')
			RegistarResultadosFaseGruposAdmin(grupo2G)
			ObtenerPuntajeUsuarios(grupo2G,0)
			RegistroPosicionesEquiposUsuarios(grupo2G)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_3_Groups_G' in request.POST:
		try:

			grupo3G = request.POST.getlist('3_Groups_G')
			RegistarResultadosFaseGruposAdmin(grupo3G)
			ObtenerPuntajeUsuarios(grupo3G,0)
			RegistroPosicionesEquiposUsuarios(grupo3G)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_4_Groups_G' in request.POST:
		try:

			grupo4G = request.POST.getlist('4_Groups_G')
			RegistarResultadosFaseGruposAdmin(grupo4G)
			ObtenerPuntajeUsuarios(grupo4G,0)
			RegistroPosicionesEquiposUsuarios(grupo4G)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_5_Groups_G' in request.POST:
		try:

			grupo5G = request.POST.getlist('5_Groups_G')
			RegistarResultadosFaseGruposAdmin(grupo5G)
			ObtenerPuntajeUsuarios(grupo5G,0)
			RegistroPosicionesEquiposUsuarios(grupo5G)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_6_Groups_G' in request.POST:
		try:

			grupo6G = request.POST.getlist('6_Groups_G')
			RegistarResultadosFaseGruposAdmin(grupo6G)
			ObtenerPuntajeUsuarios(grupo6G,0)
			RegistroPosicionesEquiposUsuarios(grupo6G)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_1_Groups_H' in request.POST:
		try:

			grupo1H = request.POST.getlist('1_Groups_H')
			RegistarResultadosFaseGruposAdmin(grupo1H)
			ObtenerPuntajeUsuarios(grupo1H,0)
			RegistroPosicionesEquiposUsuarios(grupo1H)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_2_Groups_H' in request.POST:
		try:

			grupo2H = request.POST.getlist('2_Groups_H')
			RegistarResultadosFaseGruposAdmin(grupo2H)
			ObtenerPuntajeUsuarios(grupo2H,0)
			RegistroPosicionesEquiposUsuarios(grupo2H)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_3_Groups_H' in request.POST:
		try:

			grupo3H = request.POST.getlist('3_Groups_H')
			RegistarResultadosFaseGruposAdmin(grupo3H)
			ObtenerPuntajeUsuarios(grupo3H,0)
			RegistroPosicionesEquiposUsuarios(grupo3H)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_4_Groups_H' in request.POST:
		try:

			grupo4H = request.POST.getlist('4_Groups_H')
			RegistarResultadosFaseGruposAdmin(grupo4H)
			ObtenerPuntajeUsuarios(grupo4H,0)
			RegistroPosicionesEquiposUsuarios(grupo4H)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_5_Groups_H' in request.POST:
		try:

			grupo5H = request.POST.getlist('5_Groups_H')
			RegistarResultadosFaseGruposAdmin(grupo5H)
			ObtenerPuntajeUsuarios(grupo5H,0)
			RegistroPosicionesEquiposUsuarios(grupo5H)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_6_Groups_H' in request.POST:
		try:

			grupo6H = request.POST.getlist('6_Groups_H')
			RegistarResultadosFaseGruposAdmin(grupo6H)
			ObtenerPuntajeUsuarios(grupo6H,0)
			RegistroPosicionesEquiposUsuarios(grupo6H)
			sweetify.success(request, 'Registro exitoso!')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	return render(request, 'adminResultados/registroFaseGruposAdmin.html')

# funcion para el registro en base de datos del list con los resultados registrados por el Administrador
def RegistarResultadosFaseGruposAdmin(partido):
	ResultadoPartido = FaseGruposAdminModel ( 
		FechaPartido=partido[0],
		Grupo=partido[1],
		Equipo1=partido[2],
		MarcadorEquipo1=partido[3],
		Equipo2=partido[4],
		MarcadorEquipo2 = partido[5],
		Participante =ParticipantesModel.objects.get(id=partido[6])
	)
	ResultadoPartido.save (force_insert = True)

#funcion para obtener el puntaje del usuario segun sea el resultado del partido registrado por el admin
def ObtenerPuntajeUsuarios(partido,identificador):
	ResultadosUsuarios =  FaseGruposUsuariosModel.objects.filter(FechaPartido=partido[0],Grupo=partido[1],Equipo1=partido[2],Equipo2=partido[4])
	contador = 0
	for i in ResultadosUsuarios:
		if i.MarcadorEquipo1 == int(partido[3]) and i.MarcadorEquipo2 == int(partido[5]):
			contador += 3
		if i.MarcadorEquipo1 > i.MarcadorEquipo2 and partido[3] > partido[5]:
			contador += 1
		if i.MarcadorEquipo1 < i.MarcadorEquipo2 and partido[3] < partido[5]:
			contador += 1
		registroRanking(contador,i.Participante.id,identificador)

def registroRanking(contador,idUsuario, identificador):
	try:
		RankingModel.objects.get(Participante=idUsuario)
		# registro puntaje fase de GRUPOS 
		if identificador == 0:
			PuntajeUsuario = RankingModel.objects.get(Participante=idUsuario)
			PuntajeUsuario.PuntajeFaseGrupos = int(PuntajeUsuario.PuntajeFaseGrupos) + contador
			PuntajeUsuario.Puntaje = int(PuntajeUsuario.Puntaje) + contador
			PuntajeUsuario.save()

		# registro puntaje fase de octavos
		if identificador == 1:
			PuntajeUsuario = RankingModel.objects.get(Participante=idUsuario)
			PuntajeUsuario.PuntajeOctavos = contador
			PuntajeUsuario.Puntaje = int(PuntajeUsuario.Puntaje) + contador
			PuntajeUsuario.save()

		# registro puntaje fase de cuartos
		if identificador == 2:
			PuntajeUsuario = RankingModel.objects.get(Participante=idUsuario)
			PuntajeUsuario.PuntajeCuartos = contador
			PuntajeUsuario.Puntaje = int(PuntajeUsuario.Puntaje) + contador
			PuntajeUsuario.save()

		# registro puntaje fase de semifinales
		if identificador == 3:
			PuntajeUsuario = RankingModel.objects.get(Participante=idUsuario)
			PuntajeUsuario.PuntajeSeminFinales = contador
			PuntajeUsuario.Puntaje = int(PuntajeUsuario.Puntaje) + contador
			PuntajeUsuario.save()

		# registro puntaje fase de Final
		if identificador == '4':
			PuntajeUsuario = RankingModel.objects.get(Participante=idUsuario)
			PuntajeUsuario.PuntajeFinal = contador
			PuntajeUsuario.Puntaje = int(PuntajeUsuario.Puntaje) + contador
			PuntajeUsuario.save()

	except RankingModel.DoesNotExist:
		PuntajeUsuario = RankingModel ( 
		Participante=ParticipantesModel.objects.get(id=idUsuario),
		PuntajeFaseGrupos=contador,
		Puntaje = contador
		)
		PuntajeUsuario.save (force_insert = True)
        







