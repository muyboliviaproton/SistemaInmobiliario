from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from clientes.models import Cliente
from gestion_seguimientos.models import Seguimiento
from oportunidades.models import Oportunidad
from visitas.models import Visita

from django.utils import timezone


@login_required
def dashboard(request):

    hoy = timezone.localdate()

    contexto = {

        "fecha": hoy,

        "total_clientes": Cliente.objects.filter(
            eliminado=False
        ).count(),

        "total_seguimientos": Seguimiento.objects.count(),

        "total_oportunidades": Oportunidad.objects.count(),

        "total_visitas": Visita.objects.count(),

        "total_recordatorios": 0,

        "total_lotes": 0,

        "agenda_semana": 0,

        "pendientes_hoy": 0,

    }

    return render(

        request,

        "dashboard/dashboard.html",

        contexto

    )