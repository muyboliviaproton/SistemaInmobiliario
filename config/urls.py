
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


def inicio(request):
    return redirect('login')


urlpatterns = [
# ========================================================
# ADMIN
# ========================================================
    path(
        'admin/',
        admin.site.urls
    ),
# ========================================================
# ACCOUNTS
# LOGIN / LOGOUT / DASHBOARDS
# ========================================================
    path(
        'accounts/',
        include('accounts.urls')
    ),
# ========================================================
# CLIENTES
# ========================================================

    path(
        'clientes/',
        include('clientes.urls')
    ),


# ========================================================
# INICIO
# ========================================================
    path(
        '',
        inicio,
        name='inicio'
    ),

# ========================================================
# SEGUIMIENTOS DE CLIENTES
# ========================================================
path(
    'seguimientos/',
    include('gestion_seguimientos.urls')
),

# ========================================================
# OPORTUNIDADES COMERCIALES
# ========================================================

path(
    'oportunidades/',
    include('oportunidades.urls')
),

# ========================================================
# VISITAS
# ========================================================

path(
    'visitas/',
    include('visitas.urls')
),

]