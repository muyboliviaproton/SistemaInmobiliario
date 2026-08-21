from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from clientes.models import Cliente
from visitas.models import Visita

from .forms import OportunidadForm
from .models import Oportunidad


# ============================================================
# FUNCIÓN AUXILIAR
# ============================================================

def usuario_es_master(user):
    """
    Determina si el usuario pertenece al grupo MASTER.
    """

    return user.groups.filter(
        name='MASTER'
    ).exists()


# ============================================================
# LISTA PRINCIPAL DE OPORTUNIDADES
# ============================================================

@login_required
def oportunidad_lista(request):

    es_master = usuario_es_master(
        request.user
    )

    # ========================================================
    # OPORTUNIDADES VISIBLES
    # ========================================================

    if es_master:

        oportunidades = Oportunidad.objects.all()
    else:
        oportunidades = Oportunidad.objects.filter(
            asesor=request.user
        )

    # ========================================================
    # VISITA REALIZADA SE ADMINISTRA DESDE VISITAS
    #
    # Una vez realizada la visita, la oportunidad sale de
    # esta lista principal.
    # ========================================================

    oportunidades = oportunidades.exclude(
        etapa='VISITA_REALIZADA'
    )

    # ========================================================
    # OPTIMIZAR CONSULTA
    # ========================================================

    oportunidades = oportunidades.select_related(
        'cliente',
        'asesor'
    )

    # ========================================================
    # CONTADORES DE OPORTUNIDADES
    # ========================================================

    total_oportunidades = oportunidades.count()

    nuevas = oportunidades.filter(
        etapa='NUEVO'
    ).count()

    contactadas = oportunidades.filter(
        etapa='CONTACTADO'
    ).count()

    interesadas = oportunidades.filter(
        etapa='INTERESADO'
    ).count()

    visitas_pendientes = oportunidades.filter(
        etapa='VISITA_PENDIENTE'
    ).count()

    negociaciones = oportunidades.filter(
        etapa='NEGOCIACION'
    ).count()

    reservas = oportunidades.filter(
        etapa='RESERVA'
    ).count()

    ventas_cerradas = oportunidades.filter(
        etapa='VENTA_CERRADA'
    ).count()

    perdidas = oportunidades.filter(
        etapa='PERDIDA'
    ).count()

    # ========================================================
    # CONTADORES DE VISITAS
    #
    # Estos sirven para mostrar en la página de oportunidades
    # un acceso rápido al módulo de visitas.
    # ========================================================

    if es_master:

        visitas_pendientes_total = Visita.objects.filter(
            estado__in=[
                'PENDIENTE',
                'CONFIRMADA'
            ]
        ).count()

        visitas_realizadas_total = Visita.objects.filter(
            estado='REALIZADA'
        ).count()

    else:

        visitas_pendientes_total = Visita.objects.filter(
            asesor=request.user,
            estado__in=[
                'PENDIENTE',
                'CONFIRMADA'
            ]
        ).count()

        visitas_realizadas_total = Visita.objects.filter(
            asesor=request.user,
            estado='REALIZADA'
        ).count()

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'oportunidades':
            oportunidades,

        'es_master':
            es_master,

        'total_oportunidades':
            total_oportunidades,

        'nuevas':
            nuevas,

        'contactadas':
            contactadas,

        'interesadas':
            interesadas,

        'visitas_pendientes':
            visitas_pendientes,

        'negociaciones':
            negociaciones,

        'reservas':
            reservas,

        'ventas_cerradas':
            ventas_cerradas,

        'perdidas':
            perdidas,

        'visitas_pendientes_total':
            visitas_pendientes_total,

        'visitas_realizadas_total':
            visitas_realizadas_total,
    }

    return render(
        request,
        'oportunidades/oportunidad_lista.html',
        contexto
    )


# ============================================================
# LISTAR OPORTUNIDADES POR ETAPA
# ============================================================

@login_required
def oportunidad_etapa(request, etapa):

    es_master = usuario_es_master(
        request.user
    )

    # ========================================================
    # VALIDAR ETAPA
    # ========================================================

    etapas_validas = dict(
        Oportunidad.ETAPAS
    )

    if etapa not in etapas_validas:

        return redirect(
            'oportunidades:oportunidad_lista'
        )

    # ========================================================
    # FILTRAR OPORTUNIDADES
    # ========================================================

    if es_master:

        oportunidades = Oportunidad.objects.filter(
            etapa=etapa
        )

    else:

        oportunidades = Oportunidad.objects.filter(
            asesor=request.user,
            etapa=etapa
        )

    # ========================================================
    # OPTIMIZAR
    # ========================================================

    oportunidades = oportunidades.select_related(
        'cliente',
        'asesor'
    )

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'oportunidades':
            oportunidades,

        'es_master':
            es_master,

        'etapa':
            etapa,

        'etapa_nombre':
            etapas_validas[etapa],

    }

    return render(
        request,
        'oportunidades/oportunidad_etapa.html',
        contexto
    )


# ============================================================
# CREAR OPORTUNIDAD
# ============================================================

@login_required
def oportunidad_crear(request, cliente_id):

    # ========================================================
    # BUSCAR CLIENTE
    # ========================================================

    cliente = get_object_or_404(
        Cliente,
        id=cliente_id,
        eliminado=False
    )

    # ========================================================
    # VERIFICAR MASTER
    # ========================================================

    es_master = usuario_es_master(
        request.user
    )

    # ========================================================
    # ASESOR
    # Solo puede crear oportunidades para sus clientes
    # ========================================================

    if not es_master:

        if cliente.asesor != request.user:

            return render(
                request,
                'clientes/cliente_no_disponible.html',
                {
                    'cliente':
                        cliente,
                },
                status=403
            )

    # ========================================================
    # PROCESAR FORMULARIO
    # ========================================================

    if request.method == 'POST':

        form = OportunidadForm(
            request.POST
        )

        if form.is_valid():

            oportunidad = form.save(
                commit=False
            )

            # ------------------------------------------------
            # RELACIÓN CON CLIENTE
            # ------------------------------------------------

            oportunidad.cliente = cliente

            # ------------------------------------------------
            # ASESOR RESPONSABLE
            # ------------------------------------------------
            #
            # La oportunidad pertenece al usuario que la crea.
            #
            # ------------------------------------------------

            oportunidad.asesor = request.user

            oportunidad.save()

            return redirect(
                'oportunidades:oportunidad_lista'
            )

    else:

        form = OportunidadForm()

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'form':
            form,

        'cliente':
            cliente,

        'es_master':
            es_master,
    }

    return render(
        request,
        'oportunidades/oportunidad_crear.html',
        contexto
    )


# ============================================================
# EDITAR OPORTUNIDAD
# ============================================================

@login_required
def oportunidad_editar(request, oportunidad_id):

    # ========================================================
    # BUSCAR OPORTUNIDAD
    # ========================================================

    oportunidad = get_object_or_404(
        Oportunidad.objects.select_related(
            'cliente',
            'asesor'
        ),
        id=oportunidad_id
    )

    # ========================================================
    # VERIFICAR MASTER
    # ========================================================

    es_master = usuario_es_master(
        request.user
    )

    # ========================================================
    # ASESOR
    # Solo puede editar sus propias oportunidades
    # ========================================================

    if not es_master:

        if oportunidad.asesor != request.user:

            return render(
                request,
                'clientes/cliente_no_disponible.html',
                {
                    'cliente':
                        oportunidad.cliente,
                },
                status=403
            )

    # ========================================================
    # PROCESAR FORMULARIO
    # ========================================================

    if request.method == 'POST':

        form = OportunidadForm(
            request.POST,
            instance=oportunidad
        )

        if form.is_valid():

            oportunidad_actualizada = form.save(
                commit=False
            )

            # =================================================
            # PROTEGER RELACIONES
            # =================================================
            #
            # El formulario no contiene cliente ni asesor,
            # por lo tanto mantenemos explícitamente las
            # relaciones originales.
            #
            # =================================================

            oportunidad_actualizada.cliente = (
                oportunidad.cliente
            )

            oportunidad_actualizada.asesor = (
                oportunidad.asesor
            )

            oportunidad_actualizada.save()

            return redirect(
                'oportunidades:oportunidad_lista'
            )

    else:

        form = OportunidadForm(
            instance=oportunidad
        )

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'form':
            form,

        'oportunidad':
            oportunidad,

        'cliente':
            oportunidad.cliente,

        'es_master':
            es_master,
    }

    return render(
        request,
        'oportunidades/oportunidad_editar.html',
        contexto
    )


# ============================================================
# ELIMINAR OPORTUNIDAD
# ============================================================

@login_required
def oportunidad_eliminar(request, oportunidad_id):

    oportunidad = get_object_or_404(
        Oportunidad,
        id=oportunidad_id
    )

    es_master = usuario_es_master(
        request.user
    )

    # ========================================================
    # VALIDAR PERMISOS
    # ========================================================

    if not es_master:

        if oportunidad.asesor != request.user:

            return render(
                request,
                'clientes/cliente_no_disponible.html',
                {
                    'cliente':
                        oportunidad.cliente,
                },
                status=403
            )

    # ========================================================
    # ELIMINAR
    # ========================================================

    if request.method == 'POST':

        oportunidad.delete()

        return redirect(
            'oportunidades:oportunidad_lista'
        )

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'oportunidad':
            oportunidad,

        'cliente':
            oportunidad.cliente,

        'es_master':
            es_master,
    }

    return render(
        request,
        'oportunidades/oportunidad_confirmar_eliminar.html',
        contexto
    )


# ============================================================
# DETALLE DE OPORTUNIDAD
# ============================================================

@login_required
def oportunidad_detalle(request, pk):

    # ========================================================
    # BUSCAR OPORTUNIDAD
    # ========================================================

    oportunidad = get_object_or_404(
        Oportunidad.objects.select_related(
            'cliente',
            'asesor'
        ),
        id=pk
    )

    # ========================================================
    # VERIFICAR MASTER
    # ========================================================

    es_master = usuario_es_master(
        request.user
    )

    # ========================================================
    # ASESOR
    # Solo puede ver sus propias oportunidades
    # ========================================================

    if not es_master:

        if oportunidad.asesor != request.user:

            return render(
                request,
                'clientes/cliente_no_disponible.html',
                {
                    'cliente':
                        oportunidad.cliente,
                },
                status=403
            )

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'oportunidad':
            oportunidad,

        'es_master':
            es_master,
    }

    return render(
        request,
        'oportunidades/oportunidad_detalle.html',
        contexto
    )