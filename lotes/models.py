from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# ============================================================
# MODELO LOTE
# ============================================================

class Lote(models.Model):
    # ========================================================
    # ESTADOS DEL LOTE
    # ========================================================
    ESTADOS = [
        ('DISPONIBLE', 'Disponible'),
        ('RESERVADO', 'Reservado'),
        ('VENDIDO', 'Vendido'),
    ]
    # ========================================================
    # TIPOS DE GEOMETRÍA
    # ========================================================
    TIPOS_GEOMETRIA = [
        ('PUNTO', 'Punto'),
        ('RECTANGULO', 'Rectángulo'),
        ('POLIGONO', 'Polígono'),
    ]
    # ========================================================
    # IDENTIFICACIÓN
    # ========================================================
    uv = models.CharField(
        max_length=20,
        verbose_name='UV'
    )
    manzano = models.CharField(
        max_length=20,
        verbose_name='Manzano'
    )

    lote = models.CharField(
        max_length=20,
        verbose_name='Lote'
    )

    codigo = models.CharField(
        max_length=70,
        unique=True,
        editable=False,
        verbose_name='Código de lote'
    )

    # ========================================================
    # ASESOR CREADOR
    # ========================================================

    asesor_creador = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='lotes_creados',
        limit_choices_to={
            'groups__name': 'ASESOR'
        },
        verbose_name='Asesor creador'
    )

    # ========================================================
    # BAJA LÓGICA
    # ========================================================

    activo = models.BooleanField(
        default=True,
        verbose_name='Lote activo'
    )

    # ========================================================
    # SUPERFICIES
    # ========================================================

    superficie_oficial = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name='Superficie oficial (m²)'
    )

    superficie_calculada = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Superficie calculada en mapa (m²)'
    )

    # ========================================================
    # DIMENSIONES
    # ========================================================

    frente = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Frente (m)'
    )

    fondo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Fondo (m)'
    )

    # ========================================================
    # INFORMACIÓN COMERCIAL
    # ========================================================

    precio_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name='Precio total'
    )

    precio_m2 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        editable=False,
        verbose_name='Precio por m²'
    )

    # ========================================================
    # ESTADO COMERCIAL
    # ========================================================

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='DISPONIBLE',
        verbose_name='Estado'
    )

    # ========================================================
    # DESCRIPCIÓN COMERCIAL
    # ========================================================

    descripcion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Descripción'
    )

    # ========================================================
    # IMAGEN
    # ========================================================

    imagen_principal = models.ImageField(
        upload_to='lotes/',
        blank=True,
        null=True,
        verbose_name='Imagen principal'
    )

    # ========================================================
    # GEOLOCALIZACIÓN
    # ========================================================

    latitud_central = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name='Latitud central'
    )

    longitud_central = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name='Longitud central'
    )

    tipo_geometria = models.CharField(
        max_length=20,
        choices=TIPOS_GEOMETRIA,
        default='POLIGONO',
        verbose_name='Tipo de geometría'
    )

    coordenadas = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Coordenadas del perímetro'
    )

    # ========================================================
    # FECHAS
    # ========================================================

    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización'
    )

    # ========================================================
    # GUARDAR
    # ========================================================

    def save(self, *args, **kwargs):

        # ----------------------------------------------------
        # GENERAR CÓDIGO AUTOMÁTICO
        # ----------------------------------------------------

        self.codigo = (
            f'{self.uv}-'
            f'{self.manzano}-'
            f'{self.lote}'
        )

        # ----------------------------------------------------
        # CALCULAR PRECIO POR M²
        # ----------------------------------------------------

        if (
            self.precio_total is not None
            and self.superficie_oficial
            and self.superficie_oficial > 0
        ):

            self.precio_m2 = (
                self.precio_total /
                self.superficie_oficial
            ).quantize(
                Decimal('0.01')
            )

        else:

            self.precio_m2 = None

        super().save(*args, **kwargs)

    # ========================================================
    # NOMBRE DEL ASESOR CREADOR
    # ========================================================

    @property
    def nombre_asesor_creador(self):

        if not self.asesor_creador:
            return 'Sin asesor'

        nombre = self.asesor_creador.get_full_name()

        return (
            nombre
            if nombre
            else self.asesor_creador.username
        )

    # ========================================================
    # RESERVA ACTIVA
    # ========================================================

    @property
    def reserva_activa(self):

        reserva = self.reservas.filter(
            estado='ACTIVA'
        ).first()

        # ----------------------------------------------------
        # SI YA VENCIÓ, NO DEBE CONSIDERARSE ACTIVA
        # ----------------------------------------------------

        if reserva and reserva.esta_vencida:

            return None

        return reserva

    # ========================================================
    # REPRESENTACIÓN
    # ========================================================

    def __str__(self):

        return self.codigo

    # ========================================================
    # META
    # ========================================================

    class Meta:

        ordering = [
            'uv',
            'manzano',
            'lote'
        ]

        verbose_name = 'Lote'
        verbose_name_plural = 'Lotes'


# ============================================================
# AUTORIZACIÓN DE LOTES
# ============================================================

class LoteAutorizacion(models.Model):

    ESTADOS = [
        ('ACTIVA', 'Activa'),
        ('REVOCADA', 'Revocada'),
    ]

    # ========================================================
    # LOTE
    # ========================================================

    lote = models.ForeignKey(
        Lote,
        on_delete=models.CASCADE,
        related_name='autorizaciones',
        verbose_name='Lote'
    )

    # ========================================================
    # ASESOR AUTORIZADO
    # ========================================================

    asesor_autorizado = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='lotes_autorizados',
        limit_choices_to={
            'groups__name': 'ASESOR'
        },
        verbose_name='Asesor autorizado'
    )

    # ========================================================
    # INFORMACIÓN
    # ========================================================

    fecha_autorizacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de autorización'
    )

    fecha_revocacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de revocación'
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='ACTIVA',
        verbose_name='Estado'
    )

    observacion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observación'
    )

    # ========================================================
    # REPRESENTACIÓN
    # ========================================================

    def __str__(self):

        return (
            f'{self.lote.codigo} → '
            f'{self.asesor_autorizado.username}'
        )

    # ========================================================
    # META
    # ========================================================

    class Meta:

        ordering = [
            '-fecha_autorizacion'
        ]

        verbose_name = 'Autorización de lote'
        verbose_name_plural = 'Autorizaciones de lotes'


# ============================================================
# RESERVA
# ============================================================

class Reserva(models.Model):

    # ========================================================
    # TIPOS DE RESERVA
    # ========================================================

    TIPOS_RESERVA = [
        (
            'NORMAL',
            'Normal - 72 horas'
        ),
        (
            'ESPECIAL',
            'Especial - 120 horas'
        ),
        (
            'EXCEPCIONAL',
            'Excepcional - 10 días'
        ),
    ]

    # ========================================================
    # ESTADOS
    # ========================================================

    ESTADOS = [
        ('ACTIVA', 'Activa'),
        ('VENCIDA', 'Vencida'),
        ('CANCELADA', 'Cancelada'),
        (
            'CONVERTIDA_VENTA',
            'Convertida en venta'
        ),
    ]

    # ========================================================
    # LOTE
    # ========================================================

    lote = models.ForeignKey(
        Lote,
        on_delete=models.PROTECT,
        related_name='reservas',
        verbose_name='Lote'
    )

    # ========================================================
    # CLIENTE
    # ========================================================

    cliente = models.ForeignKey(
        'clientes.Cliente',
        on_delete=models.PROTECT,
        related_name='reservas',
        verbose_name='Cliente'
    )

    # ========================================================
    # ASESOR RESPONSABLE
    # ========================================================

    asesor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='reservas_realizadas',
        verbose_name='Asesor responsable'
    )

    # ========================================================
    # TIPO
    # ========================================================

    tipo = models.CharField(
        max_length=20,
        choices=TIPOS_RESERVA,
        default='NORMAL',
        verbose_name='Tipo de reserva'
    )

    # ========================================================
    # FECHAS
    # ========================================================

    fecha_inicio = models.DateTimeField(
        default=timezone.now,
        verbose_name='Inicio de reserva'
    )

    fecha_vencimiento = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Vencimiento'
    )

    # ========================================================
    # ESTADO
    # ========================================================

    estado = models.CharField(
        max_length=25,
        choices=ESTADOS,
        default='ACTIVA',
        verbose_name='Estado'
    )

    # ========================================================
    # RENOVACIÓN
    # ========================================================

    renovada = models.BooleanField(
        default=False,
        verbose_name='Reserva renovada'
    )

    fecha_renovacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de renovación'
    )

    # ========================================================
    # INFORMACIÓN PRIVADA
    # ========================================================

    observacion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observación privada'
    )

    # ========================================================
    # FECHAS DE CONTROL
    # ========================================================

    fecha_registro = models.DateTimeField(
        auto_now_add=True
    )

    fecha_actualizacion = models.DateTimeField(
        auto_now=True
    )

    # ========================================================
    # DURACIÓN
    # ========================================================

    def obtener_duracion(self):

        if self.tipo == 'NORMAL':

            return timedelta(
                hours=72
            )

        if self.tipo == 'ESPECIAL':

            return timedelta(
                hours=120
            )

        if self.tipo == 'EXCEPCIONAL':

            return timedelta(
                days=10
            )

        return timedelta(
            hours=72
        )

    # ========================================================
    # GUARDAR
    # ========================================================

    def save(self, *args, **kwargs):

        if not self.fecha_inicio:

            self.fecha_inicio = timezone.now()

        if not self.fecha_vencimiento:

            self.fecha_vencimiento = (
                self.fecha_inicio +
                self.obtener_duracion()
            )

        super().save(*args, **kwargs)

    # ========================================================
    # VENCIMIENTO
    # ========================================================

    @property
    def esta_vencida(self):

        return (
            self.estado == 'ACTIVA'
            and
            self.fecha_vencimiento is not None
            and
            timezone.now() >=
            self.fecha_vencimiento
        )

    # ========================================================
    # TIEMPO RESTANTE
    # ========================================================

    @property
    def tiempo_restante(self):

        if not self.fecha_vencimiento:

            return None

        restante = (
            self.fecha_vencimiento -
            timezone.now()
        )

        if restante.total_seconds() <= 0:

            return timedelta(0)

        return restante

    # ========================================================
    # REPRESENTACIÓN
    # ========================================================

    def __str__(self):

        return (
            f'Reserva {self.lote.codigo} - '
            f'{self.cliente}'
        )

    # ========================================================
    # META
    # ========================================================

    class Meta:

        ordering = [
            '-fecha_inicio'
        ]

        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'