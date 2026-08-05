from django import forms

from .models import Oportunidad


class OportunidadForm(forms.ModelForm):

    class Meta:

        model = Oportunidad

        fields = [
            'nombre',
            'etapa',
            'prioridad',
            'presupuesto',
            'fecha_estimada_compra',
            'observaciones',
        ]

        widgets = {

            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': (
                        'Ejemplo: Compra de lote para vivienda'
                    ),
                }
            ),

            'etapa': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'prioridad': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'presupuesto': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ejemplo: 15000',
                    'step': '0.01',
                }
            ),

            'fecha_estimada_compra': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),

            'observaciones': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 5,
                    'placeholder': (
                        'Escriba información adicional '
                        'sobre esta oportunidad comercial...'
                    ),
                }
            ),

        }