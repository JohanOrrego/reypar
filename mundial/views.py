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
				email = EmailMessage('POLLA MUNDIALISTA REYPAR', mensaje , to=[form.cleaned_data['email']], from_email='johan4201@gmail.com')
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
def RankingView(request):
	ranking=RankingModel.objects.order_by(('-Puntaje'))
	usuarios=ParticipantesModel.objects.all()
	return render(request,'ranking.html',{'ranking':ranking,'usuarios':usuarios})
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
			EquipoResultado2.GolaFavor = int(EquipoResultado2.GolaFavor) + int(partidojugado[5])
			EquipoResultado2.GolContra = int(EquipoResultado2.GolContra) + int(partidojugado[3])
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
def RegistroResultadosAdminView(request):
	if FaseGruposAdminModel.objects.filter(Participante = request.user.id).count() == 48:
		btnRegistroFaseGrupos = True
	else:
		btnRegistroFaseGrupos = False

	if FaseOctavosAdminModel.objects.filter(Participante = request.user.id).count() == 8:
		btnRegistroFaseOctavos = True
	else:
		btnRegistroFaseOctavos = False

	if FaseCuartosAdminModel.objects.filter(Participante = request.user.id).count() == 4:
		btnRegistroFaseCuartos = True
	else:
		btnRegistroFaseCuartos = False

	if FaseSemifinalesAdminModel.objects.filter(Participante = request.user.id).count() == 2:
		btnRegistroFaseSemi = True
	else:
		btnRegistroFaseSemi = False

	if FaseFinalAdminModel.objects.filter(Participante = request.user.id).count() == 2:
		btnRegistroFaseFinal = True
	else:
		btnRegistroFaseFinal = False

	return render(request,'adminResultados/principalRegistroResultadosAdmin.html',
		{ 'btnRegistroFaseGrupos':btnRegistroFaseGrupos, 'btnRegistroFaseOctavos':btnRegistroFaseOctavos,
		'btnRegistroFaseCuartos':btnRegistroFaseCuartos, 'btnRegistroFaseSemi':btnRegistroFaseSemi,
		'btnRegistroFaseFinal':btnRegistroFaseFinal
		})

# vista para el registro de los resultados de la fase de grupos por el Administrador
def RegistroFaseGruposAdminView(request):
	GrupoA=FaseGruposAdminModel.objects.filter(Grupo='A').order_by('FechaPartido')
	GrupoB=FaseGruposAdminModel.objects.filter(Grupo='B').order_by('FechaPartido')
	GrupoC=FaseGruposAdminModel.objects.filter(Grupo='C').order_by('FechaPartido')
	GrupoD=FaseGruposAdminModel.objects.filter(Grupo='D').order_by('FechaPartido')
	GrupoE=FaseGruposAdminModel.objects.filter(Grupo='E').order_by('FechaPartido')
	GrupoF=FaseGruposAdminModel.objects.filter(Grupo='F').order_by('FechaPartido')
	GrupoG=FaseGruposAdminModel.objects.filter(Grupo='G').order_by('FechaPartido')
	GrupoH=FaseGruposAdminModel.objects.filter(Grupo='H').order_by('FechaPartido')

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=1).count() > 0:
		btnPartido1 = 1
	else:
		btnPartido1 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=2).count() > 0:
		btnPartido2 = 1
	else:
		btnPartido2 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=3).count() > 0:
		btnPartido3 = 1
	else:
		btnPartido3 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=4).count() > 0:
		btnPartido4 = 1
	else:
		btnPartido4 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=5).count() > 0:
		btnPartido5 = 1
	else:
		btnPartido5 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=6).count() > 0:
		btnPartido6 = 1
	else:
		btnPartido6 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=7).count() > 0:
		btnPartido7 = 1
	else:
		btnPartido7 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=8).count() > 0:
		btnPartido8 = 1
	else:
		btnPartido8 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=9).count() > 0:
		btnPartido9 = 1
	else:
		btnPartido9 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=10).count() > 0:
		btnPartido10 = 1
	else:
		btnPartido10 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=11).count() > 0:
		btnPartido11 = 1
	else:
		btnPartido11 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=12).count() > 0:
		btnPartido12 = 1
	else:
		btnPartido12 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=13).count() > 0:
		btnPartido13 = 1
	else:
		btnPartido13 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=14).count() > 0:
		btnPartido14 = 1
	else:
		btnPartido14 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=15).count() > 0:
		btnPartido15 = 1
	else:
		btnPartido15 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=16).count() > 0:
		btnPartido16 = 1
	else:
		btnPartido16 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=17).count() > 0:
		btnPartido17 = 1
	else:
		btnPartido17 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=18).count() > 0:
		btnPartido18 = 1
	else:
		btnPartido18 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=19).count() > 0:
		btnPartido19 = 1
	else:
		btnPartido19 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=20).count() > 0:
		btnPartido20 = 1
	else:
		btnPartido20 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=21).count() > 0:
		btnPartido21 = 1
	else:
		btnPartido21 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=22).count() > 0:
		btnPartido22 = 1
	else:
		btnPartido22 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=23).count() > 0:
		btnPartido23 = 1
	else:
		btnPartido23 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=24).count() > 0:
		btnPartido24 = 1
	else:
		btnPartido24 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=25).count() > 0:
		btnPartido25 = 1
	else:
		btnPartido25 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=26).count() > 0:
		btnPartido26 = 1
	else:
		btnPartido26 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=27).count() > 0:
		btnPartido27 = 1
	else:
		btnPartido27 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=28).count() > 0:
		btnPartido28 = 1
	else:
		btnPartido28 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=29).count() > 0:
		btnPartido29 = 1
	else:
		btnPartido29 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=30).count() > 0:
		btnPartido30 = 1
	else:
		btnPartido30 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=31).count() > 0:
		btnPartido31 = 1
	else:
		btnPartido31 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=32).count() > 0:
		btnPartido32 = 1
	else:
		btnPartido32 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=33).count() > 0:
		btnPartido33 = 1
	else:
		btnPartido33 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=34).count() > 0:
		btnPartido34 = 1
	else:
		btnPartido34 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=35).count() > 0:
		btnPartido35 = 1
	else:
		btnPartido35 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=36).count() > 0:
		btnPartido36 = 1
	else:
		btnPartido36 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=37).count() > 0:
		btnPartido37 = 1
	else:
		btnPartido37 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=38).count() > 0:
		btnPartido38 = 1
	else:
		btnPartido38 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=39).count() > 0:
		btnPartido39 = 1
	else:
		btnPartido39 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=40).count() > 0:
		btnPartido40 = 1
	else:
		btnPartido40 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=41).count() > 0:
		btnPartido41 = 1
	else:
		btnPartido41 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=42).count() > 0:
		btnPartido42 = 1
	else:
		btnPartido42 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=43).count() > 0:
		btnPartido43 = 1
	else:
		btnPartido43 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=44).count() > 0:
		btnPartido44 = 1
	else:
		btnPartido44 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=45).count() > 0:
		btnPartido45 = 1
	else:
		btnPartido45 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=46).count() > 0:
		btnPartido46 = 1
	else:
		btnPartido46 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=47).count() > 0:
		btnPartido47 = 1
	else:
		btnPartido47 = 0

	if FaseGruposAdminModel.objects.filter(Participante = request.user.id, Identificador=48).count() > 0:
		btnPartido48 = 1
	else:
		btnPartido48 = 0


	if request.method=='POST' and 'btn_1_Groups_A' in request.POST:
		try:

			grupo1A = request.POST.getlist('1_Groups_A')
			RegistarResultadosFaseGruposAdmin(grupo1A)
			ObtenerPuntajeFaseGruposUsuarios(grupo1A,0)
			RegistroPosicionesEquiposUsuarios(grupo1A)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:

		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_2_Groups_A' in request.POST:
		try:

			grupo2A = request.POST.getlist('2_Groups_A')
			RegistarResultadosFaseGruposAdmin(grupo2A)
			ObtenerPuntajeFaseGruposUsuarios(grupo2A,0)
			RegistroPosicionesEquiposUsuarios(grupo2A)
			sweetify.success(request, 'Registro exitoso!')
			return redirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_3_Groups_A' in request.POST:
		try:

			grupo3A = request.POST.getlist('3_Groups_A')
			RegistarResultadosFaseGruposAdmin(grupo3A)
			ObtenerPuntajeFaseGruposUsuarios(grupo3A,0)
			RegistroPosicionesEquiposUsuarios(grupo3A)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_4_Groups_A' in request.POST:
		try:

			grupo4A = request.POST.getlist('4_Groups_A')
			RegistarResultadosFaseGruposAdmin(grupo4A)
			ObtenerPuntajeFaseGruposUsuarios(grupo4A,0)
			RegistroPosicionesEquiposUsuarios(grupo4A)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_5_Groups_A' in request.POST:
		try:

			grupo5A = request.POST.getlist('5_Groups_A')
			RegistarResultadosFaseGruposAdmin(grupo5A)
			ObtenerPuntajeFaseGruposUsuarios(grupo5A,0)
			RegistroPosicionesEquiposUsuarios(grupo5A)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_6_Groups_A' in request.POST:
		try:

			grupo6A = request.POST.getlist('6_Groups_A')
			RegistarResultadosFaseGruposAdmin(grupo6A)
			ObtenerPuntajeFaseGruposUsuarios(grupo6A,0)
			RegistroPosicionesEquiposUsuarios(grupo6A)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_1_Groups_B' in request.POST:
		try:

			grupo1B = request.POST.getlist('1_Groups_B')
			RegistarResultadosFaseGruposAdmin(grupo1B)
			ObtenerPuntajeFaseGruposUsuarios(grupo1B,0)
			RegistroPosicionesEquiposUsuarios(grupo1B)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_2_Groups_B' in request.POST:
		try:

			grupo2B = request.POST.getlist('2_Groups_B')
			RegistarResultadosFaseGruposAdmin(grupo2B)
			ObtenerPuntajeFaseGruposUsuarios(grupo2B,0)
			RegistroPosicionesEquiposUsuarios(grupo2B)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_3_Groups_B' in request.POST:
		try:

			grupo3B = request.POST.getlist('3_Groups_B')
			RegistarResultadosFaseGruposAdmin(grupo3B)
			ObtenerPuntajeFaseGruposUsuarios(grupo3B,0)
			RegistroPosicionesEquiposUsuarios(grupo3B)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_4_Groups_B' in request.POST:
		try:

			grupo4B = request.POST.getlist('4_Groups_B')
			RegistarResultadosFaseGruposAdmin(grupo4B)
			ObtenerPuntajeFaseGruposUsuarios(grupo4B,0)
			RegistroPosicionesEquiposUsuarios(grupo4B)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_5_Groups_B' in request.POST:
		try:

			grupo5B = request.POST.getlist('5_Groups_B')
			RegistarResultadosFaseGruposAdmin(grupo5B)
			ObtenerPuntajeFaseGruposUsuarios(grupo5B,0)
			RegistroPosicionesEquiposUsuarios(grupo5B)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_6_Groups_B' in request.POST:
		try:

			grupo6B = request.POST.getlist('6_Groups_B')
			RegistarResultadosFaseGruposAdmin(grupo6B)
			ObtenerPuntajeFaseGruposUsuarios(grupo6B,0)
			RegistroPosicionesEquiposUsuarios(grupo6B)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_1_Groups_C' in request.POST:
		try:

			grupo1C = request.POST.getlist('1_Groups_C')
			RegistarResultadosFaseGruposAdmin(grupo1C)
			ObtenerPuntajeFaseGruposUsuarios(grupo1C,0)
			RegistroPosicionesEquiposUsuarios(grupo1C)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_2_Groups_C' in request.POST:
		try:

			grupo2C = request.POST.getlist('2_Groups_C')
			RegistarResultadosFaseGruposAdmin(grupo2C)
			ObtenerPuntajeFaseGruposUsuarios(grupo2C,0)
			RegistroPosicionesEquiposUsuarios(grupo2C)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_3_Groups_C' in request.POST:
		try:

			grupo3C = request.POST.getlist('3_Groups_C')
			RegistarResultadosFaseGruposAdmin(grupo3C)
			ObtenerPuntajeFaseGruposUsuarios(grupo3C,0)
			RegistroPosicionesEquiposUsuarios(grupo3C)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_4_Groups_C' in request.POST:
		try:

			grupo4C = request.POST.getlist('4_Groups_C')
			RegistarResultadosFaseGruposAdmin(grupo4C)
			ObtenerPuntajeFaseGruposUsuarios(grupo4C,0)
			RegistroPosicionesEquiposUsuarios(grupo4C)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_5_Groups_C' in request.POST:
		try:

			grupo5C = request.POST.getlist('5_Groups_C')
			RegistarResultadosFaseGruposAdmin(grupo5C)
			ObtenerPuntajeFaseGruposUsuarios(grupo5C,0)
			RegistroPosicionesEquiposUsuarios(grupo5C)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_6_Groups_C' in request.POST:
		try:

			grupo6C = request.POST.getlist('6_Groups_C')
			RegistarResultadosFaseGruposAdmin(grupo6C)
			ObtenerPuntajeFaseGruposUsuarios(grupo6C,0)
			RegistroPosicionesEquiposUsuarios(grupo6C)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_1_Groups_D' in request.POST:
		try:

			grupo1D = request.POST.getlist('1_Groups_D')
			RegistarResultadosFaseGruposAdmin(grupo1D)
			ObtenerPuntajeFaseGruposUsuarios(grupo1D,0)
			RegistroPosicionesEquiposUsuarios(grupo1D)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_2_Groups_D' in request.POST:
		try:

			grupo2D = request.POST.getlist('2_Groups_D')
			RegistarResultadosFaseGruposAdmin(grupo2D)
			ObtenerPuntajeFaseGruposUsuarios(grupo2D,0)
			RegistroPosicionesEquiposUsuarios(grupo2D)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_3_Groups_D' in request.POST:
		try:

			grupo3D = request.POST.getlist('3_Groups_D')
			RegistarResultadosFaseGruposAdmin(grupo3D)
			ObtenerPuntajeFaseGruposUsuarios(grupo3D,0)
			RegistroPosicionesEquiposUsuarios(grupo3D)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_4_Groups_D' in request.POST:
		try:

			grupo4D = request.POST.getlist('4_Groups_D')
			RegistarResultadosFaseGruposAdmin(grupo4D)
			ObtenerPuntajeFaseGruposUsuarios(grupo4D,0)
			RegistroPosicionesEquiposUsuarios(grupo4D)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_5_Groups_D' in request.POST:
		try:

			grupo5D = request.POST.getlist('5_Groups_D')
			RegistarResultadosFaseGruposAdmin(grupo5D)
			ObtenerPuntajeFaseGruposUsuarios(grupo5D,0)
			RegistroPosicionesEquiposUsuarios(grupo5D)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_6_Groups_D' in request.POST:
		try:

			grupo6D = request.POST.getlist('6_Groups_D')
			RegistarResultadosFaseGruposAdmin(grupo6D)
			ObtenerPuntajeFaseGruposUsuarios(grupo6D,0)
			RegistroPosicionesEquiposUsuarios(grupo6D)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_1_Groups_E' in request.POST:
		try:

			grupo1E = request.POST.getlist('1_Groups_E')
			RegistarResultadosFaseGruposAdmin(grupo1E)
			ObtenerPuntajeFaseGruposUsuarios(grupo1E,0)
			RegistroPosicionesEquiposUsuarios(grupo1E)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_2_Groups_E' in request.POST:
		try:

			grupo2E = request.POST.getlist('2_Groups_E')
			RegistarResultadosFaseGruposAdmin(grupo2E)
			ObtenerPuntajeFaseGruposUsuarios(grupo2E,0)
			RegistroPosicionesEquiposUsuarios(grupo2E)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_3_Groups_E' in request.POST:
		try:

			grupo3E = request.POST.getlist('3_Groups_E')
			RegistarResultadosFaseGruposAdmin(grupo3E)
			ObtenerPuntajeFaseGruposUsuarios(grupo3E,0)
			RegistroPosicionesEquiposUsuarios(grupo3E)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_4_Groups_E' in request.POST:
		try:

			grupo4E = request.POST.getlist('4_Groups_E')
			RegistarResultadosFaseGruposAdmin(grupo4E)
			ObtenerPuntajeFaseGruposUsuarios(grupo4E,0)
			RegistroPosicionesEquiposUsuarios(grupo4E)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_5_Groups_E' in request.POST:
		try:

			grupo5E = request.POST.getlist('5_Groups_E')
			RegistarResultadosFaseGruposAdmin(grupo5E)
			ObtenerPuntajeFaseGruposUsuarios(grupo5E,0)
			RegistroPosicionesEquiposUsuarios(grupo5E)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_6_Groups_E' in request.POST:
		try:

			grupo6E = request.POST.getlist('6_Groups_E')
			RegistarResultadosFaseGruposAdmin(grupo6E)
			ObtenerPuntajeFaseGruposUsuarios(grupo6E,0)
			RegistroPosicionesEquiposUsuarios(grupo6E)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_1_Groups_F' in request.POST:
		try:

			grupo1F = request.POST.getlist('1_Groups_F')
			RegistarResultadosFaseGruposAdmin(grupo1F)
			ObtenerPuntajeFaseGruposUsuarios(grupo1F,0)
			RegistroPosicionesEquiposUsuarios(grupo1F)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_2_Groups_F' in request.POST:
		try:

			grupo2F = request.POST.getlist('2_Groups_F')
			RegistarResultadosFaseGruposAdmin(grupo2F)
			ObtenerPuntajeFaseGruposUsuarios(grupo2F,0)
			RegistroPosicionesEquiposUsuarios(grupo2F)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_3_Groups_F' in request.POST:
		try:

			grupo3F = request.POST.getlist('3_Groups_F')
			RegistarResultadosFaseGruposAdmin(grupo3F)
			ObtenerPuntajeFaseGruposUsuarios(grupo3F,0)
			RegistroPosicionesEquiposUsuarios(grupo3F)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_4_Groups_F' in request.POST:
		try:

			grupo4F = request.POST.getlist('4_Groups_F')
			RegistarResultadosFaseGruposAdmin(grupo4F)
			ObtenerPuntajeFaseGruposUsuarios(grupo4F,0)
			RegistroPosicionesEquiposUsuarios(grupo4F)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_5_Groups_F' in request.POST:
		try:

			grupo5F = request.POST.getlist('5_Groups_F')
			RegistarResultadosFaseGruposAdmin(grupo5F)
			ObtenerPuntajeFaseGruposUsuarios(grupo5F,0)
			RegistroPosicionesEquiposUsuarios(grupo5F)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_6_Groups_F' in request.POST:
		try:

			grupo6F = request.POST.getlist('6_Groups_F')
			RegistarResultadosFaseGruposAdmin(grupo6F)
			ObtenerPuntajeFaseGruposUsuarios(grupo6F,0)
			RegistroPosicionesEquiposUsuarios(grupo6F)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_1_Groups_G' in request.POST:
		try:

			grupo1G = request.POST.getlist('1_Groups_G')
			RegistarResultadosFaseGruposAdmin(grupo1G)
			ObtenerPuntajeFaseGruposUsuarios(grupo1G,0)
			RegistroPosicionesEquiposUsuarios(grupo1G)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_2_Groups_G' in request.POST:
		try:

			grupo2G = request.POST.getlist('2_Groups_G')
			RegistarResultadosFaseGruposAdmin(grupo2G)
			ObtenerPuntajeFaseGruposUsuarios(grupo2G,0)
			RegistroPosicionesEquiposUsuarios(grupo2G)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_3_Groups_G' in request.POST:
		try:

			grupo3G = request.POST.getlist('3_Groups_G')
			RegistarResultadosFaseGruposAdmin(grupo3G)
			ObtenerPuntajeFaseGruposUsuarios(grupo3G,0)
			RegistroPosicionesEquiposUsuarios(grupo3G)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_4_Groups_G' in request.POST:
		try:

			grupo4G = request.POST.getlist('4_Groups_G')
			RegistarResultadosFaseGruposAdmin(grupo4G)
			ObtenerPuntajeFaseGruposUsuarios(grupo4G,0)
			RegistroPosicionesEquiposUsuarios(grupo4G)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_5_Groups_G' in request.POST:
		try:

			grupo5G = request.POST.getlist('5_Groups_G')
			RegistarResultadosFaseGruposAdmin(grupo5G)
			ObtenerPuntajeFaseGruposUsuarios(grupo5G,0)
			RegistroPosicionesEquiposUsuarios(grupo5G)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_6_Groups_G' in request.POST:
		try:

			grupo6G = request.POST.getlist('6_Groups_G')
			RegistarResultadosFaseGruposAdmin(grupo6G)
			ObtenerPuntajeFaseGruposUsuarios(grupo6G,0)
			RegistroPosicionesEquiposUsuarios(grupo6G)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_1_Groups_H' in request.POST:
		try:

			grupo1H = request.POST.getlist('1_Groups_H')
			RegistarResultadosFaseGruposAdmin(grupo1H)
			ObtenerPuntajeFaseGruposUsuarios(grupo1H,0)
			RegistroPosicionesEquiposUsuarios(grupo1H)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_2_Groups_H' in request.POST:
		try:

			grupo2H = request.POST.getlist('2_Groups_H')
			RegistarResultadosFaseGruposAdmin(grupo2H)
			ObtenerPuntajeFaseGruposUsuarios(grupo2H,0)
			RegistroPosicionesEquiposUsuarios(grupo2H)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_3_Groups_H' in request.POST:
		try:

			grupo3H = request.POST.getlist('3_Groups_H')
			RegistarResultadosFaseGruposAdmin(grupo3H)
			ObtenerPuntajeFaseGruposUsuarios(grupo3H,0)
			RegistroPosicionesEquiposUsuarios(grupo3H)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_4_Groups_H' in request.POST:
		try:

			grupo4H = request.POST.getlist('4_Groups_H')
			RegistarResultadosFaseGruposAdmin(grupo4H)
			ObtenerPuntajeFaseGruposUsuarios(grupo4H,0)
			RegistroPosicionesEquiposUsuarios(grupo4H)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_5_Groups_H' in request.POST:
		try:

			grupo5H = request.POST.getlist('5_Groups_H')
			RegistarResultadosFaseGruposAdmin(grupo5H)
			ObtenerPuntajeFaseGruposUsuarios(grupo5H,0)
			RegistroPosicionesEquiposUsuarios(grupo5H)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_6_Groups_H' in request.POST:
		try:

			grupo6H = request.POST.getlist('6_Groups_H')
			RegistarResultadosFaseGruposAdmin(grupo6H)
			ObtenerPuntajeFaseGruposUsuarios(grupo6H,0)
			RegistroPosicionesEquiposUsuarios(grupo6H)
			sweetify.success(request, 'Registro exitoso!')
			return HttpResponseRedirect('/registroFaseGruposAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	return render(request, 'adminResultados/registroFaseGruposAdmin.html',
		{'GrupoA':GrupoA,'GrupoB':GrupoB,'GrupoC':GrupoC,'GrupoD':GrupoD,'GrupoE':GrupoE,'GrupoF':GrupoF,'GrupoG':GrupoG,'GrupoH':GrupoH,
		'btnPartido1':btnPartido1,'btnPartido2':btnPartido2,'btnPartido3':btnPartido3,'btnPartido4':btnPartido4,
		'btnPartido5':btnPartido5,'btnPartido6':btnPartido6,'btnPartido7':btnPartido7,'btnPartido8':btnPartido8,
		'btnPartido9':btnPartido9,'btnPartido10':btnPartido10,'btnPartido11':btnPartido11,'btnPartido12':btnPartido12,
		'btnPartido13':btnPartido13,'btnPartido14':btnPartido14,'btnPartido15':btnPartido15,'btnPartido16':btnPartido16,
		'btnPartido17':btnPartido17,'btnPartido18':btnPartido18,'btnPartido19':btnPartido19,'btnPartido20':btnPartido20,
		'btnPartido21':btnPartido21,'btnPartido22':btnPartido22,'btnPartido23':btnPartido23,'btnPartido24':btnPartido24,
		'btnPartido25':btnPartido25,'btnPartido26':btnPartido26,'btnPartido27':btnPartido27,'btnPartido28':btnPartido28,
		'btnPartido29':btnPartido29,'btnPartido30':btnPartido30,'btnPartido31':btnPartido31,'btnPartido32':btnPartido32,
		'btnPartido33':btnPartido33,'btnPartido34':btnPartido34,'btnPartido35':btnPartido35,'btnPartido36':btnPartido36,'btnPartido37':btnPartido37,
		'btnPartido38':btnPartido38,'btnPartido39':btnPartido39,'btnPartido40':btnPartido40,'btnPartido41':btnPartido41,
		'btnPartido42':btnPartido42,'btnPartido43':btnPartido43,'btnPartido44':btnPartido44,'btnPartido45':btnPartido45,
		'btnPartido46':btnPartido46,'btnPartido47':btnPartido47,'btnPartido48':btnPartido48})

# funcion para el registro en base de datos del list con los resultados registrados por el Administrador
def RegistarResultadosFaseGruposAdmin(partido):
	ResultadoPartido = FaseGruposAdminModel ( 
		FechaPartido=partido[0],
		Grupo=partido[1],
		Equipo1=partido[2],
		MarcadorEquipo1=partido[3],
		Equipo2=partido[4],
		MarcadorEquipo2 = partido[5],
		Participante =ParticipantesModel.objects.get(id=partido[6]),
		Identificador = partido[7]
	)
	ResultadoPartido.save (force_insert = True)

#funcion para obtener el puntaje del usuario segun sea el resultado del partido registrado en la fase de grupos por el admin
def ObtenerPuntajeFaseGruposUsuarios(partido,identificador):
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
			PuntajeUsuario.PuntajeOctavos = int(PuntajeUsuario.PuntajeOctavos) + contador
			PuntajeUsuario.Puntaje = int(PuntajeUsuario.Puntaje) + contador
			PuntajeUsuario.save()

		# registro puntaje fase de cuartos
		if identificador == 2:
			PuntajeUsuario = RankingModel.objects.get(Participante=idUsuario)
			PuntajeUsuario.PuntajeCuartos = int(PuntajeUsuario.PuntajeCuartos) + contador
			PuntajeUsuario.Puntaje = int(PuntajeUsuario.Puntaje) + contador
			PuntajeUsuario.save()

		# registro puntaje fase de semifinales
		if identificador == 3:
			PuntajeUsuario = RankingModel.objects.get(Participante=idUsuario)
			PuntajeUsuario.PuntajeSeminFinales = int(PuntajeUsuario.PuntajeSeminFinales) + contador
			PuntajeUsuario.Puntaje = int(PuntajeUsuario.Puntaje) + contador
			PuntajeUsuario.save()

		# registro puntaje fase de Final
		if identificador == 4:
			PuntajeUsuario = RankingModel.objects.get(Participante=idUsuario)
			PuntajeUsuario.PuntajeFinal = int(PuntajeUsuario.PuntajeFinal) + contador
			PuntajeUsuario.Puntaje = int(PuntajeUsuario.Puntaje) + contador
			PuntajeUsuario.save()

	except RankingModel.DoesNotExist:
		PuntajeUsuario = RankingModel ( 
		Participante=ParticipantesModel.objects.get(id=idUsuario),
		PuntajeFaseGrupos=contador,
		Puntaje = contador
		)
		PuntajeUsuario.save (force_insert = True)

# vista para el registro de los octavos de admin
def RegistroOctavosAdminView(request):
	Octavosuno=FaseOctavosAdminModel.objects.order_by('FechaPartido')
	if FaseOctavosAdminModel.objects.filter(Participante = request.user.id, Identificador=49).count() > 0:
		btnPartido1 = 1
	else:
		btnPartido1 = 0

	if FaseOctavosAdminModel.objects.filter(Participante = request.user.id, Identificador=50).count() > 0:
		btnPartido2 = 1
	else:
		btnPartido2 = 0

	if FaseOctavosAdminModel.objects.filter(Participante = request.user.id, Identificador=51).count() > 0:
		btnPartido3 = 1
	else:
		btnPartido3 = 0

	if FaseOctavosAdminModel.objects.filter(Participante = request.user.id, Identificador=52).count() > 0:
		btnPartido4 = 1
	else:
		btnPartido4 = 0

	if FaseOctavosAdminModel.objects.filter(Participante = request.user.id, Identificador=53).count() > 0:
		btnPartido5 = 1
	else:
		btnPartido5 = 0

	if FaseOctavosAdminModel.objects.filter(Participante = request.user.id, Identificador=54).count() > 0:
		btnPartido6 = 1
	else:
		btnPartido6 = 0

	if FaseOctavosAdminModel.objects.filter(Participante = request.user.id, Identificador=55).count() > 0:
		btnPartido7 = 1
	else:
		btnPartido7 = 0

	if FaseOctavosAdminModel.objects.filter(Participante = request.user.id, Identificador=56).count() > 0:
		btnPartido8 = 1
	else:
		btnPartido8 = 0
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


	if request.method=='POST' and 'btn_partido1' in request.POST:
		try:

			resultadoOctavos1 = request.POST.getlist('partido1')

			if len(resultadoOctavos1) < 8:
				resultadoOctavos1.insert(5, 0)

			Empate = ValidarEmpateAdmin([resultadoOctavos1])

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseOctavosAdmin([resultadoOctavos1])
				ObtenerPuntajeFaseOctavosUsuarios(resultadoOctavos1,1)
				sweetify.success(request, 'Registro exitoso!')
				return HttpResponseRedirect('/registroOctavosAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_partido2' in request.POST:
		try:

			resultadoOctavos2 = request.POST.getlist('partido2')

			if len(resultadoOctavos2) < 8:
				resultadoOctavos2.insert(5, 0)

			Empate = ValidarEmpateAdmin([resultadoOctavos2])

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseOctavosAdmin([resultadoOctavos2])
				ObtenerPuntajeFaseOctavosUsuarios(resultadoOctavos2,1)
				sweetify.success(request, 'Registro exitoso!')
				return HttpResponseRedirect('/registroOctavosAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_partido3' in request.POST:
		try:

			resultadoOctavos3 = request.POST.getlist('partido3')

			if len(resultadoOctavos3) < 8:
				resultadoOctavos3.insert(5, 0)

			Empate = ValidarEmpateAdmin([resultadoOctavos3])

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseOctavosAdmin([resultadoOctavos3])
				ObtenerPuntajeFaseOctavosUsuarios(resultadoOctavos3,1)
				sweetify.success(request, 'Registro exitoso!')
				return HttpResponseRedirect('/registroOctavosAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_partido4' in request.POST:
		try:

			resultadoOctavos4 = request.POST.getlist('partido4')

			if len(resultadoOctavos4) < 8:
				resultadoOctavos4.insert(5, 0)

			Empate = ValidarEmpateAdmin([resultadoOctavos4])

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseOctavosAdmin([resultadoOctavos4])
				ObtenerPuntajeFaseOctavosUsuarios(resultadoOctavos4,1)
				sweetify.success(request, 'Registro exitoso!')
				return HttpResponseRedirect('/registroOctavosAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_partido5' in request.POST:
		try:

			resultadoOctavos5 = request.POST.getlist('partido5')

			if len(resultadoOctavos5) < 8:
				resultadoOctavos5.insert(5, 0)

			Empate = ValidarEmpateAdmin([resultadoOctavos5])

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseOctavosAdmin([resultadoOctavos5])
				ObtenerPuntajeFaseOctavosUsuarios(resultadoOctavos5,1)
				sweetify.success(request, 'Registro exitoso!')
				return HttpResponseRedirect('/registroOctavosAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_partido6' in request.POST:
		try:

			resultadoOctavos6 = request.POST.getlist('partido6')

			if len(resultadoOctavos6) < 8:
				resultadoOctavos6.insert(5, 0)

			Empate = ValidarEmpateAdmin([resultadoOctavos6])

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseOctavosAdmin([resultadoOctavos6])
				ObtenerPuntajeFaseOctavosUsuarios(resultadoOctavos6,1)
				sweetify.success(request, 'Registro exitoso!')
				return HttpResponseRedirect('/registroOctavosAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_partido7' in request.POST:
		try:

			resultadoOctavos7 = request.POST.getlist('partido7')

			if len(resultadoOctavos7) < 8:
				resultadoOctavos7.insert(5, 0)

			Empate = ValidarEmpateAdmin([resultadoOctavos7])

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseOctavosAdmin([resultadoOctavos7])
				ObtenerPuntajeFaseOctavosUsuarios(resultadoOctavos7,1)
				sweetify.success(request, 'Registro exitoso!')
				return HttpResponseRedirect('/registroOctavosAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_partido8' in request.POST:
		try:

			resultadoOctavos8 = request.POST.getlist('partido8')

			if len(resultadoOctavos8) < 8:
				resultadoOctavos8.insert(5, 0)

			Empate = ValidarEmpateAdmin([resultadoOctavos8])

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseOctavosAdmin([resultadoOctavos8])
				ObtenerPuntajeFaseOctavosUsuarios(resultadoOctavos8,1)
				sweetify.success(request, 'Registro exitoso!')
				return HttpResponseRedirect('/registroOctavosAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	return render(request,'adminResultados/registroOctavosAdmin.html',
		{'Octavosuno':Octavosuno,'partido1':partido1, 'partido2':partido2,
		'partido3':partido3, 'partido4':partido4,
		'partido5':partido5, 'partido6':partido6,
		'partido7':partido7, 'partido8':partido8,
		'btnPartido1':btnPartido1,'btnPartido2':btnPartido2,'btnPartido3':btnPartido3,'btnPartido4':btnPartido4,
		'btnPartido5':btnPartido5,'btnPartido6':btnPartido6,'btnPartido7':btnPartido7,'btnPartido8':btnPartido8
		})
        
# funcion para el registro en base de datos del list con los resultados registrados para la fase de octavos por el administrador
def RegistarResultadosFaseOctavosAdmin(partido):
    objs = [
        FaseOctavosAdminModel(
        	FechaPartido = e[0],
			Equipo1 = e[1],
			MarcadorEquipo1 = e[2],
			Equipo2 = e[3],
			MarcadorEquipo2 = e[4],
			PenalEquipoGanador = e[5],
			Identificador = e[6],
			Participante = ParticipantesModel.objects.get(id=e[7]),  

        )
    for e in partido
    ]
    detalleFaseOctavosAdmin = FaseOctavosAdminModel.objects.bulk_create(objs)

#funcion para obtener el puntaje del usuario segun sea el resultado del partido de la fase de octavos registrado por el admin
def ObtenerPuntajeFaseOctavosUsuarios(partido,identificador):
	ResultadosUsuarios =  FaseOctavosUsuariosModel.objects.filter(FechaPartido=partido[0],Equipo1=partido[1],Equipo2=partido[3])
	contador = 0
	for i in ResultadosUsuarios:
		if i.MarcadorEquipo1 == int(partido[2]) and i.MarcadorEquipo2 == int(partido[4]):
			contador += 3
		if i.MarcadorEquipo1 > i.MarcadorEquipo2 and partido[2] > partido[4]:
			contador += 1
		if i.MarcadorEquipo1 < i.MarcadorEquipo2 and partido[2] < partido[4]:
			contador += 1
		if i.PenalEquipoGanador == partido[5]:
			contador += 1
		registroRanking(contador,i.Participante.id,identificador)

# funcion para validar si existen resultados en cero en las diferentres fases
def ValidarEmpateAdmin(partido):
	contar=0
	for i in partido:
		if i[2] == i[4]:
			if i[5] == '0':
				contar += contar + 1
	return contar

#vista para el formulario de registro de fase de cuartos por el admin
def RegistroFaseCuartosAdminView(request):
	Cuartos=FaseCuartosAdminModel.objects.order_by('FechaPartido')

	if FaseCuartosAdminModel.objects.filter(Participante = request.user.id, Identificador=57).count() > 0:
		btnPartido1 = 1
	else:
		btnPartido1 = 0

	if FaseCuartosAdminModel.objects.filter(Participante = request.user.id, Identificador=58).count() > 0:
		btnPartido2 = 1
	else:
		btnPartido2 = 0

	if FaseCuartosAdminModel.objects.filter(Participante = request.user.id, Identificador=59).count() > 0:
		btnPartido3 = 1
	else:
		btnPartido3 = 0

	if FaseCuartosAdminModel.objects.filter(Participante = request.user.id, Identificador=60).count() > 0:
		btnPartido4 = 1
	else:
		btnPartido4 = 0

	EquiposCuartos = FaseOctavosAdminModel.objects.filter(Participante= request.user.id)

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

	if request.method=='POST' and 'btn_partido1' in request.POST:
		try:

			resultadoCuartos1 = request.POST.getlist('partido1')

			if len(resultadoCuartos1) < 8:
				resultadoCuartos1.insert(5, 0)

			Empate = ValidarEmpateAdmin([resultadoCuartos1])

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseCuartoAdmin([resultadoCuartos1])
				ObtenerPuntajeFaseCuartosAdmin(resultadoCuartos1,2)
				sweetify.success(request, 'Registro exitoso!')
				return HttpResponseRedirect('/registroCuartosAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_partido2' in request.POST:
		try:

			resultadoCuartos2 = request.POST.getlist('partido2')

			if len(resultadoCuartos2) < 8:
				resultadoCuartos2.insert(5, 0)

			Empate = ValidarEmpateAdmin([resultadoCuartos2])

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseCuartoAdmin([resultadoCuartos2])
				ObtenerPuntajeFaseCuartosAdmin(resultadoCuartos2,2)
				sweetify.success(request, 'Registro exitoso!')
				return HttpResponseRedirect('/registroCuartosAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_partido3' in request.POST:
		try:

			resultadoCuartos3 = request.POST.getlist('partido3')

			if len(resultadoCuartos3) < 8:
				resultadoCuartos3.insert(5, 0)

			Empate = ValidarEmpateAdmin([resultadoCuartos3])

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseCuartoAdmin([resultadoCuartos3])
				ObtenerPuntajeFaseCuartosAdmin(resultadoCuartos3,2)
				sweetify.success(request, 'Registro exitoso!')
				return HttpResponseRedirect('/registroCuartosAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_partido4' in request.POST:
		try:

			resultadoCuartos4 = request.POST.getlist('partido4')

			if len(resultadoCuartos4) < 8:
				resultadoCuartos4.insert(5, 0)

			Empate = ValidarEmpateAdmin([resultadoCuartos4])

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseCuartoAdmin([resultadoCuartos4])
				ObtenerPuntajeFaseCuartosAdmin(resultadoCuartos4,2)
				sweetify.success(request, 'Registro exitoso!')
				return HttpResponseRedirect('/registroCuartosAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	return render(request,'adminResultados/registroCuartosAdmin.html',
		{'Cuartos':Cuartos,'partido1':partido1, 'partido2':partido2,
		'partido3':partido3, 'partido4':partido4,
		'btnPartido1':btnPartido1,'btnPartido2':btnPartido2,'btnPartido3':btnPartido3,'btnPartido4':btnPartido4,
		})

# funcion para el registro en base de datos del list con los resultados registrados para la fase de cuartos por el usuario
def RegistarResultadosFaseCuartoAdmin(partido):
    objs = [
        FaseCuartosAdminModel(
        	FechaPartido = e[0],
			Equipo1 = e[1],
			MarcadorEquipo1 = e[2],
			Equipo2 = e[3],
			MarcadorEquipo2 = e[4],
			PenalEquipoGanador = e[5],
			Identificador = e[6],
			Participante = ParticipantesModel.objects.get(id=e[7]),  

        )
    for e in partido
    ]
    detalleFaseCuartosAdmin = FaseCuartosAdminModel.objects.bulk_create(objs)

#funcion para obtener el puntaje del usuario segun sea el resultado del partido de la fase de cuartos registrado por el admin
def ObtenerPuntajeFaseCuartosAdmin(partido,identificador):
	ResultadosUsuarios =  FaseCuartosUsuariosModel.objects.filter(FechaPartido=partido[0],Equipo1=partido[1],Equipo2=partido[3])
	contador = 0
	for i in ResultadosUsuarios:
		if i.MarcadorEquipo1 == int(partido[2]) and i.MarcadorEquipo2 == int(partido[4]):
			contador += 3
		if i.MarcadorEquipo1 > i.MarcadorEquipo2 and partido[2] > partido[4]:
			contador += 1
		if i.MarcadorEquipo1 < i.MarcadorEquipo2 and partido[2] < partido[4]:
			contador += 1
		if i.PenalEquipoGanador == partido[5]:
			contador += 1
		registroRanking(contador,i.Participante.id,identificador)


#vista para el formulario de registro de fase de semifinales del admin
def RegistroFaseSemifinalesAdminView(request):
	Semis=FaseSemifinalesAdminModel.objects.order_by('FechaPartido')

	if FaseSemifinalesAdminModel.objects.filter(Participante = request.user.id, Identificador=61).count() > 0:
		btnPartido1 = 1
	else:
		btnPartido1 = 0

	if FaseSemifinalesAdminModel.objects.filter(Participante = request.user.id, Identificador=62).count() > 0:
		btnPartido2 = 1
	else:
		btnPartido2 = 0

	EquiposSemifinales = FaseCuartosAdminModel.objects.filter(Participante= request.user.id)
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

	if request.method=='POST' and 'btn_partido1' in request.POST:
		try:

			resultadoCuartos1 = request.POST.getlist('partido1')

			if len(resultadoCuartos1) < 8:
				resultadoCuartos1.insert(5, 0)

			Empate = ValidarEmpateAdmin([resultadoCuartos1])

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseSemifinalesAdmin([resultadoCuartos1])
				ObtenerPuntajeFaseSemifinalesAdmin(resultadoCuartos1,3)
				sweetify.success(request, 'Registro exitoso!')
				return HttpResponseRedirect('/registroSemifinalesAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_partido2' in request.POST:
		try:

			resultadoCuartos2 = request.POST.getlist('partido2')

			if len(resultadoCuartos2) < 8:
				resultadoCuartos2.insert(5, 0)

			Empate = ValidarEmpateAdmin([resultadoCuartos2])

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseSemifinalesAdmin([resultadoCuartos2])
				ObtenerPuntajeFaseSemifinalesAdmin(resultadoCuartos2,3)
				sweetify.success(request, 'Registro exitoso!')
				return HttpResponseRedirect('/registroSemifinalesAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')


	return render(request,'adminResultados/registroSemifinalesAdmin.html',
		{'Semis':Semis,'partido1':partido1, 'partido2':partido2,
		'btnPartido1':btnPartido1,'btnPartido2':btnPartido2,
		})

# funcion para el registro en base de datos del list con los resultados registrados para la fase de cuartos por el admin
def RegistarResultadosFaseSemifinalesAdmin(partido):
    objs = [
        FaseSemifinalesAdminModel(
        	FechaPartido = e[0],
			Equipo1 = e[1],
			MarcadorEquipo1 = e[2],
			Equipo2 = e[3],
			MarcadorEquipo2 = e[4],
			PenalEquipoGanador = e[5],
			Identificador = e[6],
			Participante = ParticipantesModel.objects.get(id=e[7]),  

        )
    for e in partido
    ]
    detalleFaseSemifinalesAdmin = FaseSemifinalesAdminModel.objects.bulk_create(objs)

#funcion para obtener el puntaje del usuario segun sea el resultado del partido de la fase de semi finales registrado por el admin
def ObtenerPuntajeFaseSemifinalesAdmin(partido,identificador):
	ResultadosUsuarios =  FaseSemifinalesUsuariosModel.objects.filter(FechaPartido=partido[0],Equipo1=partido[1],Equipo2=partido[3])
	contador = 0
	for i in ResultadosUsuarios:
		if i.MarcadorEquipo1 == int(partido[2]) and i.MarcadorEquipo2 == int(partido[4]):
			contador += 3
		if i.MarcadorEquipo1 > i.MarcadorEquipo2 and partido[2] > partido[4]:
			contador += 1
		if i.MarcadorEquipo1 < i.MarcadorEquipo2 and partido[2] < partido[4]:
			contador += 1
		if i.PenalEquipoGanador == partido[5]:
			contador += 1
		registroRanking(contador,i.Participante.id,identificador)

#vista para el formulario de registro de fase de finales
def RegistroFaseFinalAdminView(request):
	Final=FaseFinalAdminModel.objects.order_by('FechaPartido')
	if FaseFinalAdminModel.objects.filter(Participante = request.user.id, Identificador=61).count() > 0:
		btnPartido1 = 1
	else:
		btnPartido1 = 0

	if FaseFinalAdminModel.objects.filter(Participante = request.user.id, Identificador=62).count() > 0:
		btnPartido2 = 1
	else:
		btnPartido2 = 0

	EquiposFinales = FaseSemifinalesAdminModel.objects.filter(Participante= request.user.id)
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

	if request.method=='POST' and 'btn_partido1' in request.POST:
		try:

			resultadoFinal = request.POST.getlist('partido1')

			if len(resultadoFinal) < 8:
				resultadoFinal.insert(5, 0)

			Empate = ValidarEmpateAdmin([resultadoFinal])

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseFinalAdmin([resultadoFinal])
				ObtenerPuntajeFaseFinalAdmin(resultadoFinal,4)
				sweetify.success(request, 'Registro exitoso!')
				return HttpResponseRedirect('/registroFinalesAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')

	if request.method=='POST' and 'btn_partido2' in request.POST:
		try:

			resultadoTercerPuesto = request.POST.getlist('partido2')

			if len(resultadoTercerPuesto) < 8:
				resultadoTercerPuesto.insert(5, 0)

			Empate = ValidarEmpateAdmin([resultadoTercerPuesto])

			if Empate > 0:

				sweetify.warning(request, 'Para los empates, por favor ingresar resultado en los penales!')

			else:

				RegistarResultadosFaseFinalAdmin([resultadoTercerPuesto])
				ObtenerPuntajeFaseFinalAdmin(resultadoTercerPuesto,4)
				sweetify.success(request, 'Registro exitoso!')
				return HttpResponseRedirect('/registroFinalesAdmin/')

		except IntegrityError as e:
			
		    sweetify.error(request, 'Ya se registro el resultado de este partido!')


	return render(request,'adminResultados/registroFinalesAdmin.html',
		{'Final':Final,'partido1':partido1, 'partido2':partido2,
		'btnPartido1':btnPartido1,'btnPartido2':btnPartido2,
		})

# funcion para el registro en base de datos del list con los resultados registrados para la final por el usuario
def RegistarResultadosFaseFinalAdmin(partido):
    objs = [
        FaseFinalAdminModel(
        	FechaPartido = e[0],
			Equipo1 = e[1],
			MarcadorEquipo1 = e[2],
			Equipo2 = e[3],
			MarcadorEquipo2 = e[4],
			PenalEquipoGanador = e[5],
			Identificador = e[6],
			Participante = ParticipantesModel.objects.get(id=e[7]),  

        )
    for e in partido
    ]
    detalleFaseFinalAdmin = FaseFinalAdminModel.objects.bulk_create(objs)

#funcion para obtener el puntaje del usuario segun sea el resultado del partido de la fase de finales registrado por el admin
def ObtenerPuntajeFaseFinalAdmin(partido,identificador):
	ResultadosUsuarios =  FaseFinalUsuariosModel.objects.filter(FechaPartido=partido[0],Equipo1=partido[1],Equipo2=partido[3])
	contador = 0
	for i in ResultadosUsuarios:
		if i.MarcadorEquipo1 == int(partido[2]) and i.MarcadorEquipo2 == int(partido[4]):
			contador += 3
		if i.MarcadorEquipo1 > i.MarcadorEquipo2 and partido[2] > partido[4]:
			contador += 1
		if i.MarcadorEquipo1 < i.MarcadorEquipo2 and partido[2] < partido[4]:
			contador += 1
		if i.PenalEquipoGanador == partido[5]:
			contador += 1
		registroRanking(contador,i.Participante.id,identificador)




