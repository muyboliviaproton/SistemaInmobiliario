from django.urls import path
from . import views

app_name = 'gestion_seguimientos'

urlpatterns = [
    # ============================================================
    # INICIO DE SEGUIMIENTOS
    # ============================================================
    path(
        '',
        views.inicio_seguimientos,
        name='inicio_seguimientos'
    ),
        # ============================================================
    # DASHBOARD COMERCIAL
    # ============================================================
        path(
        'dashboard/',
        views.dashboard_comercial,
        name='dashboard_comercial'
    ),
    # ============================================================
    # LISTA DE SEGUIMIENTOS DE UN CLIENTE
    # ============================================================
    path(
        '<int:cliente_id>/',
        views.seguimiento_lista,
        name='seguimiento_lista'
    ),


    # ============================================================
    # CREAR NUEVO SEGUIMIENTO
    # ============================================================

    path(
        '<int:cliente_id>/nuevo/',
        views.seguimiento_crear,
        name='seguimiento_crear'
    ),


    # ============================================================
    # EDITAR SEGUIMIENTO
    # ============================================================

    path(
        '<int:seguimiento_id>/editar/',
        views.seguimiento_editar,
        name='seguimiento_editar'
    ),


    # ============================================================
    # ELIMINAR SEGUIMIENTO
    # ============================================================

    path(
        '<int:seguimiento_id>/eliminar/',
        views.seguimiento_eliminar,
        name='seguimiento_eliminar'
    ),
    # ============================================================
    # AGENDA DE SEGUIMIENTOS
    # ============================================================
    path(
        'agenda/',
        views.agenda_seguimientos,
        name='agenda_seguimientos'
    ),

]