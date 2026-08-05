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

            'resultado',

            'observaciones',

        ]


        widgets = {

            # =================================================
            # FECHA
            # =================================================

            'fecha': forms.DateInput(

                attrs={

                    'type': 'date',

                    'class': 'form-control',

                }

            ),


            # =================================================
            # HORA
            # =================================================

            'hora': forms.TimeInput(

                attrs={

                    'type': 'time',

                    'class': 'form-control',

                }

            ),


            # =================================================
            # LUGAR
            # =================================================

            'lugar': forms.TextInput(

                attrs={

                    'class': 'form-control',

                    'placeholder': 'Lugar de encuentro',

                }

            ),


            # =================================================
            # ESTADO
            # =================================================

            'estado': forms.Select(

                attrs={

                    'class': 'form-select',

                }

            ),


            # =================================================
            # PRIORIDAD
            # =================================================

            'prioridad': forms.Select(

                attrs={

                    'class': 'form-select',

                }

            ),


            # =================================================
            # RESULTADO
            # =================================================

            'resultado': forms.Textarea(

                attrs={

                    'class': 'form-control',

                    'rows': 4,

                }

            ),


            # =================================================
            # OBSERVACIONES
            # =================================================

            'observaciones': forms.Textarea(

                attrs={

                    'class': 'form-control',

                    'rows': 4,

                }

            ),

        }