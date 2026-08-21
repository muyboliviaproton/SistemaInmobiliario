from django import forms
from django.contrib.auth.models import User

from .models import Cliente


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
                    'class': 'form-control',
                    'placeholder': 'Nombre completo del cliente',
                }
            ),

            'telefono': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Número de teléfono',
                }
            ),

            'whatsapp': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Número de WhatsApp',
                }
            ),

            'correo': forms.EmailInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'correo@ejemplo.com',
                }
            ),

            'direccion': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Dirección del cliente',
                }
            ),

            'capacidad_pago_mensual': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': '0.00',
                    'step': '0.01',
                    'min': '0',
                }
            ),

            'estado': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'observaciones': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Observaciones del cliente...',
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
                ).distinct().order_by(
                    'username'
                ),

                required=True,

                label='Asesor responsable',

                empty_label='Seleccione un asesor',

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


    # ========================================================
    # VALIDAR TELÉFONO
    # ========================================================

    def clean_telefono(self):

        telefono = self.cleaned_data.get(
            'telefono'
        )

        if not telefono:

            return telefono


        clientes = Cliente.objects.filter(
            telefono=telefono
        )


        # ----------------------------------------------------
        # AL EDITAR EXCLUIR EL CLIENTE ACTUAL
        # ----------------------------------------------------

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