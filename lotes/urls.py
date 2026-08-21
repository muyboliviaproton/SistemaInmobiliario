from django.urls import path

from . import views


app_name = 'lotes'


urlpatterns = [

    # ========================================================
    # LISTADO
    # ========================================================

    path(
        '',
        views.lote_lista,
        name='lote_lista'
    ),

    # ========================================================
    # CREAR
    # ========================================================

    path(
        'nuevo/',
        views.lote_crear,
        name='lote_crear'
    ),

    # ========================================================
    # DETALLE
    # ========================================================

    path(
        '<int:lote_id>/',
        views.lote_detalle,
        name='lote_detalle'
    ),

    # ========================================================
    # EDITAR
    # ========================================================

    path(
        '<int:lote_id>/editar/',
        views.lote_editar,
        name='lote_editar'
    ),

    # ========================================================
    # BAJA LÓGICA
    # ========================================================

    path(
        '<int:lote_id>/eliminar/',
        views.lote_eliminar,
        name='lote_eliminar'
    ),

    # ========================================================
    # RESTAURAR
    # SOLO MASTER
    # ========================================================

    path(
        '<int:lote_id>/restaurar/',
        views.lote_restaurar,
        name='lote_restaurar'
    ),

    # ========================================================
    # ELIMINACIÓN DEFINITIVA
    # SOLO MASTER
    # ========================================================

    path(
        '<int:lote_id>/eliminar-definitivamente/',
        views.lote_eliminar_definitivo,
        name='lote_eliminar_definitivo'
    ),

    # ========================================================
    # RESERVAR
    # ========================================================

    path(
        '<int:lote_id>/reservar/',
        views.lote_reservar,
        name='lote_reservar'
    ),

    # ========================================================
    # LIBERAR RESERVA
    # ========================================================

    path(
        '<int:lote_id>/liberar-reserva/',
        views.lote_liberar_reserva,
        name='lote_liberar_reserva'
    ),

    # ========================================================
    # AUTORIZAR A OTRO ASESOR
    # ========================================================

    path(
        '<int:lote_id>/autorizar/',
        views.lote_autorizar,
        name='lote_autorizar'
    ),

    # ========================================================
    # REVOCAR AUTORIZACIÓN
    # ========================================================

    path(
        'autorizacion/<int:autorizacion_id>/revocar/',
        views.lote_revocar_autorizacion,
        name='lote_revocar_autorizacion'
    ),
]