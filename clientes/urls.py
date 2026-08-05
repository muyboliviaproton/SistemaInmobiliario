from django.urls import path

from .views import (
    cliente_lista,
    cliente_crear,
    cliente_detalle,
    cliente_editar,
    cliente_eliminar,
    papelera_clientes,
    restaurar_cliente,
    reasignar_cliente,
    eliminar_definitivamente,
)


app_name = 'clientes'


urlpatterns = [

    # ========================================================
    # CLIENTES
    # ========================================================

    path(
        '',
        cliente_lista,
        name='cliente_lista'
    ),

    path(
        'nuevo/',
        cliente_crear,
        name='cliente_crear'
    ),

    path(
        '<int:pk>/',
        cliente_detalle,
        name='cliente_detalle'
    ),

    path(
        '<int:pk>/editar/',
        cliente_editar,
        name='cliente_editar'
    ),

    # ========================================================
    # ELIMINAR → PAPELERA
    # SOLO MASTER
    # ========================================================

    path(
        '<int:pk>/eliminar/',
        cliente_eliminar,
        name='cliente_eliminar'
    ),

    # ========================================================
    # PAPELERA
    # SOLO MASTER
    # ========================================================

    path(
        'papelera/',
        papelera_clientes,
        name='papelera_clientes'
    ),

    # ========================================================
    # RESTAURAR CLIENTE
    # SOLO MASTER
    # ========================================================

    path(
        '<int:pk>/restaurar/',
        restaurar_cliente,
        name='restaurar_cliente'
    ),

    # ========================================================
    # RESIGNAR CLIENTE A NUEVO ASESOR
    # SOLO MASTER
    # ========================================================
    path(
            '<int:pk>/reasignar/',
            reasignar_cliente,
            name='reasignar_cliente'
    ),
    # ========================================================
    # ELIMINAR DEFINITIVAMENTE
    # SOLO MASTER
    # ========================================================
        
    path(
                '<int:pk>/eliminar-definitivamente/',
                eliminar_definitivamente,
                name='eliminar_definitivamente'
    ),

]