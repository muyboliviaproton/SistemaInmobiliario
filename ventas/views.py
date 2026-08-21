from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from oportunidades.models import Oportunidad

from .forms import VisitaForm
from .models import Visita


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def usuario_es_master(user):
    """
    Determina si el usuario pertenece al grupo MASTER.
    """
    return user.groups.filter(
        name='MASTER'
    ).exists()


def oportunidad_actualizar_etapa(oportunidad):
    """
    Sincroniza automáticamente la etapa de una oportunidad
    según las visitas que tenga relacionadas.

    IMPORTANTE:
    No modifica oportunidades:
        - VENTA_CERRADA
        - PERDIDA
    """

    if not oportunidad:
        return

    # --------------------------------------------------------
    # NO MODIFICAR OPORTUNIDADES CERRADAS
    # --------------------------------------------------------

    if oportunidad.etapa in [
        'VENTA_CERRADA',
        'PERDIDA'
    ]:
        return

    # --------------------------------------------------------
    # BUSCAR VISITAS RELACIONADAS
    # --------------------------------------------------------
    visitas = oportunidad.visitas.all()
    # --------------------------------------------------------
    # ¿EXISTE UNA VISITA REALIZADA?
    # --------------------------------------------------------
    existe_realizada = visitas.filter(
        estado='REALIZADA'
    ).exists()

    # --------------------------------------------------------
    # ¿EXISTE UNA VISITA PENDIENTE O CONFIRMADA?
    # --------------------------------------------------------
    existe_pendiente = visitas.filter(
        estado__in=[
            'PENDIENTE',
            'CONFIRMADA'
        ]
    ).exists()

    # --------------------------------------------------------
    # DETERMINAR NUEVA ETAPA
    # --------------------------------------------------------

    if existe_pendiente:
        nueva_etapa = 'VISITA_PENDIENTE'
    elif existe_realizada:
        nueva_etapa = 'VISITA_REALIZADA'
    else:
        # Si ya no existen visitas activas,
        # regresamos a INTERESADO.
        nueva_etapa = 'INTERESADO'

    # --------------------------------------------------------
    # ACTUALIZAR SOLAMENTE SI CAMBIÓ
    # --------------------------------------------------------

    if oportunidad.etapa != nueva_etapa:
        oportunidad.etapa = nueva_etapa
        oportunidad.save(
            update_fields=[
                'etapa',
                'actualizado_en'
            ]
        )


# ============================================================
# LISTA DE VISITAS
# ============================================================

@login_required
def visita_lista(request):

    # ========================================================
    # VERIFICAR MASTER
    # ========================================================

    es_master = usuario_es_master(
        request.user
    )

    # ========================================================
    # FILTRAR VISITAS POR USUARIO
    # ========================================================

    if es_master:

        visitas = Visita.objects.all()

    else:

        visitas = Visita.objects.filter(
            asesor=request.user
        )

    # ========================================================
    # FILTRO OPCIONAL POR ESTADO
    # ========================================================

    estado_filtro = request.GET.get(
        'estado'
    )

    estados_validos = [
        'PENDIENTE',
        'CONFIRMADA',
        'REALIZADA',
        'CANCELADA',
    ]

    if estado_filtro in estados_validos:

        visitas = visitas.filter(
            estado=estado_filtro
        )

    # ========================================================
    # CONTADORES
    #
    # Se calculan antes del filtro para mostrar siempre
    # el resumen completo.
    # ========================================================

    if es_master:

        todas_las_visitas = Visita.objects.all()

    else:

        todas_las_visitas = Visita.objects.filter(
            asesor=request.user
        )

    total_visitas = todas_las_visitas.count()

    visitas_pendientes = todas_las_visitas.filter(
        estado='PENDIENTE'
    ).count()

    visitas_confirmadas = todas_las_visitas.filter(
        estado='CONFIRMADA'
    ).count()

    visitas_realizadas = todas_las_visitas.filter(
        estado='REALIZADA'
    ).count()

    visitas_canceladas = todas_las_visitas.filter(
        estado='CANCELADA'
    ).count()

    # ========================================================
    # OPTIMIZAR CONSULTA
    # ========================================================

    visitas = visitas.select_related(
        'cliente',
        'asesor',
        'oportunidad',
    ).order_by(
        'fecha',
        'hora'
    )

    # ========================================================
    # TÍTULO DEL FILTRO
    # ========================================================

    nombres_filtro = {

        'PENDIENTE':
            'Visitas pendientes',

        'CONFIRMADA':
            'Visitas confirmadas',

        'REALIZADA':
            'Visitas realizadas',

        'CANCELADA':
            'Visitas canceladas',
    }

    titulo_filtro = nombres_filtro.get(
        estado_filtro,
        'Todas las visitas'
    )

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'visitas':
            visitas,

        'es_master':
            es_master,

        'total_visitas':
            total_visitas,

        'visitas_pendientes':
            visitas_pendientes,

        'visitas_confirmadas':
            visitas_confirmadas,

        'visitas_realizadas':
            visitas_realizadas,

        'visitas_canceladas':
            visitas_canceladas,

        'estado_filtro':
            estado_filtro,

        'titulo_filtro':
            titulo_filtro,
    }

    return render(
        request,
        'visitas/visita_lista.html',
        contexto
    )

# ============================================================
# NUEVA VISITA DESDE LA LISTA
# ============================================================

@login_required
def visita_nueva(request):

    # ========================================================
    # VERIFICAR SI ES MASTER
    # ========================================================

    es_master = usuario_es_master(
        request.user
    )

    # ========================================================
    # OBTENER OPORTUNIDADES DISPONIBLES
    # ========================================================

    if es_master:

        oportunidades = Oportunidad.objects.select_related(
            'cliente',
            'asesor'
        ).all()

    else:

        oportunidades = Oportunidad.objects.select_related(
            'cliente',
            'asesor'
        ).filter(
            asesor=request.user
        )

    # ========================================================
    # PROCESAR SELECCIÓN
    # ========================================================

    if request.method == 'POST':

        oportunidad_id = request.POST.get(
            'oportunidad'
        )

        # ----------------------------------------------------
        # VALIDAR SELECCIÓN
        # ----------------------------------------------------

        if not oportunidad_id:

            messages.error(
                request,
                'Debe seleccionar una oportunidad comercial.'
            )

        else:

            # ------------------------------------------------
            # BUSCAR OPORTUNIDAD PERMITIDA
            # ------------------------------------------------

            oportunidad = get_object_or_404(
                oportunidades,
                id=oportunidad_id
            )

            # ------------------------------------------------
            # IR AL FORMULARIO DE VISITA
            # ------------------------------------------------

            return redirect(
                'visitas:visita_crear',
                oportunidad_id=oportunidad.id
            )

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'oportunidades': oportunidades,

        'es_master': es_master,

    }

    return render(
        request,
        'visitas/visita_nueva.html',
        contexto
    )


# ============================================================
# CREAR VISITA
# ============================================================

@login_required
def visita_crear(request, oportunidad_id):

    # ========================================================
    # VERIFICAR SI ES MASTER
    # ========================================================

    es_master = usuario_es_master(
        request.user
    )

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
    # VALIDAR ACCESO
    # ========================================================

    if not es_master:

        if oportunidad.asesor != request.user:

            return render(
                request,
                'clientes/cliente_no_disponible.html',
                {
                    'cliente': oportunidad.cliente,
                },
                status=403
            )

    # ========================================================
    # CLIENTE
    # ========================================================

    cliente = oportunidad.cliente

    # ========================================================
    # PROCESAR FORMULARIO
    # ========================================================

    if request.method == 'POST':

        form = VisitaForm(
            request.POST
        )

        if form.is_valid():

            # ------------------------------------------------
            # CREAR VISITA
            # ------------------------------------------------

            visita = form.save(
                commit=False
            )

            # ------------------------------------------------
            # ASIGNAR RELACIONES
            # ------------------------------------------------
            visita.cliente = cliente
            visita.oportunidad = oportunidad
            visita.asesor = request.user
            # ------------------------------------------------
            # TODA NUEVA VISITA COMIENZA PENDIENTE
            # ------------------------------------------------
            visita.estado = 'PENDIENTE'
            # ------------------------------------------------
            # GUARDAR
            # ------------------------------------------------
            visita.save()
            # ------------------------------------------------
            # REACTIVAR OPORTUNIDAD PERDIDA
            # ------------------------------------------------
            if oportunidad.etapa == 'PERDIDA':
                oportunidad.etapa = 'VISITA_PENDIENTE'
                oportunidad.save(
                    update_fields=[
                        'etapa',
                        'actualizado_en'
                    ]
                )

            else:

                oportunidad_actualizar_etapa(
                    oportunidad
                )
            # ------------------------------------------------
            # ACTUALIZAR ETAPA DE OPORTUNIDAD
            # ------------------------------------------------
            oportunidad_actualizar_etapa(
                oportunidad
            )

            # ------------------------------------------------
            # MENSAJE
            # ------------------------------------------------

            messages.success(
                request,
                'La visita fue agendada correctamente.'
            )

            # ------------------------------------------------
            # VOLVER A VISITAS
            # ------------------------------------------------

            return redirect(
                'visitas:visita_lista'
            )

    else:

        form = VisitaForm(
            initial={
                'estado': 'PENDIENTE'
            }
        )

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
# DETALLE DE VISITA
# ============================================================

@login_required
def visita_detalle(request, visita_id):

    # ========================================================
    # BUSCAR VISITA
    # ========================================================

    visita = get_object_or_404(
        Visita.objects.select_related(
            'cliente',
            'asesor',
            'oportunidad'
        ),
        id=visita_id
    )

    # ========================================================
    # VERIFICAR MASTER
    # ========================================================

    es_master = usuario_es_master(
        request.user
    )

    # ========================================================
    # VALIDAR ACCESO
    # ========================================================

    if not es_master:

        if visita.asesor != request.user:

            return render(
                request,
                'clientes/cliente_no_disponible.html',
                {
                    'cliente': visita.cliente,
                },
                status=403
            )

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'visita': visita,

        'es_master': es_master,

    }

    return render(
        request,
        'visitas/visita_detalle.html',
        contexto
    )


# ============================================================
# EDITAR VISITA
# ============================================================

@login_required
def visita_editar(request, visita_id):

    # ========================================================
    # BUSCAR VISITA
    # ========================================================

    visita = get_object_or_404(
        Visita.objects.select_related(
            'cliente',
            'asesor',
            'oportunidad'
        ),
        id=visita_id
    )

    # ========================================================
    # VERIFICAR MASTER
    # ========================================================

    es_master = usuario_es_master(
        request.user
    )

    # ========================================================
    # VALIDAR ACCESO
    # ========================================================

    if not es_master:

        if visita.asesor != request.user:

            return render(
                request,
                'clientes/cliente_no_disponible.html',
                {
                    'cliente': visita.cliente,
                },
                status=403
            )

    # ========================================================
    # NO EDITAR VISITA REALIZADA
    # ========================================================

    if visita.estado == 'REALIZADA':

        messages.warning(
            request,
            'Una visita realizada debe modificarse desde el registro de resultado.'
        )

        return redirect(
            'visitas:visita_detalle',
            visita_id=visita.id
        )

    # ========================================================
    # PROCESAR FORMULARIO
    # ========================================================

    if request.method == 'POST':

        form = VisitaForm(
            request.POST,
            instance=visita
        )

        if form.is_valid():

            visita_actualizada = form.save(
                commit=False
            )

            # ------------------------------------------------
            # PROTEGER RELACIONES
            # ------------------------------------------------

            visita_actualizada.cliente = visita.cliente

            visita_actualizada.oportunidad = visita.oportunidad

            visita_actualizada.asesor = visita.asesor

            # ------------------------------------------------
            # PROTEGER ESTADO
            # ------------------------------------------------

            # El estado puede ser cambiado mediante el
            # formulario, pero después sincronizamos
            # la oportunidad.
            # ------------------------------------------------

            visita_actualizada.save()

            # ------------------------------------------------
            # SINCRONIZAR OPORTUNIDAD
            # ------------------------------------------------

            oportunidad_actualizar_etapa(
                visita.oportunidad
            )

            # ------------------------------------------------
            # MENSAJE
            # ------------------------------------------------

            messages.success(
                request,
                'La visita fue actualizada correctamente.'
            )

            return redirect(
                'visitas:visita_detalle',
                visita_id=visita.id
            )

    else:

        form = VisitaForm(
            instance=visita
        )

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'form': form,

        'visita': visita,

        'cliente': visita.cliente,

        'oportunidad': visita.oportunidad,

        'es_master': es_master,

    }

    return render(
        request,
        'visitas/visita_editar.html',
        contexto
    )


# ============================================================
# REALIZAR VISITA
# ============================================================

@login_required
def visita_realizar(request, visita_id):

    # ========================================================
    # BUSCAR VISITA
    # ========================================================

    visita = get_object_or_404(
        Visita.objects.select_related(
            'cliente',
            'asesor',
            'oportunidad'
        ),
        id=visita_id
    )

    # ========================================================
    # VERIFICAR MASTER
    # ========================================================

    es_master = usuario_es_master(
        request.user
    )

    # ========================================================
    # VALIDAR ACCESO
    # ========================================================

    if not es_master:

        if visita.asesor != request.user:

            return render(
                request,
                'clientes/cliente_no_disponible.html',
                {
                    'cliente': visita.cliente,
                },
                status=403
            )

    # ========================================================
    # VALIDAR ESTADO
    # ========================================================

    if visita.estado == 'REALIZADA':

        messages.info(
            request,
            'Esta visita ya fue registrada como realizada.'
        )

        return redirect(
            'visitas:visita_detalle',
            visita_id=visita.id
        )

    # ========================================================
    # NO PERMITIR REALIZAR VISITA CANCELADA
    # ========================================================

    if visita.estado == 'CANCELADA':

        messages.warning(
            request,
            'Una visita cancelada no puede registrarse como realizada.'
        )

        return redirect(
            'visitas:visita_detalle',
            visita_id=visita.id
        )

    # ========================================================
    # PROCESAR RESULTADO
    # ========================================================

    if request.method == 'POST':

        # ----------------------------------------------------
        # RESULTADO
        # ----------------------------------------------------

        resultado = request.POST.get(
            'resultado',
            ''
        ).strip()

        # ----------------------------------------------------
        # OBSERVACIONES
        # ----------------------------------------------------

        observaciones = request.POST.get(
            'observaciones',
            ''
        ).strip()

        # ----------------------------------------------------
        # VALIDAR RESULTADO
        # ----------------------------------------------------

        if not resultado:

            messages.error(
                request,
                'Debe registrar el resultado de la visita.'
            )

            contexto = {

                'visita': visita,

                'cliente': visita.cliente,

                'oportunidad': visita.oportunidad,

                'es_master': es_master,

            }

            return render(
                request,
                'visitas/visita_realizar.html',
                contexto
            )

        # ----------------------------------------------------
        # GUARDAR RESULTADO
        # ----------------------------------------------------

        visita.resultado = resultado

        visita.observaciones = observaciones

        visita.estado = 'REALIZADA'

        visita.save()

        # ----------------------------------------------------
        # ACTUALIZAR OPORTUNIDAD
        # ----------------------------------------------------

        oportunidad_actualizar_etapa(
            visita.oportunidad
        )

        # ----------------------------------------------------
        # MENSAJE
        # ----------------------------------------------------

        messages.success(
            request,
            'La visita fue registrada como realizada correctamente.'
        )

        # ----------------------------------------------------
        # VOLVER AL DETALLE
        # ----------------------------------------------------

        return redirect(
            'visitas:visita_detalle',
            visita_id=visita.id
        )

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'visita': visita,

        'cliente': visita.cliente,

        'oportunidad': visita.oportunidad,

        'es_master': es_master,

    }

    return render(
        request,
        'visitas/visita_realizar.html',
        contexto
    )


# ============================================================
# ELIMINAR VISITA
# ============================================================

@login_required
def visita_eliminar(request, visita_id):

    # ========================================================
    # BUSCAR VISITA
    # ========================================================

    visita = get_object_or_404(
        Visita.objects.select_related(
            'cliente',
            'asesor',
            'oportunidad'
        ),
        id=visita_id
    )

    # ========================================================
    # VERIFICAR MASTER
    # ========================================================

    es_master = usuario_es_master(
        request.user
    )

    # ========================================================
    # VALIDAR ACCESO
    # ========================================================

    if not es_master:

        if visita.asesor != request.user:

            return render(
                request,
                'clientes/cliente_no_disponible.html',
                {
                    'cliente': visita.cliente,
                },
                status=403
            )

    # ========================================================
    # ELIMINAR
    # ========================================================

    if request.method == 'POST':

        # ----------------------------------------------------
        # GUARDAR OPORTUNIDAD ANTES DE ELIMINAR
        # ----------------------------------------------------

        oportunidad = visita.oportunidad

        # ----------------------------------------------------
        # ELIMINAR VISITA
        # ----------------------------------------------------

        visita.delete()

        # ----------------------------------------------------
        # SINCRONIZAR OPORTUNIDAD
        # ----------------------------------------------------

        oportunidad_actualizar_etapa(
            oportunidad
        )

        # ----------------------------------------------------
        # MENSAJE
        # ----------------------------------------------------

        messages.success(
            request,
            'La visita fue eliminada correctamente.'
        )

        # ----------------------------------------------------
        # VOLVER A VISITAS
        # ----------------------------------------------------

        return redirect(
            'visitas:visita_lista'
        )

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {
        'visita': visita,
        'cliente': visita.cliente,
        'oportunidad': visita.oportunidad,
        'es_master': es_master,
    }

    return render(
        request,
        'visitas/visita_confirmar_eliminar.html',
        contexto
    )