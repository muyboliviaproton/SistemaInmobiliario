from django.urls import path

from . import views

app_name = 'oportunidades'
urlpatterns = [
    # ========================================================
    # LISTA PRINCIPAL
    # ========================================================
    path('',views.oportunidad_lista,name='oportunidad_lista'),
    # ========================================================
    # LISTA POR ETAPA
    # ========================================================
    path('etapa/<str:etapa>/',views.oportunidad_etapa,name='oportunidad_etapa'),
    # ========================================================
    # CREAR OPORTUNIDAD DESDE CLIENTE
    # ========================================================
    path(
        'cliente/<int:cliente_id>/nueva/',
        views.oportunidad_crear,
        name='oportunidad_crear'
    ),
    # ========================================================
    # EDITAR
    # ========================================================
    path(
        '<int:oportunidad_id>/editar/',
        views.oportunidad_editar,
        name='oportunidad_editar'
    ),
    # ========================================================
    # ELIMINAR
    # ========================================================
    path(
        '<int:oportunidad_id>/eliminar/',
        views.oportunidad_eliminar,
        name='oportunidad_eliminar'
    ),
    # ========================================================
    # DETALLE
    # ========================================================
    path(
        '<int:pk>/',
        views.oportunidad_detalle,
        name='oportunidad_detalle'
    ),
]