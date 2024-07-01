from django.apps import AppConfig
# from Fedeteria.utilities import iniciar_sucursales, iniciar_tags, inicializar_categorias_precios

class PublicoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'publico'

    # def ready(self):
    #     iniciar_sucursales()
    #     iniciar_tags()
    #     inicializar_categorias_precios()