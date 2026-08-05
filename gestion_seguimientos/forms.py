from django import forms
from .models import Seguimiento


class SeguimientoForm(forms.ModelForm):

    class Meta:

        model = Seguimiento

        fields = [
            'tipo_contacto',
            'resultado',
            'estado_comercial',
            'prioridad',
            'proxima_gestion',
            'observaciones',
        ]

        widgets = {

            # ====================================================
            # TIPO DE CONTACTO
            # ====================================================

            'tipo_contacto': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),


            # ====================================================
            # RESULTADO
            # ====================================================

            'resultado': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),


            # ====================================================
            # ESTADO COMERCIAL
            # ====================================================

            'estado_comercial': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),


            # ====================================================
            # PRIORIDAD
            # ====================================================

            'prioridad': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),


            # ====================================================
            # PRÓXIMA GESTIÓN
            # ====================================================

            'proxima_gestion': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                }
            ),


            # ====================================================
            # OBSERVACIONES
            # ====================================================

            'observaciones': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': (
                        'Escriba los detalles del contacto '
                        'con el cliente...'
                    ),
                }
            ),
        }

        labels = {

            'tipo_contacto':
                'Tipo de contacto',

            'resultado':
                'Resultado del contacto',

            'estado_comercial':
                'Estado comercial',

            'prioridad':
                'Prioridad',

            'proxima_gestion':
                'Próxima gestión',

            'observaciones':
                'Observaciones',
        }