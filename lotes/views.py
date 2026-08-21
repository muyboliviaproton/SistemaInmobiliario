from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render
)
from django.utils import timezone

from .forms import (
    LoteAutorizacionForm,
    LoteForm,
    ReservaLoteForm
)

from .models import (
    Lote,
    LoteAutorizacion,
    Reserva
)


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def usuario_es_master(user):

    return user.groups.filter(
        name='MASTER'
    ).exists()


def usuario_es_asesor(user):

    return user.groups.filter(
        name='ASESOR'
    ).exists()


# ============================================================
# ACTUALIZAR RESERVAS VENCIDAS
# ============================================================

def actualizar_reservas_vencidas():

    ahora = timezone.now()

    reservas = Reserva.objects.filter(
        estado='ACTIVA',
        fecha_vencimiento__isnull=False,
        fecha_vencimiento__lte=ahora
    ).select_related(
        'lote'
    )

    for reserva in reservas:

        reserva.estado = 'VENCIDA'

        reserva.save(
            update_fields=[
                'estado',
                'fecha_actualizacion'
            ]
        )

        lote = reserva.lote

        # ----------------------------------------------------
        # LIBERAR EL LOTE
        # ----------------------------------------------------

        if lote.estado == 'RESERVADO':

            existe_otra_reserva = Reserva.objects.filter(
                lote=lote,
                estado='ACTIVA'
            ).exists()

            if not existe_otra_reserva:

                lote.estado = 'DISPONIBLE'

                lote.save(
                    update_fields=[
                        'estado',
                        'fecha_actualizacion'
                    ]
                )


# ============================================================
# LOTES VISIBLES
# ============================================================

def obtener_lotes_visibles(user):

    actualizar_reservas_vencidas()

    lotes_base = Lote.objects.filter(
        activo=True
    )

    # --------------------------------------------------------
    # MASTER VE TODOS
    # --------------------------------------------------------

    if usuario_es_master(user):

        return lotes_base

    # --------------------------------------------------------
    # LOTES CREADOS POR EL ASESOR
    # --------------------------------------------------------

    propios = lotes_base.filter(
        asesor_creador=user
    )

    # --------------------------------------------------------
    # LOTES AUTORIZADOS
    # --------------------------------------------------------

    autorizados = lotes_base.filter(
        autorizaciones__asesor_autorizado=user,
        autorizaciones__estado='ACTIVA'
    ).exclude(
        asesor_creador=user
    )

    return (
        propios |
        autorizados
    ).distinct()


# ============================================================
# LISTA DE LOTES
# ============================================================

@login_required
def lote_lista(request):

    lotes = obtener_lotes_visibles(
        request.user
    )

    es_master = usuario_es_master(
        request.user
    )

    # --------------------------------------------------------
    # MIS LOTES
    # --------------------------------------------------------

    mis_lotes = lotes.filter(
        asesor_creador=request.user
    )

    # --------------------------------------------------------
    # LOTES AUTORIZADOS
    # --------------------------------------------------------

    lotes_autorizados = lotes.filter(
        autorizaciones__asesor_autorizado=request.user,
        autorizaciones__estado='ACTIVA'
    ).exclude(
        asesor_creador=request.user
    ).distinct()

    contexto = {

        'lotes':
            lotes,

        'mis_lotes':
            mis_lotes,

        'lotes_autorizados':
            lotes_autorizados,

        'es_master':
            es_master,

        'total_lotes':
            lotes.count(),

        'disponibles':
            lotes.filter(
                estado='DISPONIBLE'
            ).count(),

        'reservados':
            lotes.filter(
                estado='RESERVADO'
            ).count(),

        'vendidos':
            lotes.filter(
                estado='VENDIDO'
            ).count(),
    }

    return render(
        request,
        'lotes/lote_lista.html',
        contexto
    )


# ============================================================
# CREAR LOTE
# ============================================================

@login_required
def lote_crear(request):

    # --------------------------------------------------------
    # SOLO MASTER O ASESOR
    # --------------------------------------------------------

    if not (
        usuario_es_master(request.user)
        or usuario_es_asesor(request.user)
    ):

        messages.error(
            request,
            'No tiene autorización para registrar lotes.'
        )

        return redirect(
            'lotes:lote_lista'
        )

    if request.method == 'POST':

        form = LoteForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            lote = form.save(
                commit=False
            )

            # ------------------------------------------------
            # EL ASESOR ACTUAL ES EL CREADOR
            # ------------------------------------------------

            lote.asesor_creador = request.user

            lote.activo = True

            lote.save()

            messages.success(
                request,
                (
                    f'El lote {lote.codigo} '
                    'fue registrado correctamente.'
                )
            )

            return redirect(
                'lotes:lote_lista'
            )

    else:

        form = LoteForm()

    return render(
        request,
        'lotes/lote_crear.html',
        {
            'form': form
        }
    )


# ============================================================
# DETALLE DEL LOTE
# ============================================================

@login_required
def lote_detalle(request, lote_id):

    actualizar_reservas_vencidas()

    lote = get_object_or_404(
        Lote,
        id=lote_id
    )

    es_master = usuario_es_master(
        request.user
    )

    # --------------------------------------------------------
    # ¿ES EL CREADOR?
    # --------------------------------------------------------

    es_creador = (
        lote.asesor_creador ==
        request.user
    )

    # --------------------------------------------------------
    # ¿ESTÁ AUTORIZADO?
    # --------------------------------------------------------

    es_autorizado = LoteAutorizacion.objects.filter(
        lote=lote,
        asesor_autorizado=request.user,
        estado='ACTIVA'
    ).exists()

    # --------------------------------------------------------
    # CONTROL DE ACCESO
    # --------------------------------------------------------

    if (
        not es_master
        and not es_creador
        and not es_autorizado
    ):

        messages.error(
            request,
            'No tiene autorización para ver este lote.'
        )

        return redirect(
            'lotes:lote_lista'
        )

    # --------------------------------------------------------
    # LOTES INACTIVOS
    # --------------------------------------------------------

    if (
        not lote.activo
        and not es_master
    ):

        messages.error(
            request,
            'Este lote se encuentra dado de baja.'
        )

        return redirect(
            'lotes:lote_lista'
        )

    # --------------------------------------------------------
    # RESERVA ACTIVA
    # --------------------------------------------------------

    reserva = lote.reserva_activa

    # --------------------------------------------------------
    # PRIVACIDAD
    #
    # MASTER:
    #   VE TODO
    #
    # ASESOR QUE HIZO LA RESERVA:
    #   VE TODO
    #
    # CREADOR / AUTORIZADO:
    #   VE INFORMACIÓN PÚBLICA
    #   + ASESOR RESPONSABLE
    #   PERO NO CLIENTE NI OBSERVACIÓN
    # --------------------------------------------------------

    mostrar_datos_privados = False

    if es_master:

        mostrar_datos_privados = True

    elif reserva:

        if reserva.asesor == request.user:

            mostrar_datos_privados = True

    # --------------------------------------------------------
    # ASESOR RESPONSABLE DE LA RESERVA
    # --------------------------------------------------------

    asesor_responsable = None

    if reserva:

        asesor_responsable = reserva.asesor

    autorizaciones = lote.autorizaciones.filter(
    estado='ACTIVA'
    ).select_related(
    'asesor_autorizado'
    )

    contexto = {

        'lote':lote,

        'es_master':
            es_master,

        'es_creador':
            es_creador,

        'es_autorizado':
            es_autorizado,

        'reserva':
            reserva,

        'mostrar_datos_privados':
            mostrar_datos_privados,

        'asesor_responsable':
            asesor_responsable,

        'autorizaciones':autorizaciones,    
    }

    return render(
        request,
        'lotes/lote_detalle.html',
        contexto
    )


# ============================================================
# EDITAR LOTE
# ============================================================

@login_required
def lote_editar(request, lote_id):

    lote = get_object_or_404(
        Lote,
        id=lote_id
    )

    es_master = usuario_es_master(
        request.user
    )

    es_creador = (
        lote.asesor_creador ==
        request.user
    )

    # --------------------------------------------------------
    # SOLO MASTER O CREADOR
    # --------------------------------------------------------

    if (
        not es_master
        and not es_creador
    ):

        messages.error(
            request,
            (
                'Solo el MASTER o el asesor creador '
                'pueden editar este lote.'
            )
        )

        return redirect(
            'lotes:lote_detalle',
            lote_id=lote.id
        )

    if request.method == 'POST':

        form = LoteForm(
            request.POST,
            request.FILES,
            instance=lote
        )

        if form.is_valid():

            lote = form.save(
                commit=False
            )

            # ------------------------------------------------
            # El formulario no contiene asesor_creador,
            # por lo tanto conserva automáticamente
            # el asesor creador existente.
            # ------------------------------------------------

            lote.save()

            messages.success(
                request,
                (
                    f'El lote {lote.codigo} '
                    'fue actualizado correctamente.'
                )
            )

            return redirect(
                'lotes:lote_detalle',
                lote_id=lote.id
            )

    else:

        form = LoteForm(
            instance=lote
        )

    return render(
        request,
        'lotes/lote_editar.html',
        {
            'form':
                form,

            'lote':
                lote,

            'es_master':
                es_master,

            'es_creador':
                es_creador,
        }
    )


# ============================================================
# BAJA LÓGICA
# ============================================================

@login_required
def lote_eliminar(request, lote_id):

    lote = get_object_or_404(
        Lote,
        id=lote_id
    )

    es_master = usuario_es_master(
        request.user
    )

    es_creador = (
        lote.asesor_creador ==
        request.user
    )

    # --------------------------------------------------------
    # SOLO MASTER O CREADOR
    # --------------------------------------------------------

    if (
        not es_master
        and not es_creador
    ):

        messages.error(
            request,
            (
                'No tiene autorización para '
                'dar de baja este lote.'
            )
        )

        return redirect(
            'lotes:lote_lista'
        )

    if request.method == 'POST':

        codigo = lote.codigo

        lote.activo = False

        lote.save(
            update_fields=[
                'activo',
                'fecha_actualizacion'
            ]
        )

        messages.success(
            request,
            (
                f'El lote {codigo} '
                'fue dado de baja correctamente.'
            )
        )

        return redirect(
            'lotes:lote_lista'
        )

    return render(
        request,
        'lotes/lote_confirmar_eliminar.html',
        {
            'lote':
                lote
        }
    )


# ============================================================
# RESTAURAR LOTE
# SOLO MASTER
# ============================================================

@login_required
def lote_restaurar(request, lote_id):

    if not usuario_es_master(
        request.user
    ):

        messages.error(
            request,
            'Solo el MASTER puede restablecer lotes.'
        )

        return redirect(
            'lotes:lote_lista'
        )

    lote = get_object_or_404(
        Lote,
        id=lote_id
    )

    if request.method == 'POST':

        lote.activo = True

        lote.save(
            update_fields=[
                'activo',
                'fecha_actualizacion'
            ]
        )

        messages.success(
            request,
            (
                f'El lote {lote.codigo} '
                'fue restablecido correctamente.'
            )
        )

    return redirect(
        'lotes:lote_lista'
    )


# ============================================================
# ELIMINACIÓN DEFINITIVA
# SOLO MASTER
# ============================================================

@login_required
def lote_eliminar_definitivo(
    request,
    lote_id
):

    if not usuario_es_master(
        request.user
    ):

        messages.error(
            request,
            (
                'Solo el MASTER puede eliminar '
                'definitivamente un lote.'
            )
        )

        return redirect(
            'lotes:lote_lista'
        )

    lote = get_object_or_404(
        Lote,
        id=lote_id
    )

    if request.method == 'POST':

        codigo = lote.codigo

        lote.delete()

        messages.success(
            request,
            (
                f'El lote {codigo} '
                'fue eliminado definitivamente.'
            )
        )

        return redirect(
            'lotes:lote_lista'
        )

    return render(
        request,
        'lotes/lote_confirmar_eliminar_definitivo.html',
        {
            'lote':
                lote
        }
    )


# ============================================================
# RESERVAR LOTE
# ============================================================

@login_required
def lote_reservar(
    request,
    lote_id
):

    actualizar_reservas_vencidas()

    lote = get_object_or_404(
        Lote,
        id=lote_id,
        activo=True
    )

    es_master = usuario_es_master(
        request.user
    )

    es_creador = (
        lote.asesor_creador ==
        request.user
    )

    es_autorizado = LoteAutorizacion.objects.filter(
        lote=lote,
        asesor_autorizado=request.user,
        estado='ACTIVA'
    ).exists()

    # --------------------------------------------------------
    # CONTROL DE ACCESO
    # --------------------------------------------------------

    if (
        not es_master
        and not es_creador
        and not es_autorizado
    ):

        messages.error(
            request,
            (
                'No tiene autorización para '
                'reservar este lote.'
            )
        )

        return redirect(
            'lotes:lote_detalle',
            lote_id=lote.id
        )

    # --------------------------------------------------------
    # COMPROBAR DISPONIBILIDAD
    # --------------------------------------------------------

    if lote.estado != 'DISPONIBLE':

        messages.warning(
            request,
            'Este lote no se encuentra disponible.'
        )

        return redirect(
            'lotes:lote_detalle',
            lote_id=lote.id
        )

    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == 'POST':

        form = ReservaLoteForm(
            request.POST,
            usuario=request.user
        )

        if form.is_valid():

            tipo = form.cleaned_data[
                'tipo'
            ]

            # ------------------------------------------------
            # RESERVA EXCEPCIONAL
            # ------------------------------------------------

            if (
                tipo == 'EXCEPCIONAL'
                and not es_master
            ):

                messages.error(
                    request,
                    (
                        'La reserva excepcional '
                        'de 10 días solo puede ser '
                        'autorizada por el MASTER.'
                    )
                )

                return render(
                    request,
                    'lotes/lote_reservar.html',
                    {
                        'form':
                            form,

                        'lote':
                            lote,

                        'es_master':
                            es_master,
                    }
                )

            # ------------------------------------------------
            # VERIFICACIÓN DE SEGURIDAD
            # ------------------------------------------------

            reserva_existente = Reserva.objects.filter(
                lote=lote,
                estado='ACTIVA'
            ).exists()

            if reserva_existente:

                messages.error(
                    request,
                    (
                        'El lote acaba de ser reservado '
                        'por otro usuario.'
                    )
                )

                return redirect(
                    'lotes:lote_detalle',
                    lote_id=lote.id
                )

            # ------------------------------------------------
            # CREAR RESERVA
            # ------------------------------------------------

            with transaction.atomic():

                reserva = form.save(
                    commit=False
                )

                reserva.lote = lote

                reserva.asesor = request.user

                reserva.fecha_inicio = (
                    timezone.now()
                )

                reserva.save()

                lote.estado = 'RESERVADO'

                lote.save(
                    update_fields=[
                        'estado',
                        'fecha_actualizacion'
                    ]
                )

            messages.success(
                request,
                (
                    f'El lote {lote.codigo} '
                    'fue reservado correctamente.'
                )
            )

            return redirect(
                'lotes:lote_detalle',
                lote_id=lote.id
            )

    else:

        form = ReservaLoteForm(
            usuario=request.user
        )

    return render(
        request,
        'lotes/lote_reservar.html',
        {
            'form':
                form,

            'lote':
                lote,

            'es_master':
                es_master,
        }
    )


# ============================================================
# LIBERAR RESERVA
# ============================================================

@login_required
def lote_liberar_reserva(
    request,
    lote_id
):

    actualizar_reservas_vencidas()

    lote = get_object_or_404(
        Lote,
        id=lote_id
    )

    reserva = lote.reserva_activa

    if not reserva:

        messages.warning(
            request,
            'Este lote no tiene una reserva activa.'
        )

        return redirect(
            'lotes:lote_detalle',
            lote_id=lote.id
        )

    es_master = usuario_es_master(
        request.user
    )

    es_asesor_reserva = (
        reserva.asesor ==
        request.user
    )

    # --------------------------------------------------------
    # SOLO MASTER O ASESOR RESPONSABLE
    # --------------------------------------------------------

    if (
        not es_master
        and not es_asesor_reserva
    ):

        messages.error(
            request,
            (
                'Solo el MASTER o el asesor '
                'responsable de la reserva '
                'pueden liberarla.'
            )
        )

        return redirect(
            'lotes:lote_detalle',
            lote_id=lote.id
        )

    if request.method == 'POST':

        reserva.estado = 'CANCELADA'

        reserva.save(
            update_fields=[
                'estado',
                'fecha_actualizacion'
            ]
        )

        lote.estado = 'DISPONIBLE'

        lote.save(
            update_fields=[
                'estado',
                'fecha_actualizacion'
            ]
        )

        messages.success(
            request,
            (
                f'La reserva del lote {lote.codigo} '
                'fue liberada correctamente.'
            )
        )

    return redirect(
        'lotes:lote_detalle',
        lote_id=lote.id
    )


# ============================================================
# AUTORIZAR LOTE
# ============================================================

@login_required
def lote_autorizar(
    request,
    lote_id
):

    lote = get_object_or_404(
        Lote,
        id=lote_id,
        activo=True
    )

    es_master = usuario_es_master(
        request.user
    )

    es_creador = (
        lote.asesor_creador ==
        request.user
    )

    # --------------------------------------------------------
    # SOLO MASTER O CREADOR
    # --------------------------------------------------------

    if (
        not es_master
        and not es_creador
    ):

        messages.error(
            request,
            (
                'Solo el MASTER o el asesor creador '
                'pueden autorizar este lote.'
            )
        )

        return redirect(
            'lotes:lote_detalle',
            lote_id=lote.id
        )

    if request.method == 'POST':

        form = LoteAutorizacionForm(
            request.POST
        )

        if form.is_valid():

            asesor = form.cleaned_data[
                'asesor_autorizado'
            ]

            # ------------------------------------------------
            # NO AUTORIZARSE A SÍ MISMO
            # ------------------------------------------------

            if asesor == lote.asesor_creador:

                messages.warning(
                    request,
                    (
                        'El asesor creador ya tiene '
                        'acceso al lote.'
                    )
                )

            else:

                existe = LoteAutorizacion.objects.filter(
                    lote=lote,
                    asesor_autorizado=asesor,
                    estado='ACTIVA'
                ).exists()

                if existe:

                    messages.warning(
                        request,
                        (
                            'Este asesor ya tiene '
                            'autorización para el lote.'
                        )
                    )

                else:

                    autorizacion = form.save(
                        commit=False
                    )

                    autorizacion.lote = lote

                    autorizacion.estado = 'ACTIVA'

                    autorizacion.save()

                    messages.success(
                        request,
                        (
                            f'El lote {lote.codigo} '
                            f'fue autorizado para '
                            f'{asesor.get_full_name() or asesor.username}.'
                        )
                    )

                    return redirect(
                        'lotes:lote_detalle',
                        lote_id=lote.id
                    )

    else:

        form = LoteAutorizacionForm()

    return render(
        request,
        'lotes/lote_autorizar.html',
        {
            'form':
                form,

            'lote':
                lote,
        }
    )


# ============================================================
# REVOCAR AUTORIZACIÓN
# ============================================================

@login_required
def lote_revocar_autorizacion(
    request,
    autorizacion_id
):

    autorizacion = get_object_or_404(
        LoteAutorizacion,
        id=autorizacion_id,
        estado='ACTIVA'
    )

    lote = autorizacion.lote

    es_master = usuario_es_master(
        request.user
    )

    es_creador = (
        lote.asesor_creador ==
        request.user
    )

    # --------------------------------------------------------
    # SOLO MASTER O CREADOR
    # --------------------------------------------------------

    if (
        not es_master
        and not es_creador
    ):

        messages.error(
            request,
            (
                'No tiene autorización para '
                'revocar esta autorización.'
            )
        )

        return redirect(
            'lotes:lote_detalle',
            lote_id=lote.id
        )

    if request.method == 'POST':

        autorizacion.estado = 'REVOCADA'

        autorizacion.fecha_revocacion = (
            timezone.now()
        )

        autorizacion.save()

        messages.success(
            request,
            'La autorización fue revocada correctamente.'
        )

    return redirect(
        'lotes:lote_detalle',
        lote_id=lote.id
    )