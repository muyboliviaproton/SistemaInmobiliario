# ============================================================
# CONTEXT PROCESSORS
# Variables globales para todas las plantillas
# ============================================================
def datos_generales(request):
    es_master = False
    if request.user.is_authenticated:
        es_master = request.user.groups.filter(
            name='MASTER'
        ).exists()
    return {
        'es_master': es_master,
        'usuario': request.user,
    }