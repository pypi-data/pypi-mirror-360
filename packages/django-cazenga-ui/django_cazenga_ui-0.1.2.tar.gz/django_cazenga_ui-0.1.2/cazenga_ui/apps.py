from django.apps import AppConfig

class CazengaUiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cazenga_ui'
    verbose_name = "Django Cazenga UI"

    def ready(self):
        """Executado quando a app é carregada"""
        pass
