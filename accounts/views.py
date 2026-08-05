from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.models import User, Group
from clientes.models import Cliente
from django.shortcuts import redirect, render


# ============================================================
# LOGIN
# ============================================================

class LoginUsuarioView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = False


# ============================================================
# LOGOUT
# ============================================================

class LogoutUsuarioView(LogoutView):
    next_page = '/accounts/login/'


# ============================================================
# INICIO DE ACCOUNTS
# ============================================================

def inicio_accounts(request):
    return redirect('login')


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
# PROTECCIÓN PARA MASTER
# ============================================================

def master_required(view_func):

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        if not request.user.groups.filter(
            name='MASTER'
        ).exists():

            return redirect('dashboard')

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# PROTECCIÓN PARA ASESOR
# ============================================================

def asesor_required(view_func):

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        if not request.user.groups.filter(
            name='ASESOR'
        ).exists():

            return redirect('dashboard')

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# DASHBOARD GENERAL
# ============================================================

@login_required
def dashboard(request):

    rol = obtener_rol_usuario(request.user)

    # Si es MASTER
    if rol == 'MASTER':

        return redirect('dashboard_master')


    # Si es ASESOR
    elif rol == 'ASESOR':

        return redirect('dashboard_asesor')


    # Si no tiene ningún rol
    return render(
        request,
        'accounts/sin_rol.html',
        {
            'usuario': request.user,
        }
    )

# ============================================================
# GESTIÓN DE USUARIOS / ASESORES
# SOLO MASTER
# ============================================================

@master_required
def usuarios_lista(request):

    usuarios = User.objects.filter(
        groups__name='ASESOR'
    ).distinct().order_by(
        'username'
    )

    contexto = {
        'usuarios': usuarios,
        'rol': 'MASTER',
    }

    return render(
        request,
        'accounts/usuarios_lista.html',
        contexto
    )
# ============================================================
# CREAR NUEVO ASESOR
# SOLO MASTER
# ============================================================

@master_required
def usuario_crear(request):

    if request.method == 'POST':

        username = request.POST.get(
            'username',
            ''
        ).strip()

        first_name = request.POST.get(
            'first_name',
            ''
        ).strip()

        last_name = request.POST.get(
            'last_name',
            ''
        ).strip()

        email = request.POST.get(
            'email',
            ''
        ).strip()

        password = request.POST.get(
            'password',
            ''
        )

        password_confirmacion = request.POST.get(
            'password_confirmacion',
            ''
        )

        # ====================================================
        # VALIDAR USUARIO
        # ====================================================

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(
                request,
                'El nombre de usuario ya existe.'
            )

            return render(
                request,
                'accounts/usuario_form.html'
            )


        # ====================================================
        # VALIDAR CONTRASEÑAS
        # ====================================================

        if password != password_confirmacion:

            messages.error(
                request,
                'Las contraseñas no coinciden.'
            )

            return render(
                request,
                'accounts/usuario_form.html'
            )


        # ====================================================
        # VALIDAR CONTRASEÑA VACÍA
        # ====================================================

        if not password:

            messages.error(
                request,
                'Debe ingresar una contraseña.'
            )

            return render(
                request,
                'accounts/usuario_form.html'
            )


        # ====================================================
        # CREAR USUARIO
        # ====================================================

        usuario = User.objects.create_user(

            username=username,

            first_name=first_name,

            last_name=last_name,

            email=email,

            password=password

        )


        # ====================================================
        # ASIGNAR GRUPO ASESOR
        # ====================================================

        grupo_asesor, creado = Group.objects.get_or_create(

            name='ASESOR'

        )

        usuario.groups.add(
            grupo_asesor
        )


        # ====================================================
        # MENSAJE
        # ====================================================

        messages.success(

            request,

            f'El asesor "{usuario.username}" fue registrado correctamente.'

        )


        return redirect(
            'usuarios_lista'
        )


    return render(
        request,
        'accounts/usuario_form.html'
    )
# ============================================================
# DASHBOARD MASTER
# ============================================================

@master_required
def dashboard_master(request):

    contexto = {
        'usuario': request.user,
        'rol': 'MASTER',
    }

    return render(
        request,
        'accounts/dashboard_master.html',
        contexto
    )


# ============================================================
# DASHBOARD ASESOR
# ============================================================

@asesor_required
def dashboard_asesor(request):

    contexto = {
        'usuario': request.user,
        'rol': 'ASESOR',
    }

    return render(
        request,
        'accounts/dashboard_asesor.html',
        contexto
    )
# ============================================================
# EDITAR ASESOR
# SOLO MASTER
# ============================================================

@master_required
def usuario_editar(request, pk):

    usuario = User.objects.filter(
        pk=pk,
        groups__name='ASESOR'
    ).first()

    if not usuario:

        messages.error(
            request,
            'El asesor no existe o no pertenece al grupo ASESOR.'
        )

        return redirect(
            'usuarios_lista'
        )


    if request.method == 'POST':

        usuario.first_name = request.POST.get(
            'first_name',
            ''
        ).strip()

        usuario.last_name = request.POST.get(
            'last_name',
            ''
        ).strip()

        usuario.email = request.POST.get(
            'email',
            ''
        ).strip()

        usuario.save()


        messages.success(
            request,
            f'El asesor "{usuario.username}" fue actualizado correctamente.'
        )


        return redirect(
            'usuarios_lista'
        )


    contexto = {

        'usuario': usuario,

    }


    return render(
        request,
        'accounts/usuario_editar.html',
        contexto
    )
# ============================================================
# ACTIVAR / DESACTIVAR ASESOR
# SOLO MASTER
# ============================================================

@master_required
def usuario_cambiar_estado(request, pk):

    usuario = User.objects.filter(
        pk=pk,
        groups__name='ASESOR'
    ).first()

    if not usuario:

        messages.error(
            request,
            'El asesor no existe o no pertenece al grupo ASESOR.'
        )

        return redirect(
            'usuarios_lista'
        )


    # Evitar que un usuario pueda cambiar su propio estado
    if usuario == request.user:

        messages.error(
            request,
            'No puedes cambiar el estado de tu propio usuario MASTER.'
        )

        return redirect(
            'usuarios_lista'
        )


    if request.method == 'POST':

        usuario.is_active = not usuario.is_active

        usuario.save(
            update_fields=[
                'is_active'
            ]
        )


        if usuario.is_active:

            messages.success(
                request,
                f'El asesor "{usuario.username}" fue activado correctamente.'
            )

        else:

            messages.warning(
                request,
                f'El asesor "{usuario.username}" fue desactivado correctamente.'
            )


        return redirect(
            'usuarios_lista'
        )


    contexto = {

        'usuario': usuario,

    }


    return render(
        request,
        'accounts/confirmar_cambio_estado.html',
        contexto
    )
# ============================================================
# CLIENTES DE UN ASESOR
# SOLO MASTER
# ============================================================

@master_required
def usuario_clientes(request, pk):

    asesor = User.objects.filter(
        pk=pk,
        groups__name='ASESOR'
    ).first()

    if not asesor:

        messages.error(
            request,
            'El asesor no existe o no pertenece al grupo ASESOR.'
        )

        return redirect(
            'usuarios_lista'
        )


    clientes = Cliente.objects.filter(
        asesor=asesor,
        eliminado=False
    ).order_by(
        '-fecha_registro'
    )


    contexto = {

        'asesor': asesor,

        'clientes': clientes,

    }


    return render(
        request,
        'accounts/usuario_clientes.html',
        contexto
    )
# ============================================================
# REASIGNAR CLIENTES DE UN ASESOR
# SOLO MASTER
# ============================================================

@master_required
def usuario_reasignar_clientes(request, pk):

    # ========================================================
    # BUSCAR ASESOR ACTUAL
    # ========================================================

    asesor_actual = User.objects.filter(
        pk=pk,
        groups__name='ASESOR'
    ).first()

    if not asesor_actual:

        messages.error(
            request,
            'El asesor no existe o no pertenece al grupo ASESOR.'
        )

        return redirect(
            'usuarios_lista'
        )


    # ========================================================
    # OBTENER CLIENTES ACTIVOS DEL ASESOR
    # ========================================================

    clientes = Cliente.objects.filter(
        asesor=asesor_actual,
        eliminado=False
    ).order_by(
        'nombre_completo'
    )


    # ========================================================
    # OBTENER OTROS ASESORES ACTIVOS
    # ========================================================

    asesores = User.objects.filter(
        groups__name='ASESOR',
        is_active=True
    ).exclude(
        pk=asesor_actual.pk
    ).distinct().order_by(
        'username'
    )


    # ========================================================
    # PROCESAR REASIGNACIÓN
    # ========================================================

    if request.method == 'POST':

        clientes_ids = request.POST.getlist(
            'clientes'
        )

        nuevo_asesor_id = request.POST.get(
            'nuevo_asesor'
        )


        # ====================================================
        # VALIDAR CLIENTES SELECCIONADOS
        # ====================================================

        if not clientes_ids:

            messages.error(
                request,
                'Debes seleccionar al menos un cliente para reasignar.'
            )

            return redirect(
                'usuario_reasignar_clientes',
                pk=pk
            )


        # ====================================================
        # VALIDAR NUEVO ASESOR
        # ====================================================

        nuevo_asesor = User.objects.filter(
            pk=nuevo_asesor_id,
            groups__name='ASESOR',
            is_active=True
        ).first()


        if not nuevo_asesor:

            messages.error(
                request,
                'El nuevo asesor seleccionado no es válido o está inactivo.'
            )

            return redirect(
                'usuario_reasignar_clientes',
                pk=pk
            )


        # ====================================================
        # EVITAR REASIGNACIÓN AL MISMO ASESOR
        # ====================================================

        if nuevo_asesor.pk == asesor_actual.pk:

            messages.error(
                request,
                'No puedes reasignar los clientes al mismo asesor.'
            )

            return redirect(
                'usuario_reasignar_clientes',
                pk=pk
            )


        # ====================================================
        # REASIGNAR CLIENTES
        # ====================================================

        clientes_reasignados = Cliente.objects.filter(
            id__in=clientes_ids,
            asesor=asesor_actual,
            eliminado=False
        )


        cantidad = clientes_reasignados.count()


        clientes_reasignados.update(
            asesor=nuevo_asesor
        )


        # ====================================================
        # MENSAJE DE CONFIRMACIÓN
        # ====================================================

        messages.success(
            request,
            f'Se reasignaron correctamente '
            f'{cantidad} cliente(s) de '
            f'"{asesor_actual.username}" a '
            f'"{nuevo_asesor.username}".'
        )


        return redirect(
            'usuario_clientes',
            pk=asesor_actual.pk
        )


    # ========================================================
    # CONTEXTO
    # ========================================================

    contexto = {

        'asesor_actual': asesor_actual,

        'clientes': clientes,

        'asesores': asesores,

    }


    return render(
        request,
        'accounts/usuario_reasignar_clientes.html',
        contexto
    )
# ============================================================
# CAMBIAR CONTRASEÑA DE ASESOR
# SOLO MASTER
# ============================================================

@master_required
def usuario_cambiar_password(request, pk):

    # ========================================================
    # BUSCAR ASESOR
    # ========================================================

    usuario = User.objects.filter(
        pk=pk,
        groups__name='ASESOR'
    ).first()


    # ========================================================
    # VALIDAR QUE EL USUARIO EXISTA
    # ========================================================

    if not usuario:

        messages.error(
            request,
            'El asesor no existe o no pertenece al grupo ASESOR.'
        )

        return redirect(
            'usuarios_lista'
        )


    # ========================================================
    # PROCESAR FORMULARIO
    # ========================================================

    if request.method == 'POST':

        password = request.POST.get(
            'password',
            ''
        )

        password_confirmacion = request.POST.get(
            'password_confirmacion',
            ''
        )


        # ====================================================
        # VALIDAR CONTRASEÑA VACÍA
        # ====================================================

        if not password:

            messages.error(
                request,
                'Debe ingresar una nueva contraseña.'
            )

            return render(
                request,
                'accounts/usuario_cambiar_password.html',
                {
                    'usuario': usuario,
                }
            )


        # ====================================================
        # VALIDAR LONGITUD
        # ====================================================

        if len(password) < 6:

            messages.error(
                request,
                'La contraseña debe tener al menos 6 caracteres.'
            )

            return render(
                request,
                'accounts/usuario_cambiar_password.html',
                {
                    'usuario': usuario,
                }
            )


        # ====================================================
        # VALIDAR CONFIRMACIÓN
        # ====================================================

        if password != password_confirmacion:

            messages.error(
                request,
                'Las contraseñas no coinciden.'
            )

            return render(
                request,
                'accounts/usuario_cambiar_password.html',
                {
                    'usuario': usuario,
                }
            )


        # ====================================================
        # CAMBIAR CONTRASEÑA
        # ====================================================

        usuario.set_password(
            password
        )

        usuario.save()


        # ====================================================
        # MENSAJE
        # ====================================================

        messages.success(

            request,

            f'La contraseña del asesor "{usuario.username}" '
            f'fue actualizada correctamente.'

        )


        # ====================================================
        # VOLVER A LISTA DE ASESORES
        # ====================================================

        return redirect(
            'usuarios_lista'
        )


    # ========================================================
    # MOSTRAR FORMULARIO
    # ========================================================

    contexto = {

        'usuario': usuario,

    }


    return render(

        request,

        'accounts/usuario_cambiar_password.html',

        contexto

    )