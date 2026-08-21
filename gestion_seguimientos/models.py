from django.db import models
from django.contrib.auth.models import User
from clientes.models import Cliente
class Seguimiento(models.Model):
    # ============================================================
    # TIPOS DE CONTACTO
    # ============================================================
    TIPOS_CONTACTO = [
        ('LLAMADA', 'Llamada telefónica'),
        ('WHATSAPP', 'WhatsApp'),
        ('VISITA', 'Visita presencial'),
        ('MENSAJE', 'Mensaje'),
        ('CORREO', 'Correo electrónico'),
        ('OTRO', 'Otro'),
    ]
    # ============================================================
    # RESULTADOS DEL CONTACTO
    # ============================================================
    RESULTADOS = [
        ('SIN_RESPUESTA', 'Sin respuesta'),
        ('CONTACTADO', 'Contactado'),
        ('INTERESADO', 'Cliente interesado'),
        ('SEGUIMIENTO', 'Requiere seguimiento'),
        ('VISITA_AGENDADA', 'Visita agendada'),
        ('NEGOCIACION', 'En negociación'),
        ('VENTA', 'Venta realizada'),
        ('NO_INTERESADO', 'No interesado'),
    ]
    # ============================================================
    # ESTADOS COMERCIALES
    # ============================================================

    ESTADOS_COMERCIALES = [
        ('NUEVO', 'Cliente nuevo'),
        ('CONTACTADO', 'Contactado'),
        ('INTERESADO', 'Interesado'),
        ('VISITA', 'Visita programada'),
        ('NEGOCIACION', 'En negociación'),
        ('VENTA', 'Venta realizada'),
        ('NO_INTERESADO', 'No interesado'),
        ('PERDIDO', 'Cliente perdido'),
    ]


    # ============================================================
    # PRIORIDADES
    # ============================================================

    PRIORIDADES = [
        ('ALTA', 'Alta'),
        ('MEDIA', 'Media'),
        ('BAJA', 'Baja'),
    ]


    # ============================================================
    # CLIENTE
    # ============================================================

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='seguimientos'
    )


    # ============================================================
    # ASESOR QUE REALIZA EL SEGUIMIENTO
    # ============================================================

    asesor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='seguimientos_realizados'
    )


    # ============================================================
    # TIPO DE CONTACTO
    # ============================================================

    tipo_contacto = models.CharField(
        max_length=20,
        choices=TIPOS_CONTACTO
    )


    # ============================================================
    # RESULTADO DEL CONTACTO
    # ============================================================

    resultado = models.CharField(
        max_length=30,
        choices=RESULTADOS
    )


    # ============================================================
    # ESTADO COMERCIAL ACTUAL
    # ============================================================

    estado_comercial = models.CharField(
        max_length=30,
        choices=ESTADOS_COMERCIALES,
        default='NUEVO'
    )


    # ============================================================
    # PRIORIDAD
    # ============================================================

    prioridad = models.CharField(
        max_length=10,
        choices=PRIORIDADES,
        default='MEDIA'
    )


    # ============================================================
    # FECHA DEL CONTACTO
    # ============================================================

    fecha = models.DateTimeField(
        auto_now_add=True
    )


    # ============================================================
    # PRÓXIMA GESTIÓN
    # ============================================================

    proxima_gestion = models.DateTimeField(
        blank=True,
        null=True
    )


    # ============================================================
    # OBSERVACIONES
    # ============================================================

    observaciones = models.TextField(
        blank=True,
        null=True
    )
    # ============================================================
    # FECHA DE ACTUALIZACION DEL REGISTRO
    # ============================================================
    actualizado_en = models.DateTimeField(
        auto_now=True
    )
    # ============================================================
    # REPRESENTACIÓN DEL OBJETO
    # ============================================================

    def __str__(self):

        return (
            f"{self.cliente.nombre_completo} - "
            f"{self.get_tipo_contacto_display()}"
        )


    # ============================================================
    # CONFIGURACIÓN
    # ============================================================

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Seguimiento'
        verbose_name_plural = 'Seguimientos'