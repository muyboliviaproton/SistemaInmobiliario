from django.urls import path

from .views import (
    LoginUsuarioView,
    LogoutUsuarioView,
    inicio_accounts,
    usuarios_lista,
    usuario_crear,
    usuario_editar,
    usuario_cambiar_estado,
    usuario_clientes,
    usuario_reasignar_clientes,
    usuario_cambiar_password,
    dashboard_master,
    dashboard_asesor,
)

app_name = 'accounts'

urlpatterns = [
    # ========================================================
    # LOGIN
    # ========================================================
    path('login/',LoginUsuarioView.as_view(),name='login'),
    # ========================================================
    # LOGOUT
    # ========================================================
    path('logout/',LogoutUsuarioView.as_view(),name='logout'),
    # ========================================================
    # INICIO DE ACCOUNTS
    # ========================================================
    path('',inicio_accounts,
        name='inicio_accounts'),
    # ========================================================
    # GESTIÓN DE ASESORES
    # SOLO MASTER
    # ========================================================
    path('usuarios/',
        usuarios_lista,
        name='usuarios_lista'),
    # ========================================================
    # CREAR ASESOR
    # ========================================================
    path('usuarios/crear/',
        usuario_crear,
        name='usuario_crear'),
    # ========================================================
    # EDITAR ASESOR
    # ========================================================
    path('usuarios/<int:pk>/editar/',
        usuario_editar,
        name='usuario_editar'),
    # ========================================================
    # ACTIVAR / DESACTIVAR ASESOR
    # ========================================================
    path('usuarios/<int:pk>/estado/',
        usuario_cambiar_estado,
        name='usuario_cambiar_estado'),
    # ========================================================
    # CLIENTES DEL ASESOR
    # ========================================================
    path('usuarios/<int:pk>/clientes/',
        usuario_clientes,
        name='usuario_clientes'),
    # ========================================================
    # REASIGNAR CLIENTES
    # ========================================================
    path('usuarios/<int:pk>/reasignar-clientes/',
        usuario_reasignar_clientes,
        name='usuario_reasignar_clientes'),
    # ========================================================
    # CAMBIAR CONTRASEÑA
    # ========================================================
    path('usuarios/<int:pk>/cambiar-password/',
        usuario_cambiar_password,
        name='usuario_cambiar_password'),
    # ========================================================
    # DASHBOARD MASTER
    # Estas vistas antiguas las mantenemos temporalmente
    # para no romper las rutas existentes.
    # ========================================================
    path('dashboard/master/',
        dashboard_master,
        name='dashboard_master'),
    # ========================================================
    # DASHBOARD ASESOR
    # ========================================================
    path('dashboard/asesor/',
        dashboard_asesor,
        name='dashboard_asesor'),

    
]