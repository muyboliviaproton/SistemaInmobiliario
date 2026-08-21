from django import forms

from .models import Visita


# ============================================================
# FORMULARIO DE VISITAS
# ============================================================

class VisitaForm(forms.ModelForm):

    class Meta:

        model = Visita

        fields = [
            'fecha',
            'hora',
            'lugar',
            'estado',
            'prioridad',
        ]

        widgets = {

            'fecha': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                }
            ),

            'hora': forms.TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control',
                }
            ),

            'lugar': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Lugar de encuentro',
                }
            ),

            'estado': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),

            'prioridad': forms.Select(
                attrs={
                    'class': 'form-select',
                }
            ),
        }