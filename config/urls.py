from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def inicio(request):
    return redirect('login')

urlpatterns = [
# ========================================================
# Rutas
# ========================================================
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('clientes/', include('clientes.urls')),
    path('', inicio, name='inicio'),
    path('seguimientos/', include('gestion_seguimientos.urls')),
    path('oportunidades/', include('oportunidades.urls')),
    path('visitas/', include('visitas.urls')),
    path('dashboard/', include('dashboard.urls')),

]