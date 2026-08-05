from django.db import models
from django.contrib.auth.models import User


class Cliente(models.Model):
    ESTADOS = [
        ('NUEVO', 'Nuevo'),
        ('CONTACTADO', 'Contactado'),
        ('INTERESADO', 'Interesado'),
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]


    # ========================================================
    # ASESOR RESPONSABLE
    # ========================================================

    asesor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='clientes',
        limit_choices_to={
            'groups__name': 'ASESOR'
        },
        verbose_name='Asesor'
    )
    # ========================================================
    # DATOS DEL CLIENTE
    # ========================================================
    nombre_completo = models.CharField(
        max_length=150
    )

    telefono = models.CharField(
    max_length=30,
    unique=True,
    verbose_name='Teléfono'
    )
    
    whatsapp = models.CharField(
        max_length=30,
        blank=True,
        null=True
    )

    correo = models.EmailField(
        blank=True,
        null=True
    )

    direccion = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )


    capacidad_pago_mensual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True
    )


    # ========================================================
    # ESTADO
    # ========================================================

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='NUEVO'
    )


    # ========================================================
    # OBSERVACIONES
    # ========================================================
    observaciones = models.TextField(
        blank=True,
        null=True
    )


    # ========================================================
    # CONTROL DE REGISTRO
    # ========================================================
    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True
    )

    # ========================================================
    # PAPELERA
    # ========================================================

    eliminado = models.BooleanField(
        default=False
    )


    fecha_eliminacion = models.DateTimeField(
        blank=True,
        null=True
    )


    eliminado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='clientes_eliminados'
    )


    def __str__(self):
        return self.nombre_completo