from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from clientes.models import Cliente
from gestion_seguimientos.models import Seguimiento
from oportunidades.models import Oportunidad
from visitas.models import Visita


# ============================================================
# OBTENER ROL DEL USUARIO
# ============================================================

def obtener_rol_usuario(usuario):

    if usuario.groups.filter(name='MASTER').exists():
        return 'MASTER'

    elif usuario.groups.filter(name='ASESOR').exists():
        return 'ASESOR'

    return None
# ============================================================
# DASHBOARD
# ============================================================
@login_required
def dashboard(request):

    usuario = request.user

    rol = obtener_rol_usuario(usuario)
    # ========================================================
    # FILTRO SEGÚN USUARIO
    # ========================================================
    if rol == 'MASTER':

        clientes = Cliente.objects.filter(
            eliminado=False
        )

        seguimientos = Seguimiento.objects.all()
        oportunidades = Oportunidad.objects.all()
        visitas = Visita.objects.all()

    elif rol == 'ASESOR':

        clientes = Cliente.objects.filter(
            asesor=usuario,
            eliminado=False
        )

        seguimientos = Seguimiento.objects.filter(
            asesor=usuario
        )

        oportunidades = Oportunidad.objects.filter(
            asesor=usuario
        )

        visitas = Visita.objects.filter(
            asesor=usuario
        )


    else:

        # Usuario sin rol definido
        clientes = Cliente.objects.none()
        seguimientos = Seguimiento.objects.none()
        oportunidades = Oportunidad.objects.none()
        visitas = Visita.objects.none()
    # ========================================================
    # TOTALES
    # ========================================================
    total_clientes = clientes.count()
    total_seguimientos = seguimientos.count()
    total_oportunidades = oportunidades.count()
    total_visitas = visitas.count()
    # ========================================================
    # DATOS TEMPORALES
    # ========================================================
    # Estos campos los vamos a conectar más adelante con
    # Agenda de la Semana y Pendientes de Hoy.
    #
    # No estamos utilizando Recordatorio ni Lote todavía.
    #

    agenda_semana = 0
    pendientes_hoy = 0

    # ========================================================
    # CONTEXTO
    # ========================================================
    contexto = {
        'usuario': usuario,
        'rol': rol,
        'es_master': rol == 'MASTER',
        'es_asesor': rol == 'ASESOR',
        'total_clientes': total_clientes,
        'total_seguimientos': total_seguimientos,
        'total_oportunidades': total_oportunidades,
        'total_visitas': total_visitas,
        'agenda_semana': agenda_semana,
        'pendientes_hoy': pendientes_hoy,
    }

    # ========================================================
    # RENDER
    # ========================================================
    return render(
        request,
        'dashboard/dashboard.html',
        contexto
    )