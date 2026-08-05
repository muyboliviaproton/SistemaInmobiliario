from django import forms
from .models import Cliente
from django.contrib.auth.models import User


class ClienteForm(forms.ModelForm):

    class Meta:

        model = Cliente

        fields = [
            'nombre_completo',
            'telefono',
            'whatsapp',
            'correo',
            'direccion',
            'capacidad_pago_mensual',
            'estado',
            'observaciones',
        ]

        widgets = {

            'nombre_completo': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'telefono': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'whatsapp': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'correo': forms.EmailInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'direccion': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'capacidad_pago_mensual': forms.NumberInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'estado': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'observaciones': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4
                }
            ),
        }


    # ========================================================
    # CONFIGURACIÓN DEL FORMULARIO
    # ========================================================

    def __init__(self, *args, **kwargs):

        self.es_master = kwargs.pop(
            'es_master',
            False
        )

        super().__init__(
            *args,
            **kwargs
        )


        # ====================================================
        # SOLO MASTER PUEDE SELECCIONAR ASESOR
        # ====================================================

        if self.es_master:

            self.fields['asesor'] = forms.ModelChoiceField(

                queryset=User.objects.filter(
                    groups__name='ASESOR',
                    is_active=True
                ).distinct(),

                required=True,

                label='Asesor responsable',

                widget=forms.Select(
                    attrs={
                        'class': 'form-select'
                    }
                )
            )


            # =================================================
            # MOSTRAR ASESOR ACTUAL AL EDITAR
            # =================================================

            if self.instance and self.instance.pk:

                self.fields['asesor'].initial = (
                    self.instance.asesor
                )

def clean_telefono(self):

        telefono = self.cleaned_data.get('telefono')

        if not telefono:
            return telefono

        # Buscar si ya existe otro cliente con este teléfono
        clientes = Cliente.objects.filter(
            telefono=telefono
        )

        # Si estamos editando, excluir el cliente actual
        if self.instance and self.instance.pk:

            clientes = clientes.exclude(
                pk=self.instance.pk
            )

        if clientes.exists():

            raise forms.ValidationError(
                '⚠️ Este número de teléfono ya está registrado. '
                'Verifique los datos del cliente.'
            )

        return telefono