from django.db import models
from django.contrib.auth.models import User

from clientes.models import Cliente
from oportunidades.models import Oportunidad


# ============================================================
# VISITA
# ============================================================

class Visita(models.Model):

    # ========================================================
    # ESTADOS
    # ========================================================

    ESTADOS = [

        ('PENDIENTE', 'Pendiente'),

        ('CONFIRMADA', 'Confirmada'),

        ('REALIZADA', 'Realizada'),

        ('CANCELADA', 'Cancelada'),

    ]


    # ========================================================
    # PRIORIDAD
    # ========================================================

    PRIORIDADES = [

        ('BAJA', 'Baja'),

        ('MEDIA', 'Media'),

        ('ALTA', 'Alta'),

    ]


    # ========================================================
    # RELACIONES
    # ========================================================

    cliente = models.ForeignKey(

        Cliente,

        on_delete=models.CASCADE,

        related_name='visitas'

    )


    oportunidad = models.ForeignKey(

        Oportunidad,

        on_delete=models.SET_NULL,

        null=True,

        blank=True,

        related_name='visitas'

    )


    asesor = models.ForeignKey(

        User,

        on_delete=models.PROTECT

    )


    # ========================================================
    # DATOS DE LA VISITA
    # ========================================================

    fecha = models.DateField()

    hora = models.TimeField()

    lugar = models.CharField(

        max_length=200

    )


    estado = models.CharField(

        max_length=20,

        choices=ESTADOS,

        default='PENDIENTE'

    )


    prioridad = models.CharField(

        max_length=10,

        choices=PRIORIDADES,

        default='MEDIA'

    )


    resultado = models.TextField(

        blank=True

    )


    observaciones = models.TextField(

        blank=True

    )


    # ========================================================
    # AUDITORÍA
    # ========================================================

    fecha_creacion = models.DateTimeField(

        auto_now_add=True

    )


    fecha_modificacion = models.DateTimeField(

        auto_now=True

    )


    # ========================================================
    # ORDEN
    # ========================================================

    class Meta:

        ordering = [

            'fecha',

            'hora'

        ]


        verbose_name = 'Visita'

        verbose_name_plural = 'Visitas'


    # ========================================================
    # REPRESENTACIÓN
    # ========================================================

    def __str__(self):

        return (

            f'{self.cliente.nombre_completo} - '

            f'{self.fecha} {self.hora}'

        )