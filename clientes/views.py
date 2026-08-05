from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from oportunidades.models import Oportunidad

from accounts.views import master_required
from .forms import ClienteForm
from .models import Cliente


# ============================================================
# FUNCIÓN AUXILIAR
# ============================================================

def usuario_es_master(user):
    return user.groups.filter(
        name='MASTER'
    ).exists()


# ============================================================
# LISTA DE CLIENTES
# ============================================================

@login_required
def cliente_lista(request):

    if usuario_es_master(request.user):

        # MASTER puede ver todos los clientes activos
        clientes = Cliente.objects.filter(
            eliminado=False
        ).select_related(
            'asesor'
        ).order_by(
            '-fecha_registro'
        )

    else:

        # ASESOR solo puede ver sus propios clientes
        clientes = Cliente.objects.filter(
            asesor=request.user,
            eliminado=False
        ).order_by(
            '-fecha_registro'
        )

    contexto = {
        'clientes': clientes,
        'es_master': usuario_es_master(request.user),
    }

    return render(
        request,
        'clientes/cliente_lista.html',
        contexto
    )


# ============================================================
# CREAR CLIENTE
# ============================================================

@login_required
def cliente_crear(request):

    es_master = usuario_es_master(request.user)

    if request.method == 'POST':

        form = ClienteForm(
            request.POST,
            es_master=es_master
        )

        if form.is_valid():

            cliente = form.save(
                commit=False
            )

            # =================================================
            # MASTER
            # El MASTER selecciona el asesor
            # =================================================

            if es_master:

                cliente.asesor = form.cleaned_data[
                    'asesor'
                ]

            # =================================================
            # ASESOR
            # Se asigna automáticamente al usuario actual
            # =================================================

            else:

                cliente.asesor = request.user

            cliente.save()

            messages.success(
                request,
                'Cliente registrado correctamente.'
            )

            return redirect(
                'clientes:cliente_lista'
            )

    else:

        form = ClienteForm(
            es_master=es_master
        )

    contexto = {

        'form': form,

        'titulo': 'Registrar nuevo cliente',

        'es_master': es_master,

    }

    return render(
        request,
        'clientes/cliente_form.html',
        contexto
    )
# ============================================================
# DETALLE DEL CLIENTE
# ============================================================

@login_required
def cliente_detalle(request, pk):

    # ========================================================
    # BUSCAR CLIENTE
    # ========================================================

    try:

        cliente = Cliente.objects.get(
            pk=pk
        )

    except Cliente.DoesNotExist:

        return render(
            request,
            'clientes/cliente_no_disponible.html',
            status=404
        )


    # ========================================================
    # VERIFICAR SI EL CLIENTE ESTÁ ELIMINADO
    # ========================================================

    if cliente.eliminado:

        return render(
            request,
            'clientes/cliente_no_disponible.html',
            status=404
        )


    # ========================================================
    # VERIFICAR SI EL USUARIO ES MASTER
    # ========================================================

    es_master = usuario_es_master(
        request.user
    )


    # ========================================================
    # MASTER
    # Puede ver cualquier cliente activo
    # ========================================================

    if es_master:

        puede_ver = True


    # ========================================================
    # ASESOR
    # Solo puede ver sus propios clientes
    # ========================================================

    else:

        puede_ver = (
            cliente.asesor == request.user
        )


    # ========================================================
    # SIN PERMISOS
    # ========================================================

    if not puede_ver:

        return render(
            request,
            'clientes/cliente_no_disponible.html',
            status=404
        )


    # ========================================================
    # OPORTUNIDADES COMERCIALES
    # ========================================================
    #
    # Obtener todas las oportunidades asociadas
    # al cliente que estamos visualizando.
    #
    # select_related('asesor') permite cargar directamente
    # los datos del asesor de cada oportunidad.
    #
    # Esto evita consultas innecesarias a la base de datos.
    # ========================================================

    oportunidades = Oportunidad.objects.filter(
        cliente=cliente
    ).select_related(
        'asesor'
    ).order_by(
        '-id'
    )


    # ========================================================
    # MOSTRAR CLIENTE
    # ========================================================

    contexto = {

        # ----------------------------------------------------
        # DATOS DEL CLIENTE
        # ----------------------------------------------------

        'cliente':
            cliente,


        # ----------------------------------------------------
        # OPORTUNIDADES COMERCIALES
        # ----------------------------------------------------

        'oportunidades':
            oportunidades,


        # ----------------------------------------------------
        # PERMISOS MASTER
        # ----------------------------------------------------

        'es_master':
            es_master,

    }


    # ========================================================
    # MOSTRAR PÁGINA DE DETALLE
    # ========================================================

    return render(
        request,
        'clientes/cliente_detalle.html',
        contexto
    )

# ============================================================
# MARCAR CLIENTE COMO INACTIVO
# MASTER Y ASESOR
# ============================================================

@login_required
def cliente_inactivar(request, pk):

    # ========================================================
    # MASTER
    # Puede inactivar cualquier cliente
    # ========================================================

    if usuario_es_master(request.user):

        cliente = get_object_or_404(
            Cliente,
            pk=pk,
            eliminado=False
        )

    # ========================================================
    # ASESOR
    # Solo puede inactivar sus propios clientes
    # ========================================================

    else:

        cliente = get_object_or_404(
            Cliente,
            pk=pk,
            asesor=request.user,
            eliminado=False
        )

    # ========================================================
    # CONFIRMACIÓN
    # ========================================================

    if request.method == 'POST':

        cliente.estado = 'INACTIVO'

        cliente.save()

        messages.success(
            request,
            f'El cliente "{cliente.nombre_completo}" '
            'ha sido marcado como INACTIVO.'
        )

        return redirect(
            'clientes:cliente_lista'
        )

    contexto = {
        'cliente': cliente,
    }

    return render(
        request,
        'clientes/confirmar_inactivacion.html',
        contexto
    )

# ============================================================
# EDITAR CLIENTE
# ============================================================

@login_required
def cliente_editar(request, pk):

    # ========================================================
    # BUSCAR CLIENTE
    # ========================================================

    try:

        cliente = Cliente.objects.get(
            pk=pk
        )

    except Cliente.DoesNotExist:

        return render(
            request,
            'clientes/cliente_no_disponible.html',
            status=404
        )


    # ========================================================
    # VERIFICAR SI EL CLIENTE ESTÁ ELIMINADO
    # ========================================================

    if cliente.eliminado:

        return render(
            request,
            'clientes/cliente_no_disponible.html',
            status=404
        )


    # ========================================================
    # MASTER
    # Puede editar cualquier cliente activo
    # ========================================================

    if usuario_es_master(request.user):

        puede_editar = True


    # ========================================================
    # ASESOR
    # Solo puede editar sus propios clientes
    # ========================================================

    else:

        puede_editar = (
            cliente.asesor == request.user
        )


    # ========================================================
    # SIN PERMISOS
    # ========================================================

    if not puede_editar:

        return render(
            request,
            'clientes/cliente_no_disponible.html',
            status=404
        )


    # ========================================================
    # EDITAR CLIENTE
    # ========================================================

    if request.method == 'POST':

        form = ClienteForm(
            request.POST,
            instance=cliente,
            es_master=usuario_es_master(
                request.user
            )
        )

        if form.is_valid():

            cliente_actualizado = form.save(
                commit=False
            )


            # ====================================================
            # PROTEGER EL ASESOR
            # ====================================================
            # Si es MASTER, puede cambiar el asesor.
            # Si es ASESOR, conserva el asesor original.

            if not usuario_es_master(request.user):

                cliente_actualizado.asesor = cliente.asesor


            cliente_actualizado.save()


            messages.success(
                request,
                'Cliente actualizado correctamente.'
            )


            return redirect(
                'clientes:cliente_lista'
            )


    else:

        form = ClienteForm(
            instance=cliente,
            es_master=usuario_es_master(
                request.user
            )
        )


    contexto = {

        'form': form,

        'cliente': cliente,

        'titulo': 'Editar cliente',

        'es_master': usuario_es_master(
            request.user
        ),

    }


    return render(
        request,
        'clientes/cliente_form.html',
        contexto
    )
# ============================================================
# ELIMINAR CLIENTE
# PRIMERA CONFIRMACIÓN
# SOLO MASTER
#
# El cliente NO se elimina todavía.
# Se muestra la pantalla de confirmación.
# ============================================================

@master_required
def cliente_eliminar(request, pk):

    cliente = get_object_or_404(
        Cliente,
        pk=pk,
        eliminado=False
    )

    if request.method == 'POST':

        # Enviar el cliente a la PAPELERA
        cliente.eliminado = True
        cliente.fecha_eliminacion = timezone.now()
        cliente.eliminado_por = request.user
        cliente.save()

        messages.success(
            request,
            'El cliente fue enviado a la papelera.'
        )

        return redirect(
            'clientes:cliente_lista'
        )

    contexto = {
        'cliente': cliente,
    }

    return render(
    request,
    'clientes/cliente_confirmar_eliminar.html',
    contexto
)

# ============================================================
# PAPELERA DE CLIENTES
# SOLO MASTER
# ============================================================

@master_required
def papelera_clientes(request):

    clientes = Cliente.objects.filter(
        eliminado=True
    ).select_related(
        'asesor',
        'eliminado_por'
    ).order_by(
        '-fecha_eliminacion'
    )

    contexto = {
        'clientes': clientes,
    }

    return render(
        request,
        'clientes/papelera.html',
        contexto
    )


# ============================================================
# RESTAURAR CLIENTE
# SOLO MASTER
# ============================================================

@master_required
def restaurar_cliente(request, pk):

    cliente = get_object_or_404(
        Cliente,
        pk=pk,
        eliminado=True
    )

    if request.method == 'POST':
        cliente.eliminado = False
        cliente.fecha_eliminacion = None
        cliente.eliminado_por = None
        cliente.save()
        messages.success(
            request,
            'El cliente fue restaurado correctamente.'
        )

        return redirect(
            'clientes:papelera_clientes'
        )

    contexto = {
        'cliente': cliente,
    }

    return render(
        request,
        'clientes/confirmar_restaurar.html',
        contexto
    )

# ============================================================
# REASIGNAR CLIENTE
# SACAR DE PAPELERA Y ASIGNAR A OTRO ASESOR
# SOLO MASTER
# ============================================================

@master_required
def reasignar_cliente(request, pk):

    cliente = get_object_or_404(
        Cliente,
        pk=pk,
        eliminado=True
    )

    # ========================================================
    # OBTENER ASESORES ACTIVOS
    # ========================================================

    asesores = User.objects.filter(
        groups__name='ASESOR',
        is_active=True
    ).distinct().order_by(
        'username'
    )


    # ========================================================
    # GUARDAR REASIGNACIÓN
    # ========================================================

    if request.method == 'POST':

        asesor_id = request.POST.get(
            'asesor'
        )

        if not asesor_id:

            messages.error(
                request,
                'Debe seleccionar un asesor.'
            )

            return redirect(
                'clientes:reasignar_cliente',
                pk=cliente.pk
            )


        nuevo_asesor = get_object_or_404(
            User,
            pk=asesor_id,
            groups__name='ASESOR',
            is_active=True
        )


        # ====================================================
        # REASIGNAR CLIENTE
        # ====================================================
        cliente.asesor = nuevo_asesor

        # Sacar de la papelera
        cliente.eliminado = False

        # Estado ACTIVO por que INACTIVO NO PUEDE VER EL ASESOR
        cliente.estado = 'ACTIVO'

        # Limpiar información de eliminación
        cliente.fecha_eliminacion = None

        cliente.eliminado_por = None

        cliente.save()


        messages.success(
            request,
            f'El cliente "{cliente.nombre_completo}" '
            f'fue reasignado correctamente a '
            f'{nuevo_asesor.username} y quedó en estado INACTIVO.'
        )


        return redirect(
            'clientes:cliente_lista'
        )
    # ========================================================
    # MOSTRAR FORMULARIO
    # ========================================================
    contexto = {
        'cliente': cliente,
        'asesores': asesores,
    }

    return render(
        request,
        'clientes/confirmar_reasignar.html',
        contexto
    )
# ============================================================
# ELIMINAR DEFINITIVAMENTE
# SEGUNDA CONFIRMACIÓN
# SOLO MASTER
# ============================================================

@master_required
def eliminar_definitivamente(request, pk):

    cliente = get_object_or_404(
        Cliente,
        pk=pk,
        eliminado=True
    )

    if request.method == 'POST':

        nombre_cliente = cliente.nombre_completo

        # Eliminación física de PostgreSQL
        cliente.delete()

        messages.success(
            request,
            f'El cliente "{nombre_cliente}" fue eliminado definitivamente.'
        )

        return redirect(
            'clientes:papelera_clientes'
        )

    contexto = {
        'cliente': cliente,
    }

    return render(
        request,
        'clientes/confirmar_eliminacion_definitiva.html',
        contexto
    )