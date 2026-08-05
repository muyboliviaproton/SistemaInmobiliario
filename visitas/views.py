from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from clientes.models import Cliente
from oportunidades.models import Oportunidad

from .forms import VisitaForm
from .models import Visita

# ============================================================
# LISTA DE VISITAS
# ============================================================

@login_required
def visita_lista(request):

    # ========================================================
    # VERIFICAR SI ES MASTER
    # ========================================================

    es_master = request.user.groups.filter(
        name='MASTER'
    ).exists()


    # ========================================================
    # FILTRAR VISITAS
    # ========================================================

    if es_master:

        visitas = Visita.objects.all()

    else:

        visitas = Visita.objects.filter(
            asesor=request.user
        )


    visitas = visitas.select_related(

        'cliente',

        'asesor',

        'oportunidad',

    )


    contexto = {

        'visitas': visitas,

        'es_master': es_master,

    }


    return render(

        request,

        'visitas/visita_lista.html',

        contexto

    )

# ============================================================
# CREAR VISITA
# ============================================================

@login_required
def visita_crear(request, oportunidad_id):

    # ========================================================
    # BUSCAR OPORTUNIDAD
    # ========================================================

    oportunidad = get_object_or_404(

        Oportunidad,

        id=oportunidad_id

    )


    cliente = oportunidad.cliente


    # ========================================================
    # VERIFICAR SI ES MASTER
    # ========================================================

    es_master = request.user.groups.filter(
        name='MASTER'
    ).exists()


    # ========================================================
    # VALIDAR ACCESO
    # ========================================================

    if not es_master:

        if oportunidad.asesor != request.user:

            return render(

                request,

                'clientes/cliente_no_disponible.html',

                {

                    'cliente': cliente,

                },

                status=403

            )


    # ========================================================
    # GUARDAR
    # ========================================================

    if request.method == 'POST':

        form = VisitaForm(request.POST)

        if form.is_valid():

            visita = form.save(

                commit=False

            )

            visita.cliente = cliente

            visita.oportunidad = oportunidad

            visita.asesor = request.user

            visita.save()

            return redirect(

                'visitas:visita_lista'

            )

    else:

        form = VisitaForm()


    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'form': form,

        'cliente': cliente,

        'oportunidad': oportunidad,

        'es_master': es_master,

    }


    return render(

        request,

        'visitas/visita_crear.html',

        contexto

    )

# ============================================================
# DETALLE
# ============================================================

@login_required
def visita_detalle(request, visita_id):

    return render(
        request,
        'visitas/visita_detalle.html'
    )


# ============================================================
# EDITAR
# ============================================================

@login_required
def visita_editar(request, visita_id):

    return render(
        request,
        'visitas/visita_editar.html'
    )


# ============================================================
# ELIMINAR
# ============================================================

@login_required
def visita_eliminar(request, visita_id):

    return render(
        request,
        'visitas/visita_confirmar_eliminar.html'
    )
