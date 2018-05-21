# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
import views
from .views import *

urlpatterns = [
	
	url(r'^registro/$', RegistroUsuarioView.as_view(), name='registro'),
	url(r'^terminosCondiciones/$', TerminosCondicionesView.as_view(), name='terminosCondiciones'),
	url(r'^validarCliente/$', ValidarClienteView, name='validarCliente'),
	url(r'^$', PrincipalView.as_view(), name='Principal'),
	url(r'^inicio/$', login_required(InicioView), name='index'),
	url(r'^indexadmin/$', login_required(IndexAdmin), name='indexadmin'),
	url(r'^filtros/$', login_required(filtros), name='filtros'),
	url(r'^ranking/$', login_required(RankingView), name='ranking'),
    url(r'^inscritos/$', AlumnosList_view, name='inscritos'),
    url(r'^participantes.data/', views.ListaParticipantes, name='participantes'),
    url(r'^cupos.data/', views.Cupos, name='cupos'),

	# registro de resultados por parte de los usuarios participantes
	url(r'^registroFaseGrupos/$', login_required(RegistroFaseGruposView), name='registroFaseGrupos'),
	url(r'^registroOctavos/$', login_required(RegistroOctavosView), name='registroOctavos'),
	url(r'^registroCuartos/$', login_required(RegistroFaseCuartosView), name='registroCuartos'),
	url(r'^registroSemifinales/$', login_required(RegistroFaseSemifinalesView), name='registroSemifinales'),
	url(r'^registroFinales/$', login_required(RegistroFaseFinalView), name='registroFinales'),
	url(r'^verFaseGrupos/$', login_required(verFaseGruposView), name='verFaseGrupos'),

	# registro de resultados por parte del adminstrador
	url(r'^PrincipalRegistroResultados/$', login_required(RegistroResultadosAdminView), name='PrincipalRegistroResultados'),
	url(r'^registroFaseGruposAdmin/$', login_required(RegistroFaseGruposAdminView), name='registroFaseGruposAdmin'),
	url(r'^registroOctavosAdmin/$', login_required(RegistroOctavosAdminView), name='registroOctavosAdmin'),
	url(r'^registroCuartosAdmin/$', login_required(RegistroFaseCuartosAdminView), name='registroCuartosAdmin'),
	url(r'^registroSemifinalesAdmin/$', login_required(RegistroFaseSemifinalesAdminView), name='registroSemifinalesAdmin'),
	url(r'^registroFinalesAdmin/$', login_required(RegistroFaseFinalAdminView), name='registroFinalesAdmin'),

]