from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from clientes.models import Cliente

from .forms import OportunidadForm
from .models import Oportunidad


# ============================================================
# LISTA DE OPORTUNIDADES
# ============================================================

@login_required
def oportunidad_lista(request):

    # ========================================================
    # VERIFICAR SI EL USUARIO ES MASTER
    # ========================================================

    es_master = request.user.groups.filter(
        name='MASTER'
    ).exists()


    # ========================================================
    # OBTENER TODAS LAS OPORTUNIDADES
    # ========================================================

    if es_master:

        oportunidades = Oportunidad.objects.all()

    else:

        # ====================================================
        # EL ASESOR SOLO VE SUS PROPIAS OPORTUNIDADES
        # ====================================================

        oportunidades = Oportunidad.objects.filter(
            asesor=request.user
        )


    # ========================================================
    # CARGAR RELACIONES
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

    }


    # ========================================================
    # MOSTRAR LISTA
    # ========================================================

    return render(

        request,

        'oportunidades/oportunidad_lista.html',

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


            # =================================================
            # ASIGNAR CLIENTE
            # =================================================

            oportunidad.cliente = cliente


            # =================================================
            # ASIGNAR ASESOR
            # =================================================

            oportunidad.asesor = request.user


            # =================================================
            # GUARDAR
            # =================================================

            oportunidad.save()


            # =================================================
            # VOLVER A LA LISTA
            # =================================================

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


    # ========================================================
    # MOSTRAR FORMULARIO
    # ========================================================

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

        Oportunidad,

        id=oportunidad_id

    )


    # ========================================================
    # VERIFICAR SI EL USUARIO ES MASTER
    # ========================================================

    es_master = request.user.groups.filter(

        name='MASTER'

    ).exists()


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
    # PROCESAR FORMULARIO
    # ========================================================

    if request.method == 'POST':

        form = OportunidadForm(

            request.POST,

            instance=oportunidad

        )


        if form.is_valid():

            form.save()


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


    # ========================================================
    # MOSTRAR FORMULARIO
    # ========================================================

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

    # ========================================================
    # BUSCAR OPORTUNIDAD
    # ========================================================

    oportunidad = get_object_or_404(

        Oportunidad,

        id=oportunidad_id

    )


    # ========================================================
    # VERIFICAR SI EL USUARIO ES MASTER
    # ========================================================

    es_master = request.user.groups.filter(

        name='MASTER'

    ).exists()


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


    # ========================================================
    # MOSTRAR CONFIRMACIÓN
    # ========================================================

    return render(

        request,

        'oportunidades/oportunidad_confirmar_eliminar.html',

        contexto

    )

# ========================================================
# MOSTRAR CONFIRMACIÓN
# ========================================================
@login_required
def oportunidad_detalle(request, pk):

    oportunidad = get_object_or_404(
        Oportunidad,
        id=pk
    )

    return render(
        request,
        'oportunidades/oportunidad_detalle.html',
        {
            'oportunidad': oportunidad,
        }
    )