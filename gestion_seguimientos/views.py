from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import datetime, time, timedelta

from clientes.models import Cliente

from .forms import SeguimientoForm
from .models import Seguimiento


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


def usuario_es_asesor(user):
    """
    Determina si el usuario pertenece al grupo ASESOR.
    """
    return user.groups.filter(
        name='ASESOR'
    ).exists()


def obtener_asesores():
    """
    Obtiene únicamente usuarios activos pertenecientes
    al grupo ASESOR.
    """

    return User.objects.filter(
        is_active=True,
        groups__name='ASESOR'
    ).distinct().order_by(
        'first_name',
        'last_name',
        'username'
    )


# ============================================================
# INICIO DE SEGUIMIENTOS
# ============================================================

@login_required
def inicio_seguimientos(request):

    es_master = usuario_es_master(
        request.user
    )

    # --------------------------------------------------------
    # ASESOR SELECCIONADO
    # --------------------------------------------------------

    asesor_id = request.GET.get(
        'asesor'
    )

    asesor_seleccionado = None

    # --------------------------------------------------------
    # MASTER
    # --------------------------------------------------------

    if es_master:

        asesores = obtener_asesores()

        if asesor_id:

            asesor_seleccionado = User.objects.filter(
                id=asesor_id,
                is_active=True,
                groups__name='ASESOR'
            ).first()

    # --------------------------------------------------------
    # ASESOR
    # --------------------------------------------------------

    else:

        asesores = []

        asesor_seleccionado = request.user

    # --------------------------------------------------------
    # CLIENTES ACTIVOS
    # --------------------------------------------------------

    clientes_base = Cliente.objects.filter(
        eliminado=False
    )

    # --------------------------------------------------------
    # FILTRAR CLIENTES POR ASESOR
    # --------------------------------------------------------

    if asesor_seleccionado:

        clientes_base = clientes_base.filter(
            asesor=asesor_seleccionado
        )

    # --------------------------------------------------------
    # CLIENTES SIN SEGUIMIENTO
    # --------------------------------------------------------

    clientes_sin_seguimiento = (
        clientes_base
        .filter(
            seguimientos__isnull=True
        )
        .select_related(
            'asesor'
        )
        .distinct()
        .order_by(
            'nombre_completo'
        )
    )

    # --------------------------------------------------------
    # TOTALES
    # --------------------------------------------------------

    total_clientes = clientes_base.count()

    clientes_con_seguimiento = (
        clientes_base
        .filter(
            seguimientos__isnull=False
        )
        .distinct()
        .count()
    )

    total_sin_seguimiento = (
        clientes_sin_seguimiento.count()
    )

    # --------------------------------------------------------
    # CONTEXTO
    # --------------------------------------------------------

    contexto = {

        'es_master':
            es_master,

        'asesores':
            asesores,

        'asesor_seleccionado':
            asesor_seleccionado,

        'clientes_sin_seguimiento':
            clientes_sin_seguimiento,

        'total_clientes':
            total_clientes,

        'clientes_con_seguimiento':
            clientes_con_seguimiento,

        'total_sin_seguimiento':
            total_sin_seguimiento,

    }

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

    cliente = get_object_or_404(
        Cliente,
        id=cliente_id,
        eliminado=False
    )

    es_master = usuario_es_master(
        request.user
    )

    # --------------------------------------------------------
    # CONTROL DE ACCESO
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # SEGUIMIENTOS
    # --------------------------------------------------------

    seguimientos = (
        Seguimiento.objects
        .filter(
            cliente=cliente
        )
        .select_related(
            'asesor'
        )
        .order_by(
            '-fecha'
        )
    )

    # --------------------------------------------------------
    # CONTEXTO
    # --------------------------------------------------------

    contexto = {

        'cliente':
            cliente,

        'seguimientos':
            seguimientos,

        'es_master':
            es_master,

    }

    return render(
        request,
        'gestion_seguimientos/seguimiento_lista.html',
        contexto
    )


# ============================================================
# CREAR SEGUIMIENTO
# ============================================================

@login_required
def seguimiento_crear(request, cliente_id):

    cliente = get_object_or_404(
        Cliente,
        id=cliente_id,
        eliminado=False
    )

    es_master = usuario_es_master(
        request.user
    )

    # --------------------------------------------------------
    # CONTROL DE ACCESO
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # FORMULARIO
    # --------------------------------------------------------

    if request.method == 'POST':

        form = SeguimientoForm(
            request.POST
        )

        if form.is_valid():

            seguimiento = form.save(
                commit=False
            )

            # Cliente al que pertenece el seguimiento
            seguimiento.cliente = cliente

            # Usuario que registra la gestión
            seguimiento.asesor = request.user

            seguimiento.save()

            return redirect(
                'gestion_seguimientos:seguimiento_lista',
                cliente_id=cliente.id
            )

    else:

        form = SeguimientoForm()

    # --------------------------------------------------------
    # CONTEXTO
    # --------------------------------------------------------

    contexto = {

        'form':
            form,

        'cliente':
            cliente,

    }

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

    seguimiento = get_object_or_404(
        Seguimiento,
        id=seguimiento_id
    )

    cliente = seguimiento.cliente

    es_master = usuario_es_master(
        request.user
    )

    # --------------------------------------------------------
    # CONTROL DE ACCESO
    #
    # MASTER:
    # puede editar cualquier seguimiento.
    #
    # ASESOR:
    # solamente puede editar seguimientos de sus clientes.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # PROCESAR
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CONTEXTO
    # --------------------------------------------------------

    contexto = {

        'form':
            form,

        'cliente':
            cliente,

        'seguimiento':
            seguimiento,

        'es_master':
            es_master,

    }

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

    seguimiento = get_object_or_404(
        Seguimiento,
        id=seguimiento_id
    )

    cliente = seguimiento.cliente

    es_master = usuario_es_master(
        request.user
    )

    # --------------------------------------------------------
    # CONTROL DE ACCESO
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # ELIMINAR
    # --------------------------------------------------------

    if request.method == 'POST':

        seguimiento.delete()

        return redirect(
            'gestion_seguimientos:seguimiento_lista',
            cliente_id=cliente.id
        )

    # --------------------------------------------------------
    # CONTEXTO
    # --------------------------------------------------------

    contexto = {

        'seguimiento':
            seguimiento,

        'cliente':
            cliente,

        'es_master':
            es_master,

    }

    return render(
        request,
        'gestion_seguimientos/confirmar_eliminar_seguimiento.html',
        contexto
    )


# ============================================================
# AGENDA DE SEGUIMIENTOS
# ============================================================

@login_required
def agenda_seguimientos(request):

    es_master = usuario_es_master(
        request.user
    )

    # --------------------------------------------------------
    # BASE
    #
    # La agenda se determina por el ASESOR DEL CLIENTE,
    # no por quién registró el seguimiento.
    # --------------------------------------------------------

    seguimientos = (
        Seguimiento.objects
        .filter(
            proxima_gestion__isnull=False,
            cliente__eliminado=False
        )
        .select_related(
            'cliente',
            'asesor'
        )
    )

    # --------------------------------------------------------
    # ASESOR
    # --------------------------------------------------------

    asesor_id = request.GET.get(
        'asesor'
    )

    # --------------------------------------------------------
    # ASESOR NORMAL
    # --------------------------------------------------------

    if not es_master:

        seguimientos = seguimientos.filter(
            cliente__asesor=request.user
        )

        asesores = []

    # --------------------------------------------------------
    # MASTER
    # --------------------------------------------------------

    else:

        asesores = obtener_asesores()

        if asesor_id:

            asesor_valido = User.objects.filter(
                id=asesor_id,
                is_active=True,
                groups__name='ASESOR'
            ).exists()

            if asesor_valido:

                seguimientos = seguimientos.filter(
                    cliente__asesor_id=asesor_id
                )

            else:

                asesor_id = ''

    # --------------------------------------------------------
    # FECHA Y HORA ACTUAL
    # --------------------------------------------------------

    ahora = timezone.localtime()

    fecha_hoy = ahora.date()

    inicio_hoy = timezone.make_aware(
        datetime.combine(
            fecha_hoy,
            time.min
        )
    )

    inicio_manana = inicio_hoy + timedelta(
        days=1
    )

    # --------------------------------------------------------
    # GESTIONES VENCIDAS
    #
    # Todo lo que tenga fecha anterior a HOY.
    # --------------------------------------------------------

    gestiones_vencidas = (
        seguimientos
        .filter(
            proxima_gestion__lt=inicio_hoy
        )
        .order_by(
            'proxima_gestion'
        )
    )

    # --------------------------------------------------------
    # GESTIONES PARA HOY
    #
    # Desde las 00:00 de hoy hasta antes de las 00:00
    # del día siguiente.
    #
    # Así NO se mezclan con las vencidas.
    # --------------------------------------------------------

    gestiones_hoy = (
        seguimientos
        .filter(
            proxima_gestion__gte=inicio_hoy,
            proxima_gestion__lt=inicio_manana
        )
        .order_by(
            'proxima_gestion'
        )
    )

    # --------------------------------------------------------
    # PRÓXIMAS GESTIONES
    #
    # A partir de mañana.
    # --------------------------------------------------------

    gestiones_proximas = (
        seguimientos
        .filter(
            proxima_gestion__gte=inicio_manana
        )
        .order_by(
            'proxima_gestion'
        )
    )

    # --------------------------------------------------------
    # CONTEXTO
    # --------------------------------------------------------

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

    es_master = usuario_es_master(
        request.user
    )

    # --------------------------------------------------------
    # ASESOR SELECCIONADO
    # --------------------------------------------------------

    asesor_id = request.GET.get(
        'asesor'
    )

    asesor_seleccionado = None

    # --------------------------------------------------------
    # MASTER
    # --------------------------------------------------------

    if es_master:

        asesores = obtener_asesores()

        if asesor_id:

            asesor_seleccionado = User.objects.filter(
                id=asesor_id,
                is_active=True,
                groups__name='ASESOR'
            ).first()

    # --------------------------------------------------------
    # ASESOR
    # --------------------------------------------------------

    else:

        asesores = []

        asesor_seleccionado = request.user

    # --------------------------------------------------------
    # CLIENTES ACTIVOS
    # --------------------------------------------------------

    clientes_base = Cliente.objects.filter(
        eliminado=False
    )

    if asesor_seleccionado:

        clientes_base = clientes_base.filter(
            asesor=asesor_seleccionado
        )

    # --------------------------------------------------------
    # SEGUIMIENTOS
    # --------------------------------------------------------

    seguimientos_base = Seguimiento.objects.filter(
        cliente__eliminado=False
    )

    if asesor_seleccionado:

        seguimientos_base = seguimientos_base.filter(
            cliente__asesor=asesor_seleccionado
        )

    # --------------------------------------------------------
    # CLIENTES
    # --------------------------------------------------------

    total_clientes = clientes_base.count()

    clientes_con_seguimiento = (
        clientes_base
        .filter(
            seguimientos__isnull=False
        )
        .distinct()
        .count()
    )

    clientes_sin_seguimiento = (
        clientes_base
        .filter(
            seguimientos__isnull=True
        )
        .distinct()
        .count()
    )

    # --------------------------------------------------------
    # TOTAL SEGUIMIENTOS
    # --------------------------------------------------------

    total_seguimientos = (
        seguimientos_base.count()
    )

    # --------------------------------------------------------
    # INTERESADOS
    # --------------------------------------------------------

    clientes_interesados = (
        seguimientos_base
        .filter(
            resultado='INTERESADO'
        )
        .values(
            'cliente'
        )
        .distinct()
        .count()
    )

    # --------------------------------------------------------
    # NEGOCIACIÓN
    # --------------------------------------------------------

    clientes_negociacion = (
        seguimientos_base
        .filter(
            resultado='NEGOCIACION'
        )
        .values(
            'cliente'
        )
        .distinct()
        .count()
    )

    # --------------------------------------------------------
    # VISITAS
    # --------------------------------------------------------

    visitas_agendadas = (
        seguimientos_base
        .filter(
            resultado='VISITA_AGENDADA'
        )
        .values(
            'cliente'
        )
        .distinct()
        .count()
    )

    # --------------------------------------------------------
    # VENTAS
    # --------------------------------------------------------

    ventas_realizadas = (
        seguimientos_base
        .filter(
            resultado='VENTA'
        )
        .values(
            'cliente'
        )
        .distinct()
        .count()
    )

    # --------------------------------------------------------
    # CONTEXTO
    # --------------------------------------------------------

    contexto = {

        'es_master':
            es_master,

        'asesores':
            asesores,

        'asesor_seleccionado':
            asesor_seleccionado,

        'total_clientes':
            total_clientes,

        'clientes_con_seguimiento':
            clientes_con_seguimiento,

        'clientes_sin_seguimiento':
            clientes_sin_seguimiento,

        'total_seguimientos':
            total_seguimientos,

        'clientes_interesados':
            clientes_interesados,

        'clientes_negociacion':
            clientes_negociacion,

        'visitas_agendadas':
            visitas_agendadas,

        'ventas_realizadas':
            ventas_realizadas,

    }

    return render(
        request,
        'gestion_seguimientos/dashboard.html',
        contexto
    )