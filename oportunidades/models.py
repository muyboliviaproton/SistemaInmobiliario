from django.db import models
from django.contrib.auth.models import User

from clientes.models import Cliente


class Oportunidad(models.Model):

    # ========================================================
    # ETAPAS DEL PROCESO COMERCIAL
    # ========================================================

    ETAPAS = [

        ('NUEVO', 'Nuevo'),

        ('CONTACTADO', 'Contactado'),

        ('INTERESADO', 'Cliente interesado'),

        ('VISITA_PENDIENTE', 'Visita pendiente'),

        ('VISITA_REALIZADA', 'Visita realizada'),

        ('NEGOCIACION', 'En negociación'),

        ('RESERVA', 'Reserva'),

        ('VENTA_CERRADA', 'Venta cerrada'),

        ('PERDIDA', 'Oportunidad perdida'),

    ]


    # ========================================================
    # NIVELES DE PRIORIDAD
    # ========================================================

    PRIORIDADES = [

        ('BAJA', 'Baja'),

        ('MEDIA', 'Media'),

        ('ALTA', 'Alta'),

        ('URGENTE', 'Urgente'),

    ]


    # ========================================================
    # CLIENTE
    # ========================================================

    cliente = models.ForeignKey(

        Cliente,

        on_delete=models.CASCADE,

        related_name='oportunidades'

    )


    # ========================================================
    # ASESOR RESPONSABLE
    # ========================================================

    asesor = models.ForeignKey(

        User,

        on_delete=models.PROTECT,

        related_name='oportunidades'

    )


    # ========================================================
    # NOMBRE DE LA OPORTUNIDAD
    # ========================================================

    nombre = models.CharField(

        max_length=150

    )


    # ========================================================
    # ETAPA COMERCIAL
    # ========================================================

    etapa = models.CharField(

        max_length=30,

        choices=ETAPAS,

        default='NUEVO'

    )


    # ========================================================
    # PRIORIDAD
    # ========================================================

    prioridad = models.CharField(

        max_length=20,

        choices=PRIORIDADES,

        default='MEDIA'

    )


    # ========================================================
    # PRESUPUESTO ESTIMADO
    # ========================================================

    presupuesto = models.DecimalField(

        max_digits=12,

        decimal_places=2,

        null=True,

        blank=True

    )


    # ========================================================
    # FECHA ESTIMADA DE COMPRA
    # ========================================================

    fecha_estimada_compra = models.DateField(

        null=True,

        blank=True

    )


    # ========================================================
    # OBSERVACIONES
    # ========================================================

    observaciones = models.TextField(

        blank=True,

        null=True

    )


    # ========================================================
    # FECHAS DE CONTROL
    # ========================================================

    creado_en = models.DateTimeField(

        auto_now_add=True

    )


    actualizado_en = models.DateTimeField(

        auto_now=True

    )


    # ========================================================
    # REPRESENTACIÓN
    # ========================================================

    def __str__(self):

        return (

            f"{self.nombre} - "

            f"{self.cliente.nombre_completo}"

        )


    # ========================================================
    # CONFIGURACIÓN
    # ========================================================

    class Meta:

        ordering = [

            '-creado_en'

        ]

        verbose_name = 'Oportunidad'

        verbose_name_plural = 'Oportunidades'