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

	# registro de resultados por parte de los usuarios participantes
	url(r'^registroFaseGrupos/$', login_required(RegistroFaseGruposView), name='registroFaseGrupos'),
	url(r'^registroOctavos/$', login_required(RegistroOctavosView), name='registroOctavos'),
	url(r'^registroCuartos/$', login_required(RegistroFaseCuartosView), name='registroCuartos'),
	url(r'^registroSemifinales/$', login_required(RegistroFaseSemifinalesView), name='registroSemifinales'),
	url(r'^registroFinales/$', login_required(RegistroFaseFinalView), name='registroFinales'),
	url(r'^verFaseGrupos/$', login_required(verFaseGruposView), name='verFaseGrupos'),

	# registro de resultados por parte del adminstrador
	url(r'^PrincipalRegistroResultados/$', login_required(RegistroResultadosAdminView.as_view()), name='PrincipalRegistroResultados'),
	url(r'^registroFaseGruposAdmin/$', login_required(RegistroFaseGruposAdminView), name='registroFaseGruposAdmin'),
	url(r'^registroOctavosAdmin/$', login_required(RegistroOctavosAdminView), name='registroOctavosAdmin'),

]