from django.urls import path

from . import views

app_name = 'visitas'

urlpatterns = [

    # ========================================================
    # LISTA
    # ========================================================

    path(
        '',
        views.visita_lista,
        name='visita_lista'
    ),

    # ========================================================
    # CREAR
    # ========================================================

    path(
        'nueva/<int:oportunidad_id>/',
        views.visita_crear,
        name='visita_crear'
    ),

    # ========================================================
    # DETALLE
    # ========================================================

    path(
        '<int:visita_id>/',
        views.visita_detalle,
        name='visita_detalle'
    ),

    # ========================================================
    # EDITAR
    # ========================================================

    path(
        '<int:visita_id>/editar/',
        views.visita_editar,
        name='visita_editar'
    ),

    # ========================================================
    # ELIMINAR
    # ========================================================

    path(
        '<int:visita_id>/eliminar/',
        views.visita_eliminar,
        name='visita_eliminar'
    ),

]