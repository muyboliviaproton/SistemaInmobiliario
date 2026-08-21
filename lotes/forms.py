from django import forms
from django.contrib.auth.models import User

from clientes.models import Cliente

from .models import (
    Lote,
    LoteAutorizacion,
    Reserva
)


# ============================================================
# FORMULARIO DE LOTE
# ============================================================

class LoteForm(forms.ModelForm):

    class Meta:

        model = Lote

        fields = [
            'uv',
            'manzano',
            'lote',
            'superficie_oficial',
            'frente',
            'fondo',
            'precio_total',
            'estado',
            'descripcion',
            'imagen_principal',
            'latitud_central',
            'longitud_central',
            'tipo_geometria',
            'coordenadas',
        ]

        widgets = {

            'uv': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej. 41'
                }
            ),

            'manzano': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej. 118'
                }
            ),

            'lote': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ej. 10A'
                }
            ),

            'superficie_oficial': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': 'Ej. 300'
                }
            ),

            'frente': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': 'Ej. 10'
                }
            ),

            'fondo': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': 'Ej. 30'
                }
            ),

            'precio_total': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.01',
                    'placeholder': 'Ej. 12000'
                }
            ),

            'estado': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder':
                        'Descripción comercial del lote...'
                }
            ),

            'imagen_principal':
                forms.ClearableFileInput(
                    attrs={
                        'class': 'form-control'
                    }
                ),

            'latitud_central': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.0000001'
                }
            ),

            'longitud_central': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'step': '0.0000001'
                }
            ),

            'tipo_geometria': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'coordenadas': forms.HiddenInput(),
        }

    def clean(self):

        cleaned_data = super().clean()

        uv = cleaned_data.get('uv')
        manzano = cleaned_data.get('manzano')
        lote = cleaned_data.get('lote')

        if uv and manzano and lote:

            codigo = f'{uv}-{manzano}-{lote}'

            consulta = Lote.objects.filter(
                codigo=codigo
            )

            if self.instance.pk:
                consulta = consulta.exclude(
                    pk=self.instance.pk
                )

            if consulta.exists():

                raise forms.ValidationError(
                    'Ya existe un lote con este código.'
                )

        return cleaned_data


# ============================================================
# FORMULARIO DE RESERVA
# ============================================================

class ReservaLoteForm(forms.ModelForm):

    class Meta:

        model = Reserva

        fields = [
            'tipo',
            'cliente',
            'observacion',
        ]

        widgets = {

            'tipo': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'cliente': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'observacion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder':
                        'Información privada de la reserva...'
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        usuario = kwargs.pop(
            'usuario',
            None
        )

        super().__init__(
            *args,
            **kwargs
        )

        # ----------------------------------------------------
        # SIN USUARIO
        # ----------------------------------------------------

        if not usuario:
            self.fields[
                'cliente'
            ].queryset = Cliente.objects.none()

            return

        # ----------------------------------------------------
        # MASTER
        # ----------------------------------------------------

        es_master = usuario.groups.filter(
            name='MASTER'
        ).exists()

        if es_master:

            self.fields[
                'cliente'
            ].queryset = Cliente.objects.filter(
                eliminado=False
            ).order_by(
                'nombre'
            )

        # ----------------------------------------------------
        # ASESOR
        # ----------------------------------------------------

        else:

            self.fields[
                'cliente'
            ].queryset = Cliente.objects.filter(
                asesor=usuario,
                eliminado=False
            ).order_by(
                'nombre'
            )


# ============================================================
# FORMULARIO DE AUTORIZACIÓN
# ============================================================

class LoteAutorizacionForm(
    forms.ModelForm
):

    class Meta:

        model = LoteAutorizacion

        fields = [
            'asesor_autorizado',
            'observacion',
        ]

        widgets = {

            'asesor_autorizado':
                forms.Select(
                    attrs={
                        'class': 'form-select'
                    }
                ),

            'observacion':
                forms.Textarea(
                    attrs={
                        'class': 'form-control',
                        'rows': 3,
                        'placeholder':
                            'Observación opcional...'
                    }
                ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(
            *args,
            **kwargs
        )

        self.fields[
            'asesor_autorizado'
        ].queryset = User.objects.filter(
            groups__name='ASESOR',
            is_active=True
        ).distinct().order_by(
            'first_name',
            'last_name',
            'username'
        )