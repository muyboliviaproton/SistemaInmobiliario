from django.urls import path

from .views import (
    LoginUsuarioView,
    LogoutUsuarioView,
    inicio_accounts,
    dashboard,
    dashboard_master,
    dashboard_asesor,
    usuarios_lista,
    usuario_crear,
    usuario_editar,
    usuario_cambiar_estado,
    usuario_clientes,
    usuario_reasignar_clientes,
    usuario_cambiar_password,
)

urlpatterns = [

    # ========================================================
    # INICIO DE ACCOUNTS
    # ========================================================

    path(
        '',
        inicio_accounts,
        name='accounts_inicio'
    ),


    # ========================================================
    # LOGIN
    # ========================================================

    path(
        'login/',
        LoginUsuarioView.as_view(),
        name='login'
    ),


    # ========================================================
    # LOGOUT
    # ========================================================

    path(
        'logout/',
        LogoutUsuarioView.as_view(),
        name='logout'
    ),


    # ========================================================
    # DASHBOARD GENERAL
    # Detecta automáticamente MASTER o ASESOR
    # ========================================================

    path(
        'dashboard/',
        dashboard,
        name='dashboard'
    ),


    # ========================================================
    # DASHBOARD MASTER
    # ========================================================

    path(
        'dashboard/master/',
        dashboard_master,
        name='dashboard_master'
    ),


    # ========================================================
    # DASHBOARD ASESOR
    # ========================================================

    path(
        'dashboard/asesor/',
        dashboard_asesor,
        name='dashboard_asesor'
    ),
    # ========================================================
    # GESTIÓN DE USUARIOS / ASESORES
    # SOLO MASTER
    # ========================================================

    path(
        'usuarios/',
        usuarios_lista,
        name='usuarios_lista'
    ),
    # ========================================================
      # CREAR USUARIOS / ASESORES
      # SOLO MASTER
      # ========================================================
    path(
    'usuarios/nuevo/',
    usuario_crear,
    name='usuario_crear'
),
    # ========================================================
    # EDITAR USUARIOS / ASESORES
    # SOLO MASTER
    # ========================================================
    path(
    'usuarios/<int:pk>/editar/',
    usuario_editar,
    name='usuario_editar'
),
# ========================================================
# CAMBIAR ESTADO DE USUARIOS / ASESORES
# SOLO MASTER
# ========================================================

path(
    'usuarios/<int:pk>/cambiar-estado/',
    usuario_cambiar_estado,
    name='usuario_cambiar_estado'
),
# ========================================================
# VER CLIENTES DE UN USUARIO / ASESOR
# SOLO MASTER
# ========================================================
path(
    'usuarios/<int:pk>/clientes/',
    usuario_clientes,
    name='usuario_clientes'
),

# ========================================================
# REASIGNAR CLIENTES DE UN USUARIO / ASESOR
# SOLO MASTER
# ========================================================
path(
    'usuarios/<int:pk>/clientes/reasignar/',
    usuario_reasignar_clientes,
    name='usuario_reasignar_clientes'
),
# ========================================================
# CAMBIAR CONTRASEÑA DE USUARIO / ASESOR
# SOLO MASTER
# ========================================================

path(
    'usuarios/<int:pk>/cambiar-password/',
    usuario_cambiar_password,
    name='usuario_cambiar_password'
),

]