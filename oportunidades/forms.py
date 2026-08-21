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
            'modalidad_venta',
            'precio_final',
            'cuota_inicial',
            'observaciones',
        ]

        widgets = {

            # ==================================================
            # NOMBRE
            # ==================================================

            'nombre': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': (
                        'Ejemplo: Compra de lote para vivienda'
                    ),
                }
            ),

            # ==================================================
            # ETAPA
            # ==================================================

            'etapa': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            # ==================================================
            # PRIORIDAD
            # ==================================================

            'prioridad': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            # ==================================================
            # PRESUPUESTO
            # ==================================================

            'presupuesto': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ejemplo: 15000.00',
                    'step': '0.01',
                    'min': '0',
                }
            ),

            # ==================================================
            # FECHA ESTIMADA DE COMPRA
            # ==================================================

            'fecha_estimada_compra': forms.DateInput(
                attrs={
                    'class': 'form-control',
                    'type': 'date',
                }
            ),

            # ==================================================
            # MODALIDAD DE VENTA
            # ==================================================

            'modalidad_venta': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            # ==================================================
            # PRECIO FINAL
            # USD
            # ==================================================

            'precio_final': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ejemplo: 11500.00',
                    'step': '0.01',
                    'min': '0',
                }
            ),

            # ==================================================
            # CUOTA INICIAL
            # USD
            # ==================================================

            'cuota_inicial': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ejemplo: 600.00',
                    'step': '0.01',
                    'min': '0',
                }
            ),

            # ==================================================
            # OBSERVACIONES
            # ==================================================

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