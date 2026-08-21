from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django import forms


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
# OBTENER ROL
# ============================================================
def obtener_rol_usuario(usuario):

    if usuario.groups.filter(name='MASTER').exists():
        return 'MASTER'

    elif usuario.groups.filter(name='ASESOR').exists():
        return 'ASESOR'

    return None


# ============================================================
# PROTECCIÓN MASTER
# ============================================================

def master_required(view_func):

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        if not request.user.groups.filter(
            name='MASTER'
        ).exists():

            return redirect('dashboard:inicio')

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# PROTECCIÓN ASESOR
# ============================================================

def asesor_required(view_func):

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        if not request.user.groups.filter(
            name='ASESOR'
        ).exists():

            return redirect('dashboard:inicio')

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper


# ============================================================
# LISTA DE ASESORES
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
# CREAR ASESOR
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

        if password != password_confirmacion:

            messages.error(
                request,
                'Las contraseñas no coinciden.'
            )

            return render(
                request,
                'accounts/usuario_form.html'
            )

        if not password:

            messages.error(
                request,
                'Debe ingresar una contraseña.'
            )

            return render(
                request,
                'accounts/usuario_form.html'
            )

        usuario = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )

        grupo_asesor, creado = Group.objects.get_or_create(
            name='ASESOR'
        )

        usuario.groups.add(
            grupo_asesor
        )

        messages.success(
            request,
            f'El asesor "{usuario.username}" '
            'fue registrado correctamente.'
        )

        return redirect(
            'accounts:usuarios_lista'
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
# FORMULARIO PARA EDITAR ASESOR
# ============================================================

class AsesorEditarForm(forms.ModelForm):

    class Meta:

        model = User

        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
        ]

        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
        }

        widgets = {

            'username': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'readonly': 'readonly',
                }
            ),

            'first_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'last_name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                }
            ),

        }


# ============================================================
# EDITAR ASESOR
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
            'accounts:usuarios_lista'
        )

    # ========================================================
    # GUARDAR CAMBIOS
    # ========================================================

    if request.method == 'POST':

        form = AsesorEditarForm(
            request.POST,
            instance=usuario
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                f'El asesor "{usuario.username}" '
                'fue actualizado correctamente.'
            )

            return redirect(
                'accounts:usuarios_lista'
            )

    # ========================================================
    # MOSTRAR DATOS ACTUALES
    # ========================================================

    else:

        form = AsesorEditarForm(
            instance=usuario
        )

    contexto = {

        'usuario': usuario,

        'form': form,

    }

    return render(
        request,
        'accounts/usuario_editar.html',
        contexto
    )


# ============================================================
# CAMBIAR ESTADO
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
            'accounts:usuarios_lista'
        )

    if usuario == request.user:

        messages.error(
            request,
            'No puedes cambiar el estado de tu propio usuario MASTER.'
        )

        return redirect(
            'accounts:usuarios_lista'
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
                f'El asesor "{usuario.username}" '
                'fue activado correctamente.'
            )

        else:

            messages.warning(
                request,
                f'El asesor "{usuario.username}" '
                'fue desactivado correctamente.'
            )

        return redirect(
            'accounts:usuarios_lista'
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
# CLIENTES DEL ASESOR
# ============================================================

@master_required
def usuario_clientes(request, pk):

    from clientes.models import Cliente

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
            'accounts:usuarios_lista'
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
# REASIGNAR CLIENTES
# ============================================================

@master_required
def usuario_reasignar_clientes(request, pk):

    from clientes.models import Cliente

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
            'accounts:usuarios_lista'
        )

    clientes = Cliente.objects.filter(
        asesor=asesor_actual,
        eliminado=False
    ).order_by(
        'nombre_completo'
    )

    asesores = User.objects.filter(
        groups__name='ASESOR',
        is_active=True
    ).exclude(
        pk=asesor_actual.pk
    ).distinct().order_by(
        'username'
    )

    if request.method == 'POST':

        clientes_ids = request.POST.getlist(
            'clientes'
        )

        nuevo_asesor_id = request.POST.get(
            'nuevo_asesor'
        )

        if not clientes_ids:

            messages.error(
                request,
                'Debes seleccionar al menos un cliente para reasignar.'
            )

            return redirect(
                'accounts:usuario_reasignar_clientes',
                pk=pk
            )

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
                'accounts:usuario_reasignar_clientes',
                pk=pk
            )

        if nuevo_asesor.pk == asesor_actual.pk:

            messages.error(
                request,
                'No puedes reasignar los clientes al mismo asesor.'
            )

            return redirect(
                'accounts:usuario_reasignar_clientes',
                pk=pk
            )

        clientes_reasignados = Cliente.objects.filter(
            id__in=clientes_ids,
            asesor=asesor_actual,
            eliminado=False
        )

        cantidad = clientes_reasignados.count()

        clientes_reasignados.update(
            asesor=nuevo_asesor
        )

        messages.success(
            request,
            f'Se reasignaron correctamente '
            f'{cantidad} cliente(s) de '
            f'"{asesor_actual.username}" a '
            f'"{nuevo_asesor.username}".'
        )

        return redirect(
            'accounts:usuario_clientes',
            pk=asesor_actual.pk
        )

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
# CAMBIAR CONTRASEÑA
# ============================================================

@master_required
def usuario_cambiar_password(request, pk):

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
            'accounts:usuarios_lista'
        )

    if request.method == 'POST':

        password = request.POST.get(
            'password',
            ''
        )

        password_confirmacion = request.POST.get(
            'password_confirmacion',
            ''
        )

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

        usuario.set_password(
            password
        )

        usuario.save()

        messages.success(
            request,
            f'La contraseña del asesor "{usuario.username}" '
            'fue actualizada correctamente.'
        )

        return redirect(
            'accounts:usuarios_lista'
        )

    contexto = {
        'usuario': usuario,
    }

    return render(
        request,
        'accounts/usuario_cambiar_password.html',
        contexto
    )