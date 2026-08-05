from django.urls import path
from . import views

app_name = 'oportunidades'

urlpatterns = [
    # ========================================================
    # LISTA GENERAL DE OPORTUNIDADES
    # ========================================================
    path(
        '',
        views.oportunidad_lista,
        name='oportunidad_lista'
    ),
    # ========================================================
    # CREAR OPORTUNIDAD DESDE UN CLIENTE
    # ========================================================

    path(
        'cliente/<int:cliente_id>/nueva/',
        views.oportunidad_crear,
        name='oportunidad_crear'
    ),


    # ========================================================
    # EDITAR OPORTUNIDAD
    # ========================================================

    path(
        '<int:oportunidad_id>/editar/',
        views.oportunidad_editar,
        name='oportunidad_editar'
    ),


    # ========================================================
    # ELIMINAR OPORTUNIDAD
    # ========================================================

    path(
        '<int:oportunidad_id>/eliminar/',
        views.oportunidad_eliminar,
        name='oportunidad_eliminar'
    ),

   # DETALLE DE UNA OPORTUNIDAD
    path(
        '<int:pk>/',
        views.oportunidad_detalle,
        name='oportunidad_detalle'
    ),

]