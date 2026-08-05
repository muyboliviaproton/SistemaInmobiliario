from django.contrib import admin
from .models import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):

    list_display = (
        'nombre_completo',
        'telefono',
        'whatsapp',
        'asesor',
        'estado',
        'fecha_registro',
    )

    list_filter = (
        'estado',
        'asesor',
        'fecha_registro',
    )

    search_fields = (
        'nombre_completo',
        'telefono',
        'whatsapp',
        'correo',
    )

    ordering = (
        '-fecha_registro',
    )