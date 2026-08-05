from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from clientes.models import Cliente

from .forms import SeguimientoForm
from .models import Seguimiento


# ============================================================
# INICIO DE SEGUIMIENTOS
# ============================================================

@login_required
def inicio_seguimientos(request):

    # ========================================================
    # VERIFICAR SI EL USUARIO ES MASTER
    # ========================================================

    es_master = request.user.groups.filter(
        name='MASTER'
    ).exists()

    # ========================================================
    # OBTENER ASESOR SELECCIONADO
    # ========================================================

    asesor_id = request.GET.get('asesor')

    asesor_seleccionado = None

    # ========================================================
    # LISTA DE ASESORES PARA EL MASTER
    # ========================================================

    if es_master:

        asesores = User.objects.filter(
            is_active=True,
            groups__name='ASESOR'
        ).distinct().order_by(
            'first_name',
            'last_name',
            'username'
        )

        # ====================================================
        # SI EL MASTER SELECCIONÓ UN ASESOR
        # ====================================================

        if asesor_id:

            try:

                asesor_seleccionado = User.objects.get(
                    id=asesor_id,
                    is_active=True,
                    groups__name='ASESOR'
                )

            except User.DoesNotExist:

                asesor_seleccionado = None

    else:

        # ====================================================
        # SI ES ASESOR
        # SOLO TRABAJA CON SUS PROPIOS CLIENTES
        # ====================================================

        asesor_seleccionado = request.user

        asesores = []

    # ========================================================
    # BASE DE CLIENTES ACTIVOS
    # ========================================================

    clientes_base = Cliente.objects.filter(
        eliminado=False
    )

    # ========================================================
    # FILTRAR POR ASESOR
    # ========================================================

    if asesor_seleccionado:

        clientes_base = clientes_base.filter(
            asesor=asesor_seleccionado
        )

    # ========================================================
    # CLIENTES SIN SEGUIMIENTO
    # ========================================================

    clientes_sin_seguimiento = clientes_base.filter(
        seguimientos__isnull=True
    ).select_related(
        'asesor'
    ).distinct()

    # ========================================================
    # TOTAL DE CLIENTES
    # ========================================================

    total_clientes = clientes_base.count()

    # ========================================================
    # TOTAL DE CLIENTES CON SEGUIMIENTO
    # ========================================================

    clientes_con_seguimiento = clientes_base.filter(
        seguimientos__isnull=False
    ).distinct().count()

    # ========================================================
    # TOTAL DE CLIENTES SIN SEGUIMIENTO
    # ========================================================

    total_sin_seguimiento = clientes_sin_seguimiento.count()

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'es_master': es_master,

        'asesores': asesores,

        'asesor_seleccionado': asesor_seleccionado,

        'clientes_sin_seguimiento':
            clientes_sin_seguimiento,

        'total_clientes':
            total_clientes,

        'clientes_con_seguimiento':
            clientes_con_seguimiento,

        'total_sin_seguimiento':
            total_sin_seguimiento,

    }

    # ========================================================
    # MOSTRAR PÁGINA
    # ========================================================

    return render(
        request,
        'gestion_seguimientos/inicio.html',
        contexto
    )


# ============================================================
# LISTA DE SEGUIMIENTOS DE UN CLIENTE
# ============================================================

@login_required
def seguimiento_lista(request, cliente_id):

    # ========================================================
    # BUSCAR CLIENTE
    # ========================================================

    cliente = get_object_or_404(
        Cliente,
        id=cliente_id
    )

    # ========================================================
    # VERIFICAR SI EL USUARIO ES MASTER
    # ========================================================

    es_master = request.user.groups.filter(
        name='MASTER'
    ).exists()

    # ========================================================
    # VALIDAR ACCESO DEL ASESOR
    # ========================================================

    if not es_master:

        if cliente.asesor != request.user:

            return render(
                request,
                'clientes/cliente_no_disponible.html',
                {
                    'cliente': cliente,
                },
                status=403
            )

    # ========================================================
    # OBTENER SEGUIMIENTOS
    # ========================================================

    seguimientos = Seguimiento.objects.filter(
        cliente=cliente
    ).select_related(
        'asesor'
    )

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'cliente': cliente,

        'seguimientos': seguimientos,

        'es_master': es_master,

    }

    # ========================================================
    # MOSTRAR HISTORIAL
    # ========================================================

    return render(
        request,
        'gestion_seguimientos/seguimiento_lista.html',
        contexto
    )


# ============================================================
# CREAR NUEVO SEGUIMIENTO
# ============================================================

@login_required
def seguimiento_crear(request, cliente_id):

    # ========================================================
    # BUSCAR CLIENTE ACTIVO
    # ========================================================

    cliente = get_object_or_404(
        Cliente,
        id=cliente_id,
        eliminado=False
    )

    # ========================================================
    # VERIFICAR SI ES MASTER
    # ========================================================

    es_master = request.user.groups.filter(
        name='MASTER'
    ).exists()

    # ========================================================
    # VALIDAR ACCESO DEL ASESOR
    # ========================================================

    if not es_master:

        if cliente.asesor != request.user:

            return render(
                request,
                'clientes/cliente_no_disponible.html',
                {
                    'cliente': cliente,
                },
                status=403
            )

    # ========================================================
    # PROCESAR FORMULARIO
    # ========================================================

    if request.method == 'POST':

        form = SeguimientoForm(
            request.POST
        )

        if form.is_valid():

            seguimiento = form.save(
                commit=False
            )

            # Asignar cliente
            seguimiento.cliente = cliente

            # Registrar usuario que realizó el seguimiento
            seguimiento.asesor = request.user

            # Guardar
            seguimiento.save()

            # =================================================
            # VOLVER AL HISTORIAL
            # =================================================

            return redirect(
                'gestion_seguimientos:seguimiento_lista',
                cliente_id=cliente.id
            )

    else:

        form = SeguimientoForm()

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'form': form,

        'cliente': cliente,

    }

    # ========================================================
    # MOSTRAR FORMULARIO
    # ========================================================

    return render(
        request,
        'gestion_seguimientos/seguimiento_crear.html',
        contexto
    )


# ============================================================
# EDITAR SEGUIMIENTO
# ============================================================

@login_required
def seguimiento_editar(request, seguimiento_id):

    # ========================================================
    # BUSCAR SEGUIMIENTO
    # ========================================================

    seguimiento = get_object_or_404(
        Seguimiento,
        id=seguimiento_id
    )

    # ========================================================
    # OBTENER CLIENTE
    # ========================================================

    cliente = seguimiento.cliente

    # ========================================================
    # VERIFICAR SI ES MASTER
    # ========================================================

    es_master = request.user.groups.filter(
        name='MASTER'
    ).exists()

    # ========================================================
    # VALIDAR PERMISOS
    #
    # MASTER:
    # Puede editar cualquier seguimiento.
    #
    # ASESOR:
    # Solo puede editar sus propios seguimientos.
    # ========================================================

    if not es_master:

        if seguimiento.asesor != request.user:

            return render(
                request,
                'clientes/cliente_no_disponible.html',
                {
                    'cliente': cliente,
                },
                status=403
            )

    # ========================================================
    # PROCESAR FORMULARIO
    # ========================================================

    if request.method == 'POST':

        form = SeguimientoForm(
            request.POST,
            instance=seguimiento
        )

        if form.is_valid():

            form.save()

            return redirect(
                'gestion_seguimientos:seguimiento_lista',
                cliente_id=cliente.id
            )

    else:

        form = SeguimientoForm(
            instance=seguimiento
        )

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'form': form,

        'cliente': cliente,

        'seguimiento': seguimiento,

        'es_master': es_master,

    }

    # ========================================================
    # MOSTRAR FORMULARIO
    # ========================================================

    return render(
        request,
        'gestion_seguimientos/seguimiento_editar.html',
        contexto
    )


# ============================================================
# ELIMINAR SEGUIMIENTO
# ============================================================

@login_required
def seguimiento_eliminar(request, seguimiento_id):

    # ========================================================
    # BUSCAR SEGUIMIENTO
    # ========================================================

    seguimiento = get_object_or_404(
        Seguimiento,
        id=seguimiento_id
    )

    # ========================================================
    # OBTENER CLIENTE
    # ========================================================

    cliente = seguimiento.cliente

    # ========================================================
    # VERIFICAR SI ES MASTER
    # ========================================================

    es_master = request.user.groups.filter(
        name='MASTER'
    ).exists()

    # ========================================================
    # VALIDAR PERMISOS
    #
    # MASTER:
    # Puede eliminar cualquier seguimiento.
    #
    # ASESOR:
    # Solo puede eliminar sus propios seguimientos.
    # ========================================================

    if not es_master:

        if seguimiento.asesor != request.user:

            return render(
                request,
                'clientes/cliente_no_disponible.html',
                {
                    'cliente': cliente,
                },
                status=403
            )

    # ========================================================
    # CONFIRMAR ELIMINACIÓN
    # ========================================================

    if request.method == 'POST':

        seguimiento.delete()

        return redirect(
            'gestion_seguimientos:seguimiento_lista',
            cliente_id=cliente.id
        )

    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'seguimiento': seguimiento,

        'cliente': cliente,

        'es_master': es_master,

    }

    # ========================================================
    # MOSTRAR CONFIRMACIÓN
    # ========================================================

    return render(
        request,
        'gestion_seguimientos/confirmar_eliminar_seguimiento.html',
        contexto
    )
# ============================================================
# AGENDA DE SEGUIMIENTOS
# ============================================================

from django.utils import timezone


@login_required
def agenda_seguimientos(request):

    # ========================================================
    # VERIFICAR SI EL USUARIO ES MASTER
    # ========================================================

    es_master = request.user.groups.filter(
        name='MASTER'
    ).exists()


    # ========================================================
    # OBTENER SEGUIMIENTOS CON PRÓXIMA GESTIÓN
    # ========================================================

    seguimientos = Seguimiento.objects.filter(
        proxima_gestion__isnull=False
    ).select_related(
        'cliente',
        'asesor'
    )


    # ========================================================
    # SI NO ES MASTER
    # SOLO VE SUS PROPIOS SEGUIMIENTOS
    # ========================================================

    if not es_master:

        seguimientos = seguimientos.filter(
            asesor=request.user
        )


    # ========================================================
    # FILTRO POR ASESOR PARA MASTER
    # ========================================================

    asesor_id = request.GET.get(
        'asesor'
    )


    if es_master and asesor_id:

        seguimientos = seguimientos.filter(
            asesor_id=asesor_id
        )


    # ========================================================
    # FECHA Y HORA ACTUAL
    # ========================================================

    ahora = timezone.localtime()


    # ========================================================
    # GESTIONES VENCIDAS
    # ========================================================

    gestiones_vencidas = seguimientos.filter(
        proxima_gestion__lt=ahora
    ).order_by(
        'proxima_gestion'
    )


    # ========================================================
    # GESTIONES PARA HOY
    # ========================================================

    gestiones_hoy = seguimientos.filter(
        proxima_gestion__date=ahora.date()
    ).order_by(
        'proxima_gestion'
    )


    # ========================================================
    # GESTIONES FUTURAS
    # ========================================================

    gestiones_proximas = seguimientos.filter(
        proxima_gestion__gt=ahora
    ).exclude(
        proxima_gestion__date=ahora.date()
    ).order_by(
        'proxima_gestion'
    )


    # ========================================================
    # LISTA DE ASESORES
    # ========================================================

    if es_master:

        asesores = User.objects.filter(
            is_active=True
        ).order_by(
            'first_name',
            'last_name',
            'username'
        )

    else:

        asesores = []


    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'es_master':
            es_master,

        'asesores':
            asesores,

        'asesor_id':
            asesor_id,

        'gestiones_vencidas':
            gestiones_vencidas,

        'gestiones_hoy':
            gestiones_hoy,

        'gestiones_proximas':
            gestiones_proximas,

        'total_vencidas':
            gestiones_vencidas.count(),

        'total_hoy':
            gestiones_hoy.count(),

        'total_proximas':
            gestiones_proximas.count(),

    }


    # ========================================================
    # MOSTRAR AGENDA
    # ========================================================

    return render(
        request,
        'gestion_seguimientos/agenda.html',
        contexto
    )
# ============================================================
# DASHBOARD COMERCIAL
# ============================================================

@login_required
def dashboard_comercial(request):

    # ========================================================
    # VERIFICAR SI EL USUARIO ES MASTER
    # ========================================================

    es_master = request.user.groups.filter(
        name='MASTER'
    ).exists()


    # ========================================================
    # OBTENER ASESOR SELECCIONADO
    # ========================================================

    asesor_id = request.GET.get('asesor')


    asesor_seleccionado = None


    # ========================================================
    # LISTA DE ASESORES
    # ========================================================

    if es_master:

        asesores = User.objects.filter(
            is_active=True
        ).order_by(
            'first_name',
            'last_name',
            'username'
        )


        # ====================================================
        # FILTRAR POR ASESOR
        # ====================================================

        if asesor_id:

            try:

                asesor_seleccionado = User.objects.get(
                    id=asesor_id,
                    is_active=True
                )

            except User.DoesNotExist:

                asesor_seleccionado = None


    else:

        # ====================================================
        # EL ASESOR SOLO VE SUS DATOS
        # ====================================================

        asesor_seleccionado = request.user

        asesores = []


    # ========================================================
    # BASE DE CLIENTES ACTIVOS
    # ========================================================

    clientes_base = Cliente.objects.filter(
        eliminado=False
    )


    # ========================================================
    # FILTRAR CLIENTES POR ASESOR
    # ========================================================

    if asesor_seleccionado:

        clientes_base = clientes_base.filter(
            asesor=asesor_seleccionado
        )


    # ========================================================
    # BASE DE SEGUIMIENTOS
    # ========================================================

    seguimientos_base = Seguimiento.objects.filter(
        cliente__eliminado=False
    )


    # ========================================================
    # FILTRAR SEGUIMIENTOS POR ASESOR
    # ========================================================

    if asesor_seleccionado:

        seguimientos_base = seguimientos_base.filter(
            cliente__asesor=asesor_seleccionado
        )


    # ========================================================
    # ESTADÍSTICAS DE CLIENTES
    # ========================================================

    total_clientes = clientes_base.count()


    clientes_con_seguimiento = clientes_base.filter(
        seguimientos__isnull=False
    ).distinct().count()


    clientes_sin_seguimiento = clientes_base.filter(
        seguimientos__isnull=True
    ).distinct().count()


    # ========================================================
    # ESTADÍSTICAS DE SEGUIMIENTOS
    # ========================================================

    total_seguimientos = seguimientos_base.count()


    # ========================================================
    # CLIENTES INTERESADOS
    # ========================================================

    clientes_interesados = seguimientos_base.filter(
        resultado='INTERESADO'
    ).values(
        'cliente'
    ).distinct().count()


    # ========================================================
    # CLIENTES EN NEGOCIACIÓN
    # ========================================================

    clientes_negociacion = seguimientos_base.filter(
        resultado='NEGOCIACION'
    ).values(
        'cliente'
    ).distinct().count()


    # ========================================================
    # VISITAS AGENDADAS
    # ========================================================

    visitas_agendadas = seguimientos_base.filter(
        resultado='VISITA_AGENDADA'
    ).values(
        'cliente'
    ).distinct().count()


    # ========================================================
    # VENTAS REALIZADAS
    # ========================================================

    ventas_realizadas = seguimientos_base.filter(
        resultado='VENTA'
    ).values(
        'cliente'
    ).distinct().count()


    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'es_master':
            es_master,

        'asesores':
            asesores,

        'asesor_seleccionado':
            asesor_seleccionado,

        # ----------------------------------------------------
        # CLIENTES
        # ----------------------------------------------------

        'total_clientes':
            total_clientes,

        'clientes_con_seguimiento':
            clientes_con_seguimiento,

        'clientes_sin_seguimiento':
            clientes_sin_seguimiento,

        # ----------------------------------------------------
        # SEGUIMIENTOS
        # ----------------------------------------------------

        'total_seguimientos':
            total_seguimientos,

        # ----------------------------------------------------
        # ESTADOS COMERCIALES
        # ----------------------------------------------------

        'clientes_interesados':
            clientes_interesados,

        'clientes_negociacion':
            clientes_negociacion,

        'visitas_agendadas':
            visitas_agendadas,

        'ventas_realizadas':
            ventas_realizadas,

    }


    # ========================================================
    # MOSTRAR DASHBOARD
    # ========================================================

    return render(
        request,
        'gestion_seguimientos/dashboard.html',
        contexto
    )