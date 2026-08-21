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
    # CREAR VISITA DESDE LA LISTA
    # ========================================================

    path(
        'nueva/',
        views.visita_nueva,
        name='visita_nueva'
    ),

    # ========================================================
    # CREAR VISITA DESDE UNA OPORTUNIDAD
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
    # REALIZAR VISITA
    # ========================================================

    path(
        '<int:visita_id>/realizar/',
        views.visita_realizar,
        name='visita_realizar'
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